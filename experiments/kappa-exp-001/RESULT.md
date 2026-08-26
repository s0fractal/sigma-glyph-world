# KAPPA-EXP-001 — result

**Status: `H-KAPPA` refuted. κ is not an invariant of the calculus.**

> **Two errata. Read both before this document.**
> [Erratum 1](#erratum-2026-08-26) — the positive replacement and the successor
> question, raised by [`talks/claude-fable-002.md`](../../talks/claude-fable-002.md).
> [Erratum 2](#erratum-2-2026-08-26--representation-and-signature) — the machine
> does not have the representation this experiment pinned, and the word
> "materialized" is not supported by it. Raised by
> [Codex's review](../../reviews/codex-2026-08-26.md), findings 1 and 4.
> The algebra over the declared metric survives both; the physical reading does
> not.

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

---

## Erratum, 2026-08-26

Raised by [`talks/claude-fable-002.md`](../../talks/claude-fable-002.md). Three
corrections. The refutation of `H-KAPPA` above is untouched by all three: it
rests entirely on `C_unit`, where the measurement is real and the separation is
341× at `n = 12`.

### 1. κ ≤ 1 under `C_size` is a theorem, not a measurement

`DERIVATION`: call a cost model **materialization-charging** if every action
satisfies `Δsize ≤ cost − 1`. `C_size` is one: for a redex `(λx.M) N`,

```text
Δsize  = (occ − 1)·size(N) − occ − 2
cost   = 1 + occ·size(N)
cost − 1 − Δsize = size(N) + occ + 2  >  0
```

Summing over `k` actions gives `size_k ≤ size_0 + cost_k − k`, hence

```text
κ = (peak − 1)/cost  ≤  1 + (size_0 − 1)/cost − steps/cost  ≤  1 + (size_0 − 1)/cost
```

For this family `size_0 = 1 + 7n` while `cost` is `Θ(2^n)`, so the bound is
`1 + o(1)`. The measured 0.236 and 0.501 are therefore **not evidence about the
family**. Boundedness under `C_size` was never in question; it follows from the
shape of the cost model for any calculus, any strategy, and any term.

The section above presented this as a finding. It is a construction. Retracted
as a finding; retained as a derivation.

### 2. The successor question was trivial. Retracted.

The stated successor — *fix a materialization-charging cost model; does a
calculus exist whose κ is unbounded under every strategy?* — is answered "no" by
the inequality in §1, in one line, for every calculus. It is not a question about
calculi. The mirror question, whether `1/κ` can be unbounded, is answered "yes"
by any family with a time–space gap in any calculus that can count. Neither
carries an invariant.

**Replacement, from `claude-fable-002`:** the quantity that is not fixed by the
cost model is the *spread* between strategies on the same term.

```text
spread(t) := max_S κ_S(t) / min_S κ_S(t)
```

Under `C_unit` the spread on `h_n` is unbounded — that is this experiment's
result, 341× at `n = 12`. Under `C_size` it is `0.501 / 0.236 ≈ 2.12`. The open
question is whether `sup_t spread(t)` is finite for λ under a fixed
materialization-charging cost model. A finite value would be a strategy-insensitivity
constant of the calculus and would make λ comparable against interaction nets,
where `sigma-glyph` EXP-004 reports a schedule spread of `2·min(grow, shrink)`.

`DERIVATION`, and a caution the replacement needs: the spread must be defined
**per term**, not across a family. Across terms, `min_S κ_S` can be driven toward
zero by any work-heavy, space-light term, so a cross-term ratio is unbounded for
trivial reasons.

`FACT`, found while checking the above: `C_size` charges `occ · size(N)`, which
bills `size(N)` even when `occ = 1` — a copy that duplicates nothing and that a
sharing implementation would never make. Σ-GLYPH does not do this: `R-I` costs 1
and only `R-S` costs `1 + size(z)`. A tighter model `C_dup`, charging
`1 + max(0, occ − 1)·size(N)`, is still materialization-charging by the same
computation. Whether λ's spread is finite may depend on which of the two is
pinned — which is this experiment's own lesson applied to its successor. Both
are measured in KAPPA-EXP-003.

### 3. The `UNKNOWN` about Σ-GLYPH is removed

`claude-fable-002` reports that the Σ-GLYPH accounting satisfies
`Δsize ≤ cost − 1` per action. This repository checked that claim directly
rather than accepting the report, against a local checkout of `s0fractal/sigma-glyph`:

`FACT`: `spec/book-1-truth.en.md` §3.4 is titled "ATP: size-priced, hash-leaf
model (MUST)" and prices `R-S` at `1 + size(z)`, `R-I` and `R-K` and `R-R` at 1,
and `force` at 1–3 by node kind.

`FACT`: `spec/appendix-a-complexity.md` §1 tabulates `Δsize` against `cost` for
every action and asserts `Δsize < cost` in every row, concluding
`s(t) − 1 ≤ spent` by induction — described there as normative in Book I §3.4.

`DERIVATION`: Σ-GLYPH's cost model is an instance of the materialization-charging
shape, and its memory bound is the tight case of §1 above with `size_0 = 1`,
since evaluation begins from a single term hash. So the main conclusion of this
result — that `size ≤ atp + 1` is a design constraint discharged by the cost
model rather than a property discovered in a calculus — is corroborated from the
specification side.

`DERIVATION`: Σ-GLYPH is stronger than `C_size` in a way worth naming precisely.
`C_size` prices only rewriting. §3.4 also prices **materialization from
storage**: forcing a thunk costs 1–3, and an unresolved hash leaf counts as size
1 regardless of what it denotes. That second half is what makes the bound hold
against terms that arrive from the network rather than from a reduction, and it
is the mechanism KAPPA-EXP-002 tests.

`UNKNOWN`: whether the reference implementation conforms to §3.4 on this family.
Nothing here executed Book I's oracle. Reading a specification is not running it.

---

## Erratum 2, 2026-08-26 — representation and signature

From [`reviews/codex-2026-08-26.md`](../../reviews/codex-2026-08-26.md),
findings 1 and 4. Both reproduced here before acting.

### Finding 1 — the "no sharing" machine shares objects

`FACT`: the preregistration pins "explicit syntax tree" with "no sharing". The
implementation does not satisfy that.
[`substitute`](lambda_machine.py) returns the *same* `value` object at every
substituted occurrence, and returns `term` itself whenever the bound name is
absent from its free variables. The executable object graph is therefore a
persistent DAG.

Reproduced:

```python
nf = normalize(family(1), "S_in", 100)["normal_form"]
assert nf.fun.arg is nf.arg      # holds
```

`FACT`, distinct reachable Python objects against the reported `size`:

| strategy | n | reported `size` | distinct objects |
|---|---:|---:|---:|
| `S_in` | 4 | 61 | 10 |
| `S_in` | 8 | 1021 | **18** |
| `S_out` | 4 | 61 | 32 |
| `S_out` | 8 | 1021 | 512 |

`DERIVATION`: `Term.size` is an **occurrence-weighted tree size** — a correct and
standard measure of a λ-term as a term — computed over an object graph that is
strictly more compact. Every number in this experiment is a correct measurement
of that metric. No number is a measurement of what the harness allocated.

**What is retracted:** every sentence in this document, in its preregistration,
and in KAPPA-EXP-003 and KAPPA-EXP-005, that reads `peak` as *materialized
state*, or describes `C_size` as charging for copies the harness makes. The
harness does not make them. The correct name for the machine is **a persistent
DAG with an occurrence-weighted tree metric**, and that is what the results are
about.

**What survives:** the algebra. Size explosion is a real property of λ-terms:
`S_in` reaches a term of tree size `4·2^n − 3` in `n` β-steps while `S_out`
spends `2^n − 1`. `H-KAPPA` is refuted **over this metric**, and that refutation
does not depend on how any implementation stores the term.

**What this makes sharper rather than weaker:** representation was already a
component of the pinned machine tuple, and this is a demonstration of that axis
rather than an escape from it. Under a DAG metric — distinct nodes rather than
occurrences — `S_in`'s peak at `n = 8` is 18, not 1021, and its κ would be
bounded. The counterexample is a counterexample for the tree metric and
dissolves under the DAG metric. KAPPA-EXP-002 is the same statement from the
other side, and its claims *are* about physical materialization: the Book I
oracle was checked at object level and produces 1021 distinct Python objects for
`size_tree = 1021` at `n = 8`, so it genuinely materializes once per occurrence.

`UNKNOWN`: what happens when logical occurrence size, distinct reachable
objects, distinct content hashes, cumulative allocations, peak live objects,
steps, and charged cost are seven separately measured quantities instead of one
cached field. That is KAPPA-EXP-006, and this experiment's numbers must not be
reused as measurements of physical materialization.

### Finding 4 — the target quantity slipped between two signatures

`FACT`: the preregistration defines `κ_M(t)` and then "`κ_M` over the family" as
`sup_n κ_M(h_n)`, while the headline says κ is not an invariant of *the
calculus*. Those are different statements, and the second does not follow from
the first.

`DERIVATION`: the correct signature is `κ(M, T) = sup_{t ∈ T} (peak_M(t) − 1) /
cost_M(t)`, and `T` must never be erased. Three readings of the claim under
attack are distinguishable:

1. equality of global suprema over all λ-terms;
2. a uniform pointwise comparison across strategies on the same term;
3. an ordering of machines on a declared workload distribution.

This experiment refutes **reading 2**, which is the natural reading of "κ is an
invariant of the calculus, not of the strategy": if κ were strategy-independent,
two strategies would agree up to a bounded factor on each term, and on `h_n`
they diverge as `Θ(2^n/n)`.

Reading 1 is **untouched**. Both global suprema may well be infinite, in which
case they are trivially equal and the h_n family says nothing about them.
Reading 3 requires a declared workload and was never attempted.

`FACT`: the headline of this document should be read as *"κ is not uniform
across strategies pointwise"*, not as *"the calculus has no κ constant"*.
