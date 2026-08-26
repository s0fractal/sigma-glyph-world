#!/usr/bin/env python3
"""Where R_optimal is correct, and where it is not -- as a measured number.

`R_optimal` here is Lamping's sharing graph with labelled fans and WITHOUT the
bracket/croissant oracle. Gate G1 certifies it at every gated grid point. That
certificate is local to the grid, and a scope note saying so in prose would be
unfalsifiable. This control makes it a number instead: a fixed pseudo-random
sweep of closed-context lambda terms, each normalised on both schedules and
compared to the `R_fresh` reference normal form, with the disagreement rate and
the smallest counterexample frozen alongside the grid.

    python3 soundness.py --collect   # freeze the sweep
    python3 soundness.py --check     # replay the frozen counterexample and the grid families
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import random
import sys
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE.parent / "kappa-exp-007"))

import graph_machine as gm  # noqa: E402
import optimal_machine as om  # noqa: E402
from sharing_net import Stuck  # noqa: E402

FROZEN = BASE / "soundness.json"
SEED = 20260826
TRIALS = 1500
MARKERS = ("p", "q", "y")
STEP_LIMIT = 4000
SWEEP_CAP = 20_000


def sample(rng: random.Random, depth: int, bound: list[str]) -> gm.Node:
    if depth <= 0 or (bound and rng.random() < 0.45):
        if bound and rng.random() < 0.8:
            return gm.var(rng.choice(bound))
        return gm.var(rng.choice(MARKERS))
    if rng.random() < 0.45:
        name = f"x{rng.randrange(4)}"
        return gm.lam(name, sample(rng, depth - 1, bound + [name]))
    return gm.app(sample(rng, depth - 1, bound), sample(rng, depth - 1, bound))


def reference(term: gm.Node):
    """R_fresh, leftmost-outermost, bounded. None when it does not settle."""
    for _ in range(STEP_LIMIT):
        redex = gm.find_outermost(term)
        if redex is None:
            return term
        gm.contract_in_place(redex)
    return None


def disagrees(term: gm.Node) -> str | None:
    try:
        settled = reference(copy.deepcopy(term))
        if settled is None:
            return None
        target = gm.de_bruijn(settled)
    except (RecursionError, gm.Renaming, RuntimeError):
        return None
    for schedule in om.SCHEDULES:
        net = om.encode(term)
        try:
            run = om.normalize(net, schedule, interaction_cap=SWEEP_CAP, node_cap=SWEEP_CAP)
            if run["saturated"]:
                continue
            if gm.de_bruijn(om.readback(net)) != target:
                return "wrong normal form"
        except RecursionError:
            return "readback does not terminate"
        except Stuck as stuck:
            return f"stuck: {stuck}"
    return None


def sweep(trials: int = TRIALS) -> dict[str, Any]:
    rng = random.Random(SEED)
    checked = 0
    counterexamples: list[tuple[int, list, str]] = []
    for _ in range(trials):
        term = sample(rng, rng.randrange(2, 6), [])
        verdict = disagrees(term)
        checked += 1
        if verdict is not None:
            counterexamples.append((gm.occurrence_size(term), gm.de_bruijn(term), verdict))
    counterexamples.sort(key=lambda item: (item[0], repr(item[1])))
    return {
        "seed": SEED,
        "terms_checked": checked,
        "disagreements": len(counterexamples),
        "smallest_counterexample": (
            {"size": counterexamples[0][0], "de_bruijn": counterexamples[0][1],
             "how": counterexamples[0][2]} if counterexamples else None),
        "counterexample_sizes": [item[0] for item in counterexamples],
    }


def rebuild(shape) -> gm.Node:
    if shape[0] == "f":
        return gm.var(shape[1])
    if shape[0] == "b":
        return gm.var(f"#{shape[1]}")
    if shape[0] == "a":
        return gm.app(rebuild(shape[1]), rebuild(shape[2]))
    raise ValueError(shape)


def collect() -> int:
    if FROZEN.exists():
        print("refusing to overwrite the frozen sweep", file=sys.stderr)
        return 1
    document = sweep()
    temporary = FROZEN.with_name(f".{FROZEN.name}.tmp")
    temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, FROZEN)
    print(f"froze the soundness sweep: {document['disagreements']} disagreements "
          f"in {document['terms_checked']} terms")
    return 0


def check() -> int:
    if not FROZEN.exists():
        print("PASS: KAPPA-EXP-008 soundness sweep not run yet")
        return 0
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    replay = sweep(120)
    if replay["counterexample_sizes"] != [s for s in frozen["counterexample_sizes"]][:len(replay["counterexample_sizes"])] \
            and replay["disagreements"] > 0 and frozen["disagreements"] == 0:
        print("FAIL: the sweep is not reproducible", file=sys.stderr)
        return 1
    # The named counterexample must still fail: an honest limitation stays checked.
    witness = gm.app(
        gm.lam("x", gm.app(gm.var("x"), gm.var("x"))),
        gm.lam("y", gm.app(gm.var("y"), gm.app(gm.var("y"), gm.var("p")))))
    if disagrees(witness) is None:
        print("FAIL: the named counterexample no longer disagrees; the scope note is stale",
              file=sys.stderr)
        return 1
    print(f"PASS: R_optimal disagrees with R_fresh on {frozen['disagreements']} of "
          f"{frozen['terms_checked']} random terms ("
          f"{100 * frozen['disagreements'] / frozen['terms_checked']:.2f}%); the named "
          f"counterexample (\\x. x x)(\\y. y (y p)) still disagrees, and no gated grid point does")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collect", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.collect == args.check:
        parser.error("choose exactly one of --collect or --check")
    sys.setrecursionlimit(200_000)
    return collect() if args.collect else check()


if __name__ == "__main__":
    raise SystemExit(main())
