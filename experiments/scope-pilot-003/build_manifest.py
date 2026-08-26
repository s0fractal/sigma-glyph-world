#!/usr/bin/env python3
"""Freeze a minimized, auditable evidence manifest for every screened candidate.

Codex review 2026-08-26, finding 5: the 168 search checkpoints are committed but
the evidence behind the 60 substantive screening decisions is not, so another
reviewer can reproduce that the decisions were written in order but not why they
were correct at the retrieved time.

This is built from `evidence-cache/`, the evidence actually used at screening
time, so `retrieved_at` and every digest are the originals. Bodies and comments
are truncated to a fixed budget: enough to audit a decision, short of
republishing third-party threads in full. Digests cover the untruncated API
responses.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent
CACHE = BASE / "evidence-cache"
AUDIT = BASE / "evidence-audit"
LOG = BASE / "screening-log.json"
MANIFEST = BASE / "evidence-manifest.json"

BODY_BUDGET = 900
COMMENT_BUDGET = 400


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def clip(text: str, budget: int) -> dict[str, Any]:
    text = text or ""
    return {
        "sha256": digest(text),
        "chars": len(text),
        "truncated": len(text) > budget,
        "excerpt": text[:budget],
    }


def entry(position: int, decision: dict[str, Any]) -> dict[str, Any]:
    evidence = json.loads((CACHE / f"C{position:03d}.json").read_text(encoding="utf-8"))
    audit_path = AUDIT / f"C{position:03d}.json"
    record: dict[str, Any] = {
        "position": position,
        "url": evidence["url"],
        "repository": evidence["repository"],
        "number": evidence["number"],
        "stratum": evidence["stratum"],
        "matched_terms": evidence["matched_terms"],
        "retrieved_at": evidence["retrieved_at"],
        "issue_response_sha256": evidence["issue_response_sha256"],
        "comments_response_sha256": evidence["comments_response_sha256"],
        "title": evidence["title"],
        "labels": evidence["labels"],
        "state": evidence["state"],
        "state_reason": evidence["state_reason"],
        "created_at": evidence["created_at"],
        "closed_at": evidence["closed_at"],
        "comment_count_at_screening": evidence["comment_count"],
        "body": clip(evidence["body"], BODY_BUDGET),
        "comments": [
            {
                "id": comment["id"],
                "author": comment["author"],
                "author_association": comment["author_association"],
                "created_at": comment["created_at"],
                **clip(comment["body"], COMMENT_BUDGET),
            }
            for comment in evidence["comments"]
        ],
        "decision": decision["decision"],
        "reason_code": decision["reason_code"],
        "reason": decision["reason"],
        "evidence_urls": decision["evidence_urls"],
    }
    if "sampling_assessment" in decision:
        record["sampling_assessment"] = decision["sampling_assessment"]

    # The original fetcher did not paginate. Where a thread exceeded one page it
    # was re-fetched later, and the audit is recorded rather than backdated.
    if audit_path.exists():
        audited = json.loads(audit_path.read_text(encoding="utf-8"))
        seen = {comment["id"] for comment in evidence["comments"]}
        missed = [comment for comment in audited["comments"] if comment["id"] not in seen]
        record["completeness_audit"] = {
            "reason": "the screening-time fetch requested one page and did not paginate",
            "audited_at": audited["retrieved_at"],
            "declared_comment_total": audited["declared_comment_total"],
            "comments_missing_at_screening": len(missed),
            "comments_page_sha256": audited["comments_page_sha256"],
            "missed": [
                {
                    "author": comment["author"],
                    "author_association": comment["author_association"],
                    "created_at": comment["created_at"],
                    **clip(comment["body"], COMMENT_BUDGET),
                }
                for comment in missed
            ],
        }
        record["comments_complete_at_screening"] = False
    else:
        record["comments_complete_at_screening"] = evidence["comment_count"] < 100
    return record


def main() -> int:
    if MANIFEST.exists():
        print("refusing to overwrite a frozen evidence manifest", file=sys.stderr)
        return 1
    log = json.loads(LOG.read_text(encoding="utf-8"))
    entries = [entry(decision["position"], decision) for decision in log["entries"]]
    document = {
        "pilot": "SCOPE-PILOT-003",
        "built_from": "evidence-cache/, the evidence used at screening time",
        "body_budget_chars": BODY_BUDGET,
        "comment_budget_chars": COMMENT_BUDGET,
        "note": (
            "Excerpts are truncated; digests cover the untruncated API responses. This "
            "manifest makes each screening decision auditable against the evidence "
            "available when it was made. It does not validate the decision: screen.py "
            "checks identity, order, enums and caps, never the substance of a reason."
        ),
        "screened": len(entries),
        "incomplete_at_screening": [e["position"] for e in entries if not e["comments_complete_at_screening"]],
        "entries": entries,
    }
    temporary = MANIFEST.with_name(f".{MANIFEST.name}.tmp")
    temporary.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, MANIFEST)
    print(f"froze {len(entries)} evidence entries; "
          f"incomplete at screening: {document['incomplete_at_screening']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
