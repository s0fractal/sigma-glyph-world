#!/usr/bin/env python3
"""Render evidence-only packets without repository identity or researcher labels."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parent
REPLACEMENTS = {
    "P01": {"PAO": "the wrapper", "Pest": "the underlying runner", "Laravel": "the host framework"},
    "P02": {"vstest.console.exe": "the test runner", ".NET": "the language runtime"},
    "P03": {"Kyverno": "the policy validator", "kyverno": "the policy validator"},
    "P04": {"nyc": "the coverage tool", "webpack": "the bundler"},
    "P05": {"actions/upload-artifact@v3.1.3": "the artifact action at the reported version", "GitHub Actions": "the CI service"},
    "P06": {
        "Hadolint": "the upstream linter",
        "SonarQube": "the downstream analyzer",
        "Sonar": "the downstream analyzer",
        "sonar.externalIssuesReportPaths": "the downstream analyzer's external-report setting",
    },
    "P07": {"Bats": "the test runner", "bats": "the test runner", "nixpkgs": "the caller repository"},
    "P08": {},
    "P09": {"jest-runner-groups": "the grouping extension", "Jest": "the underlying runner", "jest": "the underlying runner"},
    "P10": {"Flutter": "the framework", "flutter": "the framework"},
    "P11": {"Ghidra": "the project", "Gradle": "the build tool", "JUnit": "the test-report format"},
    "P12": {"redpandadata/connect:4.42": "the version-pinned tool container", "Redpanda Connect": "the lint tool"},
}


def redact(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, str):
        for old, new in replacements.items():
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [redact(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: redact(item, replacements) for key, item in value.items()}
    return value


def render(packet: dict[str, Any], blind_id: str) -> dict[str, Any]:
    evidence = [
        {"id": source["id"], "kind": source["kind"], "evidence_excerpt": source["evidence_excerpt"]}
        for source in packet["sources"]
    ]
    result = {
        "blind_packet_version": 1,
        "blind_id": blind_id,
        "incident_date": packet["incident_date"],
        "control_kind": packet["control_kind"],
        "evidence": evidence,
        "intended_control": packet["intended_control"],
        "false_acceptance": packet["false_acceptance"],
        "causal_chain": packet["causal_chain"],
        "reproducer": packet["reproducer"],
        "epistemic": packet["epistemic"],
        "evidence_confidence": packet["evidence_confidence"],
    }
    return redact(result, REPLACEMENTS[packet["packet_id"]])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if committed renders differ")
    args = parser.parse_args()

    packet_paths = sorted((BASE / "packets").glob("P*.json"))
    out_dir = BASE / "blind"
    out_dir.mkdir(exist_ok=True)
    mismatches: list[str] = []
    expected_names: set[str] = set()

    for index, path in enumerate(packet_paths, start=1):
        packet = json.loads(path.read_text(encoding="utf-8"))
        name = f"B{index:02d}.json"
        expected_names.add(name)
        content = json.dumps(render(packet, name[:-5]), indent=2, ensure_ascii=False) + "\n"
        target = out_dir / name
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != content:
                mismatches.append(name)
        else:
            target.write_text(content, encoding="utf-8")

    extras = {path.name for path in out_dir.glob("B*.json")} - expected_names
    if extras:
        mismatches.extend(sorted(extras))

    if mismatches:
        print("blind render mismatch: " + ", ".join(mismatches))
        return 1
    print(f"blind render {'verified' if args.check else 'wrote'}: {len(packet_paths)} packets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
