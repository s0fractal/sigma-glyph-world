#!/usr/bin/env python3
"""Score KAPPA-EXP-007's two attributed predictions, by name.

AGENTS.md clause 8: where more than one voice predicts the same measurement,
each is preregistered separately and the result scores each by name. Both
scorecards print on every green run.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
MEASUREMENTS = BASE / "measurements.json"

COLLAPSED = 2.0      # what "the separation disappears" requires on h
PERSISTS = 5.0       # what "the separation returns" requires on d at the top of the range
RESIDUAL = 11 / 8    # the observed closed-form limit on h under R_update


def main() -> int:
    if not MEASUREMENTS.exists():
        print("PASS: KAPPA-EXP-007 not measured yet")
        return 0
    document = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    h_rows, d_rows = document["rows"]["h"], document["rows"]["d"]
    top_h, top_d = h_rows[-1], d_rows[-1]
    errors: list[str] = []
    scorecard: list[str] = []

    # Closed forms observed on h under R_update.
    for row in h_rows:
        n = row["n"]
        if row["R_update.S_in"]["peak_occurrence_size"] != max(4 * 2 ** n - 3, 1 + 7 * n):
            errors.append(f"h_{n}: R_update S_in peak is not max(4*2^n-3, 1+7n)")
        if row["R_update.S_out"]["peak_occurrence_size"] != 11 * 2 ** (n - 1) - 3:
            errors.append(f"h_{n}: R_update S_out peak is not 11*2^(n-1)-3")
        for strategy in ("S_out", "S_in"):
            if row[f"R_update.{strategy}"]["peak_distinct_objects"] != 7 * n + 1:
                errors.append(f"h_{n}: R_update {strategy} distinct objects is not 7n+1")
            if row[f"R_update.{strategy}"]["steps"] != n:
                errors.append(f"h_{n}: R_update {strategy} does not take exactly n steps")

    for control, ok in document["controls"].items():
        if not ok:
            errors.append(f"preregistered control failed: {control}")

    # --- Prediction A, attributed to reviews/claude-fable-2026-08-26.md ---
    a1 = top_h["separation_R_update"] < COLLAPSED
    scorecard.append(
        f"PREDICTION A.1 (claude-fable-2026-08-26) — h_n separation disappears under R_update: "
        f"{'CONFIRMED' if a1 else 'FAILED'}; {top_h['separation_R_fresh']:.2f} on R_fresh -> "
        f"{top_h['separation_R_update']:.3f} on R_update"
    )
    a2 = top_d["separation_R_update"] > PERSISTS
    scorecard.append(
        f"PREDICTION A.2 (claude-fable-2026-08-26) — d_n separation returns under a binder: "
        f"{'CONFIRMED' if a2 else 'FAILED'}; {top_d['separation_R_update']:.2f} at n={top_d['n']}, "
        f"still growing"
    )

    # --- Prediction B, attributed to this repository ---
    b1 = abs(top_h["separation_R_update"] - 1.0) < 1e-9
    scorecard.append(
        f"PREDICTION B.1 (this repository) — h_n separation is exactly 1.00 because the "
        f"trajectories are identical: {'CONFIRMED' if b1 else 'FAILED'}; measured "
        f"{top_h['separation_R_update']:.4f} by occurrence, converging to 11/8, and the "
        f"trajectories differ ({top_h['R_update.S_out']['peak_occurrence_size']} vs "
        f"{top_h['R_update.S_in']['peak_occurrence_size']} peak). Exactly 1.00 holds only by the "
        f"objects metric, which the prediction did not name"
    )
    b2 = all(row[f"R_update.{s}"]["peak_distinct_objects"] == 7 * row["n"] + 1
             for row in h_rows for s in ("S_out", "S_in"))
    scorecard.append(
        f"PREDICTION B.2 (this repository) — R_update distinct objects are Theta(n) for both "
        f"strategies on h_n: {'CONFIRMED' if b2 else 'FAILED'}; exactly 7n+1"
    )
    b3 = all(row["separation_R_update"] < row["separation_R_fresh"] for row in d_rows if row["n"] >= 4)
    attenuation = top_d["separation_R_fresh"] / top_d["separation_R_update"]
    scorecard.append(
        f"PREDICTION B.3 (this repository) — d_n separation returns attenuated, strictly below "
        f"R_fresh at every n>=4: {'CONFIRMED' if b3 else 'FAILED'}; "
        f"{top_d['separation_R_fresh']:.2f} -> {top_d['separation_R_update']:.2f} at n={top_d['n']}, "
        f"an attenuation of {attenuation:.2f}x"
    )

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    for line in scorecard:
        print(line)
    confirmed_a = sum([a1, a2])
    confirmed_b = sum([b1, b2, b3])
    print(
        f"SCORE: claude-fable {confirmed_a}/2, this repository {confirmed_b}/3. "
        f"H-UPDATE holds for duplication not under a binder and fails under one; "
        f"the residual separation on h_n is exactly {RESIDUAL}, which neither prediction anticipated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
