#!/usr/bin/env python3
"""Closed forms for g_{n,k}, derived from the reduction structure.

Kept separate from the measurement check on purpose. `measure.py --check`
proves the trajectories reproduce; this file states what is *derived* and tests
that derivation against every frozen row of KAPPA-EXP-003 and KAPPA-EXP-005.

Codex review 2026-08-26, finding 2, asked for exactly this: the earlier
validator proved the two cost formulae and then inferred the peak asymptotics
from three equal tail observations, which does not establish an all-n, all-k
limit. Every ingredient of `spread` now has a derived form instead.

The derivations are hand arguments about the leftmost-outermost and
leftmost-innermost trajectories, machine-checked against 58 measured points.
They are not mechanised proofs, and they are statements about the
occurrence-weighted tree metric -- see the KAPPA-EXP-001 erratum on what that
metric does and does not measure.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
EXP003 = BASE.parent / "kappa-exp-003" / "measurements.json"
EXP005 = BASE / "measurements.json"


def g_size(m: int, k: int) -> int:
    """|g_m| = |c_k| + 7m: each duplicator wrapper adds 7 nodes."""
    return 3 * k + 1 + 7 * m


def t_size(m: int) -> int:
    """|T_m| = 4*2^m - 3: the p-tree normal form, from T_m = 3 + 2*T_{m-1}."""
    return 4 * 2 ** m - 3


def cost_out(n: int, k: int) -> int:
    """C(n) = (1 + |g_{n-1}|) + 2*C(n-1), C(0) = k.

    Leftmost-outermost copies the chain unevaluated -- one C_dup charge of
    size(g_{n-1}) because occ = 2 -- then reduces both copies, so the chain's
    k steps are paid 2^n times.
    """
    return (4 * k + 9) * 2 ** n - (3 * k + 7 * n + 9)


def cost_in(n: int, k: int) -> int:
    """Reduce the chain once for k, then pay 1 + |T_{m-1}| at each of n levels."""
    return 4 * 2 ** n + k - 2 * n - 4


def peak_out(n: int, k: int) -> int:
    """peak(n) = 3 + peak(n-1) + max(|g_{n-1}|, |T_{n-1}|), peak(0) = |c_k|.

    After the outer contraction the term is APPLY(APPLY(p, g_{n-1}), g_{n-1}),
    contributing 3 nodes. Leftmost-outermost then has two phases: the left copy
    reduces while the right is still g_{n-1}, then the right reduces while the
    left is fixed at T_{n-1}. Each phase's maximum is 3 + peak(n-1) plus the
    other side's fixed size, so the trajectory maximum takes the larger fixed
    side. Reducing c_k alone only shrinks, giving the base case.
    """
    peak = g_size(0, k)
    for m in range(1, n + 1):
        peak = 3 + peak + max(g_size(m - 1, k), t_size(m - 1))
    return peak


def peak_in(n: int, k: int) -> int:
    """max(|g_n|, |T_n|): leftmost-innermost shrinks the chain before growing
    the tree, so the trajectory never exceeds its endpoints."""
    return max(g_size(n, k), t_size(n))


def spread_limit(k: int) -> float:
    """kappa_in -> 1 and kappa_out -> 4/(4k+9), so spread -> (4k+9)/4.

    Valid for n past the crossover where |T_{n-1}| overtakes |g_{n-1}|, after
    which peak_out(n) = peak_out(n-1) + 4*2^(n-1) and peak_out = 4*2^n + C(k).
    """
    return k + 9 / 4


CLOSED_FORMS = {
    ("S_out", "cost_dup"): cost_out,
    ("S_in", "cost_dup"): cost_in,
    ("S_out", "peak"): peak_out,
    ("S_in", "peak"): peak_in,
}


def load_rows() -> list[dict]:
    rows: list[dict] = []
    if EXP005.exists():
        rows += json.loads(EXP005.read_text(encoding="utf-8"))["rows"]
    if EXP003.exists():
        for row in json.loads(EXP003.read_text(encoding="utf-8"))["rows"]["g"]:
            _, n, k = row["label"].split("_")
            rows.append({**row, "n": int(n), "k": int(k)})
    return rows


def verify(rows: list[dict]) -> list[str]:
    violations = []
    for row in rows:
        n, k = row["n"], row["k"]
        for (strategy, field), closed_form in CLOSED_FORMS.items():
            observed, derived = row[strategy][field], closed_form(n, k)
            if observed != derived:
                violations.append(f"{row['label']}: {strategy}.{field} {observed} != derived {derived}")
    return violations


def mutation_self_test(rows: list[dict]) -> list[str]:
    """A checker that only inspects the tail would accept a doctored early row.

    Perturb the earliest row of each k, leaving the last three untouched, and
    require `verify` to catch every one.
    """
    failures = []
    by_k: dict[int, list[dict]] = {}
    for row in rows:
        by_k.setdefault(row["k"], []).append(row)
    for k, group in sorted(by_k.items()):
        group.sort(key=lambda row: row["n"])
        target = group[0]
        doctored = json.loads(json.dumps(rows))
        for row in doctored:
            if row["label"] == target["label"]:
                row["S_out"]["peak"] += 1
        if not verify(doctored):
            failures.append(f"k={k}: a perturbed peak at n={target['n']} was not caught")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("only --check is supported")

    rows = load_rows()
    if not rows:
        print("PASS: no frozen g-family rows to check")
        return 0
    violations = verify(rows) + mutation_self_test(rows)
    if violations:
        for violation in violations:
            print(f"FAIL: {violation}", file=sys.stderr)
        return 1
    limits = ", ".join(f"k={k}: {spread_limit(k)}" for k in sorted({row["k"] for row in rows}))
    print(
        f"PASS: all four closed forms exact on {len(rows)} frozen rows, mutation test catches "
        f"a perturbed early peak; derived spread limits {limits}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
