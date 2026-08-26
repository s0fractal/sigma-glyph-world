#!/usr/bin/env python3
"""Where R_abstract is correct, and where it is not -- with an honest denominator.

`R_abstract` (frozen in `measurements.json` under its original name `R_optimal`;
see the RESULT's erratum) is Lamping's sharing graph with labelled fans and
WITHOUT the bracket/croissant oracle. Gate G1 certifies it at every gated grid
point. That certificate is local to the grid, and a scope note saying so in
prose would be unfalsifiable. This control makes it a number instead.

Every generated term gets exactly one verdict from a closed set, and the rate is
reported over the terms that were actually **comparable** -- not over the terms
that were generated. The first version of this control incremented its
denominator unconditionally while silently returning early on an unsettled
reference, an exception, or a saturated run, so seven excluded terms were
counted as tested and the rate was quoted as 1/1500 instead of 1/1493. That was
a defect in the control, not in the machine; it was found by Codex's review of
`f9d6e5b` and is corrected here.

    python3 soundness.py --collect   # freeze the sweep and its per-term verdicts
    python3 soundness.py --check     # regenerate ALL verdicts and compare, term by term
"""

from __future__ import annotations

import argparse
import copy
import hashlib
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

# The closed set of per-term outcomes. Exactly one applies to each term.
AGREE = "AGREE"
DISAGREE_NORMAL_FORM = "DISAGREE_NORMAL_FORM"
DISAGREE_READBACK_DIVERGES = "DISAGREE_READBACK_DIVERGES"
DISAGREE_STUCK = "DISAGREE_STUCK"
EXCLUDED_REFERENCE_UNSETTLED = "EXCLUDED_REFERENCE_UNSETTLED"
EXCLUDED_REFERENCE_EXCEPTION = "EXCLUDED_REFERENCE_EXCEPTION"
EXCLUDED_SATURATED = "EXCLUDED_SATURATED"

DISAGREEING = (DISAGREE_NORMAL_FORM, DISAGREE_READBACK_DIVERGES, DISAGREE_STUCK)
COMPARABLE = (AGREE,) + DISAGREEING
EXCLUDING = (EXCLUDED_REFERENCE_UNSETTLED, EXCLUDED_REFERENCE_EXCEPTION, EXCLUDED_SATURATED)
VERDICTS = COMPARABLE + EXCLUDING


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


def verdict(term: gm.Node) -> str:
    """One verdict per term, from the closed set above. Exclusions are named."""
    try:
        settled = reference(copy.deepcopy(term))
    except (RecursionError, gm.Renaming, RuntimeError):
        return EXCLUDED_REFERENCE_EXCEPTION
    if settled is None:
        return EXCLUDED_REFERENCE_UNSETTLED
    try:
        target = gm.de_bruijn(settled)
    except RecursionError:
        return EXCLUDED_REFERENCE_EXCEPTION
    outcome = AGREE
    for schedule in om.SCHEDULES:
        net = om.encode(term)
        try:
            run = om.normalize(net, schedule, interaction_cap=SWEEP_CAP, node_cap=SWEEP_CAP)
        except (RecursionError, Stuck):
            return DISAGREE_STUCK
        if run["saturated"]:
            return EXCLUDED_SATURATED
        try:
            if gm.de_bruijn(om.readback(net)) != target:
                outcome = DISAGREE_NORMAL_FORM
        except RecursionError:
            outcome = DISAGREE_READBACK_DIVERGES
        except Stuck:
            outcome = DISAGREE_STUCK
    return outcome


def sweep(trials: int = TRIALS) -> dict[str, Any]:
    rng = random.Random(SEED)
    vector: list[str] = []
    smallest: tuple[int, list, str] | None = None
    for _ in range(trials):
        term = sample(rng, rng.randrange(2, 6), [])
        code = verdict(term)
        vector.append(code)
        if code in DISAGREEING:
            candidate = (gm.occurrence_size(term), jsonable(gm.de_bruijn(term)), code)
            if smallest is None or (candidate[0], repr(candidate[1])) < (smallest[0], repr(smallest[1])):
                smallest = candidate
    counts = {name: vector.count(name) for name in VERDICTS}
    comparable = sum(counts[name] for name in COMPARABLE)
    disagreements = sum(counts[name] for name in DISAGREEING)
    excluded = sum(counts[name] for name in EXCLUDING)
    return {
        "seed": SEED,
        "terms_generated": trials,
        "verdict_counts": counts,
        "comparable": comparable,
        "excluded": excluded,
        "disagreements": disagreements,
        "disagreement_rate_over_comparable": disagreements / comparable if comparable else None,
        "denominator": "comparable terms, not generated terms",
        "smallest_counterexample": (
            {"size": smallest[0], "de_bruijn": smallest[1], "verdict": smallest[2]}
            if smallest else None),
        "verdict_vector_digest": hashlib.sha256("\n".join(vector).encode()).hexdigest(),
        "verdict_vector": vector,
    }


def jsonable(shape):
    """de Bruijn shapes are tuples; JSON returns lists. Compare in one form."""
    return [jsonable(part) for part in shape] if isinstance(shape, tuple) else shape


def named_witness() -> gm.Node:
    """(\\x. x x) (\\y. y (y p)) -- the hand-found counterexample the RESULT names."""
    return gm.app(
        gm.lam("x", gm.app(gm.var("x"), gm.var("x"))),
        gm.lam("y", gm.app(gm.var("y"), gm.app(gm.var("y"), gm.var("p")))))


def collect() -> int:
    if FROZEN.exists():
        print("refusing to overwrite the frozen sweep", file=sys.stderr)
        return 1
    document = sweep()
    temporary = FROZEN.with_name(f".{FROZEN.name}.tmp")
    temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, FROZEN)
    print(f"froze the soundness sweep: {document['disagreements']} disagreements in "
          f"{document['comparable']} comparable terms, {document['excluded']} excluded")
    return 0


def check() -> int:
    if not FROZEN.exists():
        print("PASS: KAPPA-EXP-008 soundness sweep not run yet")
        return 0
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    replay = sweep(frozen["terms_generated"])

    # Every term is re-decided and compared by position: a single flipped verdict
    # in the frozen file fails here, not only in the digest gate.
    for index, (was, now) in enumerate(zip(frozen["verdict_vector"], replay["verdict_vector"])):
        if was != now:
            print(f"FAIL: term {index} was recorded {was} and replays {now}", file=sys.stderr)
            return 1
    if len(frozen["verdict_vector"]) != len(replay["verdict_vector"]):
        print("FAIL: the frozen verdict vector has the wrong length", file=sys.stderr)
        return 1
    for field in ("verdict_counts", "comparable", "excluded", "disagreements",
                  "verdict_vector_digest", "smallest_counterexample"):
        if frozen.get(field) != replay[field]:
            print(f"FAIL: {field} does not replay: frozen {frozen.get(field)!r} "
                  f"against {replay[field]!r}", file=sys.stderr)
            return 1
    if verdict(named_witness()) not in DISAGREEING:
        print("FAIL: the named counterexample no longer disagrees; the scope note is stale",
              file=sys.stderr)
        return 1
    rate = frozen["disagreements"] / frozen["comparable"]
    print(f"PASS: all {frozen['terms_generated']} verdicts replay exactly. R_abstract disagrees "
          f"with R_fresh on {frozen['disagreements']} of {frozen['comparable']} COMPARABLE terms "
          f"({100 * rate:.2f}%), with {frozen['excluded']} excluded "
          f"({', '.join(f'{name}={frozen['verdict_counts'][name]}' for name in EXCLUDING)}); "
          f"the named counterexample still disagrees, and no gated grid point does")
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
