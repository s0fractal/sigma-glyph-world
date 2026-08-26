# KAPPA-EXP-008 — κ under optimal reduction: does the binder boundary dissolve, and what does the bookkeeping cost?

**Preregistration. Non-normative. Committed before its measurement harness
exists.** Predictions are attributed per [`AGENTS.md`](../AGENTS.md) clause 8;
one prediction is recorded now, and the slot for other voices stays open until
the harness first runs on any family. The result scores each by name.

## The question

[KAPPA-EXP-007](kappa-exp-007/RESULT.md) ended at a boundary: sharing
*reduction* collapses the `S_out`/`S_in` separation to exactly `11/8` where
duplication is not under a binder, and leaves it growing where it is (`d_10`:
21.16 and rising). Its own scope note says optimal reduction was not
implemented and that persistence on `d_n` "is consistent with the prior art and
is not a measurement of it".

This experiment takes the measurement. Prior art states the qualitative
outcome: Lévy defined optimality precisely because call-by-need cannot share
under a binder, and Lamping's algorithm implements it (Lamping 1990; Asperti &
Guerrini, *The Optimal Implementation of Functional Programming Languages*).
What the prior art does **not** state, and what is genuinely open:

1. the **size of the residual** — `R_update` left `11/8` on `h_n`; what
   constant, if any, does `R_optimal` leave on `d_n`?
2. the **price of the machinery** — Asperti & Mairson (POPL 1998; Inf. &
   Comp. 170(1), 2001) prove worst-case bookkeeping is not elementary
   recursive, but that is a worst case over all terms; on *these pinned
   families* the bookkeeping share has never been a measured number.
3. whether "optimal" is itself **one word for two quantities** — minimal
   family steps and minimal materialization — the same event that
   KAPPA-EXP-006 measured for the word "sharing".

`H-OPTIMAL`: on a machine that shares redex families, the schedule-to-schedule
separation of κ is bounded on every family, including under a binder — and the
cost moves into bookkeeping nodes rather than disappearing.

## The fourth representation

Added to the three of KAPPA-EXP-007:

- **`R_optimal`** — sharing-graph reduction in the Lamping / lambdascope class
  (van Oostrom, van de Looij & Zwitserlood's lambdascope is acceptable and
  simpler; the choice is the implementor's and is recorded in the result).
  Fan/scope/bracket nodes implement sharing of redex families, so one
  contraction can serve occurrences that sit under different binders.

`R_fresh`, `R_alias`, `R_update` are carried over unchanged and must reproduce
KAPPA-EXP-007's frozen numbers exactly.

**Strategy becomes schedule.** On a sharing graph the `S_out`/`S_in`
distinction is not directly expressible; what varies is which active pair
fires first. Two deterministic schedules, fixed now:

- **`SCH-root`** — the active pair at minimal node-distance from the root;
  ties broken by lowest node id.
- **`SCH-leaf`** — the active pair at maximal node-distance from the root;
  same tie-break.

κ and the separation are computed between schedules, playing the role the two
strategies played in 001–007.

## The fifth quantity

KAPPA-EXP-006 separated four quantities. `R_optimal` forces a fifth:

- **term nodes** — λ, application, variable;
- **bookkeeping nodes** — fans, scope delimiters, brackets/croissants —
  everything the sharing machinery adds.

Every measurement records `peak_term`, `peak_book`, `peak_total = peak_term +
peak_book`, `interactions` (all rule firings) and `beta_interactions` (family
contractions) separately. κ is reported in two forms: `κ_total = (peak_total −
1)/interactions` and `κ_term = (peak_term − 1)/beta_interactions`. Conflating
these five is the defect this experiment exists to avoid.

## Three families

1. **`h_n`** — duplication not under a binder, verbatim from KAPPA-EXP-001.
   Range `n ∈ [1, 12]`. Control family: everything here is already collapsed
   by `R_update`, so `R_optimal` must not do worse.
2. **`d_n`** — duplication under a binder, verbatim from KAPPA-EXP-007.
   Range `n ∈ [1, 10]`. The family the boundary was drawn on.
3. **`e_n`** — Church-numeral self-application, the classical family where
   sharing under binders is the whole game:
   ```text
   c2  = λs. λz. s (s z)
   e_1 = c2
   e_{n+1} = e_n c2
   ```
   measured as `e_n s z` reduced to normal form with `s`, `z` free markers.
   Range `n ∈ [1, 4]` — `e_4` normalizes to a term of order `2^16` marker
   applications and is expected to saturate caps; saturation is a data point,
   never silently dropped.

## Prediction A — attributed to Claude Fable 5, from [`reviews/claude-fable-2026-08-26-b.md`](../reviews/claude-fable-2026-08-26-b.md)

- **A1 (the boundary dissolves).** On `d_n` under `R_optimal`, the
  schedule-to-schedule separation of `κ_total` is ≤ 2.00 at every `n ≥ 6`,
  with last-three growth ratios ≤ 1.02 — bounded, against `R_update`'s 21.16
  and growing.
- **A2 (the cost moves, it does not vanish).** On `e_n`, `peak_book /
  peak_term ≥ 10` at the top measured point and increases at every step of
  `n`. On `h_n` the same ratio stays ≤ 2 at every `n`. This is an empirical
  claim about these families; it is **not** the Asperti–Mairson theorem and
  must not be reported as confirming it — their result is a worst case this
  grid does not reach.
- **A3 (optimality is two quantities).** At no fewer than half of the grid
  points with `n ≥ 6`, pooled across families, the schedule that minimizes
  `interactions` is not the schedule that minimizes `peak_total`. If the two
  minima coincide everywhere, A3 fails.

## Prediction B — open

Reserved for any other voice, filed as a dated addendum to this document
before the harness first runs on any family. An addendum after that point
scores nothing, per clause 8.

## Acceptance gates — the machine is not `R_optimal` until all pass

- **G1, readback.** The normal form read back from the graph is α-equivalent
  to the `R_fresh` reference normal form at **every** grid point measured. A
  single disagreement invalidates the machine, not the grid point.
- **G2, sharing sanity.** `beta_interactions ≤ min(steps_{S_out},
  steps_{S_in} on R_fresh)` at every point, and on `h_n`,
  `beta_interactions = n` exactly — KAPPA-EXP-007 measured `steps = n` for
  both strategies under `R_update`, and a family-sharing machine cannot need
  more contractions than levels.
- **G3, census.** Every node is classified term or bookkeeping, exclusively;
  `peak_term ≤ peak_total` everywhere; allocations and frees are counted per
  class and reconcile with the peak, as in KAPPA-EXP-006's allocation
  control.
- **G4, reproduction.** `R_fresh`, `R_alias`, `R_update` reproduce
  KAPPA-EXP-007's frozen numbers exactly.
- **G5, determinism.** Each schedule, run twice, produces identical traces.
- **G6, caps.** Interaction cap 500,000 and node cap 200,000 per run;
  saturated cells are reported as saturated in every table they would enter.

If G1 or G2 cannot be made to pass on the full ranges, the ranges shrink and
the shrinkage is stated in the result; the gates do not.

## Falsifiers

- `d_n` separation under `R_optimal` grows with `n` past the A1 thresholds →
  A1 fails, and the binder boundary survives even optimal sharing — which
  would contradict the prior art's qualitative claim and most likely means G1
  or G2 is hiding a defect; the result must treat it as a machine bug first
  and a finding only if the gates demonstrably hold.
- `peak_book / peak_term` stays ≤ 2 on `e_n` → A2 fails; the bookkeeping cost
  on these families is a constant factor and the "fifth quantity" adds
  nothing here.
- The interaction-minimizing schedule is the peak-minimizing schedule at
  every grid point → A3 fails; "optimal" is one quantity on these families
  after all.

## Scope

- Three families, four representations, two schedules, one calculus.
- No claim about Lévy-optimality as a formal property is made or tested; G1
  and G2 are the operational certificate that the machine is in the sharing
  class, nothing more.
- Worst-case complexity of optimal reduction is prior art (Asperti–Mairson),
  not a target.
- Any change to families, ranges, schedules, node classification, or measured
  quantities after the harness first runs creates KAPPA-EXP-009.
