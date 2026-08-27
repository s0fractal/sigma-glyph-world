#!/usr/bin/env python3
"""Three machines, three families, two contracts -- measured side by side.

Machines are not re-implemented. `R_fresh` and `R_update` run through
KAPPA-EXP-007's own `tree_run`/`graph_run`; `R_abstract` through
KAPPA-EXP-008's `optimal_machine`, on its gated fragment only. Control 1 checks
both sets of frozen numbers.

A bounded runner exists for one purpose: the ungated `e_4` cells, where the
sound machines must be *measured* to saturate rather than asserted to. It is
validated against KAPPA-EXP-007's runners on gated cells (control 6) and its
numbers never enter a scorecard.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent
EXP007 = BASE.parent / "kappa-exp-007"
EXP008 = BASE.parent / "kappa-exp-008"
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(EXP008))

import contracts as ct  # noqa: E402
import families as fam  # noqa: E402
import graph_machine as gm  # noqa: E402
import optimal_machine as om  # noqa: E402
import representation as rp  # noqa: E402

_spec = importlib.util.spec_from_file_location("kappa_exp_007_measure", EXP007 / "measure.py")
exp007 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(exp007)
exp007.TREE_FAMILIES["e"] = fam.tree_family_e
exp007.GRAPH_FAMILIES["e"] = fam.graph_family_e

MEASUREMENTS = BASE / "measurements.json"
EXP007_MEASUREMENTS = EXP007 / "measurements.json"
EXP008_MEASUREMENTS = EXP008 / "measurements.json"

C_COMPACT, C_EXPLICIT = "C-compact", "C-explicit"
CONTRACTS = (C_COMPACT, C_EXPLICIT)
VARIANTS = {"R_fresh": ("S_out", "S_in"), "R_update": ("S_out", "S_in"),
            "R_abstract": om.SCHEDULES}
MACHINES = tuple(VARIANTS)
RANGES = {"e": [1, 2, 3, 4], "d": list(range(1, 11)), "h": list(range(1, 13))}
GATED = {"e": {1, 2, 3}, "d": set(range(1, 11)), "h": set(range(1, 13))}
CHECK_UPTO = 4

MEASURED, EXCLUDED_UNGATED = "MEASURED", "EXCLUDED_UNGATED"
STEP_CAP = 500
SIZE_WORK_CAP = 2_000_000
NODE_CAP = 200_000

TREE_BUILDERS = {"h": exp007.tree_family_h, "d": exp007.tree_family_d, "e": fam.tree_family_e}
GRAPH_BUILDERS = {"h": gm.family_h, "d": gm.family_d, "e": fam.graph_family_e}


def shape_digest(shape) -> str:
    return hashlib.sha256(repr(shape).encode()).hexdigest()[:16]


class Capture:
    """Grab the final term/root and count graph allocations, without editing
    KAPPA-EXP-006 or KAPPA-EXP-007. The tick hook is the machine's own
    `distinct_hashes`, called once per step with the current term."""

    def __init__(self) -> None:
        self.last = None
        self.node_allocations = 0
        self._saved: list[tuple] = []

    def __enter__(self):
        capture = self
        for module in (rp, gm):
            original = module.distinct_hashes

            def make(original=original):
                def hooked(term):
                    capture.last = term
                    return original(term)
                return hooked
            self._saved.append((module, "distinct_hashes", original))
            module.distinct_hashes = make()
        node_init = gm.Node.__init__

        def counted(self_node, kind, name=None, left=None, right=None):
            node_init(self_node, kind, name, left, right)
            capture.node_allocations += 1
        self._saved.append((gm.Node, "__init__", node_init))
        gm.Node.__init__ = counted
        return self

    def __exit__(self, *_):
        for owner, attribute, value in reversed(self._saved):
            setattr(owner, attribute, value)
        self._saved.clear()
        return False


def bounded_tree(family: str, n: int, strategy: str) -> dict[str, Any]:
    """R_fresh under deterministic caps. Used only for ungated cells."""
    rp.ALLOCATIONS[0] = 0
    term = rp.rebuild(TREE_BUILDERS[family](n))
    start = rp.ALLOCATIONS[0]
    step = rp.STRATEGIES[strategy]
    steps, size_work, peak = 0, 0, rp.distinct_objects(term)
    saturated = None
    while True:
        if steps >= STEP_CAP:
            saturated = f"steps>={STEP_CAP}"
            break
        if size_work >= SIZE_WORK_CAP:
            saturated = f"size_work>={SIZE_WORK_CAP}"
            break
        # Guard BEFORE the step: one leftmost-outermost step on a copying
        # machine can allocate twice the term, so a cap checked only between
        # steps does not bound the run.
        if term.size > NODE_CAP:
            saturated = f"nodes>{NODE_CAP}"
            break
        reduced = step(term, True)
        if reduced is None:
            break
        steps += 1
        term = reduced[0]
        size_work += term.size
        peak = max(peak, term.size)
    return {"steps": steps, "peak_distinct_objects": peak, "size_work": size_work,
            "allocations": rp.ALLOCATIONS[0] - start, "saturated": saturated,
            "final": term}


def bounded_graph(family: str, n: int, strategy: str) -> dict[str, Any]:
    """R_update under the same caps."""
    with Capture() as capture:
        root = GRAPH_BUILDERS[family](n)
        find = gm.FINDERS[strategy]
        steps, size_work, peak = 0, 0, gm.distinct_objects(root)
        saturated = None
        while True:
            if steps >= STEP_CAP:
                saturated = f"steps>={STEP_CAP}"
                break
            if size_work >= SIZE_WORK_CAP:
                saturated = f"size_work>={SIZE_WORK_CAP}"
                break
            if gm.distinct_objects(root) > NODE_CAP:
                saturated = f"nodes>{NODE_CAP}"
                break
            redex = find(root)
            if redex is None:
                break
            gm.contract_in_place(redex)
            steps += 1
            live = gm.distinct_objects(root)
            size_work += live
            peak = max(peak, live)
    return {"steps": steps, "peak_distinct_objects": peak, "size_work": size_work,
            "allocations": capture.node_allocations, "saturated": saturated, "final": root}


def run_cell(machine: str, variant: str, family: str, n: int) -> dict[str, Any]:
    gated = n in GATED[family]
    if machine == "R_abstract":
        if not gated:
            return {"category": EXCLUDED_UNGATED,
                    "why": "outside KAPPA-EXP-008's G1; the EXP-008 erratum's rule"}
        pointwise: list[tuple[int, int, int]] = []
        net = om.encode(GRAPH_BUILDERS[family](n))
        run = om.normalize(net, variant, pointwise=pointwise)
        if run["saturated"]:
            return {"category": f"SATURATED({run['saturated']})"}
        spine, probe = ct.spine_net(net)
        explicit = om.readback(net)
        output_nodes, build_work = gm.occurrence_size(explicit), gm.occurrence_size(explicit)
        final_internal = run["final_term"] + run["final_book"]
        return {
            "category": MEASURED, "spine": spine, "probe_steps": probe,
            "work_internal_native": run["interactions"],
            "work_internal_nodes": run["allocated_term"] + run["allocated_book"],
            "peak_internal": run["peak_total"], "final_internal": final_internal,
            "output_nodes": output_nodes, "build_work": build_work,
            "beta": run["beta_interactions"],
            "census": {"term": run["allocated_term"], "book": run["allocated_book"]},
            "estimand": ct.bookkeeping_fraction_at_peak(pointwise),
            "retracted_max_over_max": (max(point[1] for point in pointwise)
                                       / max(point[2] for point in pointwise)),
            "pointwise_len": len(pointwise),
            "shape": shape_digest(gm.de_bruijn(explicit)),
            "frozen_key": f"R_optimal.{variant}",
        }
    if not gated:
        if machine == "R_update" and family == "e":
            # KAPPA-EXP-007's cost model calls occurrence_size on the TREE view of
            # a shared graph at every contraction. On e_n that view is
            # astronomically larger than the DAG, so no node cap bounds a single
            # step, and bounding it would mean editing a frozen machine. REFUSED
            # is the preregistered category for exactly this.
            return {"category": "REFUSED(per-step cost unbounded by any node cap "
                                "under KAPPA-EXP-007's frozen cost model)"}
        bounded = (bounded_tree if machine == "R_fresh" else bounded_graph)(family, n, variant)
        final = bounded.pop("final")
        record = {"category": f"SATURATED({bounded['saturated']})" if bounded["saturated"]
                  else MEASURED, "bounded": bounded,
                  "why": "ungated context point under deterministic caps; enters no scorecard"}
        if not bounded["saturated"]:
            record["spine"] = (ct.spine_tree(final) if machine == "R_fresh"
                               else ct.spine_graph(final))[0]
        return record
    with Capture() as capture:
        if machine == "R_update":
            receipt = exp007.graph_run(family, n, variant)
        else:
            receipt = exp007.tree_run(family, n, variant, True)
    receipt.pop("normal_form", None)
    final = capture.last
    if machine == "R_update":
        spine, probe = ct.spine_graph(final)
        output_nodes, build_work = ct.explicit_from_graph(final)
        final_internal = gm.distinct_objects(final)
        allocations = capture.node_allocations
        shape = shape_digest(gm.de_bruijn(final))
    else:
        spine, probe = ct.spine_tree(final)
        output_nodes, build_work = ct.explicit_from_tree(final)
        final_internal = rp.distinct_objects(final)
        allocations = receipt["allocations"]
        shape = shape_digest(rp.de_bruijn(final))
    return {
        "category": MEASURED, "spine": spine, "probe_steps": probe,
        "work_internal_native": receipt["steps"], "work_internal_nodes": allocations,
        "peak_internal": receipt["peak_distinct_objects"], "final_internal": final_internal,
        "output_nodes": output_nodes, "build_work": build_work,
        "census": {"term": allocations, "book": 0},
        "estimand": {"instant": None, "book": 0, "total": receipt["peak_distinct_objects"],
                     "fraction": 0.0, "ties": 0},
        "shape": shape, "receipt": receipt, "frozen_key": f"{machine}.{variant}",
    }


def cost_under(cell: dict[str, Any], contract: str) -> dict[str, Any]:
    """The two contracts, never averaged, never merged."""
    if cell["category"] != MEASURED or "peak_internal" not in cell:
        return {"category": cell["category"]}
    if contract == C_COMPACT:
        readback_native, readback_nodes = cell["probe_steps"], 0
        peak_endtoend = cell["peak_internal"]
    else:
        readback_native, readback_nodes = cell["build_work"], cell["build_work"]
        peak_endtoend = max(cell["peak_internal"], cell["final_internal"] + cell["build_work"])
    return {
        "category": MEASURED,
        "work_internal": cell["work_internal_native"],
        "work_readback": readback_native,
        "work_total": cell["work_internal_native"] + readback_native,
        "work_internal_nodes": cell["work_internal_nodes"],
        "work_readback_nodes": readback_nodes,
        "work_total_nodes": cell["work_internal_nodes"] + readback_nodes,
        "peak_internal": cell["peak_internal"],
        "peak_endtoend": peak_endtoend,
    }


# --------------------------------------------------------------------------
# the estimand controls
# --------------------------------------------------------------------------

def estimand_mutations(pointwise) -> dict[str, Any]:
    """Control 5, as preregistered and as it has to be repaired.

    The preregistration asks for "a planted trace mutation (swapping two
    instants)" that must flip the estimand. It cannot: `book_t/total_t` at
    `argmax(total_t)` reads the multiset of states, so permuting two instants
    leaves the peak state -- and therefore the estimand -- identical. Reported
    as measured, and filed as erratum candidate KAPPA-EXP-009-E1 rather than
    quietly replaced.

    Two mutations that do bite are added, and they are the ones that separate
    the preregistered estimand from the `max/max` ratio it replaces:
      RELOCATE -- make a differently-composed instant the peak;
      RECOMPOSE -- change the composition at the peak instant itself.
    """
    base = ct.bookkeeping_fraction_at_peak(pointwise)
    outcome = {"baseline": base["fraction"]}

    swapped = list(pointwise)
    if base["instant"] is not None and len(swapped) > 1:
        other = 0 if base["instant"] != 0 else len(swapped) - 1
        swapped[base["instant"]], swapped[other] = swapped[other], swapped[base["instant"]]
    outcome["swap_two_instants"] = ct.bookkeeping_fraction_at_peak(swapped)["fraction"]
    outcome["swap_flips"] = outcome["swap_two_instants"] != base["fraction"]

    relocated = list(pointwise)
    target = next((i for i, point in enumerate(relocated)
                   if point[2] and (point[1] / point[2]) != base["fraction"]), None)
    if target is not None:
        term, book, total = relocated[target]
        relocated[target] = (term, book, total)
        lift = base["total"] + 1 - total
        relocated[target] = (term + lift, book, total + lift)
    outcome["relocate_peak"] = ct.bookkeeping_fraction_at_peak(relocated)["fraction"]
    outcome["relocate_flips"] = outcome["relocate_peak"] != base["fraction"]

    recomposed = list(pointwise)
    if base["instant"] is not None:
        term, book, total = recomposed[base["instant"]]
        recomposed[base["instant"]] = (term - 1, book + 1, total)
    outcome["recompose_peak"] = ct.bookkeeping_fraction_at_peak(recomposed)["fraction"]
    outcome["recompose_flips"] = outcome["recompose_peak"] != base["fraction"]

    maxima = (max(point[1] for point in pointwise) /
              max(point[2] for point in pointwise)) if pointwise else None
    outcome["retracted_max_over_max"] = maxima
    outcome["differs_from_max_over_max"] = maxima != base["fraction"]
    return outcome


# --------------------------------------------------------------------------
# the grid
# --------------------------------------------------------------------------

def measure(ranges: dict[str, list[int]] | None = None) -> dict[str, Any]:
    ranges = ranges or {family: list(indices) for family, indices in RANGES.items()}
    controls = {"frozen_reproduction": True, "spine_agrees": True,
                "explicit_alpha_equivalent": True, "determinism": True,
                "estimand_mutation_bites": True, "bounded_runner_agrees": True}
    failures: list[str] = []
    categories: dict[str, int] = {}
    frozen007 = (json.loads(EXP007_MEASUREMENTS.read_text(encoding="utf-8"))["rows"]
                 if EXP007_MEASUREMENTS.exists() else {})
    frozen008 = (json.loads(EXP008_MEASUREMENTS.read_text(encoding="utf-8"))["rows"]
                 if EXP008_MEASUREMENTS.exists() else {})
    rows: dict[str, list[dict[str, Any]]] = {}
    mutation_report: dict[str, Any] = {}

    for family, indices in ranges.items():
        rows[family] = []
        for n in indices:
            if os.environ.get("KAPPA009_PROGRESS"):
                print(f"  {family}_{n}", file=sys.stderr, flush=True)
            row: dict[str, Any] = {"n": n, "gated": n in GATED[family]}
            spines: dict[str, list[str]] = {}
            shapes: dict[str, Any] = {}
            for machine in MACHINES:
                for variant in VARIANTS[machine]:
                    key = f"{machine}.{variant}"
                    if os.environ.get("KAPPA009_PROGRESS"):
                        print(f"    {family}_{n} {key}", file=sys.stderr, flush=True)
                    cell = run_cell(machine, variant, family, n)
                    categories[cell["category"]] = categories.get(cell["category"], 0) + 1
                    # Controls 2 and 3 range over gated cells only: an ungated
                    # context point is not a measured point of this experiment.
                    if cell["category"] == MEASURED and row["gated"] and "shape" in cell:
                        spines[key] = cell["spine"]
                        # Control 3: the explicit output is the reference term.
                        shapes[key] = cell["shape"]
                        # Control 1: frozen numbers.
                        prior_rows = frozen008 if machine == "R_abstract" else frozen007
                        prior = next((item for item in prior_rows.get(family, [])
                                      if item["n"] == n), None)
                        if prior is not None and cell["frozen_key"] in prior:
                            theirs = prior[cell["frozen_key"]]
                            mine = cell.get("receipt")
                            if mine is not None:
                                for field, value in theirs.items():
                                    if field in mine and mine[field] != value:
                                        controls["frozen_reproduction"] = False
                                        failures.append(f"{family}_{n} {key}.{field}: "
                                                        f"{mine[field]} != {value}")
                            elif machine == "R_abstract":
                                for field in ("interactions", "beta_interactions", "peak_total"):
                                    got = cell["work_internal_native"] if field == "interactions" \
                                        else (cell["beta"] if field == "beta_interactions"
                                              else cell["peak_internal"])
                                    if got != theirs[field]:
                                        controls["frozen_reproduction"] = False
                                        failures.append(f"{family}_{n} {key}.{field}: "
                                                        f"{got} != {theirs[field]}")
                    row[key] = {"cell": {k: v for k, v in cell.items()
                                         if k not in ("receipt", "frozen_key")},
                                **{contract: cost_under(cell, contract) for contract in CONTRACTS}}
            if len(set(map(tuple, spines.values()))) > 1:
                controls["spine_agrees"] = False
                failures.append(f"{family}_{n}: spine(8) disagrees across machines: {spines}")
            if len(set(shapes.values())) > 1:
                controls["explicit_alpha_equivalent"] = False
                failures.append(f"{family}_{n}: explicit outputs are not alpha-equivalent")
            row["spine"] = next(iter(spines.values()), None)
            rows[family].append(row)

    # Control 4: determinism, on one cell per machine.
    for machine in MACHINES:
        variant = VARIANTS[machine][0]
        first = run_cell(machine, variant, "d", 4)
        second = run_cell(machine, variant, "d", 4)
        first.pop("receipt", None)
        second.pop("receipt", None)
        if first != second:
            controls["determinism"] = False
            failures.append(f"{machine}.{variant} on d_4 is not deterministic")

    # Control 5: the estimand mutations.
    pointwise: list[tuple[int, int, int]] = []
    net = om.encode(GRAPH_BUILDERS["d"](10))
    om.normalize(net, om.SCHEDULES[0], pointwise=pointwise)
    mutation_report = estimand_mutations(pointwise)
    if not (mutation_report["relocate_flips"] and mutation_report["recompose_flips"]):
        controls["estimand_mutation_bites"] = False
        failures.append("neither repaired estimand mutation flips the value")

    # Control 6: the bounded runner reproduces the frozen runners where both apply.
    for family, n in (("h", 4), ("d", 4), ("e", 3)):
        for strategy in ("S_out", "S_in"):
            reference = exp007.tree_run(family, n, strategy, True)
            bounded = bounded_tree(family, n, strategy)
            if (bounded["steps"], bounded["allocations"]) != (
                    reference["steps"], reference["allocations"]):
                controls["bounded_runner_agrees"] = False
                failures.append(f"bounded tree runner disagrees on {family}_{n}/{strategy}")

    return {
        "experiment": "KAPPA-EXP-009",
        "contracts": {
            C_COMPACT: "graph plus spine(8); answering the 8 probes is in-band",
            C_EXPLICIT: "the full explicit normal form as a tree; building it is in-band",
        },
        "estimand": "book_t / total_t at t = argmax(total_t); never max(book)/max(total)",
        "machines": {"R_fresh": "KAPPA-EXP-007, verbatim",
                     "R_update": "KAPPA-EXP-007, verbatim",
                     "R_abstract": "KAPPA-EXP-008, gated fragment only"},
        "ranges": {family: [indices[0], indices[-1]] for family, indices in ranges.items()},
        "gated": {family: sorted(GATED[family]) for family in ranges},
        "caps": {"steps": STEP_CAP, "size_work": SIZE_WORK_CAP},
        "category_counts": categories,
        "controls": controls,
        "control_failures": failures,
        "estimand_mutations": mutation_report,
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
    print(f"froze {sum(len(group) for group in document['rows'].values())} rows; "
          f"categories {document['category_counts']}; controls {document['controls']}")
    return 0


def check() -> int:
    if not MEASUREMENTS.exists():
        print("PASS: KAPPA-EXP-009 not measured yet")
        return 0
    frozen = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    prefix = {family: [n for n in indices if n <= CHECK_UPTO]
              for family, indices in RANGES.items()}
    recomputed = measure(prefix)
    for family, indices in prefix.items():
        for row in recomputed["rows"][family]:
            prior = next(item for item in frozen["rows"][family] if item["n"] == row["n"])
            if json.loads(json.dumps(row)) != prior:
                differing = [k for k in set(row) | set(prior)
                             if json.loads(json.dumps(row.get(k))) != prior.get(k)]
                print(f"FAIL: {family}_{row['n']} differs on recomputation: {differing}",
                      file=sys.stderr)
                return 1
    failed = [name for name, ok in frozen["controls"].items() if not ok]
    if failed:
        print(f"FAIL: preregistered controls failed: {failed}", file=sys.stderr)
        return 1
    print(f"PASS: KAPPA-EXP-009 reproduced n<={CHECK_UPTO} on all three families; "
          f"controls ok; categories {frozen['category_counts']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collect", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.collect == args.check:
        parser.error("choose exactly one of --collect or --check")
    return collect() if args.collect else check()


def _deep(target) -> int:
    import threading
    sys.setrecursionlimit(1_000_000)
    threading.stack_size(512 * 1024 * 1024)
    box: list[int] = []
    thread = threading.Thread(target=lambda: box.append(target()))
    thread.start()
    thread.join()
    return box[0] if box else 1


if __name__ == "__main__":
    raise SystemExit(_deep(main))
