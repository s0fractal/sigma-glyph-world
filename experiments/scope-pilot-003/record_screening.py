#!/usr/bin/env python3
"""Append screening decisions to screening-log.json.

Decisions arrive on stdin as a JSON list of objects with `position`, `decision`,
`reason_code`, `reason`, optional `evidence_urls`, and optional
`sampling_assessment`. Identity and evidence provenance are filled in from the
frozen candidate order and the evidence cache so a decision cannot silently
disagree with the sample it was drawn from.
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ORDER = BASE / "candidate-order.json"
CACHE = BASE / "evidence-cache"
LOG = BASE / "screening-log.json"
CODEBOOK = "3c9261450ffe3553a984788e5f764cc4f829624155b53b5272ae4ebc3f7f8e01"
ORDER_DIGEST = "2e3d00332101e7ce90e4d186584b4b5cb09906f6bf337d869091dd6600f12bfb"


def main() -> int:
    decisions = json.load(sys.stdin)
    order = json.loads(ORDER.read_text(encoding="utf-8"))["candidates"]
    log = (
        json.loads(LOG.read_text(encoding="utf-8"))
        if LOG.exists()
        else {"pilot": "SCOPE-PILOT-003", "codebook_sha256": CODEBOOK, "order_sha256": ORDER_DIGEST, "entries": []}
    )
    now = dt.datetime.now(dt.timezone.utc).isoformat()

    for decision in decisions:
        position = decision["position"]
        if position != len(log["entries"]) + 1:
            raise SystemExit(f"position {position} does not continue the frozen-order prefix")
        frozen = order[position - 1]
        evidence = json.loads((CACHE / f"C{position:03d}.json").read_text(encoding="utf-8"))
        if evidence["url"] != frozen["url"]:
            raise SystemExit(f"position {position}: evidence cache does not match frozen candidate")
        entry = {
            "position": position,
            "url": frozen["url"],
            "repository": frozen["repository"],
            "repository_id": frozen["repository_id"],
            "stratum": frozen["stratum"],
            "screened_at": now,
            "evidence_retrieved_at": evidence["retrieved_at"],
            "evidence_sha256": {
                "issue": evidence["issue_response_sha256"],
                "comments": evidence["comments_response_sha256"],
            },
            "decision": decision["decision"],
            "reason_code": decision["reason_code"],
            "reason": decision["reason"],
            "evidence_urls": decision.get("evidence_urls", [frozen["url"]]),
        }
        if "sampling_assessment" in decision:
            entry["sampling_assessment"] = decision["sampling_assessment"]
        log["entries"].append(entry)

    LOG.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"recorded {len(decisions)} decisions; log now holds {len(log['entries'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
