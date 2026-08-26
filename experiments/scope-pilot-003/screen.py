#!/usr/bin/env python3
"""Screening-log validator and status reporter for SCOPE-PILOT-003.

The screening log is a research record, not a computed artifact: admission
decisions are made by the packet builder against codebook v1 and written into
`screening-log.json`. This module only enforces the preregistered constraints
so that a green `tools/test-all.sh` cannot silently mean "screening skipped".
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parent
ORDER = BASE / "candidate-order.json"
LOG = BASE / "screening-log.json"
SCHEMA = BASE / "screening.schema.json"
MANIFEST = BASE / "evidence-manifest.json"

MANIFEST_REQUIRED = True   # every screened position must appear in evidence-manifest.json

MAX_SCREENED = 60
MAX_ADMITTED = 12
MIN_ADMITTED = 8
MAX_PER_REPOSITORY = 2
MIN_CONTROL_KINDS = 3
MIN_PER_EXPECTED_COMPONENT = 2
EXPECTED_COMPONENTS = ("selector", "adapter", "gate")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_entry_shape(entry: dict[str, Any], schema: dict[str, Any], errors: list[str]) -> None:
    item = schema["properties"]["entries"]["items"]
    label = f"position {entry.get('position')}"
    for field in item["required"]:
        if field not in entry:
            errors.append(f"{label}: missing field {field}")
    for field in entry:
        if field not in item["properties"]:
            errors.append(f"{label}: unexpected field {field}")
    for field, spec in item["properties"].items():
        if field not in entry or "enum" not in spec:
            continue
        if entry[field] not in spec["enum"]:
            errors.append(f"{label}: {field}={entry[field]!r} not in enum")


def evaluate(order: list[dict[str, Any]], log: dict[str, Any], schema: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    entries = log.get("entries", [])

    if log.get("pilot") != "SCOPE-PILOT-003":
        errors.append("screening log pilot mismatch")
    if log.get("order_sha256") != digest(ORDER):
        errors.append("screening log was written against a different candidate order")
    if log.get("codebook_sha256") != schema["properties"]["codebook_sha256"]["const"]:
        errors.append("screening log codebook digest mismatch")

    for offset, entry in enumerate(entries):
        check_entry_shape(entry, schema, errors)
        expected_position = offset + 1
        if entry.get("position") != expected_position:
            errors.append(f"entry {offset}: position {entry.get('position')} breaks frozen order prefix")
            continue
        frozen = order[offset]
        for field in ("url", "repository", "repository_id", "stratum"):
            if entry.get(field) != frozen[field]:
                errors.append(f"position {expected_position}: {field} does not match frozen candidate order")
        if entry.get("decision") == "ADMIT":
            if entry.get("reason_code") != "ADMITTED":
                errors.append(f"position {expected_position}: ADMIT requires reason_code ADMITTED")
            if "sampling_assessment" not in entry:
                errors.append(f"position {expected_position}: ADMIT requires sampling_assessment")
            elif entry["sampling_assessment"].get("control_kind") != frozen["stratum"]:
                errors.append(f"position {expected_position}: control_kind must equal the frozen stratum")
        else:
            if entry.get("reason_code") in ("ADMITTED",):
                errors.append(f"position {expected_position}: non-ADMIT requires an evidential reason code")
            if "sampling_assessment" in entry:
                errors.append(f"position {expected_position}: only ADMIT may carry sampling_assessment")
        if entry.get("decision") == "CAPPED" and entry.get("reason_code") != "REPOSITORY_CAP_REACHED":
            errors.append(f"position {expected_position}: CAPPED requires reason_code REPOSITORY_CAP_REACHED")
        if entry.get("decision") == "REJECT" and entry.get("reason_code") == "REPOSITORY_CAP_REACHED":
            errors.append(f"position {expected_position}: repository cap is CAPPED, not REJECT")

    # Codex review 2026-08-26, finding 5: decisions must be auditable against the
    # evidence available when they were made, not merely well-ordered.
    if MANIFEST_REQUIRED and entries:
        if not MANIFEST.exists():
            errors.append("screening log exists without evidence-manifest.json")
        else:
            manifest = load(MANIFEST)
            covered = {item["position"]: item for item in manifest["entries"]}
            for entry in entries:
                item = covered.get(entry.get("position"))
                if item is None:
                    errors.append(f"position {entry.get('position')}: absent from the evidence manifest")
                    continue
                if item["url"] != entry.get("url"):
                    errors.append(f"position {entry['position']}: manifest url does not match the screening log")
                if item["issue_response_sha256"] != entry.get("evidence_sha256", {}).get("issue"):
                    errors.append(f"position {entry['position']}: manifest issue digest does not match the screening log")
                if item["reason"] != entry.get("reason"):
                    errors.append(f"position {entry['position']}: manifest reason does not match the screening log")

    admitted = [entry for entry in entries if entry.get("decision") == "ADMIT"]
    per_repository: collections.Counter[str] = collections.Counter()
    for entry in entries:
        repository = entry.get("repository")
        if entry.get("decision") == "ADMIT":
            per_repository[repository] += 1
            if per_repository[repository] > MAX_PER_REPOSITORY:
                errors.append(f"position {entry.get('position')}: repository cap exceeded for {repository}")
        elif entry.get("decision") == "CAPPED" and per_repository[repository] < MAX_PER_REPOSITORY:
            errors.append(f"position {entry.get('position')}: CAPPED before {repository} reached the cap")

    if len(entries) > MAX_SCREENED:
        errors.append(f"screened {len(entries)} candidates; preregistered ceiling is {MAX_SCREENED}")
    if len(admitted) > MAX_ADMITTED:
        errors.append(f"admitted {len(admitted)} packets; preregistered ceiling is {MAX_ADMITTED}")

    # `control_kind` is required equal to the frozen stratum, so this counts
    # SAMPLING STRATA, not independently observed incident kinds. Codex review
    # 2026-08-26, finding 9. A successor must carry sampling_stratum and
    # observed_control_kind as separate fields and permit them to disagree.
    kinds = {entry["sampling_assessment"]["control_kind"] for entry in admitted if "sampling_assessment" in entry}
    components = collections.Counter(
        entry["sampling_assessment"]["expected_component"] for entry in admitted if "sampling_assessment" in entry
    )

    complete = len(admitted) >= MAX_ADMITTED or len(entries) >= MAX_SCREENED
    unmet: list[str] = []
    if complete:
        if len(admitted) < MIN_ADMITTED:
            unmet.append(f"only {len(admitted)} admitted; minimum to code is {MIN_ADMITTED}")
        if len(kinds) < MIN_CONTROL_KINDS:
            unmet.append(f"only {len(kinds)} sampling strata among admitted; minimum is {MIN_CONTROL_KINDS}")
        for component in EXPECTED_COMPONENTS:
            if components[component] < MIN_PER_EXPECTED_COMPONENT:
                unmet.append(f"only {components[component]} expected {component} cases; minimum is {MIN_PER_EXPECTED_COMPONENT}")

    state = {
        "screened": len(entries),
        "admitted": len(admitted),
        "rejected": sum(1 for entry in entries if entry.get("decision") == "REJECT"),
        "capped": sum(1 for entry in entries if entry.get("decision") == "CAPPED"),
        "repositories": len(per_repository),
        "sampling_strata_of_admitted": sorted(kinds),
        "expected_components": dict(sorted(components.items())),
        "complete": complete,
        "unmet_constraints": unmet,
        "status": "IN_PROGRESS" if not complete else ("SAMPLING_FAILURE" if unmet else "READY_FOR_PACKETS"),
    }
    return errors, state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--next", type=int, default=0, metavar="N", help="print the next N unscreened candidates")
    args = parser.parse_args()
    if not (args.check or args.status or args.next):
        parser.error("choose --check, --status, or --next N")

    if not ORDER.exists():
        print("FAIL: candidate order is not frozen", file=sys.stderr)
        return 1
    order = load(ORDER)["candidates"]
    schema = load(SCHEMA)

    if not LOG.exists():
        if args.next:
            for candidate in order[: args.next]:
                print(json.dumps(candidate, ensure_ascii=False))
            return 0
        print("PASS: P003 screening not started; candidate order frozen and unscreened")
        return 0

    errors, state = evaluate(order, load(LOG), schema)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1

    if args.next:
        for candidate in order[state["screened"] : state["screened"] + args.next]:
            print(json.dumps(candidate, ensure_ascii=False))
        return 0
    if args.status:
        print(json.dumps(state, indent=2, ensure_ascii=False))
        return 0
    print(
        f"PASS: P003 screening {state['status']}; screened={state['screened']}/{MAX_SCREENED}, "
        f"admitted={state['admitted']}/{MAX_ADMITTED}, rejected={state['rejected']}, capped={state['capped']}, "
        f"sampling_strata={len(state['sampling_strata_of_admitted'])}, components={state['expected_components']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
