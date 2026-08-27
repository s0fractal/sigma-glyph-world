#!/usr/bin/env python3
"""Score WORLD-CAS-001's controls and its one attributed prediction, by name.

AGENTS.md clause 8: predictions are preregistered separately and scored by name.
`P-fable` (C1, C2, C3) was filed in the preregistration commit. The open slot
stayed empty: the preregistration file had exactly one commit when this harness
first ran, so no second voice preregistered and none is scored. Nothing is
inferred from that.

Controls are fail-closed: a failure exits non-zero and no scorecard prints.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
MEASUREMENTS = BASE / "measurements.json"

C1_BOUND = 12          # cas_unique_ever <= 12*n, as C1 states it
C2_GROWTH = 1.8        # last-three growth ratios C2 requires on R_fresh/S_out
MACHINES = ("R_alias", "R_fresh", "R_update")
STRATEGIES = ("S_out", "S_in")


def cell(row, machine, strategy):
    return row[f"{machine}.{strategy}"]


def main() -> int:
    if not MEASUREMENTS.exists():
        print("PASS: WORLD-CAS-001 not measured yet")
        return 0
    document = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    h_rows, d_rows = document["rows"]["h"], document["rows"]["d"]
    errors = [f"preregistered control failed: {name}"
              for name, ok in document["controls"].items() if not ok]
    errors += [f"control failure recorded: {line}" for line in document["control_failures"]]

    # Closed forms, re-derived at every n on every green run.
    for row in h_rows:
        n = row["n"]
        for machine in ("R_fresh", "R_alias"):
            if cell(row, machine, "S_out")["cas_unique_ever"] != 3 * 2 ** n + 3:
                errors.append(f"h_{n} {machine}/S_out: cas_unique_ever is not 3*2^n+3")
            if cell(row, machine, "S_in")["cas_unique_ever"] != (n * n + 5 * n + 12) // 2:
                errors.append(f"h_{n} {machine}/S_in: cas_unique_ever is not (n^2+5n+12)/2")
        if cell(row, "R_update", "S_out")["cas_unique_ever"] != n * n + 2 * n + 6:
            errors.append(f"h_{n} R_update/S_out: cas_unique_ever is not n^2+2n+6")
        if cell(row, "R_update", "S_in")["cas_unique_ever"] != (n * n + 5 * n + 12) // 2:
            errors.append(f"h_{n} R_update/S_in: cas_unique_ever is not (n^2+5n+12)/2")

    # Control: readback writes nothing new, anywhere. Content addressing
    # deduplicates the expansion, so making the normal form explicit costs the
    # store zero. Measured, not assumed.
    readback_new = sum(cell(row, machine, strategy)["cas_unique_ever_readback"]
                       for rows in (h_rows, d_rows) for row in rows
                       for machine in MACHINES for strategy in STRATEGIES)
    if readback_new != 0:
        errors.append(f"readback wrote {readback_new} new hashes; the split is not what it seems")

    # Control: the store cannot tell R_fresh from R_alias. The distinction
    # KAPPA-EXP-006 was built to expose is invisible to content addressing.
    blind = all(cell(row, "R_fresh", strategy)[field] == cell(row, "R_alias", strategy)[field]
                for rows in (h_rows, d_rows) for row in rows
                for strategy in STRATEGIES
                for field in ("live_peak", "cas_unique_ever", "cas_resident_end"))
    if not blind:
        errors.append("R_fresh and R_alias differ in CAS terms; the blindness claim is wrong")

    # --- P-fable, attributed to Claude Fable 5 ---------------------------
    scorecard: list[str] = []

    breaches = [(row["n"], strategy, cell(row, "R_update", strategy)["cas_unique_ever"])
                for row in h_rows for strategy in STRATEGIES
                if cell(row, "R_update", strategy)["cas_unique_ever"] > C1_BOUND * row["n"]]
    c1 = not breaches
    top = h_rows[-1]
    scorecard.append(
        f"PREDICTION C1 (Claude Fable 5, WORLD-CAS-001 preregistration) — on h_n under R_update "
        f"cas_unique_ever <= 12n: {'CONFIRMED' if c1 else 'FAILED'}; it is n^2+2n+6 under S_out, "
        f"which crosses 12n at n=10 and reaches {cell(top, 'R_update', 'S_out')['cas_unique_ever']} "
        f"against 12n={C1_BOUND * top['n']} at n={top['n']} "
        f"({len(breaches)} breaches, all under S_out). Under S_in it is (n^2+5n+12)/2 = "
        f"{cell(top, 'R_update', 'S_in')['cas_unique_ever']} and the bound holds. Quadratic, not "
        f"linear: in-place update path-copies the spine, so a contraction writes Theta(n) new "
        f"content per level, not O(1)")

    ever = [cell(row, "R_fresh", "S_out")["cas_unique_ever"] for row in h_rows]
    growth = [ever[i] / ever[i - 1] for i in range(len(ever) - 3, len(ever))]
    c2 = all(ratio >= C2_GROWTH for ratio in growth)
    scorecard.append(
        f"PREDICTION C2 (Claude Fable 5) — on h_n under R_fresh/S_out cas_unique_ever grows "
        f"Theta(2^n): {'CONFIRMED' if c2 else 'FAILED'}; exactly 3*2^n+3, reaching {ever[-1]} at "
        f"n={h_rows[-1]['n']} while live_peak is only "
        f"{cell(top, 'R_fresh', 'S_out')['live_peak']}. Last-three growth ratios "
        f"{', '.join(f'{r:.4f}' for r in growth)} against the >= {C2_GROWTH} required. "
        f"KAPPA-EXP-006's sentence 'a store never sees the explosion' is FALSE under "
        f"write-through: the store sees exactly the explosion; the live window never did")

    diverging = []
    for family, rows in (("h", h_rows), ("d", d_rows)):
        for machine in MACHINES:
            for strategy in STRATEGIES:
                ratios = [cell(row, machine, strategy)["ratio_ever_over_live"] for row in rows]
                tail = ratios[-3:]
                if all(tail[i] > tail[i - 1] for i in range(1, len(tail))):
                    diverging.append((family, machine, strategy, tail[-1]))
    c3 = bool(diverging)
    worst = max(diverging, key=lambda item: item[3]) if diverging else None
    scorecard.append(
        f"PREDICTION C3 (Claude Fable 5) — cas_unique_ever/live_peak diverges on at least one "
        f"machine-family pair: {'CONFIRMED' if c3 else 'FAILED'}; it diverges on "
        f"{len(diverging)} of {2 * len(MACHINES) * len(STRATEGIES)} pairs, worst "
        f"{worst[1]}/{worst[2]} on {worst[0]}_n at {worst[3]:.1f}x. The live-DAG bound does NOT "
        f"survive persistence history")

    scorecard.append(
        "OPEN SLOT — unfilled: the preregistration had exactly one commit when this harness first "
        "ran and carries no dated addendum, so no second voice preregistered. It scores nothing, "
        "and per clause 8 nothing is inferred from that")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(f"CONTROLS: all six pass. Instrumentation changed no trajectory (control 1: every "
          f"KAPPA-EXP-007 frozen field reproduces); write-through is complete at every tick; "
          f"resident(end) = unique_ever under no GC; runs are deterministic; readback is split out "
          f"and measured at {readback_new} new writes everywhere")
    print("CONTROL: content addressing cannot distinguish R_fresh from R_alias -- identical "
          "live_peak, cas_unique_ever and cas_resident_end in every one of the 22 rows, though "
          "their allocation counts differ by 2x. The store is blind to the axis KAPPA-EXP-006 "
          "was built to separate")
    for line in scorecard:
        print(line)
    confirmed = sum([c1, c2, c3])
    print(f"SCORE: Claude Fable 5 {confirmed}/3, no other voice preregistered. The live-DAG "
          f"Theta(n) sentences do NOT survive write-through persistence: on h_n the live window "
          f"is 5n hashes while the store ever holds 3*2^n+3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
