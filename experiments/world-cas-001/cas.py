#!/usr/bin/env python3
"""Write-through content-addressable storage, bolted onto the KAPPA machines.

ChatGPT's review found that every "store" number in the kappa arc counts live
reachable hashes of the *current* term, while the Store is pre-filled and never
written during evaluation. `content-addressable != content-stored`. This module
adds the missing half without touching one line of KAPPA-EXP-006's or
KAPPA-EXP-007's code: the machines are instrumented by runtime patching, run,
and un-patched. Control 1 is what makes that discipline checkable -- every
frozen KAPPA-EXP-007 number must come out identical with instrumentation on.

THE POLICY, stated because the preregistration leaves it to the implementor.
A node is *materialized* when its content comes into existence. Under content
addressing an object's address is a function of its whole subtree, so:

- for the immutable tree machines (`R_fresh`, `R_alias`) materialization is
  allocation, and the hook is the constructor -- literally "put at the moment
  of materialization";
- for `R_update`, `become()` rewrites a node in place. An immutable store
  cannot do that. Changing a node changes the address of the node AND of every
  ancestor, so a write-through CAS must **path-copy**: after each in-place
  update every content reachable from the root is put. That is not an
  interpretation of convenience -- it is the only way a mutable-graph machine
  can be given a content-addressed history at all, and control 2 would fail
  without it.

A consequence, recorded rather than hidden: control 2 (`live(t) subset of
ever-written`) is a genuine test of the constructor hook on the two tree
machines, and is satisfied by construction on `R_update`, whose policy is
defined as the reachable closure. It is reported as such.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parent / "kappa-exp-006"))
sys.path.insert(0, str(BASE.parent / "kappa-exp-007"))

import graph_machine as gm  # noqa: E402
import representation as rp  # noqa: E402

DIGEST_BYTES = 16


def _h(*parts: bytes) -> bytes:
    digest = hashlib.blake2b(digest_size=DIGEST_BYTES)
    for part in parts:
        digest.update(len(part).to_bytes(4, "big"))
        digest.update(part)
    return digest.digest()


class Store:
    """No GC, by preregistration. Resident is monotone; unique-ever is its end."""

    __slots__ = ("_resident", "writes", "trace")

    def __init__(self) -> None:
        self._resident: set[bytes] = set()
        self.writes = 0
        self.trace: list[int] = []

    def put(self, digest: bytes) -> bool:
        self.writes += 1
        if digest in self._resident:
            return False
        self._resident.add(digest)
        return True

    def put_many(self, digests) -> int:
        new = 0
        for digest in digests:
            if self.put(digest):
                new += 1
        return new

    def __contains__(self, digest: bytes) -> bool:
        return digest in self._resident

    @property
    def resident(self) -> int:
        return len(self._resident)

    def sample(self) -> None:
        self.trace.append(self.resident)


class Instrumentation:
    """One live installation. `install()` patches, `remove()` restores."""

    def __init__(self) -> None:
        self.store = Store()
        self.term_digest: dict[int, bytes] = {}
        self.retained: list = []          # keeps ids stable for term_digest
        self.current_root: list = [None]
        self.live_trace: list[int] = []
        self.live_peak = 0
        self.completeness_misses = 0
        self.last_seen = None    # the final tick's term/root is the normal form
        self._saved: list[tuple] = []

    # -- digests ---------------------------------------------------------
    def digest_of_term(self, term) -> bytes:
        return self.term_digest[id(term)]

    def _new_term_digest(self, term) -> bytes:
        if isinstance(term, rp.Var):
            return _h(b"v", term.name.encode())
        if isinstance(term, rp.Lam):
            return _h(b"l", term.var.encode(), self.term_digest[id(term.body)])
        return _h(b"a", self.term_digest[id(term.fun)], self.term_digest[id(term.arg)])

    def digest_of_node(self, node, memo: dict[int, bytes]) -> bytes:
        hit = memo.get(id(node))
        if hit is not None:
            return hit
        if node.kind == gm.VAR:
            value = _h(b"v", node.name.encode())
        elif node.kind == gm.LAM:
            value = _h(b"l", node.name.encode(), self.digest_of_node(node.left, memo))
        else:
            value = _h(b"a", self.digest_of_node(node.left, memo),
                       self.digest_of_node(node.right, memo))
        memo[id(node)] = value
        return value

    # -- live sets -------------------------------------------------------
    def live_term_digests(self, term) -> set[bytes]:
        seen: set[int] = set()
        digests: set[bytes] = set()
        stack = [term]
        while stack:
            node = stack.pop()
            if id(node) in seen:
                continue
            seen.add(id(node))
            found = self.term_digest.get(id(node))
            if found is None:
                self.completeness_misses += 1
            else:
                digests.add(found)
            if isinstance(node, rp.App):
                stack.append(node.fun)
                stack.append(node.arg)
            elif isinstance(node, rp.Lam):
                stack.append(node.body)
        return digests

    def live_node_digests(self, root) -> set[bytes]:
        memo: dict[int, bytes] = {}
        seen: set[int] = set()
        digests: set[bytes] = set()
        stack = [root]
        while stack:
            node = stack.pop()
            if id(node) in seen:
                continue
            seen.add(id(node))
            digests.add(self.digest_of_node(node, memo))
            if node.kind == gm.LAM:
                stack.append(node.left)
            elif node.kind == gm.APP:
                stack.append(node.left)
                stack.append(node.right)
        return digests

    def observe(self, live: set[bytes]) -> None:
        """One tick. Control 2 is checked here, not assumed."""
        for digest in live:
            if digest not in self.store:
                self.completeness_misses += 1
                self.store.put(digest)
        self.live_peak = max(self.live_peak, len(live))
        self.live_trace.append(len(live))
        self.store.sample()

    # -- patching --------------------------------------------------------
    def install(self) -> None:
        instrument = self

        for cls in (rp.Var, rp.Lam, rp.App):
            original = cls.__init__

            def make(original=original):
                def patched(self, *args):
                    original(self, *args)
                    digest = instrument._new_term_digest(self)
                    instrument.term_digest[id(self)] = digest
                    instrument.retained.append(self)
                    instrument.store.put(digest)
                return patched
            self._saved.append((cls, "__init__", original))
            cls.__init__ = make()

        original_hashes = rp.distinct_hashes

        def tree_tick(term):
            instrument.last_seen = term
            instrument.observe(instrument.live_term_digests(term))
            return original_hashes(term)
        self._saved.append((rp, "distinct_hashes", original_hashes))
        rp.distinct_hashes = tree_tick

        node_init = gm.Node.__init__

        def node_patched(self, kind, name=None, left=None, right=None):
            node_init(self, kind, name, left, right)
            instrument.store.put(instrument.digest_of_node(self, {}))
        self._saved.append((gm.Node, "__init__", node_init))
        gm.Node.__init__ = node_patched

        node_become = gm.Node.become

        def become_patched(self, other):
            node_become(self, other)
            root = instrument.current_root[0]
            if root is not None:
                # path copy: in-place update moves every ancestor's address
                instrument.store.put_many(instrument.live_node_digests(root))
        self._saved.append((gm.Node, "become", node_become))
        gm.Node.become = become_patched

        original_finders = gm.FINDERS

        def wrap(finder):
            def call(root):
                instrument.current_root[0] = root
                return finder(root)
            return call
        self._saved.append((gm, "FINDERS", original_finders))
        gm.FINDERS = {name: wrap(fn) for name, fn in original_finders.items()}

        original_graph_hashes = gm.distinct_hashes

        def graph_tick(root):
            instrument.last_seen = root
            instrument.observe(instrument.live_node_digests(root))
            return original_graph_hashes(root)
        self._saved.append((gm, "distinct_hashes", original_graph_hashes))
        gm.distinct_hashes = graph_tick

    def remove(self) -> None:
        for owner, attribute, value in reversed(self._saved):
            setattr(owner, attribute, value)
        self._saved.clear()

    # -- readback --------------------------------------------------------
    def readback_writes(self, normal_form, graph: bool) -> int:
        """Materialize the explicit normal form and count writes it adds.

        Walked as a DAG with a memo rather than as a tree. A content-addressed
        put is idempotent, so the SET of digests an expanded tree would write is
        exactly the set the DAG walk writes; only the redundant put count would
        differ, and the preregistration asks for distinct hashes.
        """
        if graph:
            digests = self.live_node_digests(normal_form)
        else:
            digests = self.live_term_digests(normal_form)
        return self.store.put_many(digests)
