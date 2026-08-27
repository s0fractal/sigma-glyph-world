#!/usr/bin/env python3
"""The two output contracts, and one observer every machine must answer.

KAPPA-EXP-008's erratum found that its harness priced graph reduction and not
readback, so machines delivering different outputs were compared as though they
delivered the same one. This module fixes the interface instead of the machine:

- **C-compact** -- the outcome is whatever the machine holds, plus `spine(8)`.
  Answering the 8 probes is in-band; nothing else is demanded.
- **C-explicit** -- the outcome is the explicit normal form as a tree. Building
  it is in-band: its constructions count as `work_readback`, its nodes in the
  census, its live nodes in `peak_endtoend`.

`spine(k)` is alpha-invariant by construction: an abstraction reports `lam`, an
application `app`, a free variable its name, and a bound variable its de Bruijn
index relative to the binders passed on the way down. Control 2 requires all
three machines to return the same 8 symbols at every measured point -- that is
what makes C-compact one contract rather than three.
"""

from __future__ import annotations

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parent / "kappa-exp-006"))
sys.path.insert(0, str(BASE.parent / "kappa-exp-007"))
sys.path.insert(0, str(BASE.parent / "kappa-exp-008"))

import graph_machine as gm  # noqa: E402
import optimal_machine as om  # noqa: E402
import representation as rp  # noqa: E402
from sharing_net import APP, DEL, DUP, LAM, ROOT, VAR, Stuck  # noqa: E402

SPINE_K = 8


# --------------------------------------------------------------------------
# the observer, one per representation
# --------------------------------------------------------------------------

def _symbol_free(name: str) -> str:
    return f"var:{name}"


def _symbol_bound(index: int) -> str:
    return f"bvar:{index}"


def spine_tree(term, k: int = SPINE_K) -> tuple[list[str], int]:
    """Leftmost spine of a KAPPA-EXP-006 Term. Returns (symbols, probe cost)."""
    binders: list[str] = []
    symbols: list[str] = []
    steps = 0
    while len(symbols) < k:
        steps += 1
        if isinstance(term, rp.App):
            symbols.append("app")
            term = term.fun
        elif isinstance(term, rp.Lam):
            symbols.append("lam")
            binders.append(term.var)
            term = term.body
        else:
            for depth, name in enumerate(reversed(binders)):
                if name == term.name:
                    symbols.append(_symbol_bound(depth))
                    break
            else:
                symbols.append(_symbol_free(term.name))
            break
    return symbols, steps


def spine_graph(node, k: int = SPINE_K) -> tuple[list[str], int]:
    """Leftmost spine of a KAPPA-EXP-007 graph node."""
    binders: list[str] = []
    symbols: list[str] = []
    steps = 0
    while len(symbols) < k:
        steps += 1
        if node.kind == gm.APP:
            symbols.append("app")
            node = node.left
        elif node.kind == gm.LAM:
            symbols.append("lam")
            binders.append(node.name)
            node = node.left
        else:
            for depth, name in enumerate(reversed(binders)):
                if name == node.name:
                    symbols.append(_symbol_bound(depth))
                    break
            else:
                symbols.append(_symbol_free(node.name))
            break
    return symbols, steps


def spine_net(net, k: int = SPINE_K) -> tuple[list[str], int]:
    """Leftmost spine of a sharing graph, WITHOUT reading the whole term back.

    This is the work C-compact prices for `R_abstract`: the same fan-context
    walk `optimal_machine.readback` performs, but following only the leftmost
    child and stopping after k symbols. Every node stepped through -- fans and
    delimiters included -- costs one probe step.
    """
    binders: list[int] = []
    stacks: dict[object, list[int]] = {}
    symbols: list[str] = []
    steps = 0
    port = net.facing((net.root, 0))
    while len(symbols) < k:
        steps += 1
        nid, pid = port
        kind = net.kind[nid]
        if kind == VAR:
            symbols.append(_symbol_free(str(net.label[nid])))
            break
        if kind == LAM and pid == 0:
            symbols.append("lam")
            binders.append(nid)
            port = net.facing((nid, 1))
            continue
        if kind == LAM and pid == 2:
            for depth, held in enumerate(reversed(binders)):
                if held == nid:
                    symbols.append(_symbol_bound(depth))
                    break
            else:
                raise Stuck("spine reached a variable outside its binder")
            break
        if kind == APP and pid == 2:
            symbols.append("app")
            port = net.facing((nid, 0))
            continue
        if kind == DEL:
            port = net.facing((nid, 1 - pid))
            continue
        if kind == DUP:
            stack = stacks.setdefault(net.label[nid], [])
            if pid == 0:
                if not stack:
                    raise Stuck("spine reached a fan with no matching copy")
                side = stack.pop()
                port = net.facing((nid, side))
            else:
                stack.append(pid)
                port = net.facing((nid, 0))
            continue
        raise Stuck(f"spine reached {kind} port {pid}")
    return symbols, steps


# --------------------------------------------------------------------------
# C-explicit: build the tree, and price building it
# --------------------------------------------------------------------------

def explicit_from_tree(term) -> tuple[int, int]:
    """`R_fresh` already holds an unshared tree: nothing is built. (nodes, work)"""
    return rp.distinct_objects(term), 0


def explicit_from_graph(node) -> tuple[int, int]:
    """Expand a KAPPA-EXP-007 DAG into a tree. One construction per node."""
    size = gm.occurrence_size(node)
    return size, size


def explicit_from_net(net) -> tuple[int, int]:
    """Read the sharing graph back. One construction per output node."""
    size = gm.occurrence_size(om.readback(net))
    return size, size


# --------------------------------------------------------------------------
# the composition estimand, fixed by the preregistration
# --------------------------------------------------------------------------

def bookkeeping_fraction_at_peak(pointwise) -> dict:
    """`book_t / total_t` at `t = argmax(total_t)`; first instant wins a tie.

    Never `max(book)/max(total)`: those are maxima from different instants and
    are not the composition of any state. That is the EXP-008 erratum, and this
    function is the preregistered replacement.
    """
    if not pointwise:
        return {"instant": None, "book": None, "total": None, "fraction": None, "ties": 0}
    best = max(point[2] for point in pointwise)
    ties = sum(1 for point in pointwise if point[2] == best)
    instant = next(i for i, point in enumerate(pointwise) if point[2] == best)
    term, book, total = pointwise[instant]
    return {"instant": instant, "book": book, "total": total,
            "fraction": book / total if total else None, "ties": ties}
