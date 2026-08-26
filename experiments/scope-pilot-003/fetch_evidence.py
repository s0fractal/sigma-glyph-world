#!/usr/bin/env python3
"""Fetch primary evidence for candidates in frozen screening order.

Read-only. Caches one minimized record per candidate with its retrieval time
and the SHA-256 of each raw API response, so a screening decision can cite a
stable primary URL and a timestamp without re-querying GitHub.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parent
CACHE = BASE / "evidence-cache"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def api(path: str, page: int = 1) -> tuple[Any, str]:
    completed = subprocess.run(
        ["gh", "api", "-X", "GET", path, "-f", "per_page=100", "-f", f"page={page}"],
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.decode("utf-8", errors="replace").strip())
    return json.loads(completed.stdout), sha256_bytes(completed.stdout)


def api_all(path: str) -> tuple[list[Any], list[str]]:
    """Page to exhaustion.

    The first version of this tool requested per_page=100 without paginating and
    recorded `comment_count` as the number of items it happened to fetch, so a
    thread with more than 100 comments was silently truncated and indistinguishable
    from a complete one. Codex review 2026-08-26, finding 8.
    """
    items: list[Any] = []
    digests: list[str] = []
    page = 1
    while True:
        batch, digest = api(path, page)
        digests.append(digest)
        items.extend(batch)
        if len(batch) < 100:
            return items, digests
        page += 1


def fetch(candidate: dict[str, Any]) -> dict[str, Any]:
    repository = candidate["repository"]
    number = candidate["number"]
    retrieved_at = utc_now()
    issue, issue_sha = api(f"repos/{repository}/issues/{number}")
    comments, comment_digests = api_all(f"repos/{repository}/issues/{number}/comments")
    return {
        "position": candidate["position"],
        "url": candidate["url"],
        "repository": repository,
        "repository_id": candidate["repository_id"],
        "number": number,
        "stratum": candidate["stratum"],
        "matched_terms": candidate["matched_terms"],
        "retrieved_at": retrieved_at,
        "issue_response_sha256": issue_sha,
        "comments_response_sha256": comment_digests[0],
        "comments_page_sha256": comment_digests,
        "comments_pages": len(comment_digests),
        "comments_complete": True,
        "declared_comment_total": issue.get("comments"),
        "title": issue["title"],
        "state": issue["state"],
        "state_reason": issue.get("state_reason"),
        "created_at": issue["created_at"],
        "closed_at": issue.get("closed_at"),
        "labels": [label["name"] for label in issue.get("labels", [])],
        "is_pull_request": "pull_request" in issue,
        "body": issue.get("body") or "",
        "comment_count": len(comments),
        "comments": [
            {
                "id": comment["id"],
                "author": comment["user"]["login"] if comment.get("user") else None,
                "author_association": comment.get("author_association"),
                "created_at": comment["created_at"],
                "body": comment.get("body") or "",
            }
            for comment in comments
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from", dest="start", type=int, required=True, help="1-based position in frozen order")
    parser.add_argument("--count", type=int, default=10)
    args = parser.parse_args()

    order = json.loads((BASE / "candidate-order.json").read_text(encoding="utf-8"))["candidates"]
    CACHE.mkdir(exist_ok=True)
    for offset in range(args.start, args.start + args.count):
        if offset > len(order):
            break
        path = CACHE / f"C{offset:03d}.json"
        if path.exists():
            print(f"{offset}: cached", flush=True)
            continue
        candidate = {**order[offset - 1], "position": offset}
        try:
            record = fetch(candidate)
        except Exception as exc:
            print(f"{offset}: FETCH_FAILED {exc}", file=sys.stderr, flush=True)
            path.write_text(
                json.dumps(
                    {**candidate, "retrieved_at": utc_now(), "fetch_error": str(exc)},
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            continue
        path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{offset}: {record['repository']}#{record['number']} comments={record['comment_count']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
