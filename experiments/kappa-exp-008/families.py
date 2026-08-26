#!/usr/bin/env python3
"""The three preregistered families, in both term representations.

`h_n` and `d_n` are verbatim from KAPPA-EXP-001 and KAPPA-EXP-007 and are taken
from that harness's own builders, so KAPPA-EXP-007's frozen numbers are
reproduced by reuse rather than by re-implementation (gate G4).

`e_n` is Church-numeral self-application, new here. ERRATUM CANDIDATE
`KAPPA-EXP-008-E1`: the preregistration writes it with binder names `s` and `z`
identical to the free markers `s` and `z` it is then applied to. The carried-over
reference machines substitute without alpha-renaming and *refuse* on a capture
(KAPPA-EXP-006's `no_renaming` control), so that literal term cannot be run on
`R_fresh`, `R_alias` or `R_update` at all -- it raises before the first
measurement. The harness uses the alpha-equivalent form with a distinct binder
pair per copy of `c2`. Steps, peaks, costs and normal forms are invariant under
alpha, so nothing measured changes; what changes is that the term is runnable.
The defect is recorded, not silently fixed.
"""

from __future__ import annotations

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parent / "kappa-exp-006"))
sys.path.insert(0, str(BASE.parent / "kappa-exp-007"))

import graph_machine as gm  # noqa: E402
import representation as rp  # noqa: E402

H_RANGE = list(range(1, 13))
D_RANGE = list(range(1, 11))
E_RANGE = list(range(1, 5))
RANGES = {"h": H_RANGE, "d": D_RANGE, "e": E_RANGE}

DESCRIPTIONS = {
    "h": "h_0 = y ; h_{n+1} = (lambda x. p x x) h_n -- duplication not under a binder",
    "d": "d_0 = lambda w. y ; d_{n+1} = (lambda x. lambda w. p (x w) (x (q w))) d_n",
    "e": "c2 = lambda s. lambda z. s (s z) ; e_1 = c2 ; e_{n+1} = e_n c2 ; measured as e_n s z",
}


def _graph_c2(i: int) -> gm.Node:
    s, z = f"s{i}", f"z{i}"
    return gm.lam(s, gm.lam(z, gm.app(gm.var(s), gm.app(gm.var(s), gm.var(z)))))


def graph_family_e(n: int) -> gm.Node:
    term = _graph_c2(0)
    for i in range(1, n):
        term = gm.app(term, _graph_c2(i))
    return gm.app(gm.app(term, gm.var("s")), gm.var("z"))


def _tree_c2(i: int) -> rp.Term:
    s, z = f"s{i}", f"z{i}"
    return rp.Lam(s, rp.Lam(z, rp.App(rp.Var(s), rp.App(rp.Var(s), rp.Var(z)))))


def tree_family_e(n: int) -> rp.Term:
    term = _tree_c2(0)
    for i in range(1, n):
        term = rp.App(term, _tree_c2(i))
    return rp.App(rp.App(term, rp.Var("s")), rp.Var("z"))
