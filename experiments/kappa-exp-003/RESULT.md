# KAPPA-EXP-003 — result

**Status: `H-SPREAD` refuted under `C_size`. Under `C_dup` the spread is not
settled — it is still rising at the edge of the preregistered grid.**

> **Settled by [KAPPA-EXP-005](../kappa-exp-005/RESULT.md).** The extended grid
> shows the spread *saturating* in `n` and driven by `k` instead, converging to
> `k + 9/4` — unbounded, so `H-SPREAD` falls under `C_dup` too. Both the hand
> derivation in this document and the prediction in KAPPA-EXP-005's own
> preregistration were wrong about which parameter drives it.

The question, from [`talks/claude-fable-002.md`](../../talks/claude-fable-002.md)
and adopted in the [KAPPA-EXP-001 erratum](../kappa-exp-001/RESULT.md#erratum-2026-08-26):
is `sup_t spread(t)` finite for λ under a fixed materialization-charging cost
model, where `spread(t) = max_S κ_S(t) / min_S κ_S(t)`?

A finite value would be a strategy-insensitivity constant of the calculus. There
is no such constant for `C_size`.

## Outcome under `C_size`: refuted, with a closed form

`FACT`, family `c_0 = y`, `c_{k+1} = (λz. z) c_k` — a chain of identity
applications, no duplication anywhere:

| k | `\|c_k\|` | κ `S_out` | κ `S_in` | spread |
|---:|---:|---:|---:|---:|
| 8 | 25 | 0.2400 | 1.5 | 6.25 |
| 32 | 97 | 0.0619 | 1.5 | 24.25 |
| 128 | 385 | 0.0156 | 1.5 | 96.25 |
| 512 | 1537 | 0.0039 | 1.5 | **384.25** |

`FACT`: `spread_{C_size}(c_k) = (3k + 1)/4` exactly, at every measured `k`.

`DERIVATION`: both strategies take `k` steps and reach `y`, and `peak = 3k + 1`
for both. `S_in` contracts the innermost redex, whose argument is always `y`, so
each step costs `1 + 1 = 2` and `κ → 1.5`. `S_out` contracts the head redex,
whose argument is the entire remaining chain, so step `j` costs `3j − 1`, the
total is `Θ(k²)`, and `κ = 6/(3k + 1) → 0`. Nothing is ever duplicated; the two
strategies differ only in *what they are billed for substituting*.

`H-SPREAD` is therefore false for `C_size`, and λ has no strategy-insensitivity
constant under it.

## But that refutation is an artifact of the cost model

`FACT`: on the same family under `C_dup`, which bills only the *extra* copies:

```text
κ_S_out(c_k) = κ_S_in(c_k) = 3.0   exactly, at every k
spread        = 1.00                exactly, at every k
```

`DERIVATION`: every redex in `c_k` has `occ = 1`. `C_size` charges `size(N)` for
a substitution that writes one copy and duplicates nothing; `C_dup` charges 0.
The 384× spread is the price of billing a copy no sharing implementation would
make. This is the defect the KAPPA-EXP-001 erratum found while checking
`claude-fable-002`, and here it is worth exactly two orders of magnitude.

Σ-GLYPH does not have this defect: `R-I` costs 1 and only `R-S` costs
`1 + size(z)`.

## Under `C_dup` the phenomenon survives — but the grid ran out

`FACT`: the third family nests the chain under duplication.
`g_0 = c_k`, `g_{m+1} = (λx. p x x) g_m`. Spread under `C_dup`:

| | k=2 | k=8 | k=32 |
|---|---:|---:|---:|
| n=1 | 2.44 | 2.50 | 2.50 |
| n=3 | 2.05 | 3.19 | 5.04 |
| n=5 | 3.45 | 5.23 | 5.72 |
| n=6 | 3.82 | 7.00 | **9.97** |

`FACT`: for comparison, the pure duplication family `h_n` converges under
`C_dup` to ≈2.25 by `n = 12`, and the pure chain family collapses to 1.

`DERIVATION`: `C_dup` removes the *artifact* — being billed for a copy that
duplicates nothing — but not the *phenomenon*. In `g_{n,k}` the duplication is
real (`occ = 2`) and it duplicates **unevaluated work**: `S_out` copies the
chain before reducing it and then reduces every copy, while `S_in` reduces the
chain once and duplicates the small result. `S_out`'s cost grows with `2^n · k`
while its peak grows more slowly, because leftmost-outermost finishes the left
copy before expanding the right and never holds all `2^n` copies at once. So
`κ_S_out → 0` while `κ_S_in` stays near 1.

`UNKNOWN`: whether `spread` under `C_dup` is unbounded. The measurement rises in
both parameters across the whole grid and shows no ceiling, but the
preregistration fixed `n ≤ 6`, `k ≤ 32`, and its scope clause makes any range
change a new experiment. Extending the grid is KAPPA-EXP-005.

**The preregistered reporting rule is honoured in the other direction too:**
three families lower-bound a supremum over all terms, and two strategies
lower-bound a supremum over all strategies. This design can witness
unboundedness; it can never certify boundedness. Nothing here says `H-SPREAD`
holds for `C_dup`.

## Controls

All four hold across all 40 measured terms:

- `same_normal_form` — `S_out` and `S_in` reach α-equivalent normal forms
  everywhere, so every number is a resource result and not a changed semantics;
- `no_renaming` — capture-avoiding substitution never α-renamed;
- `erratum_bound` — `κ ≤ 1 + (|t| − 1)/cost` held at every point under both
  materialization-charging models, an empirical check of the derivation the
  KAPPA-EXP-001 erratum introduced;
- `terminated` — every term normalized within the step ceiling.

`FACT`: control 4 of the preregistration — that extending the shared machine
with a third cost column changes no KAPPA-EXP-001 number — holds:
`kappa-exp-001/measure.py --check` reproduces its frozen measurements
bit-for-bit against the extended `lambda_machine.py`.

## What this does not establish

- Nothing about strategies beyond the two measured. A third strategy could
  widen any spread reported here; none can narrow it.
- Nothing about terms beyond the three families. `sup_t spread(t)` under `C_dup`
  is `UNKNOWN`, not "bounded".
- Nothing about interaction nets. Comparing λ against the schedule spread
  `sigma-glyph` EXP-004 reports would require measuring that machine under this
  definition, which this repository has not done. The comparison
  `claude-fable-002` proposes is not yet available in either direction.
- Nothing about Σ-GLYPH, whose strategy is pinned normatively (KAPPA-EXP-002).

## Consequence for Track A

`DERIVATION`: the first candidate invariant of this track — a
strategy-insensitivity constant for a calculus — does not exist for λ under
`C_size`, and the reason is a defect in `C_size` rather than a fact about λ.
Under the corrected `C_dup` the question is live and the evidence points the
same way, which would leave λ with no such constant at all.

If KAPPA-EXP-005 confirms that, the track's conclusion is sharper than the one
it set out to find: **there is no strategy-independent resource characterisation
of λ**, and a machine that wants the single-integer budget must pin its strategy
as well as its cost model — which is exactly what Book I does, and what
KAPPA-EXP-002 found it doing.

## Reproduction

```sh
tools/test-all.sh
```

`measure.py --check` recomputes all 40 terms from scratch, about two seconds,
and compares against the frozen `measurements.json`. Green execution is
reproducibility of a bounded computation. It is not review, adoption, or
external validity.
