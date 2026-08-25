#!/usr/bin/env python3
"""Validate calibration topologies and deterministic v1 derivations."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
ROLES = ["selector", "checker", "adapter", "gate"]
MECHANISMS = {
    "UNFENCED_SCOPE_SELF_SELECTION",
    "EMPTY_SCOPE_SUCCESS",
    "CHECKER_MISSED_CONDITION",
    "ADAPTER_MISREPRESENTED_RESULT",
    "GATE_OMITTED_OR_IGNORED_RESULT",
    "CLAIM_WEAKENED",
    "PROVENANCE_IDENTITY_MISMATCH",
    "TRUSTED_CORE_INVALID_ACCEPTANCE",
}
SPECIAL_PRIMARY = {"MULTICAUSAL", "CONTRACT_DISPUTED", "CONTRACT_UNKNOWN", "INSUFFICIENT_EVIDENCE"}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def expected_contract_status(tier: str) -> set[str]:
    return {
        "T1_NORMATIVE": {"ESTABLISHED"},
        "T2_EXECUTABLE": {"ESTABLISHED"},
        "T3_ADJUDICATED": {"SUPPORTED"},
        "T4_REPORTED": {"DISPUTED"},
        "NONE": {"UNKNOWN"},
    }[tier]


def derive_scope(case: dict[str, Any]) -> str:
    relation = case["authority_relation"]
    selected = case["selected_scope"]
    fence = case["completeness_fence"]
    if fence == "independent" or relation == "independent":
        return "no"
    if relation in {"same", "shared"} and selected in {"empty", "incomplete"} and fence in {"none", "self_owned"}:
        return "yes"
    return "unknown"


def main() -> int:
    errors: list[str] = []
    document = load(BASE / "calibration.json")
    cases = document.get("cases", [])
    seen: set[str] = set()
    contracts: Counter[str] = Counter()
    primaries: Counter[str] = Counter()

    for case in cases:
        case_id = case.get("case_id", "?")
        if case_id in seen:
            errors.append(f"{case_id}: duplicate case id")
        seen.add(case_id)

        packet_path = REPO / "experiments" / "scope-pilot-001" / "packets" / f"{case.get('source_packet')}.json"
        if not packet_path.exists():
            errors.append(f"{case_id}: missing retired source packet")
            continue
        packet = load(packet_path)
        evidence_ids = {source["id"] for source in packet["sources"]}

        components = case.get("components", [])
        roles = [component.get("role") for component in components]
        if roles != ROLES:
            errors.append(f"{case_id}: component order must be {ROLES}, got {roles}")
        for component in components:
            unknown = set(component.get("evidence", [])) - evidence_ids
            if unknown:
                errors.append(f"{case_id}/{component.get('role')}: unknown evidence {sorted(unknown)}")

        contract = case.get("success_contract", {})
        tier = contract.get("tier")
        status = contract.get("status")
        if tier not in {"T1_NORMATIVE", "T2_EXECUTABLE", "T3_ADJUDICATED", "T4_REPORTED", "NONE"}:
            errors.append(f"{case_id}: invalid contract tier {tier}")
        elif status not in expected_contract_status(tier):
            errors.append(f"{case_id}: {tier} cannot yield contract status {status}")
        unknown = set(contract.get("evidence", [])) - evidence_ids
        if unknown:
            errors.append(f"{case_id}/contract: unknown evidence {sorted(unknown)}")

        derived_scope = derive_scope(case)
        if case.get("scope_self_selection") != derived_scope:
            errors.append(f"{case_id}: scope is {case.get('scope_self_selection')}, derived {derived_scope}")

        mechanisms = set(case.get("mechanisms", []))
        if not mechanisms <= MECHANISMS:
            errors.append(f"{case_id}: invalid mechanisms {sorted(mechanisms - MECHANISMS)}")
        if derived_scope == "yes" and "UNFENCED_SCOPE_SELF_SELECTION" not in mechanisms:
            errors.append(f"{case_id}: derived self-selection lacks mechanism label")
        if case.get("selected_scope") == "empty" and status in {"ESTABLISHED", "SUPPORTED"}:
            if "EMPTY_SCOPE_SUCCESS" not in mechanisms:
                errors.append(f"{case_id}: admitted empty acceptance lacks EMPTY_SCOPE_SUCCESS")

        sufficient_sites = [
            component["role"]
            for component in components
            if component.get("breach") == "yes" and component.get("repair_changes_gate") == "yes"
        ]
        primary = case.get("primary")
        if status == "DISPUTED" and primary != "CONTRACT_DISPUTED":
            errors.append(f"{case_id}: disputed contract requires CONTRACT_DISPUTED primary")
        elif status == "UNKNOWN" and primary != "CONTRACT_UNKNOWN":
            errors.append(f"{case_id}: unknown contract requires CONTRACT_UNKNOWN primary")
        elif status in {"ESTABLISHED", "SUPPORTED"}:
            if len(sufficient_sites) > 1 and primary != "MULTICAUSAL":
                errors.append(f"{case_id}: multiple sufficient repair sites require MULTICAUSAL")
            if len(sufficient_sites) == 0 and primary != "INSUFFICIENT_EVIDENCE":
                errors.append(f"{case_id}: no sufficient repair site requires INSUFFICIENT_EVIDENCE")
            if len(sufficient_sites) == 1 and primary not in MECHANISMS:
                errors.append(f"{case_id}: unique sufficient repair site requires a mechanism primary")

        contracts[status] += 1
        primaries[primary] += 1

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(
        f"PASS: {len(cases)} retired calibration cases; "
        f"contracts={dict(sorted(contracts.items()))}; primaries={dict(sorted(primaries.items()))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
