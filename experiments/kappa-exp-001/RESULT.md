# KAPPA-EXP-001 — result

**Status: `H-KAPPA` refuted. κ is not an invariant of the calculus.**

The claim under attack, from [`talks/claude-fable-001.md`](../../talks/claude-fable-001.md)
«Наукові» §1, is that the minimal overcharge factor κ — how far the charged cost
must exceed real work for space to become a consequence of time — is a property
of a calculus rather than of an evaluation strategy.

One calculus, one representation, one cost model, one input family, two
strategies: κ diverges under one and is constant under the other.

## Outcome

`FACT`, from [`measurements.json`](measurements.json), family
`h_0 = y`, `h_{n+1} = (λx. p x x) h_n`, explicit syntax tree, no sharing:

| n | `\|h_n\|` | `S_out` steps | `S_in` steps | peak | κ `S_out` | κ `S_in` |
|---:|---:|---:|---:|---:|---:|---:|
| 4 | 29 | 15 | 4 | 61–69 | 4.53 | 15.0 |
| 6 | 43 | 63 | 6 | 253–261 | 4.13 | 42.0 |
| 8 | 57 | 255 | 8 | 1021–1029 | 4.03 | 127.5 |
| 10 | 71 | 1023 | 10 | 4093–4101 | 4.01 | 409.2 |
| 12 | 85 | 4095 | 12 | 16381–16389 | 4.00 | **1365.0** |

κ here is `(peak − 1) / cost` under `C_unit`, one unit per contracted redex.

`FACT`: at the top of the preregistered range the two strategies are separated
by a factor of **341**, and `κ_{S_in}` grows by ≈1.83× per increment of `n`
while `κ_{S_out}` converges to exactly 4.

`DERIVATION`: `κ_{S_in}(h_n) = (4·2^n − 4)/n`, which is unbounded;
`κ_{S_out}(h_n) → 4`, which is not. Both strategies reach the same normal form
of size `4·2^n − 3`. The innermost strategy pays `n` units for it; the outermost
strategy pays `2^n − 1`. Peak is the same to within an additive constant. The
entire separation comes from the denominator.

This is the size-explosion phenomenon used as a discriminator rather than as an
obstacle: `n` β-steps can materialize `Θ(2^n)` nodes, and whether they do is a
property of the reduction order, not of the calculus.

## Controls

`AGENTS.md` clause 6 forbids reporting a changed semantics as a resource
result. All four preregistered controls hold for every `n` in range:

- `same_normal_form` — `S_out` and `S_in` reach α-equivalent normal forms,
  checked by de Bruijn encoding. The comparison is about resources, not meaning.
- `same_input` — both strategies start from the identical term object.
- `terminated` — both normalize within the step ceiling.
- `no_renaming` — capture-avoiding substitution never needed to α-rename on this
  family, so no measurement is inflated by renaming work. This is enforced as an
  exception, not a counter, so a violation cannot be missed.

## Deviation from the preregistered closed forms

`FACT`: `steps`, input size, and normal-form size matched the preregistered
closed forms exactly at every `n`. `peak` did not.

The preregistration predicted `peak = 4·2^n − 3`, the normal-form size. Observed:

- `S_in`, `n ≥ 3`: exactly `4·2^n − 3`, as predicted;
- `S_out`, `n ≥ 3`: `4·2^n + 5`, an additive excess of 8 at every `n`, because
  an intermediate term holds a partially expanded `p`-tree whose leaves still
  carry unreduced `h_k` larger than their own normal forms;
- both strategies, `n ≤ 2`: the input term `1 + 7n` dominates, since `h_n` is
  larger than its normal form until `n = 3`.

`DERIVATION`: the deviation is additive and constant. It changes no asymptotic
and no conclusion. It is recorded because control 5 requires reporting a missed
closed form rather than smoothing it.

`validate.py` prints these as `DEVIATION` lines on every green run rather than
hiding them.

## The positive replacement

`FACT`: the same two trajectories, charged under `C_size`
(`1 + occ(x, M) · size(N)` per redex, i.e. paying for materialized copies):

| n | κ `S_out` | κ `S_in` |
|---:|---:|---:|
| 4 | 0.342 | 0.600 |
| 8 | 0.243 | 0.510 |
| 12 | 0.236 | 0.501 |

`DERIVATION`: both converge — `S_out` to ≈0.236, `S_in` to 0.5 — and both sit
**below 1**. Under a cost model that charges for materialization, no overcharge
is required at all on this family: `size ≤ cost + 1` holds directly, for either
strategy.

`DERIVATION`: therefore κ is a property of the pair (strategy, cost model), and
the strategy-dependence disappears exactly when the cost model stops being blind
to how much material a step creates.

This is the useful half of the result. The invariant `size ≤ atp + 1` is not a
property discovered in a calculus; on this family it is a **design constraint
satisfied by choosing a cost model that pays for materialization**. A machine
whose cost model charges one unit per step regardless of duplication cannot have
a bounded κ under every strategy, whatever its calculus.

`UNKNOWN`: whether the Σ-GLYPH cost model has the `C_size` shape. This
repository did not inspect it, and this experiment does not speak for it.

## What this does not establish

- Nothing about the value of κ for SKI. `Book I`'s finite κ there is untouched;
  a counterexample in λ says nothing about a different calculus.
- Nothing about interaction nets, Turing machines, or any machine not measured.
- Nothing about `H-SCOPE`, Track B, or the correctness of `size ≤ atp + 1` in
  the machine where it was proved.
- Nothing about strategies other than the two measured, or families other than
  the one measured. This is a counterexample to a universal claim. Refuting a
  universal needs one instance and licenses no positive generalization.
- No claim that `S_in` is a bad strategy. It reaches the same normal form in
  `n` steps rather than `2^n − 1`; it is *faster*. That is the point: the
  strategy that does less work materializes the same state, so a unit cost model
  cannot bound its space.

## Consequence for Track A

[`INTENTIONS.md`](../../INTENTIONS.md) records κ as `CONTESTED` and warns that
"paid cost / actual work" may normalize away the difference it was meant to
expose. That worry is now resolved in a specific direction: the ratio does not
normalize the difference away, but it is not a property of the calculus either,
so "the κ of a calculus" is not a well-formed quantity to compare across
machines.

`HYPOTHESIS` for a successor, which this result makes askable and did not test:

> Fix a cost model that charges for materialization. Does there exist a calculus
> whose κ is unbounded under **every** strategy?

That question is about calculi, is closed under the machine tuple `AGENTS.md`
requires, and would be the first genuine invariant in this track. A negative
answer would say the single-integer budget is always achievable given the right
accounting; a positive answer would identify a calculus that resists it.

## Reproduction

```sh
tools/test-all.sh
```

`measure.py --check` recomputes every trajectory from scratch and compares
against the frozen `measurements.json`; it takes about two seconds.
`validate.py` checks the preregistered closed forms, the refutation criterion,
and the boundedness of κ under `C_size`. Green execution is reproducibility of a
bounded computation. It is not review, adoption, or external validity.
