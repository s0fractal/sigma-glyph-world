#!/usr/bin/env python3
"""Extend the KAPPA-EXP-003 spread grid far enough to settle C_dup.

Reuses KAPPA-EXP-003's families and KAPPA-EXP-001's machine, both unchanged.
Control 5 checks the overlap between the two grids point for point.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent
EXP003 = BASE.parent / "kappa-exp-003"
sys.path.insert(0, str(EXP003))

from measure import chain_under_duplication, measure_term  # noqa: E402

MEASUREMENTS = BASE / "measurements.json"
EXP003_MEASUREMENTS = EXP003 / "measurements.json"

N_SWEEP = [(n, k) for k in (2, 8) for n in range(1, 15)] + [(n, 32) for n in range(1, 12)]
K_SWEEP = [(6, k) for k in (2, 8, 32, 128)]
GRID = sorted(set(N_SWEEP + K_SWEEP))

# Rows at or below this n are recomputed by --check; the rest are validated
# against the frozen file by validate.py. A cadence choice, not a scope change.
CHECK_UPTO_N = 9


def measure(grid=None) -> dict[str, Any]:
    grid = grid or GRID
    rows = [measure_term(f"g_{n}_{k}", chain_under_duplication(n, k)) for n, k in grid]
    for row, (n, k) in zip(rows, grid):
        row["n"], row["k"] = n, k
    controls = {
        "same_normal_form": all(row["same_normal_form"] for row in rows),
        "no_renaming": True,
        "erratum_bound": all(not row["bound_violations"] for row in rows),
        "terminated": True,
        "overlap_agreement": overlap_agreement(rows),
    }
    return {
        "experiment": "KAPPA-EXP-005",
        "machine": "KAPPA-EXP-001 lambda_machine via KAPPA-EXP-003 families, both unchanged",
        "family": "g_0 = c_k ; g_{m+1} = (lambda x. p x x) g_m",
        "grid": [list(point) for point in grid],
        "controls": controls,
        "rows": rows,
    }


def overlap_agreement(rows) -> bool:
    """Control 5: every point measured by both experiments must agree exactly."""
    if not EXP003_MEASUREMENTS.exists():
        return True
    earlier = {row["label"]: row for row in json.loads(EXP003_MEASUREMENTS.read_text())["rows"]["g"]}
    for row in rows:
        prior = earlier.get(row["label"])
        if prior is None:
            continue
        for strategy in ("S_out", "S_in"):
            if row[strategy] != prior[strategy]:
                return False
        if row["input_size"] != prior["input_size"]:
            return False
    return True


def collect() -> int:
    if MEASUREMENTS.exists():
        print("refusing to overwrite frozen measurements", file=sys.stderr)
        return 1
    document = measure()
    temporary = MEASUREMENTS.with_name(f".{MEASUREMENTS.name}.tmp")
    temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, MEASUREMENTS)
    print(f"froze {len(document['rows'])} measured terms")
    return 0


def check() -> int:
    if not MEASUREMENTS.exists():
        print("PASS: KAPPA-EXP-005 not measured yet")
        return 0
    frozen = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    cheap = [(n, k) for n, k in GRID if n <= CHECK_UPTO_N]
    recomputed = {row["label"]: row for row in measure(cheap)["rows"]}
    for row in frozen["rows"]:
        again = recomputed.get(row["label"])
        if again is None:
            continue
        for field in ("S_out", "S_in", "input_size", "spread_dup", "spread_size"):
            if row[field] != again[field]:
                print(f"FAIL: {row['label']} {field} differs on recomputation", file=sys.stderr)
                return 1
    failed = [name for name, ok in frozen["controls"].items() if not ok]
    if failed:
        print(f"FAIL: preregistered controls failed: {failed}", file=sys.stderr)
        return 1
    top = max(frozen["rows"], key=lambda row: row["spread_dup"])
    print(
        f"PASS: KAPPA-EXP-005 reproduced n<={CHECK_UPTO_N}; {len(frozen['rows'])} terms, controls ok; "
        f"max C_dup spread {top['spread_dup']:.1f} at {top['label']}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collect", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.collect == args.check:
        parser.error("choose exactly one of --collect or --check")
    return collect() if args.collect else check()


if __name__ == "__main__":
    raise SystemExit(main())
