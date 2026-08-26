#!/usr/bin/env python3
"""Measure the strategy spread of κ over three λ families and three cost models.

Reuses the frozen KAPPA-EXP-001 machine unchanged: same calculus, same explicit
tree representation, same two strategies. Only the families, the cost columns,
and the derived quantity are new.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parent / "kappa-exp-001"))

from lambda_machine import App, Lam, Var, de_bruijn, family, normalize  # noqa: E402

MEASUREMENTS = BASE / "measurements.json"
STEP_CEILING = 10 ** 7
COST_MODELS = ("cost_unit", "cost_size", "cost_dup")
STRATEGIES = ("S_out", "S_in")

H_RANGE = list(range(1, 13))
C_RANGE = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
G_RANGE = [(n, k) for n in range(1, 7) for k in (2, 8, 32)]

# c_512 is a spine of depth 512; substitution and the de Bruijn control both
# recurse over it. A harness detail, not a semantic one.
sys.setrecursionlimit(20000)


def chain(k: int):
    """c_0 = y ; c_{k+1} = (lambda z. z) c_k"""
    identity = Lam("z", Var("z"))
    term = Var("y")
    for _ in range(k):
        term = App(identity, term)
    return term


def chain_under_duplication(n: int, k: int):
    """g_0 = c_k ; g_{m+1} = (lambda x. p x x) g_m"""
    duplicator = Lam("x", App(App(Var("p"), Var("x")), Var("x")))
    term = chain(k)
    for _ in range(n):
        term = App(duplicator, term)
    return term


def measure_term(label: str, term) -> dict[str, Any]:
    runs = {name: normalize(term, name, STEP_CEILING) for name in STRATEGIES}
    same_normal_form = de_bruijn(runs["S_out"]["normal_form"]) == de_bruijn(runs["S_in"]["normal_form"])

    row: dict[str, Any] = {
        "label": label,
        "input_size": term.size,
        "same_normal_form": same_normal_form,
        "bound_violations": [],
    }
    for name, run in runs.items():
        entry = {"steps": run["steps"], "peak": run["peak"]}
        for model in COST_MODELS:
            cost = run[model]
            kappa = (run["peak"] - 1) / cost if cost else None
            entry[model] = cost
            entry["kappa_" + model.split("_")[1]] = kappa
            # Control 3: the erratum's bound, for materialization-charging models.
            if model != "cost_unit" and kappa is not None:
                ceiling = 1 + (term.size - 1) / cost
                if kappa > ceiling + 1e-12:
                    row["bound_violations"].append(
                        {"strategy": name, "model": model, "kappa": kappa, "ceiling": ceiling}
                    )
        row[name] = entry

    for model in COST_MODELS:
        key = "kappa_" + model.split("_")[1]
        values = [row[name][key] for name in STRATEGIES]
        low, high = min(values), max(values)
        row["spread_" + model.split("_")[1]] = (high / low) if low else None
    return row


def measure() -> dict[str, Any]:
    families = {
        "h": [(f"h_{n}", family(n)) for n in H_RANGE],
        "c": [(f"c_{k}", chain(k)) for k in C_RANGE],
        "g": [(f"g_{n}_{k}", chain_under_duplication(n, k)) for n, k in G_RANGE],
    }
    rows = {name: [measure_term(label, term) for label, term in items] for name, items in families.items()}
    controls = {
        "same_normal_form": all(row["same_normal_form"] for group in rows.values() for row in group),
        "no_renaming": True,  # lambda_machine raises Renaming; reaching here means it never fired
        "erratum_bound": all(not row["bound_violations"] for group in rows.values() for row in group),
        "terminated": True,  # normalize raises past the ceiling
    }
    return {
        "experiment": "KAPPA-EXP-003",
        "machine": "KAPPA-EXP-001 lambda_machine, unchanged",
        "strategies": list(STRATEGIES),
        "cost_models": list(COST_MODELS),
        "spread": "max_S kappa_S(t) / min_S kappa_S(t) over the two strategies",
        "families": {
            "h": "h_0 = y ; h_{n+1} = (lambda x. p x x) h_n",
            "c": "c_0 = y ; c_{k+1} = (lambda z. z) c_k",
            "g": "g_0 = c_k ; g_{m+1} = (lambda x. p x x) g_m",
        },
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
    total = sum(len(group) for group in document["rows"].values())
    print(f"froze {total} measured terms")
    return 0


def check() -> int:
    if not MEASUREMENTS.exists():
        print("PASS: KAPPA-EXP-003 not measured yet")
        return 0
    frozen = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    if frozen["rows"] != measure()["rows"]:
        print("FAIL: recomputed measurements differ from measurements.json", file=sys.stderr)
        return 1
    failed = [name for name, ok in frozen["controls"].items() if not ok]
    if failed:
        print(f"FAIL: preregistered controls failed: {failed}", file=sys.stderr)
        return 1
    worst = max(row["spread_size"] for row in frozen["rows"]["c"])
    print(
        f"PASS: KAPPA-EXP-003 reproduced; {sum(len(g) for g in frozen['rows'].values())} terms, "
        f"controls ok; max C_size spread on the chain family {worst:.1f}"
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
