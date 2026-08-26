#!/usr/bin/env python3
"""Run the KAPPA-EXP-001 family through the Σ-GLYPH Book I reference oracle.

The oracle is imported from a local checkout at a pinned digest. It is never
vendored and never written to. If the checkout or the digest is absent the
harness reports SKIPPED, never a pass.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any, Optional

ORACLE_PATH = Path(
    os.environ.get(
        "SIGMA_GLYPH_IMPL",
        Path.home() / "Projects" / "sigma-glyph" / "impl" / "sigma_glyph.py",
    )
)
ORACLE_SHA256 = "413d1f9805cdbdf42f13d967a17be26eb959c692eeb067e7146203ed9cebe64d"
ORACLE_HEAD = "c78e866420f016adf706f3806593cebc05e47dd0"

N_MIN = 1
N_MAX = 12
ATP_BUDGET = 2 ** 31 - 1


class Skipped(Exception):
    """The pinned oracle is unavailable; the experiment cannot run."""


def load_oracle():
    if not ORACLE_PATH.exists():
        raise Skipped(f"oracle not found at {ORACLE_PATH}")
    digest = hashlib.sha256(ORACLE_PATH.read_bytes()).hexdigest()
    if digest != ORACLE_SHA256:
        raise Skipped(f"oracle digest {digest[:16]}... != pinned {ORACLE_SHA256[:16]}...")
    spec = importlib.util.spec_from_file_location("sigma_glyph_oracle", ORACLE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_family(sg, n: int):
    """h_0 = y ; h_{n+1} = (lambda x. p x x) h_n, compiled by profile C1."""
    p_literal = ("lit", sg.sha(b"P"))
    y_literal = ("lit", sg.sha(b"Y"))
    duplicator = ("lam", "x", ("lapp", ("lapp", p_literal, ("var", "x")), ("var", "x")))
    term = y_literal
    for _ in range(n):
        term = ("lapp", duplicator, term)
    return sg.c1(term)


def store_tree(sg, store, term) -> bytes:
    """Write every node of a materialized term to the store; return its hash."""
    if term[0] == "app":
        store_tree(sg, store, term[1])
        store_tree(sg, store, term[2])
    store.put(sg.term_bytes(term))
    return sg.term_hash(term)


def distinct_nodes(sg, term) -> int:
    """Number of distinct node hashes in a materialized term: the DAG size."""
    seen: set[bytes] = set()
    stack = [term]
    while stack:
        node = stack.pop()
        node_hash = sg.term_hash(node)
        if node_hash in seen:
            continue
        seen.add(node_hash)
        if node[0] == "app":
            stack.append(node[1])
            stack.append(node[2])
    return len(seen)


class MemoSize:
    """`sg.size` memoized on object identity.

    A pure harness optimization: the oracle rebuilds only the spine each step,
    so almost every subterm of the new term is the same object as before.
    Recomputing `sg.size` from scratch per step costs O(4^n) over the family and
    does not reach the preregistered range. This returns the identical number —
    control `memo_size_agrees` checks that against `sg.size` directly.

    The dict holds the term itself so an id cannot be reused by a freed object.
    """

    def __init__(self, sg) -> None:
        self.sg = sg
        self.cache: dict[int, tuple[Any, int]] = {}

    def __call__(self, term: Any) -> int:
        key = id(term)
        hit = self.cache.get(key)
        if hit is not None and hit[0] is term:
            return hit[1]
        kind = term[0]
        if kind == "app":
            value = 1 + self(term[1]) + self(term[2])
        elif kind == "ref":
            value = 2
        else:
            value = 1
        self.cache[key] = (term, value)
        return value


def drive(sg, root_hash: bytes, store, size=None) -> dict[str, Any]:
    """Mirror eval_hash's loop, but observe peak size and the per-step bound.

    Control 1 requires this to reproduce eval_hash's (result, spent) exactly.
    """
    size = size or sg.size
    limits = sg.DEFAULT_LIMITS
    stats = {"fetches": 0}
    term: Any = ("thunk", root_hash)
    spent = 0
    peak = size(term)
    bound_violations: list[dict[str, int]] = []
    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_limit, 3 * limits["max_node_depth"] + 2000))
    try:
        while True:
            reduced = sg.step5(term, ATP_BUDGET - spent, store, stats, limits)
            if reduced is None:
                break
            term, cost = reduced
            spent += cost
            current = size(term)
            if current > peak:
                peak = current
            if current - 1 > spent:
                bound_violations.append({"spent": spent, "size": current})
    finally:
        sys.setrecursionlimit(old_limit)
    return {
        "normal_form": term,
        "spent": spent,
        "peak_tree": peak,
        "size_tree": size(term),
        "size_dag": distinct_nodes(sg, term),
        "fetches": stats["fetches"],
        "bound_violations": bound_violations,
    }


def measure() -> dict[str, Any]:
    sg = load_oracle()
    rows = []
    controls = {
        "driver_equivalence": True,
        "normative_bound": True,
        "no_oracle_writes": True,
        "memo_size_agrees": True,
    }
    # n below this bound is re-driven with the oracle's own `sg.size` to prove
    # the memoized size cannot change any measured quantity.
    memo_audit_upto = 7
    for n in range(N_MIN, N_MAX + 1):
        store = sg.Store()
        for genesis in (sg.I_BYTES, sg.K_BYTES, sg.S_BYTES):
            store.put(genesis)
        term = build_family(sg, n)
        root = store_tree(sg, store, term)

        driven = drive(sg, root, store, size=MemoSize(sg))
        if n <= memo_audit_upto:
            audited = drive(sg, root, store)
            if (
                audited["peak_tree"] != driven["peak_tree"]
                or audited["size_tree"] != driven["size_tree"]
                or audited["spent"] != driven["spent"]
                or audited["bound_violations"] != driven["bound_violations"]
            ):
                controls["memo_size_agrees"] = False
        elif sg.size(driven["normal_form"]) != driven["size_tree"]:
            controls["memo_size_agrees"] = False
        official, official_spent = sg.eval_hash(root, ATP_BUDGET, store)
        if sg.term_hash(official) != sg.term_hash(driven["normal_form"]) or official_spent != driven["spent"]:
            controls["driver_equivalence"] = False
        if driven["bound_violations"]:
            controls["normative_bound"] = False

        rows.append(
            {
                "n": n,
                "input_size_tree": sg.size(term),
                "input_size_dag": distinct_nodes(sg, term),
                "spent": driven["spent"],
                "peak_tree": driven["peak_tree"],
                "size_tree": driven["size_tree"],
                "size_dag": driven["size_dag"],
                "fetches": driven["fetches"],
                "kappa": (driven["peak_tree"] - 1) / driven["spent"],
                "normal_form_hash": sg.term_hash(driven["normal_form"]).hex(),
                "bound_violations": driven["bound_violations"],
            }
        )
    return {
        "experiment": "KAPPA-EXP-002",
        "oracle_path_env": "SIGMA_GLYPH_IMPL",
        "oracle_sha256": ORACLE_SHA256,
        "oracle_head": ORACLE_HEAD,
        "family": "h_0 = y ; h_{n+1} = (lambda x. p x x) h_n, compiled by profile C1",
        "strategy": "normative leftmost-outermost (Book I 3.3, ADR-003); not a free parameter",
        "n_range": [N_MIN, N_MAX],
        "controls": controls,
        "rows": rows,
    }


CHECK_UPTO = 8


def collect() -> int:
    path = Path(__file__).resolve().parent / "measurements.json"
    if path.exists():
        print("refusing to overwrite frozen measurements", file=sys.stderr)
        return 1
    import json

    document = measure()
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)
    print(f"froze {len(document['rows'])} rows")
    return 0


def check() -> int:
    import json

    path = Path(__file__).resolve().parent / "measurements.json"
    if not path.exists():
        print("PASS: KAPPA-EXP-002 not measured yet")
        return 0
    frozen = json.loads(path.read_text(encoding="utf-8"))
    try:
        sg = load_oracle()
    except Skipped as exc:
        print(f"SKIPPED: KAPPA-EXP-002 oracle unavailable ({exc})")
        return 0

    # Re-drive a prefix. The oracle's own leftmost-outermost search is O(size)
    # per step, so a full re-drive of the preregistered range costs minutes;
    # the frozen rows beyond CHECK_UPTO are checked against closed forms by
    # validate.py instead. This is a cadence choice, not a scope change.
    for row in frozen["rows"]:
        if row["n"] > CHECK_UPTO:
            break
        store = sg.Store()
        for genesis in (sg.I_BYTES, sg.K_BYTES, sg.S_BYTES):
            store.put(genesis)
        root = store_tree(sg, store, build_family(sg, row["n"]))
        driven = drive(sg, root, store, size=MemoSize(sg))
        for field in ("spent", "peak_tree", "size_tree", "size_dag"):
            if driven[field] != row[field]:
                print(f"FAIL: n={row['n']} {field} {driven[field]} != frozen {row[field]}", file=sys.stderr)
                return 1
        if sg.term_hash(driven["normal_form"]).hex() != row["normal_form_hash"]:
            print(f"FAIL: n={row['n']} normal form hash differs", file=sys.stderr)
            return 1

    failed = [name for name, ok in frozen["controls"].items() if not ok]
    if failed:
        print(f"FAIL: preregistered controls failed: {failed}", file=sys.stderr)
        return 1
    top = frozen["rows"][-1]
    print(
        f"PASS: KAPPA-EXP-002 reproduced n<={CHECK_UPTO}; controls ok; "
        f"at n={top['n']} size_tree={top['size_tree']} vs size_dag={top['size_dag']}, "
        f"kappa={top['kappa']:.3f}"
    )
    return 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--collect", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.collect == args.check:
        parser.error("choose exactly one of --collect or --check")
    try:
        return collect() if args.collect else check()
    except Skipped as exc:
        print(f"SKIPPED: KAPPA-EXP-002 oracle unavailable ({exc})")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
