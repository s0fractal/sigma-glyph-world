# KAPPA-EXP-005 — does λ's spread grow without bound under `C_dup`?

**Preregistration. Non-normative. Committed before its measurement harness
exists.**

## Why this exists

[KAPPA-EXP-003](kappa-exp-003/RESULT.md) refuted `H-SPREAD` under `C_size` and
found that refutation to be an artifact of a cost model that bills a copy which
duplicates nothing. Under the corrected `C_dup` it left the question open: the
spread on `g_{n,k}` rose across the whole grid to 9.97 at `n = 6, k = 32` with no
ceiling in sight, and its scope clause forbids extending the range in place.

This is that extension. Everything else — calculus, representation, strategies,
cost models, the `spread` definition, the reporting rule — is carried over
unchanged from KAPPA-EXP-003.

## Hypothesis

`H-SPREAD-DUP`: under `C_dup`, `sup_t spread(t)` is finite for λ.

**Predicted outcome: false, driven by `n` and not by `k`.**

## Derivation of the prediction

`DERIVATION` from KAPPA-EXP-003's *published* measurements, which are frozen and
public — this prediction is read off existing data, not off a run of this
experiment:

For `g_0 = c_k`, `g_{m+1} = (λx. p x x) g_m`:

- `S_in` reduces the chain once, then duplicates the small result. Its peak and
  its `C_dup` cost both track `4·2^n`, so `κ_S_in → 1`. Observed: 0.93 at
  `n = 6, k = 32`.
- `S_out` copies the chain unevaluated and reduces every copy. Its cost grows as
  `Θ(2^n · k)` — observed `cost_dup` at `k = 32` is 162, 429, 970, 2059, 4244,
  8621 for `n = 1…6`, a ratio approaching 2 per increment.
- `S_out`'s peak grows only **polynomially** in `n`, because leftmost-outermost
  finishes the left copy before expanding the right and never holds all `2^n`
  copies at once. Observed peak at `k = 32` is 197, 304, 418, 539, 667, 802 —
  second differences a constant 7, i.e. quadratic.

Therefore `κ_S_out = peak/cost ≈ Θ(n²/2^n) → 0` and
`spread ≈ Θ(2^n / n²)` — roughly doubling per increment of `n`.

`DERIVATION`: `k` is not the driver. At `n = 6`, `κ_S_out` fell only as
`k^{-0.45}` across `k = 2, 8, 32`, so growth in `k` is sublinear and cannot
settle the question by itself.

**Concrete preregistered prediction:** at `k = 8`, `spread_{C_dup}(g_{14,8})
> 100`.

## Ranges

Chosen so the harness finishes; the ceilings are set by wall-clock, not by the
question. `S_out` takes `≈ 2^n(k+1)` steps over terms of size `O(n²+nk)`, so the
work is `Θ(4^n)`-ish in `n`.

- **n-sweep**: `n ∈ [1, 14]` at `k ∈ {2, 8}`; `n ∈ [1, 11]` at `k = 32`.
- **k-sweep**: `k ∈ {2, 8, 32, 128}` at `n = 6`.

## Controls

Carried over from KAPPA-EXP-003 and re-checked on every measured term:

1. `same_normal_form` — `S_out` and `S_in` reach α-equivalent normal forms.
2. `no_renaming` — capture-avoiding substitution never α-renames.
3. `erratum_bound` — `κ ≤ 1 + (|t| − 1)/cost` under both materialization-charging
   models.
4. `terminated` — every term normalizes within the step ceiling.
5. **Overlap agreement** — every `(n, k)` measured by both experiments MUST give
   identical `steps`, `peak`, and every cost, proving the machine is the same
   one and the extension changed nothing.

## Falsifiers

- `spread` saturates in `n` — stops growing or levels off below the predicted
  doubling. Then `H-SPREAD-DUP` may hold and the prediction above is wrong.
- `spread(g_{14,8}) ≤ 100`.
- `κ_S_out` stops falling, or `κ_S_in` stops tracking 1.
- Control 5 fails: the two experiments are not measuring the same machine and no
  comparison between them is valid.

## Reporting rule, unchanged

Two strategies lower-bound a supremum over all strategies; a finite grid
lower-bounds a supremum over all terms. This design can **witness**
unboundedness and can never **certify** boundedness. If the spread saturates,
the result is "no growth found on this grid", not "spread is bounded".

Witnessing unboundedness also requires care: a measurement that doubles across
fourteen points is evidence of an exponential, not a proof of one. The result
will say "grows as observed, consistent with `Θ(2^n/n²)`", and a closed-form
proof over the family remains `UNKNOWN` unless one is derived and stated
separately.

## Scope

- Same two strategies, same one calculus, same one representation.
- Nothing here bears on Σ-GLYPH, whose strategy is pinned normatively, nor on
  interaction nets, which this repository has never measured.
- Any change to families, ranges, cost models, or strategies after the harness
  first runs creates KAPPA-EXP-006 and a fresh measurement.
