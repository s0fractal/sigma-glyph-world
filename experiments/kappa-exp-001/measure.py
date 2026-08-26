#!/usr/bin/env python3
"""Measure the four KAPPA-EXP-001 machines over the preregistered family.

`--collect` freezes measurements.json and refuses to overwrite it.
`--check` recomputes every trajectory from scratch and compares.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from lambda_machine import Renaming, de_bruijn, family, normalize

BASE = Path(__file__).resolve().parent
MEASUREMENTS = BASE / "measurements.json"

N_MIN = 1
N_MAX = 12
STEP_CEILING = 10 ** 7
COST_MODELS = ("cost_unit", "cost_size")
STRATEGIES = ("S_out", "S_in")


def measure() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    controls = {
        "same_normal_form": True,
        "same_input": True,
        "terminated": True,
        "no_renaming": True,
    }
    for n in range(N_MIN, N_MAX + 1):
        term = family(n)
        runs = {}
        for strategy in STRATEGIES:
            try:
                runs[strategy] = normalize(term, strategy, STEP_CEILING)
            except Renaming:
                controls["no_renaming"] = False
                raise
            except RuntimeError:
                controls["terminated"] = False
                raise
        if de_bruijn(runs["S_out"]["normal_form"]) != de_bruijn(runs["S_in"]["normal_form"]):
            controls["same_normal_form"] = False
        row: dict[str, Any] = {"n": n, "input_size": term.size}
        for strategy, run in runs.items():
            row[strategy] = {
                "steps": run["steps"],
                "peak": run["peak"],
                "normal_form_size": run["normal_form_size"],
                "cost_unit": run["cost_unit"],
                "cost_size": run["cost_size"],
                "kappa_unit": (run["peak"] - 1) / run["cost_unit"],
                "kappa_size": (run["peak"] - 1) / run["cost_size"],
            }
        rows.append(row)
    return {
        "experiment": "KAPPA-EXP-001",
        "family": "h_0 = y ; h_{n+1} = (lambda x. p x x) h_n",
        "representation": "explicit syntax tree, no sharing",
        "n_range": [N_MIN, N_MAX],
        "strategies": list(STRATEGIES),
        "cost_models": list(COST_MODELS),
        "kappa": "(peak - 1) / cost",
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
        print("PASS: KAPPA-EXP-001 not measured yet")
        return 0
    frozen = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    recomputed = measure()
    if frozen["rows"] != recomputed["rows"] or frozen["controls"] != recomputed["controls"]:
        print("FAIL: recomputed trajectories differ from measurements.json", file=sys.stderr)
        return 1
    if not all(frozen["controls"].values()):
        failed = [name for name, ok in frozen["controls"].items() if not ok]
        print(f"FAIL: preregistered controls failed: {failed}", file=sys.stderr)
        return 1
    last = frozen["rows"][-1]
    print(
        f"PASS: KAPPA-EXP-001 reproduced; n={frozen['n_range'][0]}..{frozen['n_range'][1]}, "
        f"controls ok; at n={last['n']} kappa_unit S_in={last['S_in']['kappa_unit']:.1f} "
        f"vs S_out={last['S_out']['kappa_unit']:.1f}"
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
