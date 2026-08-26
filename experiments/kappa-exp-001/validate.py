#!/usr/bin/env python3
"""Check frozen KAPPA-EXP-001 measurements against the preregistered claims.

`measure.py --check` proves the trajectories reproduce. This file checks what
the preregistration actually predicted, and reports any closed form that missed
rather than smoothing it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
MEASUREMENTS = BASE / "measurements.json"

# Ratio by which kappa under C_unit must separate the two strategies at the top
# of the measured range for the refutation to stand. Set well below the
# predicted 4*2^n/(n*4) = 85 so that the test asserts the phenomenon, not the
# exact constant.
MIN_SEPARATION = 50.0
# Bound below which a kappa sequence counts as "not growing" over the range.
BOUNDED_CEILING = 8.0
# Ceiling for kappa under the size-aware cost model across the whole range.
SIZE_CEILING = 3.0


def main() -> int:
    if not MEASUREMENTS.exists():
        print("PASS: KAPPA-EXP-001 not measured yet")
        return 0

    document = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    rows = document["rows"]
    errors: list[str] = []
    deviations: list[str] = []

    for row in rows:
        n = row["n"]
        out, inn = row["S_out"], row["S_in"]
        if out["steps"] != 2 ** n - 1:
            errors.append(f"n={n}: steps_out {out['steps']} != 2^n-1")
        if inn["steps"] != n:
            errors.append(f"n={n}: steps_in {inn['steps']} != n")
        if row["input_size"] != 1 + 7 * n:
            errors.append(f"n={n}: |h_n| {row['input_size']} != 1+7n")
        normal_form = 4 * 2 ** n - 3
        for name, run in (("S_out", out), ("S_in", inn)):
            if run["normal_form_size"] != normal_form:
                errors.append(f"n={n}: {name} normal form {run['normal_form_size']} != 4*2^n-3")
            if run["peak"] < run["normal_form_size"]:
                errors.append(f"n={n}: {name} peak below its own normal form")
            if run["peak"] != normal_form:
                deviations.append(
                    f"n={n}: {name} peak {run['peak']} exceeds the predicted "
                    f"normal-form size {normal_form} by {run['peak'] - normal_form}"
                )

    # The refutation itself: same calculus, representation, cost model and input;
    # only the strategy differs, and kappa separates without bound.
    top = rows[-1]
    separation = top["S_in"]["kappa_unit"] / top["S_out"]["kappa_unit"]
    if separation < MIN_SEPARATION:
        errors.append(
            f"kappa_unit separation at n={top['n']} is {separation:.1f}, "
            f"below the {MIN_SEPARATION} required to call H-KAPPA refuted"
        )
    if not all(
        rows[i]["S_in"]["kappa_unit"] < rows[i + 1]["S_in"]["kappa_unit"]
        for i in range(2, len(rows) - 1)
    ):
        errors.append("kappa_unit for S_in is not monotonically increasing over n>=3")
    if max(row["S_out"]["kappa_unit"] for row in rows) > BOUNDED_CEILING:
        errors.append("kappa_unit for S_out left its preregistered bounded regime")

    # The positive replacement: a size-aware cost model restores boundedness.
    # "Bounded" is tested as: not growing with n beyond the small-n regime, and
    # under a fixed ceiling across the whole range. It is not tested as <= 1;
    # kappa_size exceeds 1 at n=1, where the input term rather than any
    # materialization dominates the peak.
    for name in ("S_out", "S_in"):
        worst = max(row[name]["kappa_size"] for row in rows)
        if worst > SIZE_CEILING:
            errors.append(f"kappa_size for {name} reached {worst:.3f}; ceiling is {SIZE_CEILING}")
        if not all(
            rows[i][name]["kappa_size"] >= rows[i + 1][name]["kappa_size"]
            for i in range(2, len(rows) - 1)
        ):
            errors.append(f"kappa_size for {name} grows with n; expected bounded")

    controls = document["controls"]
    for control, ok in controls.items():
        if not ok:
            errors.append(f"preregistered control failed: {control}")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1

    for deviation in deviations:
        print(f"DEVIATION: {deviation}")
    print(
        f"PASS: H-KAPPA refuted; at n={top['n']} kappa_unit S_in={top['S_in']['kappa_unit']:.1f} "
        f"vs S_out={top['S_out']['kappa_unit']:.2f} (separation {separation:.0f}x); "
        f"kappa_size bounded for both (max "
        f"{max(max(r['S_out']['kappa_size'], r['S_in']['kappa_size']) for r in rows):.3f})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
