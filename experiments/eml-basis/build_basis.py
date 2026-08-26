#!/usr/bin/env python3
"""Transcribe the Odrzywolek EML goal-operation chain into `basis.json`.

This is a TRANSCRIPTION instrument, not a measurement harness.  It contains no
hypothesis, no null model and no statistic.  Its only job is to turn the
paper's Table S2 -- which states each goal operation as a witness expression
over *previously discovered* primitives -- into a pure S-expression over the
alphabet {eml, 1, x, y}, which is what EML-EXP-001 and EML-EXP-002 need.

Source, pinned (see basis.json "source"):
    Andrzej Odrzywolek, "All elementary functions from a single operator",
    arXiv:2603.21852v2 (2026-04-04), TeX e-print tarball.

Nothing here simplifies, corrects or improves a construction.  Each chain
primitive below is the paper's witness expression, verbatim, with the paper's
own argument names.  The expansion to pure EML is mechanical substitution:
every primitive is replaced by its own witness expression until only `eml`,
`1`, `x`, `y` remain.  That is exactly the procedure the paper describes for
its own EML compiler ("The output of the VerifyBaseSet procedure provides the
data required to reconstruct any primitive or composite elementary expression
in terms of EML Sheffer").

Run:  python3 build_basis.py            # rewrite basis.json
      python3 build_basis.py --check    # verify basis.json is up to date
"""

import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASIS = os.path.join(HERE, "basis.json")

sys.setrecursionlimit(200000)

# ---------------------------------------------------------------------------
# Hash-consed EML terms.  A term is either the string "1", "x", "y", or a
# tuple ("eml", a, b).  Structurally equal subterms are the same Python object,
# which keeps the (very large) expansions cheap to build; the *tree* they
# denote is still the fully expanded tree, and `count_tree` below counts it as
# such.
# ---------------------------------------------------------------------------

_HASHCONS = {}
ONE, X, Y = "1", "x", "y"


def eml(a, b):
    key = (id(a), id(b))
    got = _HASHCONS.get(key)
    if got is None:
        got = ("eml", a, b)
        _HASHCONS[key] = got
    return got


# ---------------------------------------------------------------------------
# The paper's chain, Table S2 (Supplementary Information, p. 6).
# Step numbers are the paper's.  Each function below is the witness expression
# of that step, with the paper's previously-discovered primitives spelled as
# the Python functions defined above it -- i.e. the chain, in the paper's own
# discovery order, with no reordering and no shortcuts.
# ---------------------------------------------------------------------------

E_CONST = eml(ONE, ONE)                                    # 1   e = eml(1,1)


def p_exp(a):                                              # 2   exp(x) = eml(x,1)
    return eml(a, ONE)


def p_ln(a):                                               # 3   ln(x) = eml(1, exp(eml(1,x)))
    return eml(ONE, p_exp(eml(ONE, a)))


def p_sub(a, b):                                           # 4   x-y = eml(ln x, exp y)
    return eml(p_ln(a), p_exp(b))


NEG1 = p_sub(p_ln(ONE), ONE)                               # 5   -1 = ln(1) - 1
TWO = p_sub(ONE, NEG1)                                     # 6   2 = 1 - (-1)


def p_neg(a):                                              # 7   -x = ln(1) - x
    return p_sub(p_ln(ONE), a)


def p_add(a, b):                                           # 8   x+y = x - (-y)
    return p_sub(a, p_neg(b))


def p_inv(a):                                              # 9   1/x = exp(-ln x)
    return p_exp(p_neg(p_ln(a)))


def p_mul(a, b):                                           # 10  x*y = exp(ln x + ln y)
    return p_exp(p_add(p_ln(a), p_ln(b)))


def p_sqr(a):                                              # 11  x^2 = x * x
    return p_mul(a, a)


def p_div(a, b):                                           # 12  x/y = x * inv(y)
    return p_mul(a, p_inv(b))


def p_half(a):                                             # 13  x/2
    return p_div(a, TWO)


def p_avg(a, b):                                           # 14  avg(x,y) = half(x+y)
    return p_half(p_add(a, b))


def p_sqrt(a):                                             # 15  sqrt(x) = exp(half(ln x))
    return p_exp(p_half(p_ln(a)))


def p_pow(a, b):                                           # 16  x^y = exp(y * ln x)
    return p_exp(p_mul(b, p_ln(a)))


def p_logb(a, b):                                          # 17  log_x y = ln y / ln x
    return p_div(p_ln(b), p_ln(a))


PI = p_sqrt(p_neg(p_sqr(p_ln(NEG1))))                      # 18  pi = sqrt(-(ln(-1))^2)


def p_hypot(a, b):                                         # 19  hypot(x,y) = sqrt(x^2 + y^2)
    return p_sqrt(p_add(p_sqr(a), p_sqr(b)))


def p_sigma(a):                                            # 20  sigma(x) = 1/eml(-x, exp(-1))
    return p_inv(eml(p_neg(a), p_exp(NEG1)))


def p_cosh(a):                                             # 21  cosh(x) = avg(exp x, exp(-x))
    return p_avg(p_exp(a), p_exp(p_neg(a)))


def p_sinh(a):                                             # 22  sinh(x) = eml(x, exp(cosh x))
    return eml(a, p_exp(p_cosh(a)))


def p_tanh(a):                                             # 23  tanh(x) = sinh x / cosh x
    return p_div(p_sinh(a), p_cosh(a))


def p_cos(a):                                              # 24  cos(x) = cosh(sqrt(-x^2))
    return p_cosh(p_sqrt(p_neg(p_sqr(a))))


def p_sin(a):                                              # 25  sin(x) = cos(x - pi/2)
    return p_cos(p_sub(a, p_div(PI, TWO)))


def p_tan(a):                                              # 26  tan(x) = sin x / cos x
    return p_div(p_sin(a), p_cos(a))


def p_arsinh(a):                                           # 27  arsinh(x) = ln(x + hypot(-1,x))
    return p_ln(p_add(a, p_hypot(NEG1, a)))


def p_arcosh(a):                                           # 28  arcosh(x) = arsinh(hypot(x, sqrt(-1)))
    return p_arsinh(p_hypot(a, p_sqrt(NEG1)))


def p_arccos(a):                                           # 29  arccos(x) = arcosh(cos(arcosh(x)))
    return p_arcosh(p_cos(p_arcosh(a)))


def p_artanh(a):                                           # 30  artanh(x) = arsinh(1/tan(arccos(x)))
    return p_arsinh(p_inv(p_tan(p_arccos(a))))


def p_arcsin(a):                                           # 31  arcsin(x) = pi/2 - arccos(x)
    return p_sub(p_div(PI, TWO), p_arccos(a))


def p_arctan(a):                                           # 32  arctan(x) = arcsin(tanh(arsinh(x)))
    return p_arcsin(p_tanh(p_arsinh(a)))


# ---------------------------------------------------------------------------
# Serialization and tree statistics.
# ---------------------------------------------------------------------------


def to_sexpr(term):
    """Render as `(eml A B)` over the alphabet {eml, 1, x, y}. Iterative: the
    fully expanded trees run to ~5e5 nodes and ~260 levels."""
    out = []
    stack = [("n", term)]
    while stack:
        kind, v = stack.pop()
        if kind == "l":
            out.append(v)
        elif isinstance(v, str):
            out.append(v)
        else:
            out.append("(eml ")
            stack.append(("l", ")"))
            stack.append(("n", v[2]))
            stack.append(("l", " "))
            stack.append(("n", v[1]))
    return "".join(out)


def count_tree(term):
    """(eml-nodes, leaves, depth, distinct-subterms) of the *tree*, computed
    over the hash-consed DAG (identical subterms have identical counts, so the
    memo is an optimisation, not a different quantity)."""
    memo = {}

    def go(t):
        if isinstance(t, str):
            return (0, 1, 1)
        k = id(t)
        hit = memo.get(k)
        if hit is not None:
            return hit
        a = go(t[1])
        b = go(t[2])
        r = (1 + a[0] + b[0], a[1] + b[1], 1 + max(a[2], b[2]))
        memo[k] = r
        return r

    nodes, leaves, depth = go(term)
    return nodes, leaves, depth, len(memo)


# ---------------------------------------------------------------------------
# Domains.  Each is a subset of the target's real domain together with the
# sampling recipe transcription_check.py uses.  Samplers:
#   uniform            u -> lo + u*(hi-lo)
#   loguniform         u -> exp(ln lo + u*(ln hi - ln lo))          (lo,hi > 0)
#   signed_loguniform  loguniform magnitude, sign from a second draw
#   shifted_loguniform base + loguniform(lo,hi)
# "exclude" is a list of closed intervals rejected by redraw (see the check).
# ---------------------------------------------------------------------------

U4 = {"sampler": "uniform", "lo": "-4", "hi": "4"}
SL4 = {"sampler": "signed_loguniform", "lo": "0.05", "hi": "4"}
UNIT = {"sampler": "uniform", "lo": "-0.99", "hi": "0.99"}
UNIT_NONNEG = {"sampler": "uniform", "lo": "0", "hi": "0.99"}
LOGPOS = {"sampler": "loguniform", "lo": "1e-3", "hi": "1e3"}


def dom(desc, **vars_):
    return {"description": desc, "vars": vars_}


# A `restriction` records that the paper's own construction does NOT compute
# its labelled target on the whole real domain, so section 1.1 samples a named
# sub-domain instead.  The construction itself is never edited.  See
# TRANSCRIPTION_LOG.md, finding T1.
def restrict(full, to, reason, counterexample):
    return {"target_real_domain": full, "checked_on": to, "reason": reason,
            "counterexample": counterexample,
            "discovered_by": "transcription_check.py (section 1.1), first run",
            "construction_edited": False}


PARITY = ("The paper's step-28 witness arcosh(x) = arsinh(hypot(x, sqrt(-1))) reaches x only "
          "through hypot, which squares it, so the EML arcosh is an even function of x. On "
          "x >= 1, arcosh's own real domain, that is harmless and step 28 verifies. Step 29 "
          "applies arcosh at |x| < 1, off that domain, where the lost sign is not recoverable, "
          "so the EML arccos computes arccos(|x|); steps 30, 31 and 32 inherit it through "
          "arccos. Agreement with the target at |x| is exact to 50 digits, which identifies "
          "the mechanism rather than a numerical accident.")


# ---------------------------------------------------------------------------
# The 32 goal operations of Table S2, in the paper's order.
#
# complex: the paper's construction routes through i somewhere on the stated
#          domain.  Asserted here, VERIFIED by transcription_check.py, which
#          fails a construction whose measured intermediate imaginary parts
#          contradict the flag.
# ---------------------------------------------------------------------------

SI = "arXiv:2603.21852v2, Supplementary Information, Table S2 (p. 6), step %d"

# Constructions whose complex intermediates come from Euler's formula and are
# therefore present at EVERY point of the domain: the chain reaches i through
# ln(-1) or sqrt(-1) applied to a CONSTANT.  The rest are `argument_dependent`:
# their complex intermediates appear only for some arguments, because the chain
# takes ln of an intermediate that happens to be negative there.  Measured: on a
# window with every argument >= e, all thirteen argument-dependent constructions
# evaluate with max|Im| exactly 0, and all ten Euler-routed ones do not.
EULER_ROUTED = {"eml_pi", "eml_cos", "eml_sin", "eml_tan", "eml_arsinh", "eml_arcosh",
                "eml_arccos", "eml_artanh", "eml_arcsin", "eml_arctan"}

ENTRIES = [
    dict(id="eml_e", step=1, target="e", definition="e = 2.718281828... (Euler's number)",
         arity=0, domain=dom("no argument (constant)"),
         witness="eml(1, 1)", K=3, chain="(eml 1 1)", term=E_CONST,
         complex=False, complex_reason=None,
         notes="Also stated in the main-text abstract and in Table 4 (EML compiler leaf count 3).",
         alternates=[]),

    dict(id="eml_exp", step=2, target="exp(x)", definition="exp(x) = e^x",
         arity=1, domain=dom("x in R (window: uniform on [-4, 4])", x=U4),
         witness="eml(x, 1)", K=3, chain="(exp x)", term=p_exp(X),
         complex=False, complex_reason=None,
         notes="Also stated in the main-text abstract: e^x = eml(x,1).",
         alternates=[]),

    dict(id="eml_ln", step=3, target="ln(x)", definition="ln(x) = natural logarithm, principal branch",
         arity=1, domain=dom("x > 0 (window: log-uniform on [1e-3, 1e3])", x=LOGPOS),
         witness="eml(1, exp(eml(1, x)))", K=6, chain="(ln x)", term=p_ln(X),
         complex=False, complex_reason=None,
         notes=("Main text Eq. (4) gives the same tree in fully expanded form, "
                "ln(z) = eml(1, eml[eml(1,z), 1]), with RPN string 11xE1EE and "
                "LeafCount 7; identical to the SI witness after exp(a) = eml(a,1)."),
         alternates=["main text Eq. (4): ln(z) = eml(1, eml[eml(1,z),1])",
                     "main text Sect. 4.1 (equivalent closed form): ln(z) = e - log(e^e / z)"]),

    dict(id="eml_sub", step=4, target="x - y", definition="subtraction",
         arity=2, domain=dom("(x, y) in R^2 (window: uniform on [-4, 4]^2)", x=U4, y=U4),
         witness="eml(ln x, exp y)", K=5, chain="(sub x y)", term=p_sub(X, Y),
         complex=True, complex_reason="ln(x) on x < 0 (branch of the EML logarithm)",
         notes=("SI Sect. 1.3 calls this 'the key algebraic insight'. Real for x > 0; "
                "for x < 0 the intermediate ln(x) is complex and exp(ln x) returns x."),
         alternates=[]),

    dict(id="eml_neg1", step=5, target="-1", definition="the constant -1",
         arity=0, domain=dom("no argument (constant)"),
         witness="ln(1) - 1", K=4, chain="(sub (ln 1) 1)", term=NEG1,
         complex=False, complex_reason=None,
         notes=("Routes through the extended reals: ln(1) = 0 and the outer subtraction "
                "takes ln(0) = -inf, exp(-inf) = 0, exactly as the main text warns "
                "(Sect. 4.1). In finite precision ln(1) is a signed residual of order "
                "10^-dps and the same limit is reached numerically."),
         alternates=[]),

    dict(id="eml_two", step=6, target="2", definition="the constant 2",
         arity=0, domain=dom("no argument (constant)"),
         witness="1 - (-1)", K=3, chain="(sub 1 neg1)", term=TWO,
         complex=False, complex_reason=None, notes="", alternates=[]),

    dict(id="eml_minus", step=7, target="-x", definition="minus(x) = -x (sign flip)",
         arity=1, domain=dom("x in R (window: uniform on [-4, 4])", x=U4),
         witness="ln(1) - x", K=4, chain="(sub (ln 1) x)", term=p_neg(X),
         complex=False, complex_reason=None,
         notes="Extended-real path as in step 5; no logarithm of a negative number.",
         alternates=[]),

    dict(id="eml_add", step=8, target="x + y", definition="addition",
         arity=2, domain=dom("(x, y) in R^2 (window: uniform on [-4, 4]^2)", x=U4, y=U4),
         witness="x - (-y)", K=4, chain="(sub x (neg y))", term=p_add(X, Y),
         complex=True, complex_reason="inherits ln(x) on x < 0 from step 4",
         notes="", alternates=[]),

    dict(id="eml_inv", step=9, target="1/x", definition="inv(x) = 1/x (reciprocal)",
         arity=1, domain=dom("x != 0 (window: signed log-uniform, |x| in [0.05, 4])", x=SL4),
         witness="exp(-ln x)", K=4, chain="(exp (neg (ln x)))", term=p_inv(X),
         complex=True, complex_reason="ln(x) on x < 0",
         notes="", alternates=[]),

    dict(id="eml_mul", step=10, target="x * y", definition="multiplication",
         arity=2, domain=dom("(x, y) in R^2, xy != 0 (window: signed log-uniform)", x=SL4, y=SL4),
         witness="exp(ln x + ln y)", K=6, chain="(exp (add (ln x) (ln y)))", term=p_mul(X, Y),
         complex=True, complex_reason="ln(x), ln(y) on negative arguments",
         notes="Expansion has 20 eml nodes, LeafCount 41, matching the main-text "
               "Table 4 EML-compiler entry for x*y (41).",
         alternates=[]),

    dict(id="eml_sqr", step=11, target="x^2", definition="sqr(x) = x^2",
         arity=1, domain=dom("x in R, x != 0 (window: signed log-uniform)", x=SL4),
         witness="x * x", K=3, chain="(mul x x)", term=p_sqr(X),
         complex=True, complex_reason="ln(x) on x < 0 inside the product",
         notes="", alternates=[]),

    dict(id="eml_div", step=12, target="x / y", definition="division",
         arity=2, domain=dom("y != 0 (window: x signed log-uniform, y signed log-uniform)",
                             x=SL4, y=SL4),
         witness="x * inv(y)", K=4, chain="(mul x (inv y))", term=p_div(X, Y),
         complex=True, complex_reason="negative arguments to ln inside the product",
         notes="", alternates=[]),

    dict(id="eml_half", step=13, target="x / 2", definition="half(x) = x/2",
         arity=1, domain=dom("x in R, x != 0 (window: signed log-uniform)", x=SL4),
         witness="x / 2", K=3, chain="(div x two)", term=p_half(X),
         complex=True, complex_reason="negative arguments to ln inside the product",
         notes="Expansion of half(1) has LeafCount 91, matching the main-text Table 4 "
               "EML-compiler entry for the constant 1/2 (91).",
         alternates=[]),

    dict(id="eml_avg", step=14, target="avg(x, y)", definition="avg(x, y) = (x + y)/2",
         arity=2, domain=dom("(x, y) in R^2, x + y != 0 (window: uniform on [-4, 4]^2)", x=U4, y=U4),
         witness="half(x + y)", K=4, chain="(half (add x y))", term=p_avg(X, Y),
         complex=True, complex_reason="negative arguments to ln inside the product",
         notes="", alternates=[]),

    dict(id="eml_sqrt", step=15, target="sqrt(x)", definition="sqrt(x) = x^(1/2), principal branch",
         arity=1, domain=dom("x > 0 (window: log-uniform on [1e-3, 1e3])", x=LOGPOS),
         witness="exp(half(ln x))", K=4, chain="(exp (half (ln x)))", term=p_sqrt(X),
         complex=True, complex_reason="ln(ln x) is negative for x < e, and the halving takes ln of it",
         notes=("Real only on x >= 1. The halving is done by the step-13 division, "
                "which takes ln of its first argument; for x < 1 that argument ln(x) "
                "is negative."),
         alternates=[]),

    dict(id="eml_pow", step=16, target="x^y", definition="pow(x, y) = x^y",
         arity=2, domain=dom("x > 0, y in R (window: x log-uniform [0.05, 20], y uniform [-3, 3])",
                             x={"sampler": "loguniform", "lo": "0.05", "hi": "20"},
                             y={"sampler": "uniform", "lo": "-3", "hi": "3"}),
         witness="exp(y * ln x)", K=5, chain="(exp (mul y (ln x)))", term=p_pow(X, Y),
         complex=True, complex_reason="ln of a negative argument inside the product",
         notes="SI Sect. 1.3 notes x^y is a dead-end of the chain: nothing later uses it.",
         alternates=[]),

    dict(id="eml_logb", step=17, target="log_x(y)", definition="log_x(y) = ln y / ln x",
         arity=2, domain=dom("x > 0, x != 1, y > 0 (window: x log-uniform [1.2, 20], "
                             "y log-uniform [1e-2, 1e2])",
                             x={"sampler": "loguniform", "lo": "1.2", "hi": "20"},
                             y={"sampler": "loguniform", "lo": "1e-2", "hi": "1e2"}),
         witness="ln y / ln x", K=5, chain="(div (ln y) (ln x))", term=p_logb(X, Y),
         complex=True, complex_reason="ln(ln x) or ln(ln y) is negative when x < e or y < e, "
                                      "and the quotient takes ln of it",
         notes="SI Sect. 1.3 notes log_x y is a dead-end of the chain.",
         alternates=[]),

    dict(id="eml_pi", step=18, target="pi", definition="pi = 3.14159265...",
         arity=0, domain=dom("no argument (constant)"),
         witness="sqrt(-(ln(-1))^2)", K=5, chain="(sqrt (neg (sqr (ln neg1))))", term=PI,
         complex=True, complex_reason="Euler: ln(-1) = -i*pi under the EML branch",
         notes=("The main text (Sect. 4.1) records that the EML logarithm disagrees with "
                "the principal branch on the negative real axis, giving ln(-1) = -i*pi "
                "rather than +i*pi. This construction is insensitive to that sign, "
                "because ln(-1) enters squared. Expansion has LeafCount 199; the "
                "main-text Table 4 EML-compiler entry for pi is 193, i.e. the prototype "
                "compiler does not emit this chain expansion."),
         alternates=[]),

    dict(id="eml_hypot", step=19, target="hypot(x, y)", definition="hypot(x, y) = sqrt(x^2 + y^2)",
         arity=2, domain=dom("(x, y) in R^2, (x,y) != (0,0) (window: uniform on [-4, 4]^2)",
                             x=U4, y=U4),
         witness="sqrt(x^2 + y^2)", K=6, chain="(sqrt (add (sqr x) (sqr y)))", term=p_hypot(X, Y),
         complex=True, complex_reason="ln of negative arguments inside the squares",
         notes="", alternates=[]),

    dict(id="eml_sigma", step=20, target="sigma(x)", definition="sigma(x) = 1/(1 + e^(-x)) (logistic sigmoid)",
         arity=1, domain=dom("x in R (window: uniform on [-4, 4])", x=U4),
         witness="1/eml(-x, exp(-1))", K=6, chain="(inv (eml (neg x) (exp neg1)))", term=p_sigma(X),
         complex=False, complex_reason=None,
         notes="eml(-x, exp(-1)) = e^(-x) - ln(e^(-1)) = e^(-x) + 1, which is > 1 for "
               "every real x, so no logarithm of a negative number occurs.",
         alternates=[]),

    dict(id="eml_cosh", step=21, target="cosh(x)", definition="cosh(x) = (e^x + e^(-x))/2",
         arity=1, domain=dom("x in R (window: uniform on [-4, 4])", x=U4),
         witness="avg(exp x, exp(-x))", K=6, chain="(avg (exp x) (exp (neg x)))", term=p_cosh(X),
         complex=False, complex_reason=None,
         notes="SI Sect. 1.1 cites this identity as the reason avg is kept in the "
               "36-primitive list at all.",
         alternates=[]),

    dict(id="eml_sinh", step=22, target="sinh(x)", definition="sinh(x) = (e^x - e^(-x))/2",
         arity=1, domain=dom("x in R (window: uniform on [-4, 4])", x=U4),
         witness="eml(x, exp(cosh x))", K=5, chain="(eml x (exp (cosh x)))", term=p_sinh(X),
         complex=False, complex_reason=None,
         notes="eml(x, exp(cosh x)) = e^x - cosh(x) = sinh(x); the raw operator is used "
               "directly rather than a derived subtraction.",
         alternates=[]),

    dict(id="eml_tanh", step=23, target="tanh(x)", definition="tanh(x) = sinh(x)/cosh(x)",
         arity=1, domain=dom("x in R (window: uniform on [-4, 4])", x=U4),
         witness="sinh x / cosh x", K=5, chain="(div (sinh x) (cosh x))", term=p_tanh(X),
         complex=True, complex_reason="ln(sinh x) is complex for x < 0",
         notes="", alternates=[]),

    dict(id="eml_cos", step=24, target="cos(x)", definition="cos(x) = cosine",
         arity=1, domain=dom("x in R (window: uniform on [-4, 4])", x=U4),
         witness="cosh(sqrt(-x^2))", K=5, chain="(cosh (sqrt (neg (sqr x))))", term=p_cos(X),
         complex=True, complex_reason="Euler: sqrt(-x^2) is imaginary for every x != 0",
         notes="", alternates=[]),

    dict(id="eml_sin", step=25, target="sin(x)", definition="sin(x) = sine",
         arity=1, domain=dom("x in R (window: uniform on [-4, 4])", x=U4),
         witness="cos(x - pi/2)", K=5, chain="(cos (sub x (div pi two)))", term=p_sin(X),
         complex=True, complex_reason="inherits Euler route from cos and pi",
         notes="", alternates=[]),

    dict(id="eml_tan", step=26, target="tan(x)", definition="tan(x) = sin(x)/cos(x)",
         arity=1, domain=dom("x in R away from the poles (window: uniform on [-4, 4], "
                             "excluding |x - pi/2| < 0.1 and |x + pi/2| < 0.1)",
                             x={"sampler": "uniform", "lo": "-4", "hi": "4",
                                "exclude": [["-1.6707963267948966", "-1.4707963267948966"],
                                            ["1.4707963267948966", "1.6707963267948966"]]}),
         witness="sin x / cos x", K=5, chain="(div (sin x) (cos x))", term=p_tan(X),
         complex=True, complex_reason="inherits Euler route from sin and cos",
         notes="", alternates=[]),

    dict(id="eml_arsinh", step=27, target="arsinh(x)", definition="arsinh(x) = ln(x + sqrt(1 + x^2))",
         arity=1, domain=dom("x in R (window: uniform on [-4, 4])", x=U4),
         witness="ln(x + hypot(-1, x))", K=6, chain="(ln (add x (hypot neg1 x)))", term=p_arsinh(X),
         complex=True, complex_reason="hypot(-1, x) squares -1 via exp(ln(-1) + ln(-1))",
         notes="hypot(-1, x) = sqrt(1 + x^2); the -1 is a way of writing the constant 1 "
               "under the square, and it drags ln(-1) into every evaluation.",
         alternates=[]),

    dict(id="eml_arcosh", step=28, target="arcosh(x)", definition="arcosh(x) = ln(x + sqrt(x^2 - 1)), x >= 1",
         arity=1, domain=dom("x >= 1 (window: 1 + log-uniform on [1e-3, 20])",
                             x={"sampler": "shifted_loguniform", "base": "1",
                                "lo": "1e-3", "hi": "20"}),
         witness="arsinh(hypot(x, sqrt(-1)))", K=5,
         chain="(arsinh (hypot x (sqrt neg1)))", term=p_arcosh(X),
         complex=True, complex_reason="explicit sqrt(-1) in the paper's witness",
         notes=("hypot(x, sqrt(-1)) = sqrt(x^2 - 1). Under the EML branch sqrt(-1) "
                "evaluates to -i rather than +i (see step 18); the construction is "
                "insensitive because it is squared inside hypot."),
         alternates=[]),

    dict(id="eml_arccos", step=29, target="arccos(x)", definition="arccos(x), |x| <= 1, range [0, pi]",
         arity=1, domain=dom("0 <= x <= 1 (window: uniform on [0, 0.99]); see domain_restriction",
                             x=UNIT_NONNEG),
         witness="arcosh(cos(arcosh(x)))", K=4, chain="(arcosh (cos (arcosh x)))", term=p_arccos(X),
         complex=True, complex_reason="arcosh(x) is purely imaginary for |x| < 1",
         restriction=restrict("|x| <= 1", "0 <= x <= 1", PARITY,
                              "x = -0.4126536009398481: construction gives 1.1454309781988448267 "
                              "= arccos(|x|), target arccos(x) = 1.9961616753909484118; agreement "
                              "with arccos(|x|) holds to all 50 digits"),
         notes="", alternates=[]),

    dict(id="eml_artanh", step=30, target="artanh(x)", definition="artanh(x) = (1/2) ln((1+x)/(1-x)), |x| < 1",
         arity=1, domain=dom("0 <= x < 1 (window: uniform on [0, 0.99]); see domain_restriction",
                             x=UNIT_NONNEG),
         witness="arsinh(1/tan(arccos(x)))", K=5,
         chain="(arsinh (inv (tan (arccos x))))", term=p_artanh(X),
         complex=True, complex_reason="inherits the Euler route from arccos and tan",
         restriction=restrict("|x| < 1", "0 <= x < 1", PARITY,
                              "x = -0.96611435661451289183: construction gives +artanh(|x|), "
                              "target is -artanh(|x|)"),
         notes="Largest expansion in the basis: 504554 eml nodes.",
         alternates=[]),

    dict(id="eml_arcsin", step=31, target="arcsin(x)", definition="arcsin(x), |x| <= 1, range [-pi/2, pi/2]",
         arity=1, domain=dom("0 <= x <= 1 (window: uniform on [0, 0.99]); see domain_restriction",
                             x=UNIT_NONNEG),
         witness="pi/2 - arccos(x)", K=5, chain="(sub (div pi two) (arccos x))", term=p_arcsin(X),
         complex=True, complex_reason="inherits the Euler route from pi and arccos",
         restriction=restrict("|x| <= 1", "0 <= x <= 1", PARITY,
                              "x = -0.89097425049776185309: construction gives +arcsin(|x|), "
                              "target is -arcsin(|x|)"),
         notes=("SI Sect. 1.3 records that the shorter candidate "
                "arcsin(x) = arccos(sin(arccos(x))) was REJECTED as a flaky witness: it "
                "passes at x = gamma and fails at x = -gamma by branch-cut disagreement. "
                "The complementarity identity above is the accepted witness -- but it "
                "inherits the same failure mode from step 29, see domain_restriction."),
         alternates=["rejected flaky witness (SI Sect. 1.3): arcsin(x) = arccos(sin(arccos(x)))"]),

    dict(id="eml_arctan", step=32, target="arctan(x)", definition="arctan(x), range (-pi/2, pi/2)",
         arity=1, domain=dom("x >= 0 (window: uniform on [0, 4]); see domain_restriction",
                             x={"sampler": "uniform", "lo": "0", "hi": "4"}),
         witness="arcsin(tanh(arsinh(x)))", K=4,
         chain="(arcsin (tanh (arsinh x)))", term=p_arctan(X),
         complex=True, complex_reason="inherits the Euler route from arcsin",
         restriction=restrict("x in R", "x >= 0", PARITY,
                              "x = -0.29887917144440330982: construction gives +arctan(|x|), "
                              "target is -arctan(|x|)"),
         notes="", alternates=[]),
]


def build():
    src = {
        "citation": ("Andrzej Odrzywolek, \"All elementary functions from a single operator\", "
                     "arXiv:2603.21852"),
        "arxiv_id": "2603.21852",
        "version": "v2",
        "version_date": "2026-04-04",
        "fetched_url": "https://arxiv.org/e-print/2603.21852v2",
        "resolved_url": "https://arxiv.org/src/2603.21852v2",
        "format": "TeX e-print source tarball (gzip), as served by arXiv",
        "bytes": 1274423,
        "sha256": "2a3b4219a7784d8fd0b3ffe6e7d3dd570cf73d60f8cf368459122fe78e1421db",
        "sha256_covers": ("exactly the bytes returned by the fetch above, i.e. the gzipped tar "
                          "containing EML.tex, EML.bib, Fig1_graph_spiral.pdf, Fig2_trees.pdf, "
                          "00README.json and anc/SupplementaryInformation.pdf"),
        "fetched_utc": "2026-08-27",
        "pdf_fallback_used": False,
        "operator": "eml(x, y) = exp(x) - ln(y), main text Eq. (3); internally over C, principal branch",
        "transcribed_from": ("Supplementary Information, Table S2 (p. 6), 'Complete EML "
                             "bootstrapping chain', steps 1-32; cross-referenced with main-text "
                             "Table 1 (the 36-primitive starting list), Table 4 (LeafCount) and "
                             "Eq. (4)."),
    }

    encoding = {
        "alphabet": ["eml", "1", "x", "y"],
        "sexpr": ("`eml_sexpr` is a parenthesized S-expression: a leaf is one of `1`, `x`, `y`; "
                  "an application is `(eml A B)` for the operator eml(A, B) = exp(A) - ln(B)."),
        "book1": ("EML-EXP-001 maps this to Book I as the draft's section 'Encoding' specifies: "
                  "E = LITERAL(sha256(\"EML\")), ONE = LITERAL(sha256(\"ONE\")), "
                  "X = LITERAL(sha256(\"X\")), Y = LITERAL(sha256(\"Y\")), "
                  "eml(a, b) = APPLY(APPLY(E, a), b). basis.json itself contains no Book I term "
                  "and no hash; it is oracle-independent."),
        "expansion": ("Table S2 states each witness over previously discovered primitives. "
                      "`witness_paper` is that row verbatim; `chain_sexpr` is the same expression "
                      "with the paper's primitive names; `eml_sexpr` is the mechanical expansion "
                      "of `chain_sexpr` down to {eml, 1, x, y}. No simplification is applied at "
                      "any stage."),
        "leafcount": ("The paper's LeafCount (main-text Table 4) equals 2*eml_nodes + 1 for a "
                      "full binary EML tree; both are recorded per entry."),
    }

    constructions = []
    for e in ENTRIES:
        nodes, leaves, depth, distinct = count_tree(e["term"])
        constructions.append({
            "id": e["id"],
            "step": e["step"],
            "target_name": e["target"],
            "target_definition": e["definition"],
            "arity": e["arity"],
            "domain": e["domain"],
            "paper_location": SI % e["step"],
            "witness_paper": e["witness"],
            "witness_K": e["K"],
            "chain_sexpr": e["chain"],
            "eml_sexpr": to_sexpr(e["term"]),
            "eml_nodes": nodes,
            "eml_leaves": leaves,
            "eml_depth": depth,
            "eml_distinct_subterms": distinct,
            "eml_leafcount": 2 * nodes + 1,
            "complex": e["complex"],
            "complex_reason": e["complex_reason"],
            "complex_route": (None if not e["complex"] else
                              ("euler" if e["id"] in EULER_ROUTED else "argument_dependent")),
            "domain_restriction": e.get("restriction"),
            "evaluation_class": "real_via_complex" if e["complex"] else "real",
            "notes": e["notes"],
            "alternates": e["alternates"],
        })

    n_complex = sum(1 for c in constructions if c["complex"])
    counts = {
        "transcribed": len(constructions),
        "paper_claim_36": ("Main text Sect. 3 says the procedure 're-generates all 36 elementary "
                           "operations from Table 1'. Table 1 lists 36 primitives, but SI Table S2 "
                           "reconstructs 32 of them and its caption states the four not "
                           "reconstructed: the two input variables x and y, the constant 1, and "
                           "the imaginary unit i. 32 is therefore the number of goal operations "
                           "the paper actually constructs."),
        "complex_flagged": n_complex,
        "complex_route_euler": sum(1 for c in constructions if c["complex_route"] == "euler"),
        "complex_route_argument_dependent":
            sum(1 for c in constructions if c["complex_route"] == "argument_dependent"),
        "domain_restricted": sum(1 for c in constructions if c["domain_restriction"]),
        "real_only": len(constructions) - n_complex,
        "complex_valued_targets": 0,
    }

    return {
        "schema": "eml-basis/1",
        "status": "FACT (transcription); the constructions are the paper's, not this repository's",
        "source": src,
        "encoding": encoding,
        "counts": counts,
        "constructions": constructions,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="verify basis.json matches what this script builds")
    args = ap.parse_args()

    doc = build()
    text = json.dumps(doc, indent=2, sort_keys=False, ensure_ascii=True) + "\n"

    if args.check:
        if not os.path.exists(BASIS):
            print("MISSING basis.json")
            return 1
        with open(BASIS, "r", encoding="ascii") as fh:
            have = fh.read()
        if have != text:
            print("STALE basis.json (rerun build_basis.py)")
            return 1
        print("basis.json up to date  sha256=%s" %
              hashlib.sha256(text.encode("ascii")).hexdigest())
        return 0

    with open(BASIS, "w", encoding="ascii") as fh:
        fh.write(text)
    print("wrote %s  (%d constructions, %d bytes, sha256=%s)" %
          (BASIS, len(doc["constructions"]), len(text),
           hashlib.sha256(text.encode("ascii")).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
