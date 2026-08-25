#!/usr/bin/env python3
"""Validate P003 canonical frame and reused instrument digests."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
P002 = REPO / "experiments" / "scope-pilot-002"
EXPECTED_CODEBOOK = "3c9261450ffe3553a984788e5f764cc4f829624155b53b5272ae4ebc3f7f8e01"
EXPECTED_PROMPT = "9b4c3c277b263d350d8dd22bac8f7d4444e98134f1b1e7a64fc6b1f3e174abf1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []
    frame = load(BASE / "sampling-frame.json")
    identities = load(BASE / "repository-identities.json")["repositories"]
    repositories = [name for values in frame["repositories"].values() for name in values]

    if len(repositories) != 24 or len(set(repositories)) != 24:
        errors.append("frame must contain 24 unique literal repository names")
    if len(identities) != 24:
        errors.append("identity file must contain 24 repositories")
    identity_names = [item["requested"] for item in identities]
    if identity_names != repositories:
        errors.append("identity order/names do not match frame")
    ids = [item["id"] for item in identities]
    if len(ids) != len(set(ids)):
        errors.append("canonical repository IDs are not unique")
    aliases = [item for item in identities if item["requested"] != item["canonical"]]
    if aliases:
        errors.append(f"frame contains non-canonical aliases: {aliases}")
    archived = [item["canonical"] for item in identities if item["archived"]]
    if archived:
        errors.append(f"frame contains archived repositories: {archived}")

    if digest(P002 / "CODEBOOK.md") != EXPECTED_CODEBOOK:
        errors.append("reused codebook digest changed")
    if digest(P002 / "CODER-PROMPT.md") != EXPECTED_PROMPT:
        errors.append("reused coder prompt digest changed")
    for name in ("coding.schema.json", "control-key.json"):
        if not (P002 / name).exists():
            errors.append(f"missing reused P002 artifact: {name}")
    if len(list((P002 / "controls").glob("CTRL*.json"))) != 4:
        errors.append("reused control set is not exactly four packets")

    if frame["pilot"] != "SCOPE-PILOT-003" or frame["seed"] != "SCOPE-PILOT-003":
        errors.append("P003 pilot or seed changed")
    if frame["per_query"] != {"maximum_results": 100, "sort": "created", "order": "asc"}:
        errors.append("P003 per-query boundary changed")
    if len(frame["query_terms"]) != 7:
        errors.append("P003 query terms changed")

    old_candidates = load(REPO / "experiments" / "scope-pilot-001" / "candidates.json")["candidates"]
    old_repositories = {item["repository"].lower() for item in old_candidates}
    overlap = sorted(name for name in repositories if name.lower() in old_repositories)
    if overlap:
        errors.append(f"P003 frame overlaps P001: {overlap}")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(
        f"PASS: P003 canonical frame; repos={len(repositories)}, unique_ids={len(set(ids))}, "
        f"queries={len(repositories) * len(frame['query_terms'])}; reused_codebook={EXPECTED_CODEBOOK}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
