#!/usr/bin/env python3
"""R_update: Wadsworth 1971 graph reduction, for KAPPA-EXP-007.

A node is mutable. Contraction rewrites the redex node *in place*, so every
reference to it observes the result: reduction itself is shared, not only
storage. Because any node may be mutated at any time and a shared node has no
unique parent, nothing is cached — size, free variables and hashes are computed
on demand. That is slower and it is the only way to stay correct here.
"""

from __future__ import annotations

from typing import Optional

VAR, LAM, APP = "var", "lam", "app"


class Node:
    __slots__ = ("kind", "name", "left", "right")

    def __init__(self, kind: str, name: Optional[str] = None,
                 left: "Node | None" = None, right: "Node | None" = None) -> None:
        self.kind = kind
        self.name = name
        self.left = left
        self.right = right

    def become(self, other: "Node") -> None:
        """In-place update. Every existing reference now sees `other`'s content."""
        self.kind, self.name, self.left, self.right = other.kind, other.name, other.left, other.right


def var(name: str) -> Node:
    return Node(VAR, name=name)


def lam(name: str, body: Node) -> Node:
    return Node(LAM, name=name, left=body)


def app(fun: Node, arg: Node) -> Node:
    return Node(APP, left=fun, right=arg)


def occurrence_size(node: Node) -> int:
    if node.kind == VAR:
        return 1
    if node.kind == LAM:
        return 1 + occurrence_size(node.left)
    return 1 + occurrence_size(node.left) + occurrence_size(node.right)


def free_vars(node: Node) -> frozenset[str]:
    if node.kind == VAR:
        return frozenset((node.name,))
    if node.kind == LAM:
        return free_vars(node.left) - {node.name}
    return free_vars(node.left) | free_vars(node.right)


def occurrences(name: str, node: Node) -> int:
    if node.kind == VAR:
        return 1 if node.name == name else 0
    if node.kind == LAM:
        return 0 if node.name == name else occurrences(name, node.left)
    return occurrences(name, node.left) + occurrences(name, node.right)


def distinct_objects(node: Node) -> int:
    seen: set[int] = set()
    stack = [node]
    while stack:
        current = stack.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        if current.kind == LAM:
            stack.append(current.left)
        elif current.kind == APP:
            stack.append(current.left)
            stack.append(current.right)
    return len(seen)


def content_hash(node: Node, memo: dict[int, tuple] | None = None) -> tuple:
    memo = memo if memo is not None else {}
    hit = memo.get(id(node))
    if hit is not None:
        return hit
    if node.kind == VAR:
        value: tuple = ("v", node.name)
    elif node.kind == LAM:
        value = ("l", node.name, content_hash(node.left, memo))
    else:
        value = ("a", content_hash(node.left, memo), content_hash(node.right, memo))
    memo[id(node)] = value
    return value


def distinct_hashes(node: Node) -> int:
    seen: set = set()
    stack = [node]
    memo: dict[int, tuple] = {}
    while stack:
        current = stack.pop()
        digest = content_hash(current, memo)
        if digest in seen:
            continue
        seen.add(digest)
        if current.kind == LAM:
            stack.append(current.left)
        elif current.kind == APP:
            stack.append(current.left)
            stack.append(current.right)
    return len(seen)


def redex_occurrences(node: Node) -> int:
    """Redexes counted by *occurrence*, not identity: what control 2 watches.

    Counting by identity would make sharing invisible by construction -- two
    aliased copies of one redex are one object and would count once, so an
    in-place update could never look like it removed more than one. The
    occurrence count is the quantity that drops by more than one exactly when a
    single contraction serves several positions.
    """
    if node.kind == VAR:
        return 0
    if node.kind == LAM:
        return redex_occurrences(node.left)
    here = 1 if node.left.kind == LAM else 0
    return here + redex_occurrences(node.left) + redex_occurrences(node.right)


class Renaming(Exception):
    pass


def substitute(node: Node, name: str, value: Node) -> Node:
    """Aliasing substitution: every occurrence receives the same argument node."""
    fv = free_vars(node)
    if name not in fv:
        return node
    if node.kind == VAR:
        return value
    if node.kind == APP:
        return app(substitute(node.left, name, value), substitute(node.right, name, value))
    if node.name in free_vars(value):
        raise Renaming(f"substituting into a binder for {node.name!r} would capture")
    return lam(node.name, substitute(node.left, name, value))


def step_cost(redex: Node) -> tuple[int, int, int]:
    binder = redex.left
    occ = occurrences(binder.name, binder.left)
    argument_size = occurrence_size(redex.right)
    return 1, 1 + occ * argument_size, 1 + max(0, occ - 1) * argument_size


def contract_in_place(redex: Node) -> tuple[int, int, int]:
    binder = redex.left
    cost = step_cost(redex)
    redex.become(substitute(binder.left, binder.name, redex.right))
    return cost


def find_outermost(node: Node) -> Optional[Node]:
    if node.kind == APP:
        if node.left.kind == LAM:
            return node
        found = find_outermost(node.left)
        return found if found is not None else find_outermost(node.right)
    if node.kind == LAM:
        return find_outermost(node.left)
    return None


def find_innermost(node: Node) -> Optional[Node]:
    if node.kind == APP:
        found = find_innermost(node.left)
        if found is not None:
            return found
        found = find_innermost(node.right)
        if found is not None:
            return found
        return node if node.left.kind == LAM else None
    if node.kind == LAM:
        return find_innermost(node.left)
    return None


FINDERS = {"S_out": find_outermost, "S_in": find_innermost}


def normalize(root: Node, strategy: str, ceiling: int = 10 ** 7) -> dict:
    """Reduce in place. The root object is never replaced, only mutated."""
    find = FINDERS[strategy]
    identity = id(root)
    steps = 0
    costs = [0, 0, 0]
    peaks = [occurrence_size(root), distinct_objects(root), distinct_hashes(root)]
    multi_update_steps = 0
    while True:
        redex = find(root)
        if redex is None:
            break
        before = redex_occurrences(root)
        cost = contract_in_place(redex)
        after = redex_occurrences(root)
        # One contraction removing more than one reachable redex is sharing of
        # reduction actually happening. Control 2.
        if before - after > 1:
            multi_update_steps += 1
        steps += 1
        if steps > ceiling:
            raise RuntimeError(f"{strategy}: exceeded step ceiling {ceiling}")
        costs = [total + part for total, part in zip(costs, cost)]
        peaks = [
            max(peaks[0], occurrence_size(root)),
            max(peaks[1], distinct_objects(root)),
            max(peaks[2], distinct_hashes(root)),
        ]
    assert id(root) == identity, "the root object was replaced instead of mutated"
    return {
        "steps": steps,
        "cost_unit": costs[0],
        "cost_size": costs[1],
        "cost_dup": costs[2],
        "peak_occurrence_size": peaks[0],
        "peak_distinct_objects": peaks[1],
        "peak_distinct_hashes": peaks[2],
        "multi_update_steps": multi_update_steps,
        "root_identity_preserved": True,
        "normal_form": root,
    }


def de_bruijn(node: Node, bound: tuple[str, ...] = ()) -> tuple:
    if node.kind == VAR:
        for depth, name in enumerate(reversed(bound)):
            if name == node.name:
                return ("b", depth)
        return ("f", node.name)
    if node.kind == APP:
        return ("a", de_bruijn(node.left, bound), de_bruijn(node.right, bound))
    return ("l", de_bruijn(node.left, bound + (node.name,)))


def family_h(n: int) -> Node:
    """h_0 = y ; h_{n+1} = (lambda x. p x x) h_n -- duplication not under a binder."""
    term = var("y")
    for _ in range(n):
        duplicator = lam("x", app(app(var("p"), var("x")), var("x")))
        term = app(duplicator, term)
    return term


def family_d(n: int) -> Node:
    """d_0 = lambda w. y ; d_{n+1} = (lambda x. lambda w. p (x w) (x (q w))) d_n."""
    term = lam("w", var("y"))
    for _ in range(n):
        duplicator = lam(
            "x",
            lam("w", app(app(var("p"), app(var("x"), var("w"))),
                         app(var("x"), app(var("q"), var("w"))))),
        )
        term = app(duplicator, term)
    return term
