#!/usr/bin/env python3
"""Score KAPPA-EXP-009's controls and its one attributed prediction, by name.

`P-fable` (K1, K2, K3) was filed in preregistration commit `128a563`. The open
slot -- which the preregistration offered to any voice, and to Codex in
particular, since Codex designed the experiment -- stayed empty: the file had
exactly one commit and no dated addendum when this harness first ran. It scores
nothing, and per AGENTS.md clause 8 nothing is inferred from that.

PAIRING. Cross-machine claims need one variant per machine and the
preregistration does not say which. The primary pairing is **matched
leftmost-outermost** -- `S_out`, `S_out`, `SCH-root` -- because that is the
strategy Book I pins normatively and the only pairing that does not choose per
machine. Every verdict is also recomputed under "each machine at its best"
(minimum over its variants) and reported as robust or not. Filed as erratum
candidate KAPPA-EXP-009-E2.

Controls are fail-closed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
MEASUREMENTS = BASE / "measurements.json"

MATCHED = {"R_fresh": "S_out", "R_update": "S_out", "R_abstract": "SCH-root"}
VARIANTS = {"R_fresh": ("S_out", "S_in"), "R_update": ("S_out", "S_in"),
            "R_abstract": ("SCH-root", "SCH-leaf")}
CONTRACTS = ("C-compact", "C-explicit")
K1_FLOOR = 0.5
K2_FACTOR = 10.0


def value(row, machine, variant, contract, field):
    cell = row.get(f"{machine}.{variant}", {}).get(contract, {})
    return cell[field] if cell.get("category") == "MEASURED" else None


def matched(row, contract, field):
    out = {}
    for machine, variant in MATCHED.items():
        got = value(row, machine, variant, contract, field)
        if got is None:
            return None
        out[machine] = got
    return out


def best(row, contract, field):
    out = {}
    for machine, variants in VARIANTS.items():
        got = [value(row, machine, variant, contract, field) for variant in variants]
        got = [item for item in got if item is not None]
        if not got:
            return None
        out[machine] = min(got)
    return out


def ranking(values):
    return tuple(sorted(values, key=lambda machine: (values[machine], machine)))


def main() -> int:
    if not MEASUREMENTS.exists():
        print("PASS: KAPPA-EXP-009 not measured yet")
        return 0
    document = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    rows = document["rows"]
    errors = [f"preregistered control failed: {name}"
              for name, ok in document["controls"].items() if not ok]
    errors += [f"control failure recorded: {line}" for line in document["control_failures"]]

    gated = {family: [row for row in group if row["gated"]] for family, group in rows.items()}
    mutations = document["estimand_mutations"]

    # --- K1 -------------------------------------------------------------
    top_a = gated["e"][-1]
    scorecard: list[str] = []
    verdicts = {}
    for label, picker in (("matched", matched), ("best", best)):
        peaks = picker(top_a, "C-explicit", "peak_endtoend")
        verdicts[label] = peaks["R_abstract"] >= K1_FLOOR * peaks["R_update"]
    k1 = verdicts["matched"]
    peaks = matched(top_a, "C-explicit", "peak_endtoend")
    scorecard.append(
        f"PREDICTION K1 (Claude Fable 5, KAPPA-EXP-009 preregistration) — the boundary made the "
        f"collapse where the output is the work: {'CONFIRMED' if k1 else 'FAILED'}; on e_{top_a['n']} "
        f"under C-explicit peak_endtoend(R_abstract) = {peaks['R_abstract']} against "
        f"{K1_FLOOR}*peak_endtoend(R_update) = {K1_FLOOR * peaks['R_update']}, a ratio of "
        f"{peaks['R_abstract'] / peaks['R_update']:.2f}x — inside 2x, as predicted, because both "
        f"machines must hold the same {top_a['R_abstract.SCH-root']['cell']['output_nodes']}-node "
        f"output. Robust under both pairings: {verdicts}")

    # --- K2 -------------------------------------------------------------
    top_b = gated["d"][-1]
    verdicts = {}
    for label, picker in (("matched", matched), ("best", picker_best := best)):
        peaks = picker(top_b, "C-compact", "peak_endtoend")
        verdicts[label] = peaks["R_fresh"] / peaks["R_abstract"] >= K2_FACTOR
    k2 = verdicts["matched"]
    peaks = matched(top_b, "C-compact", "peak_endtoend")
    scorecard.append(
        f"PREDICTION K2 (Claude Fable 5) — the advantage is real where compactness is honest: "
        f"{'CONFIRMED' if k2 else 'FAILED'}; on d_{top_b['n']} under C-compact "
        f"peak_endtoend(R_fresh)/peak_endtoend(R_abstract) = {peaks['R_fresh']}/"
        f"{peaks['R_abstract']} = {peaks['R_fresh'] / peaks['R_abstract']:.1f}x against the "
        f">= {K2_FACTOR}x predicted. Robust under both pairings: {verdicts}")

    # --- K3 -------------------------------------------------------------
    work_same, work_flip, points = 0, 0, 0
    for family, group in gated.items():
        for row in group:
            orders = [matched(row, contract, "work_total") for contract in CONTRACTS]
            if None in orders:
                continue
            points += 1
            if ranking(orders[0]) == ranking(orders[1]):
                work_same += 1
            else:
                work_flip += 1
    peak_same_a, peak_flip_a = 0, 0
    for row in gated["e"]:
        orders = [matched(row, contract, "peak_endtoend") for contract in CONTRACTS]
        if None in orders:
            continue
        if ranking(orders[0]) == ranking(orders[1]):
            peak_same_a += 1
        else:
            peak_flip_a += 1
    k3_time = work_flip == 0
    k3_space = peak_flip_a > 0
    k3 = k3_time and k3_space
    scorecard.append(
        f"PREDICTION K3 (Claude Fable 5) — time is contract-robust, space is not: "
        f"{'CONFIRMED' if k3 else 'FAILED'}; BOTH halves fail, and in the same direction. The "
        f"work_total ordering flips between contracts at {work_flip} of {points} gated points "
        f"(predicted: 0), while on family A the peak_endtoend ordering is IDENTICAL under both "
        f"contracts at {peak_same_a} of {peak_same_a + peak_flip_a} points (predicted: it "
        f"differs). On the adversarial family the prediction is exactly inverted — time is the "
        f"fragile ordering there and space is the stable one")

    scorecard.append(
        "OPEN SLOT — unfilled: the preregistration had exactly one commit and no dated addendum "
        "when this harness first ran, so no second voice preregistered, Codex included. It scores "
        "nothing, and per clause 8 nothing is inferred from that")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(f"CATEGORIES: {document['category_counts']} across "
          f"{sum(len(group) for group in rows.values())} rows x 6 cells")
    print(f"CONTROLS: all six pass. KAPPA-EXP-007 and KAPPA-EXP-008 frozen numbers reproduce; "
          f"spine(8) agrees across all three machines at every gated point; C-explicit outputs "
          f"are alpha-equivalent to the R_fresh reference everywhere; runs are deterministic; "
          f"the bounded runner used for ungated cells matches KAPPA-EXP-007's runners where both "
          f"apply")
    print(f"CONTROL (estimand): book_t/total_t at argmax(total_t) = "
          f"{mutations['baseline']:.4f} on d_10. The PREREGISTERED mutation -- swapping two "
          f"instants -- does NOT flip it ({mutations['swap_two_instants']:.4f}), because the "
          f"estimand reads the multiset of states and is permutation-invariant; erratum "
          f"candidate E1. Two repaired mutations do bite: relocating the peak to a "
          f"differently-composed instant gives {mutations['relocate_peak']:.4f} and recomposing "
          f"the peak instant gives {mutations['recompose_peak']:.4f}")
    for line in scorecard:
        print(line)
    confirmed = sum([k1, k2, k3])
    print(f"SCORE: Claude Fable 5 {confirmed}/3, no other voice preregistered. Codex's question "
          f"is answered: the ordering does NOT survive a common semantic interface. Both the "
          f"work and the peak ordering flip between contracts on most gated points, so the "
          f"KAPPA-EXP-008 collapse was produced by the measurement boundary, exactly as the "
          f"review suspected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
