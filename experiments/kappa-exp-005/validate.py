#!/usr/bin/env python3
"""Check frozen KAPPA-EXP-005 measurements, including a failed prediction.

The preregistered prediction was wrong in both directions. That is recorded
here as PREDICTION FAILED lines on every green run, not smoothed away.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
MEASUREMENTS = BASE / "measurements.json"
PREDICTED_G14_8_SPREAD = 100.0


def cost_out(n: int, k: int) -> int:
    """Derived: C(n) = (1 + |g_{n-1}|) + 2·C(n-1), C(0) = k, |g_m| = 3k+1+7m."""
    return (4 * k + 9) * 2 ** n - (3 * k + 7 * n + 9)


def cost_in(n: int, k: int) -> int:
    """Derived: reduce the chain once, then duplicate T_{m-1} at each level."""
    return 4 * 2 ** n + k - 2 * n - 4


def main() -> int:
    if not MEASUREMENTS.exists():
        print("PASS: KAPPA-EXP-005 not measured yet")
        return 0
    document = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    rows = document["rows"]
    errors: list[str] = []
    notes: list[str] = []

    # Derived closed forms for both strategies' C_dup cost.
    for row in rows:
        n, k = row["n"], row["k"]
        if row["S_out"]["cost_dup"] != cost_out(n, k):
            errors.append(f"{row['label']}: S_out cost_dup {row['S_out']['cost_dup']} != derived {cost_out(n, k)}")
        if row["S_in"]["cost_dup"] != cost_in(n, k):
            errors.append(f"{row['label']}: S_in cost_dup {row['S_in']['cost_dup']} != derived {cost_in(n, k)}")
        if row["bound_violations"]:
            errors.append(f"{row['label']}: kappa exceeded the KAPPA-EXP-001 erratum bound")

    for control, ok in document["controls"].items():
        if not ok:
            errors.append(f"preregistered control failed: {control}")

    by_k: dict[int, list[dict]] = {}
    for row in rows:
        by_k.setdefault(row["k"], []).append(row)
    for k in by_k:
        by_k[k].sort(key=lambda row: row["n"])

    # Falsifier 2 of the preregistration, explicitly.
    g14_8 = next((row for row in rows if row["n"] == 14 and row["k"] == 8), None)
    if g14_8 and g14_8["spread_dup"] <= PREDICTED_G14_8_SPREAD:
        notes.append(
            f"PREDICTION FAILED: preregistered spread_C_dup(g_14_8) > {PREDICTED_G14_8_SPREAD:.0f}; "
            f"measured {g14_8['spread_dup']:.2f}"
        )

    # The prediction also said n drives the spread exponentially. It saturates.
    for k, group in sorted(by_k.items()):
        if len(group) < 4:
            continue
        tail = [group[i + 1]["spread_dup"] / group[i]["spread_dup"] for i in range(len(group) - 4, len(group) - 1)]
        if max(tail) < 1.2:
            notes.append(
                f"PREDICTION FAILED: at k={k} the spread saturates in n "
                f"(last growth ratios {', '.join(f'{r:.3f}' for r in tail)}), not doubling"
            )

    # The observed limit law that replaced the prediction.
    for k, group in sorted(by_k.items()):
        top = group[-1]
        limit = k + 9 / 4
        if top["spread_dup"] > limit + 1e-9:
            errors.append(f"k={k}: spread {top['spread_dup']:.4f} exceeds the observed limit k+9/4={limit}")
        # peak excess over the normal form must be constant in n for the limit to hold
        excess = {row["S_out"]["peak"] - (4 * 2 ** row["n"] - 3) for row in group[-3:]}
        if len(excess) != 1:
            errors.append(f"k={k}: S_out peak excess over the normal form is not constant in n: {sorted(excess)}")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    for note in notes:
        print(note)
    limits = ", ".join(f"k={k}: {group[-1]['spread_dup']:.2f}→{k + 9/4}" for k, group in sorted(by_k.items()) if k in (2, 8, 32))
    print(
        f"PASS: H-SPREAD-DUP refuted, by k and not by n; spread(g_n_k) → k + 9/4 as n → ∞ ({limits}), "
        f"unbounded in the family's free parameter"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
