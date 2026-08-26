#!/usr/bin/env python3
"""Untyped lambda calculus over an explicit syntax tree, for KAPPA-EXP-001.

Everything the preregistration pins lives here: the representation (a plain
tree, no sharing), the two strategies, and the two cost models. Sizes and free
variable sets are cached at construction so that measuring `peak` costs nothing
extra and cannot itself distort the measurement.
"""

from __future__ import annotations

from typing import Optional


class Term:
    __slots__ = ("size", "fv")


class Var(Term):
    __slots__ = ("name",)

    def __init__(self, name: str) -> None:
        self.name = name
        self.size = 1
        self.fv = frozenset((name,))


class Lam(Term):
    __slots__ = ("var", "body")

    def __init__(self, var: str, body: Term) -> None:
        self.var = var
        self.body = body
        self.size = 1 + body.size
        self.fv = body.fv - {var}


class App(Term):
    __slots__ = ("fun", "arg")

    def __init__(self, fun: Term, arg: Term) -> None:
        self.fun = fun
        self.arg = arg
        self.size = 1 + fun.size + arg.size
        self.fv = fun.fv | arg.fv


class Renaming(Exception):
    """Raised when capture-avoiding substitution would need to rename.

    Control 4 of the preregistration asserts this never fires on the measured
    family, so no measurement is inflated by renaming work. Making it an
    exception rather than a silent counter means a violation cannot be missed.
    """


def occurrences(name: str, term: Term) -> int:
    """Count free occurrences of `name` in `term`."""
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


def substitute(term: Term, name: str, value: Term) -> Term:
    """Capture-avoiding substitution of `value` for free `name` in `term`."""
    if name not in term.fv:
        return term
    if isinstance(term, Var):
        return value
    if isinstance(term, App):
        return App(substitute(term.fun, name, value), substitute(term.arg, name, value))
    if term.var in value.fv:
        raise Renaming(f"substituting into a binder for {term.var!r} would capture")
    return Lam(term.var, substitute(term.body, name, value))


def contract(redex: App) -> Term:
    """Contract a beta redex (lambda x. M) N."""
    lam = redex.fun
    assert isinstance(lam, Lam)
    return substitute(lam.body, lam.var, redex.arg)


def step_cost(redex: App) -> tuple[int, int]:
    """Per-step cost under (C_unit, C_size)."""
    lam = redex.fun
    assert isinstance(lam, Lam)
    return 1, 1 + occurrences(lam.var, lam.body) * redex.arg.size


def leftmost_outermost(term: Term) -> Optional[tuple[Term, tuple[int, int]]]:
    """Contract the leftmost-outermost redex. Returns the new term and its cost."""
    if isinstance(term, App):
        if isinstance(term.fun, Lam):
            return contract(term), step_cost(term)
        reduced = leftmost_outermost(term.fun)
        if reduced is not None:
            return App(reduced[0], term.arg), reduced[1]
        reduced = leftmost_outermost(term.arg)
        if reduced is not None:
            return App(term.fun, reduced[0]), reduced[1]
        return None
    if isinstance(term, Lam):
        reduced = leftmost_outermost(term.body)
        if reduced is not None:
            return Lam(term.var, reduced[0]), reduced[1]
    return None


def leftmost_innermost(term: Term) -> Optional[tuple[Term, tuple[int, int]]]:
    """Contract the leftmost redex containing no redex in its proper subterms."""
    if isinstance(term, App):
        reduced = leftmost_innermost(term.fun)
        if reduced is not None:
            return App(reduced[0], term.arg), reduced[1]
        reduced = leftmost_innermost(term.arg)
        if reduced is not None:
            return App(term.fun, reduced[0]), reduced[1]
        if isinstance(term.fun, Lam):
            return contract(term), step_cost(term)
        return None
    if isinstance(term, Lam):
        reduced = leftmost_innermost(term.body)
        if reduced is not None:
            return Lam(term.var, reduced[0]), reduced[1]
    return None


STRATEGIES = {"S_out": leftmost_outermost, "S_in": leftmost_innermost}


def de_bruijn(term: Term, bound: tuple[str, ...] = ()) -> tuple:
    """Nameless encoding, for the alpha-equivalence control."""
    if isinstance(term, Var):
        for depth, name in enumerate(reversed(bound)):
            if name == term.name:
                return ("b", depth)
        return ("f", term.name)
    if isinstance(term, App):
        return ("a", de_bruijn(term.fun, bound), de_bruijn(term.arg, bound))
    return ("l", de_bruijn(term.body, bound + (term.var,)))


def family(n: int) -> Term:
    """h_0 = y ; h_{n+1} = (lambda x. p x x) h_n"""
    duplicator = Lam("x", App(App(Var("p"), Var("x")), Var("x")))
    term = Var("y")
    for _ in range(n):
        term = App(duplicator, term)
    return term


def normalize(term: Term, strategy: str, ceiling: int) -> dict:
    """Reduce to normal form, recording both cost models on one trajectory."""
    step = STRATEGIES[strategy]
    steps = 0
    cost_unit = 0
    cost_size = 0
    peak = term.size
    while True:
        reduced = step(term)
        if reduced is None:
            break
        steps += 1
        if steps > ceiling:
            raise RuntimeError(f"{strategy}: exceeded step ceiling {ceiling}")
        term, (unit, size_cost) = reduced
        cost_unit += unit
        cost_size += size_cost
        if term.size > peak:
            peak = term.size
    return {
        "strategy": strategy,
        "steps": steps,
        "cost_unit": cost_unit,
        "cost_size": cost_size,
        "peak": peak,
        "normal_form_size": term.size,
        "normal_form": term,
    }
