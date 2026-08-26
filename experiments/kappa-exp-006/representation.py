#!/usr/bin/env python3
"""Two representations of one calculus, instrumented for seven quantities.

Self-contained on purpose: KAPPA-EXP-001's machine is frozen and used by
KAPPA-EXP-003 and 005, and control 1 requires this implementation to reproduce
its numbers rather than to be it.
"""

from __future__ import annotations

from typing import Optional

ALLOCATIONS = [0]


class Term:
    __slots__ = ("size", "fv", "_hash")


class Var(Term):
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        ALLOCATIONS[0] += 1
        self.name = name
        self.size = 1
        self.fv = frozenset((name,))
        self._hash = ("v", name)


class Lam(Term):
    __slots__ = ("var", "body")

    def __init__(self, var: str, body: Term) -> None:
        ALLOCATIONS[0] += 1
        self.var = var
        self.body = body
        self.size = 1 + body.size
        self.fv = body.fv - {var}
        self._hash = ("l", var, body._hash)


class App(Term):
    __slots__ = ("fun", "arg")

    def __init__(self, fun: Term, arg: Term) -> None:
        ALLOCATIONS[0] += 1
        self.fun = fun
        self.arg = arg
        self.size = 1 + fun.size + arg.size
        self.fv = fun.fv | arg.fv
        self._hash = ("a", fun._hash, arg._hash)


class Renaming(Exception):
    pass


class Aliasing(Exception):
    """R_fresh wrote two positions that share one object."""


def occurrences(name: str, term: Term) -> int:
    total = 0
    stack = [term]
    while stack:
        node = stack.pop()
        if name not in node.fv:
            continue
        if isinstance(node, Var):
            total += 1
        elif isinstance(node, App):
            stack.append(node.fun)
            stack.append(node.arg)
        else:
            stack.append(node.body)
    return total


def rebuild(term: Term) -> Term:
    """Deep copy: every node fresh, so nothing in the result is shared."""
    if isinstance(term, Var):
        return Var(term.name)
    if isinstance(term, App):
        return App(rebuild(term.fun), rebuild(term.arg))
    return Lam(term.var, rebuild(term.body))


def substitute(term: Term, name: str, value: Term, fresh: bool) -> Term:
    """R_alias reuses `value` and unchanged subterms; R_fresh copies everything."""
    if name not in term.fv:
        return rebuild(term) if fresh else term
    if isinstance(term, Var):
        return rebuild(value) if fresh else value
    if isinstance(term, App):
        return App(substitute(term.fun, name, value, fresh), substitute(term.arg, name, value, fresh))
    if term.var in value.fv:
        raise Renaming(f"substituting into a binder for {term.var!r} would capture")
    return Lam(term.var, substitute(term.body, name, value, fresh))


def step_cost(redex: App) -> tuple[int, int, int]:
    lam = redex.fun
    assert isinstance(lam, Lam)
    occ = occurrences(lam.var, lam.body)
    return 1, 1 + occ * redex.arg.size, 1 + max(0, occ - 1) * redex.arg.size


def contract(redex: App, fresh: bool) -> Term:
    lam = redex.fun
    assert isinstance(lam, Lam)
    return substitute(lam.body, lam.var, redex.arg, fresh)


def leftmost_outermost(term: Term, fresh: bool) -> Optional[tuple[Term, tuple[int, int, int]]]:
    if isinstance(term, App):
        if isinstance(term.fun, Lam):
            return contract(term, fresh), step_cost(term)
        reduced = leftmost_outermost(term.fun, fresh)
        if reduced is not None:
            return App(reduced[0], term.arg), reduced[1]
        reduced = leftmost_outermost(term.arg, fresh)
        if reduced is not None:
            return App(term.fun, reduced[0]), reduced[1]
        return None
    if isinstance(term, Lam):
        reduced = leftmost_outermost(term.body, fresh)
        if reduced is not None:
            return Lam(term.var, reduced[0]), reduced[1]
    return None


def leftmost_innermost(term: Term, fresh: bool) -> Optional[tuple[Term, tuple[int, int, int]]]:
    if isinstance(term, App):
        reduced = leftmost_innermost(term.fun, fresh)
        if reduced is not None:
            return App(reduced[0], term.arg), reduced[1]
        reduced = leftmost_innermost(term.arg, fresh)
        if reduced is not None:
            return App(term.fun, reduced[0]), reduced[1]
        if isinstance(term.fun, Lam):
            return contract(term, fresh), step_cost(term)
        return None
    if isinstance(term, Lam):
        reduced = leftmost_innermost(term.body, fresh)
        if reduced is not None:
            return Lam(term.var, reduced[0]), reduced[1]
    return None


STRATEGIES = {"S_out": leftmost_outermost, "S_in": leftmost_innermost}


def walk(term: Term):
    stack = [term]
    while stack:
        node = stack.pop()
        yield node
        if isinstance(node, App):
            stack.append(node.fun)
            stack.append(node.arg)
        elif isinstance(node, Lam):
            stack.append(node.body)


def distinct_objects(term: Term) -> int:
    """Reachable nodes by identity. An alias is counted once."""
    seen: set[int] = set()
    stack = [term]
    while stack:
        node = stack.pop()
        if id(node) in seen:
            continue
        seen.add(id(node))
        if isinstance(node, App):
            stack.append(node.fun)
            stack.append(node.arg)
        elif isinstance(node, Lam):
            stack.append(node.body)
    return len(seen)


def distinct_hashes(term: Term) -> int:
    """Reachable subterms by structural content: the DAG a store would hold."""
    seen: set = set()
    stack = [term]
    while stack:
        node = stack.pop()
        if node._hash in seen:
            continue
        seen.add(node._hash)
        if isinstance(node, App):
            stack.append(node.fun)
            stack.append(node.arg)
        elif isinstance(node, Lam):
            stack.append(node.body)
    return len(seen)


def check_no_aliasing(term: Term) -> None:
    """Control 2 for R_fresh: no object may be reachable by two paths."""
    seen: set[int] = set()
    stack = [term]
    while stack:
        node = stack.pop()
        if id(node) in seen:
            raise Aliasing("a node is reachable by more than one path")
        seen.add(id(node))
        if isinstance(node, App):
            stack.append(node.fun)
            stack.append(node.arg)
        elif isinstance(node, Lam):
            stack.append(node.body)


def de_bruijn(term: Term, bound: tuple[str, ...] = ()) -> tuple:
    if isinstance(term, Var):
        for depth, name in enumerate(reversed(bound)):
            if name == term.name:
                return ("b", depth)
        return ("f", term.name)
    if isinstance(term, App):
        return ("a", de_bruijn(term.fun, bound), de_bruijn(term.arg, bound))
    return ("l", de_bruijn(term.body, bound + (term.var,)))


def family(n: int) -> Term:
    duplicator = Lam("x", App(App(Var("p"), Var("x")), Var("x")))
    term = Var("y")
    for _ in range(n):
        term = App(duplicator, term)
    return term


def normalize(n: int, strategy: str, fresh: bool, ceiling: int = 10 ** 7) -> dict:
    ALLOCATIONS[0] = 0
    term = family(n)
    if fresh:
        term = rebuild(term)
        check_no_aliasing(term)
    allocations_at_start = ALLOCATIONS[0]
    step = STRATEGIES[strategy]
    steps = 0
    costs = [0, 0, 0]
    peaks = [term.size, distinct_objects(term), distinct_hashes(term)]
    while True:
        reduced = step(term, fresh)
        if reduced is None:
            break
        steps += 1
        if steps > ceiling:
            raise RuntimeError(f"{strategy}: exceeded step ceiling {ceiling}")
        term, cost = reduced
        costs = [total + part for total, part in zip(costs, cost)]
        if fresh:
            check_no_aliasing(term)
        peaks = [
            max(peaks[0], term.size),
            max(peaks[1], distinct_objects(term)),
            max(peaks[2], distinct_hashes(term)),
        ]
    return {
        "steps": steps,
        "cost_unit": costs[0],
        "cost_size": costs[1],
        "cost_dup": costs[2],
        "peak_occurrence_size": peaks[0],
        "peak_distinct_objects": peaks[1],
        "peak_distinct_hashes": peaks[2],
        "allocations": ALLOCATIONS[0] - allocations_at_start,
        "normal_form_occurrence_size": term.size,
        "normal_form_distinct_objects": distinct_objects(term),
        "normal_form_distinct_hashes": distinct_hashes(term),
        "normal_form": term,
    }
