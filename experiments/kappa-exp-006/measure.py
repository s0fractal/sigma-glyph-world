#!/usr/bin/env python3
"""Measure seven quantities across two representations and two strategies."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
from representation import Aliasing, Renaming, de_bruijn, distinct_objects, normalize  # noqa: E402

MEASUREMENTS = BASE / "measurements.json"
EXP001 = BASE.parent / "kappa-exp-001" / "measurements.json"
N_MIN, N_MAX = 1, 12
CHECK_UPTO_N = 8
REPRESENTATIONS = {"R_alias": False, "R_fresh": True}
STRATEGIES = ("S_out", "S_in")


def measure(n_max: int = N_MAX) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    controls = {
        "same_normal_form": True,
        "no_renaming": True,
        "no_aliasing_on_R_fresh": True,
        "aliasing_present_on_R_alias": True,
        "metric_ordering": True,
        "reproduces_kappa_exp_001": True,
    }
    frozen001 = json.loads(EXP001.read_text(encoding="utf-8"))["rows"] if EXP001.exists() else []

    for n in range(N_MIN, n_max + 1):
        row: dict[str, Any] = {"n": n}
        normal_forms = []
        for representation, fresh in REPRESENTATIONS.items():
            for strategy in STRATEGIES:
                try:
                    run = normalize(n, strategy, fresh)
                except Renaming:
                    controls["no_renaming"] = False
                    raise
                except Aliasing:
                    controls["no_aliasing_on_R_fresh"] = False
                    raise
                normal_forms.append(run["normal_form"])
                # Control 5: hashes <= objects <= occurrences, everywhere.
                if not (
                    run["peak_distinct_hashes"] <= run["peak_distinct_objects"] <= run["peak_occurrence_size"]
                ):
                    controls["metric_ordering"] = False
                # Control 2, the other direction: R_alias must actually alias.
                if not fresh and strategy == "S_in" and n >= 1:
                    if run["normal_form_distinct_objects"] >= run["normal_form_occurrence_size"]:
                        controls["aliasing_present_on_R_alias"] = False
                entry = {key: value for key, value in run.items() if key != "normal_form"}
                entry["kappa_unit_occurrence"] = (run["peak_occurrence_size"] - 1) / run["cost_unit"]
                entry["kappa_unit_objects"] = (run["peak_distinct_objects"] - 1) / run["cost_unit"]
                row[f"{representation}.{strategy}"] = entry
        if len({de_bruijn(term) for term in normal_forms}) != 1:
            controls["same_normal_form"] = False

        # Control 1: R_alias with the occurrence functional is KAPPA-EXP-001.
        prior = next((item for item in frozen001 if item["n"] == n), None)
        if prior is not None:
            for strategy in STRATEGIES:
                mine = row[f"R_alias.{strategy}"]
                theirs = prior[strategy]
                if (
                    mine["steps"] != theirs["steps"]
                    or mine["peak_occurrence_size"] != theirs["peak"]
                    or mine["cost_unit"] != theirs["cost_unit"]
                    or mine["cost_size"] != theirs["cost_size"]
                ):
                    controls["reproduces_kappa_exp_001"] = False
        rows.append(row)

    return {
        "experiment": "KAPPA-EXP-006",
        "representations": {"R_alias": "substitution reuses the argument object", "R_fresh": "every written node is new"},
        "strategies": list(STRATEGIES),
        "family": "h_0 = y ; h_{n+1} = (lambda x. p x x) h_n",
        "n_range": [N_MIN, n_max],
        "quantities": [
            "peak_occurrence_size", "peak_distinct_objects", "peak_distinct_hashes",
            "allocations", "steps", "cost_unit", "cost_size", "cost_dup",
        ],
        "controls": controls,
        "rows": rows,
    }


def collect() -> int:
    if MEASUREMENTS.exists():
        print("refusing to overwrite frozen measurements", file=sys.stderr)
        return 1
    document = measure()
    temporary = MEASUREMENTS.with_name(f".{MEASUREMENTS.name}.tmp")
    temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, MEASUREMENTS)
    print(f"froze {len(document['rows'])} rows")
    return 0


def check() -> int:
    if not MEASUREMENTS.exists():
        print("PASS: KAPPA-EXP-006 not measured yet")
        return 0
    frozen = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    recomputed = measure(CHECK_UPTO_N)
    for row in recomputed["rows"]:
        prior = next(item for item in frozen["rows"] if item["n"] == row["n"])
        if row != prior:
            print(f"FAIL: n={row['n']} differs on recomputation", file=sys.stderr)
            return 1
    failed = [name for name, ok in frozen["controls"].items() if not ok]
    if failed:
        print(f"FAIL: preregistered controls failed: {failed}", file=sys.stderr)
        return 1
    top = frozen["rows"][-1]
    print(
        f"PASS: KAPPA-EXP-006 reproduced n<={CHECK_UPTO_N}; controls ok; at n={top['n']} "
        f"R_fresh S_in objects={top['R_fresh.S_in']['peak_distinct_objects']} vs "
        f"R_alias S_in objects={top['R_alias.S_in']['peak_distinct_objects']}"
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
