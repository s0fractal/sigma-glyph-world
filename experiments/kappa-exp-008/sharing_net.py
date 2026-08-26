#!/usr/bin/env python3
"""Interaction-net substrate for R_optimal, KAPPA-EXP-008.

Explicit ports, no dependencies. A node has one principal port (index 0) and
zero or more auxiliary ports. An *active pair* is two distinct nodes joined
principal to principal. Rewriting is local: a rule deletes the pair, allocates
replacements, and rewires the wires that hung off the deleted auxiliary ports.

The rewiring helper is the only subtle part. A rule states, for each deleted
auxiliary port, either the new port that inherits its wire (`inherits`) or the
other deleted port whose wire it is spliced onto (`merges`). Wires whose far
end is itself a deleted port are chased through those statements, so a redex
whose two nodes are joined by more than the principal wire -- `(\\x. x) y`
reduced at the root, for instance -- rewires correctly instead of leaving a
reference to a freed node.
"""

from __future__ import annotations

LAM, APP, DUP, DEL, ERA, VAR, ROOT = "lam", "app", "dup", "del", "era", "var", "root"

ARITY = {LAM: 3, APP: 3, DUP: 3, DEL: 2, ERA: 1, VAR: 1, ROOT: 1}

# The fifth quantity of the preregistration: every node is term or bookkeeping,
# exclusively. lambda, application and variable are term; everything the
# sharing machinery adds is bookkeeping.
TERM_KINDS = frozenset({LAM, APP, VAR, ROOT})
BOOK_KINDS = frozenset({DUP, DEL, ERA})
assert not (TERM_KINDS & BOOK_KINDS)


class Overflow(Exception):
    """A preregistered cap was reached. Saturation is a data point, not a bug."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class Stuck(Exception):
    """The net has no active pair but is not a readable normal form."""


class Net:
    """Nodes keyed by integer id; `port[nid][p]` holds the `(nid, p)` it faces."""

    __slots__ = ("kind", "label", "port", "next_id", "alive",
                 "allocated", "freed", "live", "root")

    def __init__(self) -> None:
        self.kind: dict[int, str] = {}
        self.label: dict[int, object] = {}
        self.port: dict[int, list[tuple[int, int] | None]] = {}
        self.next_id = 0
        self.alive: set[int] = set()
        self.allocated = {"term": 0, "book": 0}
        self.freed = {"term": 0, "book": 0}
        self.live = {"term": 0, "book": 0}
        self.root = -1

    # -- allocation ---------------------------------------------------------
    def klass(self, nid: int) -> str:
        return "term" if self.kind[nid] in TERM_KINDS else "book"

    def new(self, kind: str, label: object = None) -> int:
        nid = self.next_id
        self.next_id += 1
        self.kind[nid] = kind
        self.label[nid] = label
        self.port[nid] = [None] * ARITY[kind]
        self.alive.add(nid)
        cls = self.klass(nid)
        self.allocated[cls] += 1
        self.live[cls] += 1
        return nid

    def erase(self, nid: int) -> None:
        cls = self.klass(nid)
        self.alive.discard(nid)
        self.freed[cls] += 1
        self.live[cls] -= 1

    # -- wiring -------------------------------------------------------------
    def link(self, a: tuple[int, int], b: tuple[int, int]) -> None:
        self.port[a[0]][a[1]] = b
        self.port[b[0]][b[1]] = a

    def facing(self, p: tuple[int, int]) -> tuple[int, int]:
        return self.port[p[0]][p[1]]

    # -- census -------------------------------------------------------------
    def census(self) -> tuple[int, int, int]:
        return self.live["term"], self.live["book"], self.live["term"] + self.live["book"]

    def reachable(self) -> set[int]:
        seen: set[int] = set()
        stack = [self.root]
        while stack:
            nid = stack.pop()
            if nid in seen:
                continue
            seen.add(nid)
            for p in self.port[nid]:
                if p is not None and p[0] in self.alive and p[0] not in seen:
                    stack.append(p[0])
        return seen

    # -- the rewiring helper ------------------------------------------------
    def rewrite(self, deleted: list[int],
                inherits: dict[tuple[int, int], tuple[int, int]],
                merges: list[tuple[tuple[int, int], tuple[int, int]]]) -> None:
        """Delete `deleted`; splice their wires per `inherits` and `merges`."""
        dead = set(deleted)
        old = {(nid, p): self.port[nid][p] for nid in deleted for p in range(ARITY[self.kind[nid]])}
        mate: dict[tuple[int, int], tuple[int, int]] = {}
        for left, right in merges:
            mate[left] = right
            mate[right] = left

        def chase(target, guard):
            # A wire that only ever meets deleted ports is a closed loop with no
            # free end: disconnected garbage, dropped rather than relinked.
            while target[0] in dead:
                if target in guard:
                    return None
                guard.add(target)
                if target in inherits:
                    return inherits[target]
                if target not in mate:
                    raise Stuck(f"dangling wire into deleted port {target}")
                target = old[mate[target]]
            return target

        links: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for port, destination in inherits.items():
            links.append((chase(old[port], {port}), destination))
        for left, right in merges:
            links.append((chase(old[left], {left}), chase(old[right], {right})))
        for nid in deleted:
            self.erase(nid)
        for a, b in links:
            if a is None and b is None:
                continue
            if a is None:
                a = (self.new(ERA), 0)
            elif b is None:
                b = (self.new(ERA), 0)
            self.link(a, b)
