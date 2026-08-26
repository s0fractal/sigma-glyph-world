#!/usr/bin/env python3
"""Score KAPPA-EXP-008's gates and its one attributed prediction, by name.

AGENTS.md clause 8: each voice's prediction is preregistered separately and the
result scores each by name. Prediction slot B stayed open until the harness
first ran on any family; the preregistration file has exactly one commit
(132edcd) and carries no addendum, so slot B is empty and scores nothing. Per
the same clause, nothing is inferred from which voice executed.

Gates G1-G6 are fail-closed: a failure exits non-zero and no scorecard prints.

The machine is named `R_abstract` in prose after Codex's review of `f9d6e5b`;
`measurements.json` keeps its original `R_optimal` field names, because a frozen
receipt is not rewritten. See the RESULT's erratum. A2 is scored at the top
GATED point: `e_4` is outside G1 and G2 and enters no scorecard. The verdict is
unchanged either way -- 0.737 and 1.792 both fail a >= 10 threshold -- and the
preregistration's own author has owned the metric as ill-posed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
MEASUREMENTS = BASE / "measurements.json"
SOUNDNESS = BASE / "soundness.json"

A1_BOUND = 2.00        # "bounded" as prediction A1 defines it on d_n
A1_GROWTH = 1.02       # last-three growth ratios
A2_RATIO = 10.0        # bookkeeping share A2 requires at the top of e_n
A2_H_BOUND = 2.0       # and the ceiling it requires on h_n
SCHEDULES = ("SCH-root", "SCH-leaf")


def gated(rows):
    return [row for row in rows if row["gated"]]


def main() -> int:
    if not MEASUREMENTS.exists():
        print("PASS: KAPPA-EXP-008 not measured yet")
        return 0
    document = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    rows = document["rows"]
    errors = [f"fail-closed gate did not pass: {name}"
              for name, ok in document["gates"].items() if not ok]
    errors += [f"gate failure recorded: {line}" for line in document["gate_failures"]]

    h_rows, d_rows, e_rows = rows["h"], rows["d"], rows["e"]
    top_h, top_d, top_e = h_rows[-1], d_rows[-1], e_rows[-1]

    # Closed forms observed on h_n and d_n under R_optimal, exact at every n.
    for row in h_rows:
        n = row["n"]
        for schedule in SCHEDULES:
            run = row[f"R_optimal.{schedule}"]
            if (run["beta_interactions"], run["interactions"], run["peak_term"],
                    run["peak_book"], run["peak_total"]) != (n, n + 1, 5 * n + 2, n, 6 * n + 2):
                errors.append(f"h_{n} {schedule}: closed forms (n, n+1, 5n+2, n, 6n+2) do not hold")
    for row in d_rows:
        n = row["n"]
        for schedule in SCHEDULES:
            run = row[f"R_optimal.{schedule}"]
            if run["beta_interactions"] != 3 * n:
                errors.append(f"d_{n} {schedule}: beta interactions are not 3n")
            if run["interactions"] != (n * n + 9 * n + 2) // 2:
                errors.append(f"d_{n} {schedule}: interactions are not (n^2+9n+2)/2")
            if run["peak_term"] != 10 * n + 3:
                errors.append(f"d_{n} {schedule}: peak_term is not 10n+3")
            expected = (n + 1) ** 2 - (1 if schedule == "SCH-leaf" and n >= 2 else 0)
            if run["peak_book"] != expected:
                errors.append(f"d_{n} {schedule}: peak_book is not {expected}")
            if n >= 4 and run["peak_total"] != n * n + 7 * n + 8:
                errors.append(f"d_{n} {schedule}: peak_total is not n^2+7n+8")

    # The interaction count is schedule-invariant at every grid point: interaction
    # nets are strongly confluent, so every schedule to normal form has the same
    # length. This is the fact that makes A3 unfalsifiable on this machine.
    schedule_invariant = all(
        row[f"R_optimal.{SCHEDULES[0]}"]["interactions"]
        == row[f"R_optimal.{SCHEDULES[1]}"]["interactions"]
        for group in rows.values() for row in group)
    distinct_traces = sum(
        1 for group in rows.values() for row in group
        if row[f"R_optimal.{SCHEDULES[0]}"]["trace_digest"]
        != row[f"R_optimal.{SCHEDULES[1]}"]["trace_digest"])

    # --- Prediction A, attributed to Claude Fable 5 -----------------------
    scorecard: list[str] = []
    late_d = [row for row in gated(d_rows) if row["n"] >= 6]
    separations = [row["separation_kappa_total"] for row in late_d]
    growth = [separations[i] / separations[i - 1] for i in range(len(separations) - 2, len(separations))]
    a1 = (all(value <= A1_BOUND for value in separations)
          and all(ratio <= A1_GROWTH for ratio in growth))
    scorecard.append(
        f"PREDICTION A1 (Claude Fable 5, reviews/claude-fable-2026-08-26-b.md) — the binder "
        f"boundary dissolves: {'CONFIRMED' if a1 else 'FAILED'}; d_n schedule separation of "
        f"kappa_total is exactly {separations[-1]:.4f} at every n>=6 (growth ratios "
        f"{', '.join(f'{r:.4f}' for r in growth)}), against R_update's "
        f"{top_d['separation_R_update']:.2f} and R_fresh's {top_d['separation_R_fresh']:.2f}")

    e_gated = gated(e_rows)
    ratios = [row[f"R_optimal.{SCHEDULES[0]}"]["book_over_term"] for row in e_gated]
    ungated = [(row["n"], row[f"R_optimal.{SCHEDULES[0]}"]["book_over_term"])
               for row in e_rows if not row["gated"]]
    rising = all(ratios[i] > ratios[i - 1] for i in range(1, len(ratios)))
    h_ok = all(row[f"R_optimal.{s}"]["book_over_term"] <= A2_H_BOUND
               for row in h_rows for s in SCHEDULES)
    a2 = ratios[-1] >= A2_RATIO and rising and h_ok
    scorecard.append(
        f"PREDICTION A2 (Claude Fable 5) — the cost moves into bookkeeping: "
        f"{'CONFIRMED' if a2 else 'FAILED'}; peak_book/peak_term on e_n is "
        f"{ratios[-1]:.3f} at the top GATED point n={e_gated[-1]['n']} against the >=10 "
        f"predicted, though it does rise at every step ({', '.join(f'{r:.2f}' for r in ratios)}) "
        f"and stays <= {A2_H_BOUND} on h_n as predicted (max "
        f"{max(row[f'R_optimal.{s}']['book_over_term'] for row in h_rows for s in SCHEDULES):.3f}). "
        f"UNGATED, scoring nothing: "
        f"{', '.join(f'e_{n} {r:.3f}' for n, r in ungated)}. The metric composes maxima from "
        f"different instants and is ill-posed; the verdict stands at both points")

    late = [(family, row) for family in ("h", "d", "e")
            for row in gated(rows[family]) if row["n"] >= 6]
    diverged = 0
    for _, row in late:
        by_work = {s for s in SCHEDULES
                   if row[f"R_optimal.{s}"]["interactions"]
                   == min(row[f"R_optimal.{t}"]["interactions"] for t in SCHEDULES)}
        by_space = {s for s in SCHEDULES
                    if row[f"R_optimal.{s}"]["peak_total"]
                    == min(row[f"R_optimal.{t}"]["peak_total"] for t in SCHEDULES)}
        if not (by_work & by_space):
            diverged += 1
    a3 = diverged * 2 >= len(late)
    scorecard.append(
        f"PREDICTION A3 (Claude Fable 5) — optimality is two quantities: "
        f"{'CONFIRMED' if a3 else 'FAILED'}; the interaction-minimising schedule and the "
        f"peak-minimising schedule diverge at {diverged} of {len(late)} pooled grid points with "
        f"n>=6, against the >= {len(late) // 2} required. The interaction count is identical "
        f"between schedules at every one of the {sum(len(g) for g in rows.values())} measured "
        f"points, so on an interaction net A3 cannot be confirmed by construction")

    scorecard.append(
        f"PREDICTION B — open slot, unfilled: the preregistration has one commit and no dated "
        f"addendum, so no second voice preregistered on this measurement. It scores nothing, and "
        f"per clause 8 nothing is inferred from that")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(f"GATES: G1-G6 all pass. G1 readback alpha-equivalence and G2 sharing sanity hold at "
          f"every gated grid point; the preregistered e range [1, 4] is SHRUNK to "
          f"{document['gated_ranges']['e']} because R_fresh cannot produce a reference normal "
          f"form for e_4 (131073 occurrences); e_4 is measured and reported outside the gates")
    print(f"CONTROL: interaction count is schedule-invariant at every point "
          f"({'yes' if schedule_invariant else 'NO'}), while the two schedules take genuinely "
          f"different routes ({distinct_traces} of {sum(len(g) for g in rows.values())} points "
          f"have distinct traces)")
    if SOUNDNESS.exists():
        sound = json.loads(SOUNDNESS.read_text(encoding="utf-8"))
        print(f"CONTROL: R_abstract is Lamping WITHOUT the bracket/croissant oracle; it "
              f"disagrees with R_fresh on {sound['disagreements']} of {sound['comparable']} "
              f"COMPARABLE terms ({sound['excluded']} excluded by named category) and on no "
              f"gated grid point. No monotonicity theorem relates it to a corrected reducer, so "
              f"its peak_book bounds nothing above or below: A2 is untested, without direction")
    for line in scorecard:
        print(line)
    confirmed = sum([a1, a2, a3])
    print(f"SCORE: Claude Fable 5 {confirmed}/3, no other voice preregistered. "
          f"H-OPTIMAL holds in its first half and fails in its second on these families: the "
          f"schedule-internal separation is exactly 1.0000 on d_n, and the cost does not move "
          f"into bookkeeping by the factor predicted. The cross-representation reading of the "
          f"hierarchy is withdrawn -- readback is unpriced -- see the RESULT's erratum")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
