# KAPPA-EXP-003 — is λ's strategy spread bounded?

**Preregistration. Non-normative. Committed before its measurement harness
exists.**

## The question

From [`talks/claude-fable-002.md`](../talks/claude-fable-002.md), adopted in the
[KAPPA-EXP-001 erratum](kappa-exp-001/RESULT.md#erratum-2026-08-26):

> за фіксованої C_size, чи обмежений розкид κ між стратегіями для *всіх* сімей
> числення? … Якщо для кожної сім'ї розкид обмежений константою — ця константа і
> є першим справжнім інваріантом треку, «нечутливість до стратегії» числення.

For a term `t` and a set of strategies `S`:

```text
spread(t) := max_S κ_S(t) / min_S κ_S(t)
```

`H-SPREAD`: for λ under a fixed materialization-charging cost model,
`sup_t spread(t)` is finite.

KAPPA-EXP-002 established that this question cannot be asked of Σ-GLYPH, whose
strategy is pinned normatively. It is a question about λ.

## Why two cost models, not one

The KAPPA-EXP-001 erratum found that `C_size` charges `occ · size(N)` even when
`occ = 1` — billing a copy that duplicates nothing. Σ-GLYPH does not: `R-I`
costs 1 and only `R-S` costs `1 + size(z)`. Both models are measured:

- `C_size` — `1 + occ(x, M) · size(N)`;
- `C_dup` — `1 + max(0, occ − 1) · size(N)`, the Σ-GLYPH shape.

`DERIVATION`: both are materialization-charging, so the erratum's bound
`κ ≤ 1 + (size_0 − 1)/cost` applies to both.

```text
C_size:  cost − 1 − Δsize = size(N) + occ + 2  > 0
C_dup :  cost − 1 − Δsize = occ + 2            > 0   (and size(N) + 2 at occ = 0)
```

`C_unit` is measured alongside for continuity with KAPPA-EXP-001, where it is
already known to give unbounded spread. It is **not** materialization-charging
and is not a candidate for the invariant.

## Machine

Identical to KAPPA-EXP-001 and reusing its frozen harness
[`kappa-exp-001/lambda_machine.py`](kappa-exp-001/lambda_machine.py): untyped λ,
explicit syntax tree, no sharing, strategies `S_out` (leftmost-outermost) and
`S_in` (leftmost-innermost).

`spread` is measured over exactly these two strategies. Two points **lower-bound**
the true spread over all strategies; this experiment can therefore witness
unboundedness but can never certify boundedness.

Adding a third cost column to `lambda_machine.step_cost` must leave every
KAPPA-EXP-001 number unchanged; `kappa-exp-001/measure.py --check` is the
regression test and must stay green.

## Families

1. **`h_n`** — duplication, from KAPPA-EXP-001.
   `h_0 = y`, `h_{n+1} = (λx. p x x) h_n`. Range `n ∈ [1, 12]`.
2. **`c_k`** — identity chain. `c_0 = y`, `c_{k+1} = (λz. z) c_k`.
   Range `k ∈ {1, 2, 4, …, 512}`.
3. **`g_{n,k}`** — a chain under duplication, to test whether recomputation
   compounds. `g_{0} = c_k`, `g_{m+1} = (λx. p x x) g_m`.
   Range `n ∈ [1, 6] × k ∈ {2, 8, 32}`.

## Preregistered predictions

`DERIVATION` for `c_k`, where `|c_k| = 3k + 1` and the normal form is `y`:

| machine | steps | cost | peak | κ |
|---|---|---|---|---|
| `S_in × C_size` | `k` | `2k` | `3k + 1` | `→ 1.5` |
| `S_out × C_size` | `k` | `3k(k+1)/2 − k` | `3k + 1` | `Θ(1/k)` |
| both × `C_dup` | `k` | `k` | `3k + 1` | `→ 3` |

So `spread(c_k)` under `C_size` is `Θ(k)` — **unbounded**, refuting `H-SPREAD`
for `C_size`. Under `C_dup` it collapses to 1, because every redex in this
family has `occ = 1` and duplicates nothing.

`UNKNOWN` for `C_dup`. No prediction is offered for whether any λ family has
unbounded spread under `C_dup`. `h_n` gives ≈2.1 under `C_size` and an unmeasured
value under `C_dup`; `g_{n,k}` is included precisely because a hand derivation
suggests peak and cost scale together there, leaving spread bounded, and that
derivation may be wrong.

**Reporting rule, fixed in advance:** if no measured family exhibits growing
spread under `C_dup`, the result is *"no unbounded spread found among three
families"*, not *"spread is bounded"*. Three families lower-bound a supremum and
cannot establish it.

## Controls

1. **Same outcome.** For every measured term, `S_out` and `S_in` reach
   α-equivalent normal forms. Otherwise the comparison is void.
2. **No renaming.** Capture-avoiding substitution never α-renames on any family,
   so no measurement is inflated by renaming work.
3. **Bound.** `κ ≤ 1 + (|t| − 1)/cost` holds for `C_size` and `C_dup` at every
   measured point. A violation refutes the erratum's derivation and outranks
   everything else here.
4. **No regression.** `kappa-exp-001/measure.py --check` stays green, proving the
   shared machine was extended and not altered.
5. **Termination.** Every term normalizes within a preregistered step ceiling.

## Falsifiers

- `spread(c_k)` under `C_size` does not grow with `k`: the derivation above is
  wrong and `H-SPREAD` survives `C_size`.
- `spread` under `C_dup` grows without bound on any measured family: `H-SPREAD`
  is refuted for the Σ-GLYPH-shaped cost model too, and λ has no
  strategy-insensitivity constant.
- Control 3 fails: the erratum's bound is wrong.

## Scope

- Two strategies, three families, one calculus, one representation. No positive
  generalization is licensed by any outcome.
- Nothing here bears on interaction nets. Comparing λ against the schedule
  spread `sigma-glyph` EXP-004 reports would require measuring that machine
  under the same definition, which this repository has not done.
- Any change to the families, ranges, cost models, or strategies after the
  harness first runs creates KAPPA-EXP-005 and a fresh measurement.
