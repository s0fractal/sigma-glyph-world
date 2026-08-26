# KAPPA-EXP-008 — result

**Status: `H-OPTIMAL` splits. Its first half holds and is stronger than
predicted — on a sharing graph the schedule-to-schedule separation of κ is
exactly `1.0000` on `d_n`, so the binder boundary
[KAPPA-EXP-007](../kappa-exp-007/RESULT.md) drew does dissolve. Its second half
fails on these families: the cost does not move into bookkeeping by anything
like the factor predicted.**

**Scorecard: Claude Fable 5 1/3. Prediction slot B was never filled and scores
nothing.**

## Outcome

`FACT`: schedule-to-schedule separation of κ at the top of each range, under
`C_unit`, across the four representations. The first three columns are
KAPPA-EXP-007's frozen numbers, reproduced by reusing its harness (gate G4);
the fourth is new.

| family | duplication | `R_fresh` | `R_alias` | `R_update` | `R_optimal` |
|---|---|---:|---:|---:|---:|
| `h_12` | not under a binder | 341.08 | 341.08 | 1.375 | **1.0000** |
| `d_10` | under a binder | 99.49 | 99.49 | 21.16, growing | **1.0000** |
| `e_3` | Church self-application | 1.61 | 1.61 | 1.49 | **1.2609** |

`FACT`, closed forms on `h_n` under `R_optimal`, exact at every `n ∈ [1, 12]`
and identical for both schedules — `validate.py` re-derives them on every green
run and fails if any point departs:

```text
beta_interactions = n
interactions      = n + 1
peak_term         = 5n + 2
peak_book         = n
peak_total        = 6n + 2
κ_total           = (6n + 1)/(n + 1)      → 6
κ_term            = (5n + 1)/n            → 5
separation        = 1 exactly
```

`FACT`, closed forms on `d_n`, exact at every `n ∈ [1, 10]`:

```text
beta_interactions = 3n
interactions      = (n² + 9n + 2)/2
peak_term         = 10n + 3
peak_book         = (n + 1)²             under SCH-root
                  = (n + 1)² − 1         under SCH-leaf, n ≥ 2
peak_total        = n² + 7n + 8          both schedules, n ≥ 4
κ_total           = 2(n² + 7n + 7)/(n² + 9n + 2)  → 2
separation        = 1 exactly
```

`DERIVATION`: `peak_total ≠ peak_term + peak_book`. On `d_10` the term peak is
103 and the bookkeeping peak is 121, but the largest the graph ever gets is 178,
not 224 — the two classes peak at different moments. Reporting `peak_total` as a
sum of the two maxima would have overstated it by 26%. This is the same class of
error KAPPA-EXP-006 found in "sharing" and KAPPA-EXP-007 in "the separation":
a name standing in for two quantities.

`DERIVATION`: the residual `11/8` that `R_update` left on `h_n` is gone. Under
`R_optimal` the two schedules do not merely take the same number of steps, they
reach the same peak: `separation = 1` exactly, at every `n`, on both `h_n` and
`d_n`. KAPPA-EXP-007's `11/8` was the price of expanding a context before
reducing inside it; a sharing graph never expands the context, because the
readback rather than the reduction materialises the normal form.

`FACT`: on `h_12` the whole normalisation is 13 interactions, 12 of them β,
against `R_fresh`'s 4095 steps. On `e_4` it is 121 interactions, 25 of them β,
and the readback is `s^65536 z` — `2^16` marker applications from a graph whose
peak is 52 nodes.

## Scorecard

Predictions are attributed and scored by name per [`AGENTS.md`](../../AGENTS.md)
clause 8. `validate.py` prints all four lines on every green run.

**Prediction A — Claude Fable 5, [`reviews/claude-fable-2026-08-26-b.md`](../../reviews/claude-fable-2026-08-26-b.md): 1/3**

| | claim | outcome |
|---|---|---|
| A1 | on `d_n`, separation of `κ_total` ≤ 2.00 at every `n ≥ 6`, last-three growth ratios ≤ 1.02 | **CONFIRMED**, and by more than the margin asked: the separation is `1.0000` at every `n`, growth ratios `1.0000` |
| A2 | on `e_n`, `peak_book/peak_term ≥ 10` at the top measured point and rising at every step; ≤ 2 on `h_n` | **FAILED** on the first clause: the ratio is `1.792` at `e_4`, not ≥ 10. The other two clauses hold — it rises `0.11 → 0.50 → 0.74 → 1.79`, and on `h_n` it never exceeds `0.194` |
| A3 | at ≥ half the pooled grid points with `n ≥ 6`, the interaction-minimising schedule is not the peak-minimising schedule | **FAILED**: 0 of 12. See the erratum candidate below — on an interaction net this prediction cannot be confirmed by construction |

**Prediction B — open slot, unfilled.** The preregistration has exactly one
commit (`132edcd`) and carries no dated addendum, so no second voice
preregistered on this measurement before the harness first ran. It scores
nothing. Per clause 8's last sentence, nothing is inferred from that, in either
direction, about any voice.

`FACT`: A1 is the sharpest confirmation in this arc so far, and it was the
claim the prior art already implied. A2 and A3 were the two open questions the
preregistration said were *not* derivable from the textbook, and both failed —
one quantitatively, one structurally.

## The erratum candidates

Two defects were found in the preregistration itself. Per the standing rule they
are recorded here and were **not** silently fixed; the preregistration is
unedited.

`KAPPA-EXP-008-E1` — **`e_n` as written cannot be run on the carried-over
machines.** The preregistration defines `c2 = λs. λz. s (s z)` and measures
`e_n s z` "with `s`, `z` free markers". The bound names and the free markers are
the same two names. `R_fresh`, `R_alias` and `R_update` all substitute without
α-renaming and *refuse* on a capture — that refusal is KAPPA-EXP-006's
`no_renaming` control — so the literal term raises before the first measurement
and the reference normal form G1 needs cannot be produced at all. The harness
uses the α-equivalent form with a distinct binder pair per copy of `c2`
(`λs_i. λz_i. s_i (s_i z_i)`). Steps, peaks, costs and normal forms are
α-invariant, so nothing measured changes; what changes is that the family is
runnable. See [`families.py`](families.py).

`KAPPA-EXP-008-E2` — **A3 is unfalsifiable on the machine the preregistration
asked for.** A3 asks whether the schedule minimising `interactions` differs from
the schedule minimising `peak_total`. `FACT`: the interaction count is identical
between `SCH-root` and `SCH-leaf` at all 26 measured grid points, while the two
schedules take genuinely different routes (25 of 26 points have distinct
traces). `DERIVATION`: this is not an accident of these families. Interaction
nets are strongly confluent — every reduction to normal form has the same
length — so on *any* interaction net the set of interaction-minimising schedules
is *every* schedule, and it can never be disjoint from the set of
peak-minimising ones. A3 as preregistered can only fail. The question it was
reaching for is real and survives: it should be posed between `beta_interactions`
and `peak_total`, or between `interactions` and `peak_total` on a machine that is
not an interaction net. That reformulation is KAPPA-EXP-009's, not this one's.

## What was implemented, and what it is not

`FACT`: `R_optimal` is a **sharing graph in the Lamping class with labelled
fans and no bracket/croissant oracle** — Lamping's algorithm minus its control
machinery, sometimes called the abstract algorithm. It is not lambdascope and it
is not full Lamping. The preregistration permitted either of those and left the
choice to the implementor; this is a third thing, and saying so is the point of
this section.

`FACT`: the reason is provenance, not preference. The session had no network
access to van Oostrom, van de Looij & Zwitserlood or to Asperti & Guerrini, and
the index arithmetic of the delimiter and bracket/croissant rules is exactly the
part that cannot be reconstructed from memory with the confidence a fail-closed
gate requires. Two candidate disciplines were built and rejected against the
harness rather than against an argument:

- one label per binder, shared across a fan tree — rejected, it lets two fans
  from the same tree annihilate and the machine returns wrong normal forms;
- branch-indexed labels, where a fan split by another duplication carries which
  branch it went into — rejected, duals that are swept unequally then never
  annihilate and reduction does not terminate on `(λx. x x) (λy. y (y p))`.

`FACT`, and this is the measured statement of the limitation rather than a prose
caveat: [`soundness.py`](soundness.py) normalises 1500 pseudo-random λ-terms on
both schedules and compares each to the `R_fresh` reference normal form.
`R_optimal` disagrees on **1 of 1500** (0.07%), and on **none** of the gated grid
points. The smallest counterexample found by hand is

```text
(λx. x x) (λy. y (y p))
```

on which the readback does not terminate: two non-dual fans annihilate and leave
a fan wired to its own auxiliary port. `soundness.py --check` re-runs that
counterexample on every green run and fails if it ever stops disagreeing, so the
scope note cannot go stale.

`DERIVATION`: therefore `peak_book` and `interactions` reported here are **lower
bounds** on what a full Lamping or lambdascope reducer would spend on the same
families. A2's failure is measured on this machine and is not a refutation of
A2's substance: the brackets and croissants whose growth A2 was predicting are
precisely the nodes this machine does not have. The honest reading is that A2 is
**untested** by this harness and scored FAILED on what was actually run. It
should be re-run against a full oracle before anyone concludes anything about
the bookkeeping share of optimal reduction. Nothing here bears on
Asperti–Mairson, whose result is a worst case this grid does not approach, and
the preregistration was right to say so in advance.

## The gates

All six pass. `validate.py` exits non-zero and prints no scorecard if any fails.

- **G1, readback** — the normal form read back from the graph is α-equivalent to
  the `R_fresh` reference at every gated grid point, both schedules.
- **G2, sharing sanity** — `beta_interactions ≤ min(steps_{S_out}, steps_{S_in})`
  on `R_fresh` at every gated point, and exactly `n` on `h_n`. The margin is
  large: 12 against 4095 on `h_12`, 30 against 3069 on `d_10`.
- **G3, census** — every node is term or bookkeeping, exclusively; peaks order
  correctly and allocations minus frees reconcile with the live count per class.
- **G4, reproduction** — `R_fresh`, `R_alias` and `R_update` reproduce
  KAPPA-EXP-007's frozen numbers exactly. They are not re-implemented:
  [`measure.py`](measure.py) imports KAPPA-EXP-007's own `tree_run` and
  `graph_run` and calls them, so the gate is satisfied by reuse.
- **G5, determinism** — every schedule is run twice at every point and the
  SHA-256 trace digests agree.
- **G6, caps** — 500,000 interactions and 200,000 nodes. Nothing saturated:
  the largest run on the grid is `e_4` at 121 interactions and a peak of 54.

### The range shrinkage, stated

`FACT`: the preregistered range `e ∈ [1, 4]` is **shrunk to `e ∈ [1, 3]` for the
gates**. G1 is defined against the `R_fresh` reference normal form, and `R_fresh`
is a copying tree machine whose normal form for `e_4` has 131073 occurrences; it
does not produce one within any usable budget, so there is nothing to compare
against. `e_4` is measured and reported throughout, marked `gated: false` in
[`measurements.json`](measurements.json) and excluded from G1 and G2. The gates
were not weakened to accommodate it.

`FACT`, offered as an observation rather than as a gate: the `e_4` readback is
`s^65536 z`, and `65536 = 2^16 = 2^(2^(2^2))` is the value `e_4` denotes.

## Controls

- `interaction_count_is_schedule_invariant` — identical at all 26 points, while
  25 of 26 have distinct traces. Printed on every green run; it is what makes
  E2 a structural claim rather than an observation about three families.
- `soundness_sweep` — 1 disagreement in 1500 random terms, 0 on the grid, with
  the named counterexample re-checked on every run.
- `closed_forms` — the `h_n` and `d_n` forms above are re-derived and asserted at
  every `n`, both schedules.
- `census_reconciles`, `determinism`, `reproduces_kappa_exp_007` — G3, G5, G4.

## What this does not establish

- Three families, four representations, two schedules, one calculus.
- No claim about Lévy-optimality as a formal property. G1 and G2 are an
  operational certificate that this machine is in the sharing class on this
  grid, and the soundness sweep is the measured boundary of that certificate.
- Nothing about the bookkeeping cost of a *full* Lamping or lambdascope
  reducer, which is not what was built. See A2 above.
- Nothing about worst-case complexity. Asperti–Mairson is prior art and a worst
  case over all terms; three pinned families are not a probe of it.
- Nothing about Σ-GLYPH's own machine beyond what
  [KAPPA-EXP-002](../kappa-exp-002/RESULT.md) measured.
- Green execution is reproducibility of a bounded procedure. It is not review,
  adoption, external validity, or normative authority.

## Reproduction

```sh
tools/test-all.sh
```

`measure.py --check` recomputes `n ≤ 5` on all three families and all four
machines; `soundness.py --check` replays the counterexample; `validate.py`
prints the gates, the two controls and the scorecard. The full collect takes
about thirty seconds.
