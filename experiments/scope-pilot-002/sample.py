#!/usr/bin/env python3
"""Collect and freeze the preregistered SCOPE-PILOT-002 candidate order."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parent


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def query_issues(query: str, per_query: dict[str, Any]) -> tuple[dict[str, Any], str]:
    command = [
        "gh",
        "api",
        "-X",
        "GET",
        "search/issues",
        "-f",
        f"q={query}",
        "-f",
        f"sort={per_query['sort']}",
        "-f",
        f"order={per_query['order']}",
        "-f",
        f"per_page={per_query['maximum_results']}",
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or f"gh api exited {completed.returncode}")
    raw = completed.stdout
    return json.loads(raw), sha256_text(raw)


def validate_frozen(frame: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    order_path = BASE / "candidate-order.json"
    receipt_path = BASE / "query-receipts.json"
    if not order_path.exists() and not receipt_path.exists():
        return errors
    if not order_path.exists() or not receipt_path.exists():
        return ["candidate order and query receipts must appear together"]

    order_doc = load(order_path)
    receipt_doc = load(receipt_path)
    candidates = order_doc.get("candidates", [])
    expected = sorted(candidates, key=lambda item: item["order_sha256"])
    if candidates != expected:
        errors.append("candidate order is not ascending by order_sha256")
    urls = [item.get("url") for item in candidates]
    if len(urls) != len(set(urls)):
        errors.append("candidate order contains duplicate URLs")
    for item in candidates:
        expected_hash = sha256_text(frame["seed"] + "\n" + item["url"])
        if item.get("order_sha256") != expected_hash:
            errors.append(f"bad order hash for {item.get('url')}")
    expected_queries = sum(len(values) for values in frame["repositories"].values()) * len(frame["query_terms"])
    if len(receipt_doc.get("queries", [])) != expected_queries:
        errors.append(f"expected {expected_queries} query receipts")
    return errors


def collect(frame: dict[str, Any]) -> None:
    query_receipts: list[dict[str, Any]] = []
    candidates: dict[str, dict[str, Any]] = {}
    total_queries = sum(len(values) for values in frame["repositories"].values()) * len(frame["query_terms"])
    query_number = 0

    for stratum, repositories in frame["repositories"].items():
        for repository in repositories:
            for term in frame["query_terms"]:
                query_number += 1
                query = (
                    f'repo:{repository} is:issue is:{frame["candidate_state"]} '
                    f'created:{frame["created_from"]}..{frame["created_to"]} "{term}"'
                )
                retrieved_at = dt.datetime.now(dt.timezone.utc).isoformat()
                response, raw_sha256 = query_issues(query, frame["per_query"])
                items = response.get("items", [])
                query_receipts.append(
                    {
                        "stratum": stratum,
                        "repository": repository,
                        "term": term,
                        "query": query,
                        "retrieved_at": retrieved_at,
                        "total_count": response.get("total_count"),
                        "incomplete_results": response.get("incomplete_results"),
                        "returned": len(items),
                        "raw_response_sha256": raw_sha256,
                    }
                )
                for issue in items:
                    url = issue["html_url"]
                    candidate = candidates.setdefault(
                        url,
                        {
                            "url": url,
                            "repository": repository,
                            "stratum": stratum,
                            "number": issue["number"],
                            "title": issue["title"],
                            "created_at": issue["created_at"],
                            "closed_at": issue.get("closed_at"),
                            "matched_terms": [],
                        },
                    )
                    candidate["matched_terms"].append(term)
                print(
                    f"query {query_number}/{total_queries}: {repository!s} / {term!r} -> {len(items)}",
                    flush=True,
                )
                if query_number < total_queries:
                    time.sleep(2.1)

    ordered = []
    for candidate in candidates.values():
        candidate["matched_terms"] = sorted(set(candidate["matched_terms"]))
        candidate["order_sha256"] = sha256_text(frame["seed"] + "\n" + candidate["url"])
        ordered.append(candidate)
    ordered.sort(key=lambda item: item["order_sha256"])

    collected_at = dt.datetime.now(dt.timezone.utc).isoformat()
    order_doc = {
        "pilot": frame["pilot"],
        "collected_at": collected_at,
        "ordering": frame["ordering"],
        "candidate_count": len(ordered),
        "candidates": ordered,
    }
    receipt_doc = {
        "pilot": frame["pilot"],
        "collected_at": collected_at,
        "query_count": len(query_receipts),
        "queries": query_receipts,
    }
    (BASE / "candidate-order.json").write_text(json.dumps(order_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (BASE / "query-receipts.json").write_text(json.dumps(receipt_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(ordered)} unique candidates and {len(query_receipts)} receipts")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collect", action="store_true", help="query GitHub and write frozen artifacts")
    parser.add_argument("--check", action="store_true", help="validate existing frozen artifacts if present")
    args = parser.parse_args()
    if args.collect == args.check:
        parser.error("choose exactly one of --collect or --check")

    frame = load(BASE / "sampling-frame.json")
    if args.collect:
        if (BASE / "candidate-order.json").exists() or (BASE / "query-receipts.json").exists():
            print("refusing to overwrite frozen sampling artifacts", file=sys.stderr)
            return 1
        collect(frame)

    errors = validate_frozen(frame)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    state = "present" if (BASE / "candidate-order.json").exists() else "not collected"
    print(f"PASS: sampling artifacts {state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
