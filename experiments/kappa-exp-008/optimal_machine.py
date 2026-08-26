#!/usr/bin/env python3
"""R_optimal: a sharing-graph reducer in the Lamping / lambdascope class.

Terms are encoded as interaction nets over `sharing_net`. A variable bound to
more than one occurrence becomes a tree of *duplicator* (fan) nodes; an unused
binder becomes an *eraser*. Contraction of an application against an
abstraction is a single interaction whatever the number of occurrences, so one
contraction serves a whole redex family -- including occurrences that sit under
different binders, which is what KAPPA-EXP-007's `R_update` could not do.

Node classification, per the preregistration's fifth quantity:

    term nodes         lam, app, var, root
    bookkeeping nodes  dup (fan), del (scope delimiter), era

Which member of the class is implemented, and the fan-labelling discipline, is
recorded in `PROVENANCE` below and in the RESULT.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE.parent / "kappa-exp-007"))

import graph_machine as gm  # noqa: E402
from sharing_net import (APP, ARITY, DEL, DUP, ERA, LAM, ROOT, VAR,  # noqa: E402
                         Net, Overflow, Stuck)

INTERACTION_CAP = 500_000
NODE_CAP = 200_000


# --------------------------------------------------------------------------
# encoding: lambda term -> sharing graph
# --------------------------------------------------------------------------

def encode(term: gm.Node) -> Net:
    net = Net()
    root = net.new(ROOT)
    net.root = root
    occurrences: dict[int, list[tuple[int, int]]] = {}
    counter = [0]

    def build(node: gm.Node, destination: tuple[int, int], env: dict[str, list[int]]) -> None:
        if node.kind == gm.VAR:
            bound = env.get(node.name)
            if bound:
                occurrences[bound[-1]].append(destination)
            else:
                net.link((net.new(VAR, node.name), 0), destination)
            return
        if node.kind == gm.APP:
            nid = net.new(APP)
            net.link((nid, 2), destination)
            build(node.left, (nid, 0), env)
            build(node.right, (nid, 1), env)
            return
        nid = net.new(LAM)
        net.link((nid, 0), destination)
        occurrences[nid] = []
        env.setdefault(node.name, []).append(nid)
        build(node.left, (nid, 1), env)
        env[node.name].pop()
        sites = occurrences.pop(nid)
        source: tuple[int, int] = (nid, 2)
        if not sites:
            net.link((net.new(ERA), 0), source)
            return
        while len(sites) > 1:
            counter[0] += 1
            fan = net.new(DUP, counter[0])
            net.link((fan, 0), source)
            net.link((fan, 1), sites[0])
            source = (fan, 2)
            sites = sites[1:]
        net.link(sites[0], source)

    build(term, (root, 0), {})
    return net


# --------------------------------------------------------------------------
# interaction rules
# --------------------------------------------------------------------------

BETA, ANNIHILATE, COMMUTE, DUPLICATE, ERASE, SCOPE = (
    "beta", "annihilate", "commute", "duplicate", "erase", "scope")

INERT = frozenset({VAR, ROOT})


def classify(net: Net, a: int, b: int) -> str | None:
    """Name the rule for an active pair, or None if the pair is inert."""
    ka, kb = net.kind[a], net.kind[b]
    pair = {ka, kb}
    if ROOT in pair:
        return None
    if ERA in pair:
        return ERASE
    if pair <= INERT:
        return None
    if pair == {APP, LAM}:
        return BETA
    if ka == DUP and kb == DUP:
        return ANNIHILATE if net.label[a] == net.label[b] else COMMUTE
    if DUP in pair:
        other = kb if ka == DUP else ka
        if other in (LAM, APP, VAR):
            return DUPLICATE
        return SCOPE
    if DEL in pair:
        return SCOPE
    if VAR in pair:
        return None
    raise Stuck(f"no rule and not inert: {ka} against {kb}")


def fire(net: Net, a: int, b: int, rule: str) -> None:
    if rule == BETA:
        app, lam = (a, b) if net.kind[a] == APP else (b, a)
        net.rewrite([app, lam], {}, [((app, 2), (lam, 1)), ((app, 1), (lam, 2))])
        return
    if rule == ERASE:
        era, other = (a, b) if net.kind[a] == ERA else (b, a)
        if net.kind[other] == ERA:
            net.rewrite([era, other], {}, [])
            return
        inherits = {(other, p): (net.new(ERA), 0) for p in range(1, ARITY[net.kind[other]])}
        net.rewrite([era, other], inherits, [])
        return
    if rule == ANNIHILATE:
        net.rewrite([a, b], {}, [((a, 1), (b, 1)), ((a, 2), (b, 2))])
        return
    if rule == COMMUTE:
        left, right = a, b
        la, lb = net.label[left], net.label[right]
        # Copies keep their label. This is Lamping's algorithm WITHOUT the
        # bracket/croissant oracle: two fans that are not duals can meet with
        # equal labels and annihilate wrongly. `soundness.py` measures exactly
        # where that happens; on the preregistered grid G1 certifies it does not.
        # Carrying the branch in the label instead was tried and diverges --
        # duals that are swept unequally then never annihilate. Recorded in the
        # RESULT as a negative, not silently dropped.
        xa, xb = net.new(DUP, la), net.new(DUP, la)
        ya, yb = net.new(DUP, lb), net.new(DUP, lb)
        net.link((xa, 1), (ya, 1))
        net.link((xa, 2), (yb, 1))
        net.link((xb, 1), (ya, 2))
        net.link((xb, 2), (yb, 2))
        net.rewrite([left, right],
                    {(right, 1): (xa, 0), (right, 2): (xb, 0),
                     (left, 1): (ya, 0), (left, 2): (yb, 0)}, [])
        return
    if rule == DUPLICATE:
        dup, other = (a, b) if net.kind[a] == DUP else (b, a)
        label, kind = net.label[dup], net.kind[other]
        if kind == VAR:
            name = net.label[other]
            net.rewrite([dup, other],
                        {(dup, 1): (net.new(VAR, name), 0),
                         (dup, 2): (net.new(VAR, name), 0)}, [])
            return
        one, two = net.new(kind), net.new(kind)
        first, second = net.new(DUP, label), net.new(DUP, label)
        if kind == LAM:
            # copies inherit the abstraction; body and binder each get a fan.
            net.link((first, 1), (one, 1))
            net.link((first, 2), (two, 1))
            net.link((second, 1), (one, 2))
            net.link((second, 2), (two, 2))
        else:
            # argument and result each get a fan.
            net.link((first, 1), (one, 1))
            net.link((first, 2), (two, 1))
            net.link((second, 1), (one, 2))
            net.link((second, 2), (two, 2))
        net.rewrite([dup, other],
                    {(dup, 1): (one, 0), (dup, 2): (two, 0),
                     (other, 1): (first, 0), (other, 2): (second, 0)}, [])
        return
    raise Stuck(f"unimplemented rule {rule}")


# --------------------------------------------------------------------------
# schedules
# --------------------------------------------------------------------------
#
# On a sharing graph the S_out / S_in distinction is not directly expressible;
# what varies is which active pair fires first. The preregistration fixes two
# deterministic schedules by node-distance from the root. The distance of an
# active pair is the smaller of its two nodes' distances -- the two are adjacent
# so they differ by at most one -- and ties break by the lower node id.

SCH_ROOT, SCH_LEAF = "SCH-root", "SCH-leaf"
SCHEDULES = (SCH_ROOT, SCH_LEAF)


def distances(net: Net) -> dict[int, int]:
    depth = {net.root: 0}
    frontier = [net.root]
    while frontier:
        nxt = []
        for nid in frontier:
            here = depth[nid] + 1
            for p in net.port[nid]:
                if p is not None and p[0] not in depth and p[0] in net.alive:
                    depth[p[0]] = here
                    nxt.append(p[0])
        frontier = nxt
    return depth


def active_pairs(net: Net) -> dict[tuple[int, int], str]:
    found: dict[tuple[int, int], str] = {}
    for nid in net.alive:
        facing = net.port[nid][0]
        if facing is None or facing[1] != 0 or facing[0] == nid:
            continue
        key = (nid, facing[0]) if nid < facing[0] else (facing[0], nid)
        if key in found:
            continue
        rule = classify(net, key[0], key[1])
        if rule is not None:
            found[key] = rule
    return found


def pick(net: Net, pairs: dict[tuple[int, int], str], schedule: str) -> tuple[int, int]:
    depth = distances(net)
    unreachable = 1 + max(depth.values(), default=0)

    def key(pair: tuple[int, int]) -> tuple[int, int]:
        near = min(depth.get(pair[0], unreachable), depth.get(pair[1], unreachable))
        return (near, pair[0])

    if schedule == SCH_ROOT:
        return min(pairs, key=key)
    ranked = [(key(pair), pair) for pair in pairs]
    best = max(rank[0] for rank, _ in ranked)
    return min(pair for rank, pair in ranked if rank[0] == best)


# --------------------------------------------------------------------------
# reduction
# --------------------------------------------------------------------------

def normalize(net: Net, schedule: str,
              interaction_cap: int = INTERACTION_CAP,
              node_cap: int = NODE_CAP) -> dict:
    term, book, total = net.census()
    peak_term, peak_book, peak_total = term, book, total
    interactions = 0
    beta_interactions = 0
    rules: dict[str, int] = {}
    saturated = None
    trace: list[tuple[int, int, str]] = []
    while True:
        pairs = active_pairs(net)
        if not pairs:
            break
        if interactions >= interaction_cap:
            saturated = "interactions"
            break
        chosen = pick(net, pairs, schedule)
        rule = pairs[chosen]
        fire(net, chosen[0], chosen[1], rule)
        interactions += 1
        rules[rule] = rules.get(rule, 0) + 1
        if rule == BETA:
            beta_interactions += 1
        trace.append((chosen[0], chosen[1], rule))
        term, book, total = net.census()
        peak_term = max(peak_term, term)
        peak_book = max(peak_book, book)
        peak_total = max(peak_total, total)
        if total > node_cap:
            saturated = "nodes"
            break
    return {
        "schedule": schedule,
        "interactions": interactions,
        "beta_interactions": beta_interactions,
        "rule_counts": rules,
        "peak_term": peak_term,
        "peak_book": peak_book,
        "peak_total": peak_total,
        "final_term": net.live["term"],
        "final_book": net.live["book"],
        "allocated_term": net.allocated["term"],
        "allocated_book": net.allocated["book"],
        "freed_term": net.freed["term"],
        "freed_book": net.freed["book"],
        "saturated": saturated,
        "trace_digest": hashlib.sha256(repr(trace).encode()).hexdigest()[:16],
    }


# --------------------------------------------------------------------------
# readback
# --------------------------------------------------------------------------

def readback(net: Net) -> gm.Node:
    """Read the graph back as a term, walking fans with one stack per label."""
    binders: dict[int, list[str]] = {}
    stacks: dict[object, list[int]] = {}
    fresh = [0]

    def go(port: tuple[int, int]) -> gm.Node:
        nid, pid = port
        kind = net.kind[nid]
        if kind == VAR:
            return gm.var(str(net.label[nid]))
        if kind == LAM:
            if pid == 0:
                fresh[0] += 1
                name = f"v{fresh[0]}"
                binders.setdefault(nid, []).append(name)
                body = go(net.facing((nid, 1)))
                binders[nid].pop()
                return gm.lam(name, body)
            if pid == 2:
                held = binders.get(nid)
                if not held:
                    raise Stuck("variable read outside its binder")
                return gm.var(held[-1])
        if kind == APP and pid == 2:
            return gm.app(go(net.facing((nid, 0))), go(net.facing((nid, 1))))
        if kind == DEL:
            return go(net.facing((nid, 1 - pid)))
        if kind == DUP:
            stack = stacks.setdefault(net.label[nid], [])
            if pid == 0:
                if not stack:
                    raise Stuck("fan read with no matching copy on the path")
                side = stack.pop()
                result = go(net.facing((nid, side)))
                stack.append(side)
                return result
            stack.append(pid)
            result = go(net.facing((nid, 0)))
            stack.pop()
            return result
        raise Stuck(f"readback reached {kind} port {pid}")

    return go(net.facing((net.root, 0)))


# --------------------------------------------------------------------------
# provenance
# --------------------------------------------------------------------------

PROVENANCE = {
    "class": "Lamping / lambdascope sharing graph",
    "fans": "duplicators labelled per binder at encoding time; equal label "
            "annihilates, unequal label commutes",
}
