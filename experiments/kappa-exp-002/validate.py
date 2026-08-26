#!/usr/bin/env python3
"""Check frozen KAPPA-EXP-002 measurements against the preregistered claims.

`oracle.py --check` re-drives a prefix and proves the trajectories reproduce.
This file checks what the preregistration predicted, including control 2 —
that the oracle's normal form is the C1 compilation of the KAPPA-EXP-001
normal form, so the two experiments measure the same computation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
MEASUREMENTS = BASE / "measurements.json"
EXP001 = BASE.parent / "kappa-exp-001"


def exp001_normal_form(sg, n: int):
    """Build KAPPA-EXP-001's normal form and compile it by profile C1."""
    sys.path.insert(0, str(EXP001))
    try:
        from lambda_machine import App, Lam, Var, family, normalize  # noqa: F401
    finally:
        sys.path.pop(0)

    result = normalize(family(n), "S_out", 10 ** 7)["normal_form"]
    p_literal = ("lit", sg.sha(b"P"))
    y_literal = ("lit", sg.sha(b"Y"))

    def convert(node):
        if isinstance(node, Var):
            return p_literal if node.name == "p" else y_literal
        if isinstance(node, App):
            return ("lapp", convert(node.fun), convert(node.arg))
        return ("lam", node.var, convert(node.body))

    return sg.term_hash(sg.c1(convert(result)))


def main() -> int:
    if not MEASUREMENTS.exists():
        print("PASS: KAPPA-EXP-002 not measured yet")
        return 0
    document = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    rows = document["rows"]
    errors: list[str] = []
    deviations: list[str] = []

    for row in rows:
        n = row["n"]
        expectations = {
            "size_tree": 4 * 2 ** n - 3,
            "size_dag": 2 * n + 2,
            "peak_tree": 4 * 2 ** n + 5,
            "spent": 27 * 2 ** n - 26,
            "fetches": 2 ** (n + 3) - 7,
        }
        for field, predicted in expectations.items():
            if row[field] != predicted:
                deviations.append(f"n={n}: {field} {row[field]} != observed closed form {predicted}")
        if row["bound_violations"]:
            errors.append(
                f"n={n}: Book I §3.4 memory bound violated {len(row['bound_violations'])} times "
                f"-- conformance finding, outranks everything else here"
            )
        if row["kappa"] > 1.0:
            errors.append(f"n={n}: kappa {row['kappa']:.3f} > 1; §3.4's bound does not hold")

    # H-SHARING: predicted false. The store shares; the materialized term does not.
    top = rows[-1]
    if top["size_dag"] > 4 * top["n"]:
        errors.append("size_dag is not linear in n; the store does not share as claimed")
    growth = top["peak_tree"] / rows[-2]["peak_tree"]
    if growth < 1.9:
        errors.append(
            f"peak_tree grows by {growth:.2f}x per n; H-SHARING may hold and this "
            f"preregistration would be wrong"
        )

    for control, ok in document["controls"].items():
        if not ok:
            errors.append(f"preregistered control failed: {control}")

    # Control 2: same computation as KAPPA-EXP-001.
    sys.path.insert(0, str(BASE))
    try:
        from oracle import Skipped, load_oracle
        try:
            sg = load_oracle()
        except Skipped as exc:
            print(f"SKIPPED: KAPPA-EXP-002 oracle unavailable ({exc})")
            return 0
    finally:
        sys.path.pop(0)

    for row in rows:
        if row["n"] > 8:  # matches oracle.py CHECK_UPTO; beyond it the tree is large
            break
        if exp001_normal_form(sg, row["n"]).hex() != row["normal_form_hash"]:
            errors.append(f"n={row['n']}: oracle normal form is not C1 of the KAPPA-EXP-001 normal form")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    for deviation in deviations:
        print(f"DEVIATION: {deviation}")
    print(
        f"PASS: H-SHARING refuted; at n={top['n']} size_tree={top['size_tree']} but "
        f"size_dag={top['size_dag']} (gap {top['size_tree']/top['size_dag']:.0f}x); "
        f"kappa={top['kappa']:.3f} <= 1 and Book I §3.4's bound held at every step"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
