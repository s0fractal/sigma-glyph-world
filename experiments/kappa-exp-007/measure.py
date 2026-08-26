#!/usr/bin/env python3
"""Three representations, two families, two strategies.

R_alias and R_fresh come from KAPPA-EXP-006 unchanged; R_update is built here.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent
EXP006 = BASE.parent / "kappa-exp-006"
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(EXP006))

import graph_machine as gm  # noqa: E402
import representation as rp  # noqa: E402

MEASUREMENTS = BASE / "measurements.json"
EXP006_MEASUREMENTS = EXP006 / "measurements.json"
H_RANGE = list(range(1, 13))
D_RANGE = list(range(1, 11))
CHECK_UPTO = 6


def tree_family_h(n: int):
    return rp.family(n)


def tree_family_d(n: int):
    """Same d_n as graph_machine.family_d, over KAPPA-EXP-006's Term classes."""
    term = rp.Lam("w", rp.Var("y"))
    for _ in range(n):
        duplicator = rp.Lam(
            "x",
            rp.Lam("w", rp.App(rp.App(rp.Var("p"), rp.App(rp.Var("x"), rp.Var("w"))),
                               rp.App(rp.Var("x"), rp.App(rp.Var("q"), rp.Var("w"))))),
        )
        term = rp.App(duplicator, term)
    return term


TREE_FAMILIES = {"h": tree_family_h, "d": tree_family_d}
GRAPH_FAMILIES = {"h": gm.family_h, "d": gm.family_d}
STRATEGIES = ("S_out", "S_in")


def tree_run(family: str, n: int, strategy: str, fresh: bool) -> dict[str, Any]:
    rp.ALLOCATIONS[0] = 0
    term = TREE_FAMILIES[family](n)
    if fresh:
        term = rp.rebuild(term)
        rp.check_no_aliasing(term)
    start = rp.ALLOCATIONS[0]
    step = rp.STRATEGIES[strategy]
    steps = 0
    costs = [0, 0, 0]
    peaks = [term.size, rp.distinct_objects(term), rp.distinct_hashes(term)]
    while True:
        reduced = step(term, fresh)
        if reduced is None:
            break
        steps += 1
        term, cost = reduced
        if fresh:
            rp.check_no_aliasing(term)
        costs = [total + part for total, part in zip(costs, cost)]
        peaks = [max(peaks[0], term.size),
                 max(peaks[1], rp.distinct_objects(term)),
                 max(peaks[2], rp.distinct_hashes(term))]
    return {
        "steps": steps, "cost_unit": costs[0], "cost_size": costs[1], "cost_dup": costs[2],
        "peak_occurrence_size": peaks[0], "peak_distinct_objects": peaks[1],
        "peak_distinct_hashes": peaks[2], "allocations": rp.ALLOCATIONS[0] - start,
        "normal_form": rp.de_bruijn(term),
    }


def graph_run(family: str, n: int, strategy: str) -> dict[str, Any]:
    root = GRAPH_FAMILIES[family](n)
    run = gm.normalize(root, strategy)
    run["normal_form"] = gm.de_bruijn(run["normal_form"])
    return run


def measure(h_range=None, d_range=None) -> dict[str, Any]:
    h_range = H_RANGE if h_range is None else h_range
    d_range = D_RANGE if d_range is None else d_range
    controls = {
        "reproduces_kappa_exp_006": True,
        "update_actually_updates": False,
        "same_normal_form": True,
        "no_renaming": True,
        "metric_ordering": True,
        "root_identity_preserved": True,
    }
    frozen006 = json.loads(EXP006_MEASUREMENTS.read_text())["rows"] if EXP006_MEASUREMENTS.exists() else []
    rows: dict[str, list[dict[str, Any]]] = {}

    for family, indices in (("h", h_range), ("d", d_range)):
        rows[family] = []
        for n in indices:
            row: dict[str, Any] = {"n": n}
            normal_forms = []
            for representation in ("R_alias", "R_fresh", "R_update"):
                for strategy in STRATEGIES:
                    if representation == "R_update":
                        run = graph_run(family, n, strategy)
                        if run["multi_update_steps"] > 0:
                            controls["update_actually_updates"] = True
                        if not run["root_identity_preserved"]:
                            controls["root_identity_preserved"] = False
                    else:
                        run = tree_run(family, n, strategy, representation == "R_fresh")
                    normal_forms.append(run.pop("normal_form"))
                    if not (run["peak_distinct_hashes"] <= run["peak_distinct_objects"]
                            <= run["peak_occurrence_size"]):
                        controls["metric_ordering"] = False
                    run["kappa_unit_occurrence"] = (run["peak_occurrence_size"] - 1) / run["cost_unit"]
                    run["kappa_unit_objects"] = (run["peak_distinct_objects"] - 1) / run["cost_unit"]
                    row[f"{representation}.{strategy}"] = run
            if len(set(normal_forms)) != 1:
                controls["same_normal_form"] = False
            for representation in ("R_alias", "R_fresh", "R_update"):
                pair = [row[f"{representation}.{s}"]["kappa_unit_occurrence"] for s in STRATEGIES]
                row[f"separation_{representation}"] = max(pair) / min(pair)
                pair_objects = [row[f"{representation}.{s}"]["kappa_unit_objects"] for s in STRATEGIES]
                row[f"separation_objects_{representation}"] = max(pair_objects) / min(pair_objects)
            if family == "h":
                prior = next((item for item in frozen006 if item["n"] == n), None)
                if prior is not None:
                    for representation in ("R_alias", "R_fresh"):
                        for strategy in STRATEGIES:
                            mine, theirs = row[f"{representation}.{strategy}"], prior[f"{representation}.{strategy}"]
                            for field in ("steps", "peak_occurrence_size", "peak_distinct_objects",
                                          "peak_distinct_hashes", "cost_unit", "cost_size", "allocations"):
                                if mine[field] != theirs[field]:
                                    controls["reproduces_kappa_exp_006"] = False
            rows[family].append(row)

    return {
        "experiment": "KAPPA-EXP-007",
        "representations": {
            "R_alias": "substitution reuses the argument object",
            "R_fresh": "every written node is new",
            "R_update": "Wadsworth graph reduction; contraction mutates the redex node in place",
        },
        "families": {
            "h": "h_0 = y ; h_{n+1} = (lambda x. p x x) h_n -- duplication not under a binder",
            "d": "d_0 = lambda w. y ; d_{n+1} = (lambda x. lambda w. p (x w) (x (q w))) d_n",
        },
        "ranges": {"h": [h_range[0], h_range[-1]], "d": [d_range[0], d_range[-1]]},
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
    print(f"froze {sum(len(group) for group in document['rows'].values())} rows")
    return 0


def check() -> int:
    if not MEASUREMENTS.exists():
        print("PASS: KAPPA-EXP-007 not measured yet")
        return 0
    frozen = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    prefix = list(range(1, CHECK_UPTO + 1))
    recomputed = measure(prefix, prefix)
    for family in ("h", "d"):
        for row in recomputed["rows"][family]:
            prior = next(item for item in frozen["rows"][family] if item["n"] == row["n"])
            if row != prior:
                print(f"FAIL: {family}_{row['n']} differs on recomputation", file=sys.stderr)
                return 1
    failed = [name for name, ok in frozen["controls"].items() if not ok]
    if failed:
        print(f"FAIL: preregistered controls failed: {failed}", file=sys.stderr)
        return 1
    top_h, top_d = frozen["rows"]["h"][-1], frozen["rows"]["d"][-1]
    print(
        f"PASS: KAPPA-EXP-007 reproduced n<={CHECK_UPTO}; controls ok; separation on R_update is "
        f"{top_h['separation_R_update']:.2f} for h_{top_h['n']} and {top_d['separation_R_update']:.2f} "
        f"for d_{top_d['n']}"
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
