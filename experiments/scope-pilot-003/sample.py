#!/usr/bin/env python3
"""Append-only, resumable sampler for SCOPE-PILOT-003."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parent
CHECKPOINTS = BASE / "query-checkpoints"
FAILURES = BASE / "query-failures"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def atomic_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    if path.exists() or temporary.exists():
        raise RuntimeError(f"refusing to overwrite {path}")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def sanitize_error(value: str) -> str:
    value = re.sub(r"ghp_[A-Za-z0-9]+", "[REDACTED]", value)
    value = re.sub(r"github_pat_[A-Za-z0-9_]+", "[REDACTED]", value)
    return value.strip()


def expected_queries(frame: dict[str, Any], identities: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    index = 0
    for stratum, repositories in frame["repositories"].items():
        for repository in repositories:
            identity = identities[repository]
            for term in frame["query_terms"]:
                index += 1
                query = (
                    f'repo:{repository} is:issue is:{frame["candidate_state"]} '
                    f'created:{frame["created_from"]}..{frame["created_to"]} "{term}"'
                )
                result.append(
                    {
                        "index": index,
                        "stratum": stratum,
                        "repository": repository,
                        "repository_id": identity["id"],
                        "term": term,
                        "query": query,
                    }
                )
    return result


def run_query(expected: dict[str, Any], per_query: dict[str, Any]) -> tuple[dict[str, Any], str]:
    command = [
        "gh",
        "api",
        "-X",
        "GET",
        "search/issues",
        "-f",
        f"q={expected['query']}",
        "-f",
        f"sort={per_query['sort']}",
        "-f",
        f"order={per_query['order']}",
        "-f",
        f"per_page={per_query['maximum_results']}",
    ]
    completed = subprocess.run(command, check=False, capture_output=True)
    raw = completed.stdout
    if completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(sanitize_error(stderr) or f"gh api exited {completed.returncode}")
    return json.loads(raw), sha256_bytes(raw)


def minimize_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "url": item["html_url"],
        "number": item["number"],
        "title": item["title"],
        "created_at": item["created_at"],
        "closed_at": item.get("closed_at"),
    }


def validate_checkpoint(path: Path, expected: dict[str, Any], frame_sha256: str) -> dict[str, Any]:
    checkpoint = load(path)
    for field in ("index", "stratum", "repository", "repository_id", "term", "query"):
        if checkpoint.get(field) != expected[field]:
            raise ValueError(f"{path.name}: {field} mismatch")
    if checkpoint.get("frame_sha256") != frame_sha256:
        raise ValueError(f"{path.name}: frame digest mismatch")
    if checkpoint.get("returned") != len(checkpoint.get("items", [])):
        raise ValueError(f"{path.name}: returned/item count mismatch")
    return checkpoint


def checkpoint_path(index: int) -> Path:
    return CHECKPOINTS / f"Q{index:03d}.json"


def freeze(frame: dict[str, Any], checkpoints: list[dict[str, Any]]) -> None:
    order_path = BASE / "candidate-order.json"
    receipts_path = BASE / "query-receipts.json"
    if order_path.exists() or receipts_path.exists():
        raise RuntimeError("refusing to overwrite frozen candidate artifacts")

    candidates: dict[str, dict[str, Any]] = {}
    receipts: list[dict[str, Any]] = []
    for checkpoint in checkpoints:
        receipts.append({key: value for key, value in checkpoint.items() if key != "items"})
        for item in checkpoint["items"]:
            candidate = candidates.setdefault(
                item["url"],
                {
                    **item,
                    "repository": checkpoint["repository"],
                    "repository_id": checkpoint["repository_id"],
                    "stratum": checkpoint["stratum"],
                    "matched_terms": [],
                },
            )
            candidate["matched_terms"].append(checkpoint["term"])

    ordered: list[dict[str, Any]] = []
    for candidate in candidates.values():
        candidate["matched_terms"] = sorted(set(candidate["matched_terms"]))
        candidate["order_sha256"] = sha256_text(frame["seed"] + "\n" + candidate["url"])
        ordered.append(candidate)
    ordered.sort(key=lambda item: item["order_sha256"])
    frozen_at = utc_now()
    atomic_write(
        order_path,
        {
            "pilot": frame["pilot"],
            "frozen_at": frozen_at,
            "ordering": frame["ordering"],
            "candidate_count": len(ordered),
            "candidates": ordered,
        },
    )
    atomic_write(
        receipts_path,
        {
            "pilot": frame["pilot"],
            "frozen_at": frozen_at,
            "query_count": len(receipts),
            "queries": receipts,
        },
    )
    print(f"froze {len(ordered)} unique candidates from {len(receipts)} checkpoints", flush=True)


def collect(frame: dict[str, Any], identities: dict[str, dict[str, Any]], frame_sha256: str) -> int:
    if (BASE / "candidate-order.json").exists() or (BASE / "query-receipts.json").exists():
        print("refusing collection after final freeze", file=sys.stderr)
        return 1
    queries = expected_queries(frame, identities)
    checkpoints: list[dict[str, Any]] = []
    queried_this_run = 0

    for expected in queries:
        path = checkpoint_path(expected["index"])
        if path.exists():
            checkpoints.append(validate_checkpoint(path, expected, frame_sha256))
            continue
        retrieved_at = utc_now()
        try:
            response, raw_sha256 = run_query(expected, frame["per_query"])
        except Exception as exc:
            stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            failure = {
                **expected,
                "frame_sha256": frame_sha256,
                "failed_at": retrieved_at,
                "error": sanitize_error(str(exc)),
            }
            atomic_write(FAILURES / f"F{expected['index']:03d}-{stamp}.json", failure)
            print(f"query {expected['index']}/{len(queries)} failed; receipt retained", file=sys.stderr)
            return 1

        items = [minimize_item(item) for item in response.get("items", [])]
        checkpoint = {
            **expected,
            "frame_sha256": frame_sha256,
            "retrieved_at": retrieved_at,
            "total_count": response.get("total_count"),
            "incomplete_results": response.get("incomplete_results"),
            "returned": len(items),
            "raw_response_sha256": raw_sha256,
            "items": items,
        }
        atomic_write(path, checkpoint)
        checkpoints.append(checkpoint)
        queried_this_run += 1
        print(
            f"query {expected['index']}/{len(queries)}: {expected['repository']} / {expected['term']!r} -> {len(items)}",
            flush=True,
        )
        if expected["index"] < len(queries):
            time.sleep(2.1)

    freeze(frame, checkpoints)
    print(f"new queries this run: {queried_this_run}", flush=True)
    return 0


def check(frame: dict[str, Any], identities: dict[str, dict[str, Any]], frame_sha256: str) -> int:
    errors: list[str] = []
    queries = expected_queries(frame, identities)
    checkpoints: list[dict[str, Any]] = []
    for expected in queries:
        path = checkpoint_path(expected["index"])
        if path.exists():
            try:
                checkpoints.append(validate_checkpoint(path, expected, frame_sha256))
            except (ValueError, json.JSONDecodeError) as exc:
                errors.append(str(exc))

    for path in sorted(FAILURES.glob("F*.json")) if FAILURES.exists() else []:
        try:
            failure = load(path)
            if failure.get("frame_sha256") != frame_sha256:
                errors.append(f"{path.name}: failure frame digest mismatch")
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}: {exc}")

    order_path = BASE / "candidate-order.json"
    receipts_path = BASE / "query-receipts.json"
    if order_path.exists() != receipts_path.exists():
        errors.append("final order and receipts must appear together")
    if order_path.exists() and receipts_path.exists():
        if len(checkpoints) != len(queries):
            errors.append("final artifacts exist without every success checkpoint")
        order_doc = load(order_path)
        receipt_doc = load(receipts_path)
        candidates = order_doc.get("candidates", [])
        if candidates != sorted(candidates, key=lambda item: item["order_sha256"]):
            errors.append("candidate order is not hash-sorted")
        urls = [item["url"] for item in candidates]
        if len(urls) != len(set(urls)):
            errors.append("candidate order contains duplicate URLs")
        for item in candidates:
            if item["order_sha256"] != sha256_text(frame["seed"] + "\n" + item["url"]):
                errors.append(f"candidate order hash mismatch: {item['url']}")
        if receipt_doc.get("query_count") != len(queries):
            errors.append("final receipt query count mismatch")
    elif len(checkpoints) == len(queries):
        errors.append("all checkpoints exist but final artifacts are absent")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    failures = len(list(FAILURES.glob("F*.json"))) if FAILURES.exists() else 0
    frozen = order_path.exists()
    print(f"PASS: P003 sampling state; checkpoints={len(checkpoints)}/{len(queries)}, failures={failures}, frozen={str(frozen).lower()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collect", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.collect == args.check:
        parser.error("choose exactly one of --collect or --check")

    frame_path = BASE / "sampling-frame.json"
    frame = load(frame_path)
    identities_doc = load(BASE / "repository-identities.json")
    identities = {item["requested"]: item for item in identities_doc["repositories"]}
    frame_sha256 = sha256_bytes(frame_path.read_bytes())
    return collect(frame, identities, frame_sha256) if args.collect else check(frame, identities, frame_sha256)


if __name__ == "__main__":
    raise SystemExit(main())
