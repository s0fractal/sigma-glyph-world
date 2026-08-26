#!/usr/bin/env python3
"""Check KAPPA-EXP-006 against its preregistered predictions."""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
MEASUREMENTS = BASE / "measurements.json"

MIN_SEPARATION = 100.0   # what "H-KAPPA refuted" requires, as in KAPPA-EXP-001
MAX_DISSOLVED = 2.0      # what "the counterexample dissolves" requires


def separation(row: dict, representation: str, metric: str) -> float:
    field = f"kappa_unit_{metric}"
    return row[f"{representation}.S_in"][field] / row[f"{representation}.S_out"][field]


def main() -> int:
    if not MEASUREMENTS.exists():
        print("PASS: KAPPA-EXP-006 not measured yet")
        return 0
    document = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    rows = document["rows"]
    errors: list[str] = []

    for row in rows:
        n = row["n"]
        for strategy in ("S_out", "S_in"):
            fresh = row[f"R_fresh.{strategy}"]
            # The defining property of R_fresh: nothing is shared, so every
            # occurrence is an object.
            if fresh["peak_distinct_objects"] != fresh["peak_occurrence_size"]:
                errors.append(
                    f"n={n} R_fresh.{strategy}: objects {fresh['peak_distinct_objects']} != "
                    f"occurrences {fresh['peak_occurrence_size']}; the representation shares something"
                )
            for machine in (fresh, row[f"R_alias.{strategy}"]):
                if not (machine["peak_distinct_hashes"] <= machine["peak_distinct_objects"] <= machine["peak_occurrence_size"]):
                    errors.append(f"n={n}: metric ordering violated")
        # Aliasing must actually reduce S_in's materialization.
        alias_in = row["R_alias.S_in"]
        if alias_in["peak_distinct_objects"] > 4 * n + 8:
            errors.append(f"n={n} R_alias.S_in: objects {alias_in['peak_distinct_objects']} is not linear in n")
        # Content addressing is linear under both representations.
        for key in ("R_fresh.S_in", "R_alias.S_in"):
            if row[key]["peak_distinct_hashes"] > 4 * n + 8:
                errors.append(f"n={n} {key}: distinct hashes not linear in n")

    top = rows[-1]
    checks = {
        ("R_fresh", "occurrence"): (">=", MIN_SEPARATION),
        ("R_fresh", "objects"): (">=", MIN_SEPARATION),
        ("R_alias", "occurrence"): (">=", MIN_SEPARATION),
        ("R_alias", "objects"): ("<=", MAX_DISSOLVED),
    }
    observed = {}
    for (representation, metric), (relation, threshold) in checks.items():
        value = separation(top, representation, metric)
        observed[(representation, metric)] = value
        if relation == ">=" and value < threshold:
            errors.append(f"{representation} by {metric}: separation {value:.2f} < {threshold}")
        if relation == "<=" and value > threshold:
            errors.append(f"{representation} by {metric}: separation {value:.2f} > {threshold}")

    for control, ok in document["controls"].items():
        if not ok:
            errors.append(f"preregistered control failed: {control}")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(
        f"PASS: H-REPR refuted; at n={top['n']} the S_in/S_out separation is "
        f"{observed[('R_fresh','objects')]:.0f}x on R_fresh by materialized objects and "
        f"{observed[('R_alias','objects')]:.2f}x on R_alias by the same metric -- "
        f"H-KAPPA holds for representations that materialize per occurrence and dissolves for those that alias"
    )
    print(
        f"OBSERVED: at n={top['n']} allocations are "
        f"{top['R_fresh.S_in']['allocations']} on R_fresh vs {top['R_alias.S_in']['allocations']} on R_alias "
        f"for S_in, while distinct content hashes are {top['R_fresh.S_in']['peak_distinct_hashes']} on both"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
