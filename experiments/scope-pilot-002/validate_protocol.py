#!/usr/bin/env python3
"""Validate frozen SCOPE-PILOT-002 protocol artifacts before search."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []
    frame = load(BASE / "sampling-frame.json")
    schema = load(BASE / "coding.schema.json")
    key = load(BASE / "control-key.json")
    prereg = (REPO / "experiments" / "SCOPE-PILOT-002-preregistration.md").read_text(encoding="utf-8")

    repositories = [repository for values in frame["repositories"].values() for repository in values]
    if len(repositories) != 24 or len(set(repositories)) != 24:
        errors.append("sampling frame must contain 24 unique repositories")
    if len(frame["repositories"]) != 4 or any(len(values) != 6 for values in frame["repositories"].values()):
        errors.append("sampling frame must have four strata of six repositories")
    if len(frame["query_terms"]) != 7 or len(set(frame["query_terms"])) != 7:
        errors.append("sampling frame must have seven unique query terms")
    if frame["stop"] != {
        "admitted": 12,
        "screened": 60,
        "minimum_to_code": 8,
        "maximum_per_repository": 2,
        "minimum_control_kinds": 3,
    }:
        errors.append("sampling stop rule changed")
    if frame.get("per_query") != {"maximum_results": 100, "sort": "created", "order": "asc"}:
        errors.append("per-query result boundary changed")

    old_candidates = load(REPO / "experiments" / "scope-pilot-001" / "candidates.json")["candidates"]
    old_repositories = {candidate["repository"].lower() for candidate in old_candidates}
    overlap = sorted(repository for repository in repositories if repository.lower() in old_repositories)
    if overlap:
        errors.append(f"fresh frame overlaps SCOPE-PILOT-001: {overlap}")

    for repository in repositories:
        if repository not in prereg:
            errors.append(f"repository missing from preregistration: {repository}")
    for term in frame["query_terms"]:
        if f'"{term}"' not in prereg:
            errors.append(f"query term missing from preregistration: {term}")

    controls = sorted((BASE / "controls").glob("CTRL*.json"))
    if len(controls) != 4:
        errors.append("exactly four controls must be frozen")
    control_ids = []
    forbidden = ("github.com", "laravel", "kyverno", "ghidra", "pest", "sonar")
    for path in controls:
        control = load(path)
        control_ids.append(control.get("blind_id"))
        text = path.read_text(encoding="utf-8").lower()
        leaked = [word for word in forbidden if word in text]
        if leaked:
            errors.append(f"{path.name}: identity leak {leaked}")
        evidence_ids = [item.get("id") for item in control.get("evidence", [])]
        if not evidence_ids or len(evidence_ids) != len(set(evidence_ids)):
            errors.append(f"{path.name}: invalid evidence ids")

    key_ids = [item.get("blind_id") for item in key.get("controls", [])]
    if control_ids != key_ids:
        errors.append(f"control/key mismatch: packets={control_ids}, key={key_ids}")

    required_schema_fields = set(schema.get("required", []))
    if {"admission", "success_contract", "components", "scope", "receipt"} - required_schema_fields:
        errors.append("coding schema lost required instrument fields")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(
        "PASS: protocol frozen; "
        f"repos={len(repositories)}, strata={len(frame['repositories'])}, terms={len(frame['query_terms'])}, controls={len(controls)}; "
        f"codebook_sha256={digest(BASE / 'CODEBOOK.md')}; "
        f"prompt_sha256={digest(BASE / 'CODER-PROMPT.md')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
