# KAPPA-EXP-001 — is κ an invariant of the calculus?

**Preregistration. Non-normative. Committed before its measurement harness
exists.** This experiment does not extend the Σ-GLYPH specification and does not
speak for it.

## Hypothesis under attack

From [`talks/claude-fable-001.md`](../talks/claude-fable-001.md), «Наукові» §1:

> кожне числення має мінімальний коефіцієнт переоцінки κ (у скільки разів
> доводиться завищити ціну кроку понад реальну роботу, щоб простір став
> наслідком часу), і κ є інваріантом числення, а не стратегії.

`H-KAPPA`: for a fixed calculus, κ is the same — up to a bounded factor — under
any evaluation strategy.

[`INTENTIONS.md`](../INTENTIONS.md) already records κ as `CONTESTED` and warns
that "paid cost / actual work" may normalize away the difference it was meant to
expose. This experiment turns that worry into a decidable measurement.

**Predicted outcome: `H-KAPPA` is false.** The refutation is preregistered
below with closed forms, so the harness can disagree with the prediction.

## The machine, pinned

Per [`AGENTS.md`](../AGENTS.md) clause 6, every component is fixed before
measurement.

- **Calculus**: untyped λ-calculus, terms `Var | Lam | App`, over free variables
  `p` and `y`. β is the only rule.
- **Representation**: explicit syntax tree. No sharing, no explicit
  substitutions, no hash-consing. `size(t)` is the node count:
  `size(Var) = 1`, `size(Lam x. M) = 1 + size(M)`,
  `size(App M N) = 1 + size(M) + size(N)`.
- **Strategies**, both deterministic and total on this family:
  - `S_out` — leftmost-outermost β (normal order);
  - `S_in` — leftmost-innermost β.
- **Cost models**, charged per contracted redex `(λx.M) N`:
  - `C_unit` — 1;
  - `C_size` — `1 + occ(x, M) · size(N)`, where `occ` counts free occurrences.
    This is the model that pays for materialized copies.

Four machines are measured: `S_out × C_unit`, `S_in × C_unit`,
`S_out × C_size`, `S_in × C_size`.

## The family

```
h_0     := y
h_{n+1} := (λx. p x x) h_n
```

`DERIVATION`: `size(h_n) = 1 + 7n`, so the input is linear in `n`. Every `h_n`
is strongly normalizing, and its normal form is the complete binary `p`-tree of
depth `n` with `y` at every leaf, of size `4·2^n − 3`.

Measured range: `n ∈ [1, 12]` for all four machines. `n = 0` is excluded because
it takes zero steps and κ would divide by zero. The upper bound is set by the
harness, not by the question: naive substitution makes `S_out` cost `Θ(4^n)`
wall-clock work in total.

## Definition of κ

For machine `M` and term `t`:

- `steps_M(t)` — number of contracted redexes to normal form;
- `cost_M(t)` — sum of per-step costs under the machine's cost model;
- `peak_M(t)` — maximum `size` over every term on the trajectory, including the
  initial term and the normal form;
- `κ_M(t) := (peak_M(t) − 1) / cost_M(t)`.

κ is the smallest constant by which the charged cost must be inflated for
`size ≤ κ · cost + 1` to hold on that trajectory — that is, for space to be a
consequence of time. `κ_M` over the family is `sup_n κ_M(h_n)`, reported as the
observed growth in `n` rather than as a limit.

## Preregistered predictions

`DERIVATION`, from the recurrences above:

| machine | `steps(h_n)` | `cost(h_n)` | `peak(h_n)` | `κ(h_n)` |
|---|---|---|---|---|
| `S_out × C_unit` | `2^n − 1` | `2^n − 1` | `4·2^n − 3` | `→ 4`, bounded |
| `S_in × C_unit` | `n` | `n` | `4·2^n − 3` | `Θ(2^n / n)`, unbounded |
| `S_out × C_size` | `2^n − 1` | `Θ(2^n)` | `4·2^n − 3` | bounded |
| `S_in × C_size` | `n` | `Θ(2^n)` | `4·2^n − 3` | bounded |

If the first two rows hold, `H-KAPPA` is refuted: one calculus, one
representation, one cost model, one input family, two strategies, and κ diverges
under one while staying constant under the other.

If rows three and four also hold, the positive replacement is that κ is a
property of the pair (strategy, cost model), and a size-aware cost model
restores boundedness for both strategies.

## Controls

`AGENTS.md` clause 6 forbids reporting a changed semantics as a resource result.
Therefore the harness must check, for every `n` in range:

1. **Same outcome.** `S_out` and `S_in` reach α-equivalent normal forms.
2. **Same input.** Both start from the identical term object.
3. **Termination.** Both reach a normal form within a preregistered step ceiling.
4. **No renaming distortion.** No capture-avoiding α-renaming is performed on
   this family, so no measurement is inflated by renaming work.
5. **Closed forms.** Observed `steps`, `cost`, and `peak` equal the predicted
   closed forms exactly, or the deviation is reported rather than smoothed.

A failure of control 1, 2, or 3 voids the comparison. A failure of control 4 or
5 is reported as a deviation and does not by itself void the refutation.

## Falsifiers of the predicted refutation

- `κ_{S_in}` under `C_unit` does not grow with `n`, or grows only by a bounded
  factor relative to `κ_{S_out}`.
- `peak` differs between strategies such that the κ ratio stays bounded.
- Either strategy fails to normalize some `h_n` in range.
- The two strategies reach non-α-equivalent normal forms, which would mean the
  comparison changed the semantics rather than the resource behavior.

## Scope and stop conditions

- One family, one calculus, twelve values of `n`. This is a **counterexample**,
  not a survey. Refuting a universal claim needs one instance; it establishes
  nothing about the value of κ for any other calculus, family, or machine.
- No claim is made about SKI, interaction nets, Turing machines, or Σ-GLYPH's
  own machine. `Book I`'s finite κ for SKI is not touched by this result.
- Nothing here bears on `H-SCOPE`, on Track B, or on the correctness of
  `size ≤ atp + 1` in its own machine.
- Any change to the calculus, representation, strategies, cost models, family,
  or `n` range after the harness first runs creates KAPPA-EXP-002 and a fresh
  measurement.
- Green execution is reproducibility of a bounded computation. It is not review,
  adoption, or external validity.
