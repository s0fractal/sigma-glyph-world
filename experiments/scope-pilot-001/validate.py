#!/usr/bin/env python3
"""Validate the frozen SCOPE-PILOT-001 sampling and packet invariants."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parent
LABELS = {
    "SCOPE_SELF_SELECTED",
    "VACUOUS_ACCEPTANCE",
    "STATEMENT_WEAKENED",
    "TOOL_BLIND_SPOT",
    "TRUSTED_CORE_DEFECT",
    "PROVENANCE_STALE_OR_MISMATCHED",
    "HARNESS_ORCHESTRATION_DEFECT",
}
PRIMARY = LABELS | {"CONTESTED"}
COUNTER = PRIMARY | {"OUT_OF_SCOPE", "INSUFFICIENT_EVIDENCE"}
CONTROL_KINDS = {
    "tests",
    "proofs",
    "static analysis",
    "lint/type checks",
    "artifact/conformance validation",
}
CONFIDENCE = {"VERIFIED", "SUPPORTED", "TENTATIVE"}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path.relative_to(BASE)}: {exc}") from exc


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_packet(path: Path, errors: list[str]) -> dict[str, Any]:
    packet = load_json(path)
    prefix = path.name
    required = {
        "packet_version",
        "packet_id",
        "repository",
        "incident_date",
        "control_kind",
        "sources",
        "intended_control",
        "false_acceptance",
        "causal_chain",
        "reproducer",
        "epistemic",
        "researcher_assessment",
        "evidence_confidence",
    }
    require(required <= packet.keys(), f"{prefix}: missing required fields {sorted(required - packet.keys())}", errors)
    if not required <= packet.keys():
        return packet

    require(packet["packet_version"] == 1, f"{prefix}: packet_version must be 1", errors)
    require(path.stem == packet["packet_id"], f"{prefix}: filename/id mismatch", errors)
    require(packet["control_kind"] in CONTROL_KINDS, f"{prefix}: invalid control kind", errors)
    require(packet["evidence_confidence"] in CONFIDENCE, f"{prefix}: invalid confidence", errors)
    require(packet["evidence_confidence"] != "TENTATIVE", f"{prefix}: tentative packet cannot enter coding set", errors)

    sources = packet["sources"]
    require(isinstance(sources, list) and sources, f"{prefix}: sources must be non-empty", errors)
    source_ids: set[str] = set()
    for source in sources:
        source_id = source.get("id")
        require(isinstance(source_id, str) and source_id not in source_ids, f"{prefix}: duplicate or invalid source id", errors)
        if isinstance(source_id, str):
            source_ids.add(source_id)
        require(str(source.get("url", "")).startswith("https://github.com/"), f"{prefix}: source URL is not a stable GitHub identifier", errors)
        require(bool(source.get("evidence_excerpt")), f"{prefix}: source lacks evidence excerpt", errors)

    chain = packet["causal_chain"]
    require(isinstance(chain, list) and len(chain) >= 2, f"{prefix}: causal chain must have at least two links", errors)
    statuses: set[str] = set()
    for link in chain:
        status = link.get("status")
        statuses.add(status)
        require(status in {"FACT", "DERIVATION", "UNKNOWN"}, f"{prefix}: invalid causal status {status}", errors)
        refs = set(link.get("evidence", []))
        require(refs <= source_ids, f"{prefix}: causal link refers to unknown evidence {sorted(refs - source_ids)}", errors)
    require("FACT" in statuses, f"{prefix}: causal chain has no FACT", errors)

    epistemic = packet["epistemic"]
    require(set(epistemic) == {"facts", "derivations", "unknowns"}, f"{prefix}: epistemic fields must be facts/derivations/unknowns", errors)
    for field in ("facts", "derivations", "unknowns"):
        require(isinstance(epistemic.get(field), list) and epistemic[field], f"{prefix}: epistemic.{field} must be non-empty", errors)

    reproducer = packet["reproducer"]
    require(reproducer.get("availability") in {"executable", "documented", "unavailable"}, f"{prefix}: invalid reproducer availability", errors)
    require(isinstance(reproducer.get("steps"), list), f"{prefix}: reproducer steps must be a list", errors)
    if packet["evidence_confidence"] == "VERIFIED":
        require(reproducer.get("availability") != "unavailable", f"{prefix}: VERIFIED packet needs a reproducer or regression boundary", errors)

    assessment = packet["researcher_assessment"]
    mechanisms = assessment.get("mechanisms", [])
    require(isinstance(mechanisms, list) and set(mechanisms) <= LABELS, f"{prefix}: invalid mechanism label", errors)
    require(assessment.get("primary") in PRIMARY, f"{prefix}: invalid primary label", errors)
    require(assessment.get("scope_controlled_by_audited_artifact") in {"yes", "no", "unknown"}, f"{prefix}: invalid scope ternary", errors)
    counter = assessment.get("counterclassification", {})
    require(counter.get("label") in COUNTER, f"{prefix}: invalid counterclassification", errors)
    require(bool(counter.get("would_be_primary_if")), f"{prefix}: missing counterfactual boundary", errors)
    require(isinstance(assessment.get("expected_multilabel"), bool), f"{prefix}: expected_multilabel must be boolean", errors)
    return packet


def main() -> int:
    errors: list[str] = []
    candidates_doc = load_json(BASE / "candidates.json")
    candidates = candidates_doc.get("candidates", [])
    require(len(candidates) <= 40, "candidate stop rule exceeded 40", errors)
    ids = [candidate.get("id") for candidate in candidates]
    require(len(ids) == len(set(ids)), "candidate ids are not unique", errors)
    admitted = [candidate for candidate in candidates if candidate.get("decision") == "admit"]
    rejected = [candidate for candidate in candidates if candidate.get("decision") == "reject"]
    require(len(admitted) == 12 or len(candidates) == 40, "search stopped before 12 admissions or 40 screened candidates", errors)
    require(8 <= len(admitted) <= 12, "admitted set is outside the preregistered 8-12 range", errors)
    require(all(candidate.get("reason") for candidate in candidates), "candidate without decision reason", errors)

    packet_paths = sorted((BASE / "packets").glob("P*.json"))
    packets = [validate_packet(path, errors) for path in packet_paths]
    admitted_ids = {candidate["id"] for candidate in admitted}
    packet_ids = {packet.get("packet_id") for packet in packets}
    require(packet_ids == admitted_ids, f"packet/admission mismatch: packets={sorted(packet_ids)} admitted={sorted(admitted_ids)}", errors)

    repositories = Counter(packet.get("repository") for packet in packets)
    kinds = {packet.get("control_kind") for packet in packets}
    scopes = Counter(packet.get("researcher_assessment", {}).get("scope_controlled_by_audited_artifact") for packet in packets)
    multilabel = sum(bool(packet.get("researcher_assessment", {}).get("expected_multilabel")) for packet in packets)
    require(len(repositories) >= 3, "fewer than three repositories", errors)
    require(max(repositories.values(), default=0) <= 4, "more than four incidents from one repository", errors)
    require(len(kinds) >= 3, "fewer than three control kinds", errors)
    require(scopes["no"] >= 2, "fewer than two external-scope negative controls", errors)
    require(multilabel >= 2, "fewer than two expected multilabel packets", errors)

    blind_paths = sorted((BASE / "blind").glob("B*.json")) if (BASE / "blind").exists() else []
    if blind_paths:
        require(len(blind_paths) == len(packets), "blinded render count does not match packet count", errors)
        forbidden = {"repository", "sources", "researcher_assessment"}
        for path in blind_paths:
            blind = load_json(path)
            require(not (forbidden & blind.keys()), f"{path.name}: contains unblinded fields {sorted(forbidden & blind.keys())}", errors)

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(
        "PASS: "
        f"{len(candidates)} screened, {len(admitted)} admitted, {len(rejected)} rejected; "
        f"{len(repositories)} repositories, {len(kinds)} control kinds, "
        f"scope-no={scopes['no']}, expected-multilabel={multilabel}, blind={len(blind_paths)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
