#!/usr/bin/env python3
"""EML-EXP-002 — the integer-only Q-format evaluator.

Preregistration: `experiments/EML-EXP-002-preregistration.md` at `a6da44b`,
committed before this file existed.  The evaluator it fixes:

    signed 64-bit integers, format Q(63-n).n for n in {8,12,16,20,24,32,40};
    integer-only exp and ln with a pinned algorithm whose term count is a
    function of n fixed in advance; round-to-nearest-even primary, truncation
    a second configuration, never mixed; overflow TRAPS -- no saturation, no
    wraparound; eml(a,b) = exp(a) - ln(b) evaluated exactly as the tree says.

NO FLOAT.  Every value in this module is a Python `int` or one of the two
infinity sentinels.  `validate.py` greps this file and `measure.py` for float
literals and float-producing operators in the evaluation path.

PINNED ALGORITHM
    exp(a):  range reduction by powers of two.  k = a / ln2 rounded in the
             configured mode, r = a - k*ln2, exp(a) = 2^k * series(r) with
             series(r) = sum_{i=0..T} r^i / i!.  The scaling by 2^k is an
             exact left shift (or a rounded right shift for k < 0), which is
             what makes the reduction "by powers of two".
    ln(b):   binary normalization.  b = 2^e * m with m in [1,2), so
             ln(b) = e*ln2 + ln(m), and ln(m) = 2*atanh(z) with
             z = (m-1)/(m+1) in [0, 1/3], summed as
             2 * sum_{j=0..T-1} z^(2j+1) / (2j+1).
    T(n) = n // 2 + 6, fixed here and never varied: 10, 12, 14, 16, 18, 22, 26
    for n = 8, 12, 16, 20, 24, 32, 40.  Truncation bounds, worst case over the
    reduced range: exp |r| <= ln2 gives 0.694^T/T! <= 2^-27 at T=10 and
    2^-104 at T=26; ln z <= 1/3 gives 3^-(2T-1)/(2T-1) <= 2^-34 at T=10 and
    2^-82 at T=26.  Both are below one ulp of Q(63-n).n at every n in the
    list, so the series truncation is never the binding error.

    ln2 enters as one pinned integer constant, floor(ln2 * 2^192), rounded to
    Q(63-n).n by round-to-nearest-even.  A constant is not an operation, so it
    does not follow the configured rounding mode; control `constants_agree`
    checks it against mpmath at 50 digits.

TWO CONFIGURATIONS OF ln's DOMAIN -- and why there are two
    The preregistered evaluator says nothing about `ln` at zero.  The basis
    needs it: Odrzywolek builds the additive inverse as `neg(x) = ln(1) - x`,
    whose expansion evaluates `ln(ln 1) = ln(0) = -inf`, and `exp` of that
    infinity, before it comes back to a finite number.  The corpus's own
    committed transcription control evaluates the basis in mpmath's extended
    reals for exactly this reason.  A signed 64-bit integer has no -inf.

    `strict` (PRIMARY, the literal preregistered evaluator): `ln` of a
        non-positive representable is a trap, outcome `DOMAIN`, failure at
        that (f, n, point).  No sentinel is introduced, because the
        preregistration authorized none.
    `extended` (SECONDARY, added by the harness and labelled as such):
        two infinity sentinels with mpmath's own conventions --
        ln(0) = -inf, exp(-inf) = 0, exp(+inf) = +inf, ln(+inf) = +inf,
        finite - (-inf) = +inf.  `inf - inf` is a trap, never a number.
        This configuration exists so that the precision question can be asked
        at all; it is never used to score a prediction without the strict
        verdict printed beside it.

See `RESULT.md`, deviations D2 and D3.
"""

from __future__ import annotations

INT_MIN = -(2 ** 63)
INT_MAX = 2 ** 63 - 1

# floor(ln 2 * 2**192).  Provenance: mpmath at 80 digits; control
# `constants_agree` re-derives it whenever mpmath is present.
LN2_Q192 = 4350955369971217654477563090224794165364344896676135745069
LN2_SCALE = 192

NEAREST = "nearest_even"
TRUNCATE = "truncate"
MODES = (NEAREST, TRUNCATE)

N_LIST = (8, 12, 16, 20, 24, 32, 40)


class Trap(Exception):
    """A preregistered failure of the evaluator at this (f, n, point).

    `kind` is OVERFLOW (a value outside Q(63-n).n, per the preregistration) or
    DOMAIN (an operation the preregistered evaluator does not define, i.e. ln
    of a non-positive representable in the strict configuration)."""

    def __init__(self, kind: str, detail: str) -> None:
        super().__init__("%s: %s" % (kind, detail))
        self.kind = kind
        self.detail = detail


class Infinity:
    """A sentinel for the `extended` configuration only.  Never constructed by
    the strict configuration, so the strict evaluator holds `int` and nothing
    else."""

    __slots__ = ("sign",)

    def __init__(self, sign: int) -> None:
        self.sign = sign

    def __repr__(self) -> str:
        return "+inf" if self.sign > 0 else "-inf"


POS_INF = Infinity(1)
NEG_INF = Infinity(-1)


def term_count(n: int) -> int:
    """T(n), fixed in advance and never varied."""
    return n // 2 + 6


def trap_range(value: int, where: str) -> int:
    if value < INT_MIN or value > INT_MAX:
        raise Trap("OVERFLOW", "%s produced %d, outside Q(63-n).n" % (where, value))
    return value


def rshift_round(value: int, shift: int, mode: str) -> int:
    """value / 2**shift, rounded in `mode`.  Integer-only."""
    if shift <= 0:
        return value << (-shift)
    if mode == TRUNCATE:                       # toward zero
        return -((-value) >> shift) if value < 0 else (value >> shift)
    quotient = value >> shift                  # floor
    remainder = value - (quotient << shift)
    half = 1 << (shift - 1)
    if remainder > half or (remainder == half and (quotient & 1)):
        quotient += 1
    return quotient


def idiv_round(numerator: int, denominator: int, mode: str) -> int:
    """numerator / denominator, rounded in `mode`.  Integer-only."""
    if denominator == 0:
        raise Trap("DOMAIN", "division by zero")
    if denominator < 0:
        numerator, denominator = -numerator, -denominator
    if mode == TRUNCATE:
        return -((-numerator) // denominator) if numerator < 0 else numerator // denominator
    quotient, remainder = divmod(numerator, denominator)
    twice = 2 * remainder
    if twice > denominator or (twice == denominator and (quotient & 1)):
        quotient += 1
    return quotient


def ln2_at(n: int) -> int:
    """ln 2 in Q(63-n).n, round-to-nearest-even from the pinned constant."""
    return rshift_round(LN2_Q192, LN2_SCALE - n, NEAREST)


def one_at(n: int) -> int:
    return 1 << n


def from_fraction(numerator: int, denominator: int, n: int, mode: str) -> int:
    """An exact rational grid coordinate as a Q(63-n).n integer."""
    return trap_range(idiv_round(numerator << n, denominator, mode), "grid coordinate")


class Q:
    """One pinned configuration: fractional bits, rounding mode, ln domain."""

    def __init__(self, n: int, mode: str, extended: bool) -> None:
        if n not in N_LIST:
            raise ValueError("n=%d is not in the preregistered list" % (n,))
        if mode not in MODES:
            raise ValueError("unknown rounding mode %r" % (mode,))
        self.n = n
        self.mode = mode
        self.extended = extended
        self.one = one_at(n)
        self.ln2 = ln2_at(n)
        self.terms = term_count(n)

    # -- arithmetic ------------------------------------------------------
    def mul(self, a: int, b: int) -> int:
        return trap_range(rshift_round(a * b, self.n, self.mode), "multiply")

    def div(self, a: int, b: int) -> int:
        if b == 0:
            raise Trap("DOMAIN", "division by zero")
        return trap_range(idiv_round(a << self.n, b, self.mode), "divide")

    def div_int(self, a: int, k: int) -> int:
        return trap_range(idiv_round(a, k, self.mode), "divide by %d" % k)

    def sub(self, a: int, b: int) -> int:
        return trap_range(a - b, "subtract")

    def add(self, a: int, b: int) -> int:
        return trap_range(a + b, "add")

    # -- transcendentals -------------------------------------------------
    def exp(self, a):
        if isinstance(a, Infinity):
            if a.sign < 0:
                return 0
            return POS_INF                       # extended only; strict never holds one
        k = idiv_round(a, self.ln2, self.mode)
        if k > 64:
            raise Trap("OVERFLOW", "exp argument %d needs 2^%d, outside Q(63-n).n" % (a, k))
        remainder = trap_range(a - k * self.ln2, "exp range reduction")
        total = self.one
        term = self.one
        for i in range(1, self.terms + 1):
            term = self.mul(term, remainder)
            term = self.div_int(term, i)
            total = self.add(total, term)
        if k >= 0:
            return trap_range(total << k, "exp scaling")
        return trap_range(rshift_round(total, -k, self.mode), "exp scaling")

    def ln(self, b):
        if isinstance(b, Infinity):
            if b.sign > 0:
                return POS_INF
            raise Trap("DOMAIN", "ln of -inf is not real")
        if b < 0:
            raise Trap("DOMAIN", "ln of the negative representable %d" % b)
        if b == 0:
            if self.extended:
                return NEG_INF
            raise Trap("DOMAIN", "ln(0) is -inf, which Q(63-n).n cannot represent")
        exponent = b.bit_length() - 1 - self.n
        if exponent > 0:
            mantissa = rshift_round(b, exponent, self.mode)
        elif exponent < 0:
            mantissa = b << (-exponent)
        else:
            mantissa = b
        z = self.div(self.sub(mantissa, self.one), self.add(mantissa, self.one))
        squared = self.mul(z, z)
        term = z
        total = z
        for j in range(1, self.terms):
            term = self.mul(term, squared)
            total = self.add(total, self.div_int(term, 2 * j + 1))
        ln_mantissa = trap_range(2 * total, "ln mantissa")
        return trap_range(exponent * self.ln2 + ln_mantissa, "ln")

    def eml(self, a, b):
        """exp(a) - ln(b), exactly as the tree says.  No simplification."""
        left = self.exp(a)
        right = self.ln(b)
        if isinstance(left, Infinity) or isinstance(right, Infinity):
            if isinstance(left, Infinity) and isinstance(right, Infinity):
                if left.sign == right.sign:
                    raise Trap("OVERFLOW", "inf - inf is not a number")
                return left
            if isinstance(left, Infinity):
                return left
            return POS_INF if right.sign < 0 else NEG_INF
        return self.sub(left, right)


MAX_STEPS = 10 ** 6      # preregistration-external feasibility cap; see RESULT


class Saturated(Exception):
    def __init__(self, steps: int) -> None:
        super().__init__("evaluation exceeded %d steps" % steps)
        self.steps = steps


def evaluate(kinds, lefts, rights, syms, order, root, env, q):  # noqa: PLR0913
    """Evaluate one construction's DAG at one point.

    Memoized on node identity, which for a hash-consed DAG is memoization on
    the subterm's content: identical subterms evaluate exactly once, in the
    configuration (n, rounding mode, ln domain) fixed by `q`.  `eml` is a
    deterministic function of its two arguments in Q arithmetic, so this
    returns the number the fully expanded tree gives.  Iterative: `order` is a
    topological order of the DAG, so no Python recursion is involved.
    """
    values = {}
    steps = 0
    for i in order:
        steps += 1
        if steps > MAX_STEPS:
            raise Saturated(steps)
        if kinds[i] == 0:
            values[i] = q.one if syms[i] == "1" else env[syms[i]]
        else:
            values[i] = q.eml(values[lefts[i]], values[rights[i]])
    return values[root], steps
