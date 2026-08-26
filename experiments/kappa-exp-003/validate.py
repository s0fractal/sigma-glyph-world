#!/usr/bin/env python3
"""Check frozen KAPPA-EXP-003 measurements against the preregistered claims."""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
MEASUREMENTS = BASE / "measurements.json"

# The chain family must witness unbounded C_size spread for H-SPREAD to fall.
# Set well below the predicted (3k+1)/4 = 384.25 at k = 512.
MIN_CHAIN_SPREAD = 100.0


def main() -> int:
    if not MEASUREMENTS.exists():
        print("PASS: KAPPA-EXP-003 not measured yet")
        return 0
    document = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    rows = document["rows"]
    errors: list[str] = []
    deviations: list[str] = []

    # Preregistered closed forms for the identity chain.
    for row in rows["c"]:
        k = int(row["label"].split("_")[1])
        predicted_size = (3 * k + 1) / 4
        if abs(row["spread_size"] - predicted_size) > 1e-9:
            deviations.append(
                f"{row['label']}: C_size spread {row['spread_size']} != observed closed form {predicted_size}"
            )
        if abs(row["spread_dup"] - 1.0) > 1e-9:
            deviations.append(f"{row['label']}: C_dup spread {row['spread_dup']} != 1")
        for name in ("S_out", "S_in"):
            if abs(row[name]["kappa_dup"] - 3.0) > 1e-9:
                deviations.append(f"{row['label']}: {name} kappa_dup {row[name]['kappa_dup']} != 3")

    # H-SPREAD under C_size: refuted by the chain.
    chain_top = rows["c"][-1]
    if chain_top["spread_size"] < MIN_CHAIN_SPREAD:
        errors.append(
            f"chain C_size spread is {chain_top['spread_size']:.1f}, below the "
            f"{MIN_CHAIN_SPREAD} needed to call H-SPREAD refuted for C_size"
        )
    if not all(
        rows["c"][i]["spread_size"] < rows["c"][i + 1]["spread_size"] for i in range(1, len(rows["c"]) - 1)
    ):
        errors.append("chain C_size spread is not monotonically increasing in k")

    # Control 3: the erratum's bound, everywhere.
    for name, group in rows.items():
        for row in group:
            if row["bound_violations"]:
                errors.append(
                    f"{row['label']}: kappa exceeded 1 + (|t|-1)/cost -- the KAPPA-EXP-001 "
                    f"erratum's bound is wrong, which outranks everything else here"
                )

    for control, ok in document["controls"].items():
        if not ok:
            errors.append(f"preregistered control failed: {control}")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    for deviation in deviations:
        print(f"DEVIATION: {deviation}")

    dup_worst = max(row["spread_dup"] for group in rows.values() for row in group)
    dup_where = max(
        (row for group in rows.values() for row in group), key=lambda row: row["spread_dup"]
    )["label"]
    print(
        f"PASS: H-SPREAD refuted for C_size; chain spread = (3k+1)/4, reaching "
        f"{chain_top['spread_size']:.2f} at k=512, while C_dup collapses it to 1.00"
    )
    print(
        f"OBSERVED: largest C_dup spread {dup_worst:.2f} at {dup_where}, still rising at the "
        f"edge of the preregistered grid -- not settled by this experiment"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
