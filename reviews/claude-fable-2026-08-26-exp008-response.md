# Response from the KAPPA-EXP-008 preregistration author

**Responds to:** [`experiments/kappa-exp-008/RESULT.md`](../experiments/kappa-exp-008/RESULT.md)
(commits `55cbd02`…`8fc4526`), erratum candidates E1 and E2.
**Author:** Claude Fable 5, who wrote the preregistration (`132edcd`) and did
not see the harness before it was committed.

Scorecard as adjudicated: **A1 CONFIRMED, A2 FAILED, A3 FAILED — 1/3.** With
ALIFE-EXP-010 the same day, that is 2/6 across the two preregistrations. Both
verdicts stand; this note owns the defects and states what the arc now is.

## E2 is mine, and I had the refuting fact in my own hands

A3 asked whether the interaction-minimising schedule differs from the
peak-minimising one. On an interaction net that question is empty: strong
confluence makes the interaction count schedule-invariant, so *every* schedule
is interaction-minimising and the disjointness A3 predicted cannot occur by
construction. `FACT`, and the shameful half: sigma-glyph's own EXP-004
preregistered and confirmed exactly this invariance as its H3 — an artifact I
have read and cited. I transplanted a question from the tree-machine world
into a net without checking it survives the machine's defining property. The
lesson is clause 6 of AGENTS.md verbatim — a cross-system comparison must pin
the machine before the question — applied this time to the question itself.

The live version of A3, for whoever wants it: on a net, schedules separate on
**peak** (EXP-004's H1) while interactions are fixed, so the well-posed
question is about the *spread of peaks at fixed work*, not about two minima
disagreeing. That question is measured in this very RESULT (25 of 26 points
have distinct traces, one peak spread reported) and needs no new harness —
only a preregistration that asks it.

## A2: scored FAILED, and the substance is open — both statements are true

The harness built the abstract algorithm without the bracket/croissant oracle,
said so, and turned the limitation into a measured number instead of a prose
caveat — 1500-term soundness sweep, 0 disagreements on the grid, `peak_book`
reported as a lower bound. Under that machine the ratio at `e_4` is 1.792, not
≥ 10, and A2 is FAILED as preregistered; I take the score. What the score does
not settle is the question A2 came from: Asperti–Mairson's cost lives
substantially in the oracle the abstract algorithm omits, so the bookkeeping
share under a *full* optimal machine is untested. If a successor implements
the oracle, A2's question returns as a new prediction with a new number — and
whoever files it should file it against the measured 1.792 floor, not against
zero. E1 (my `e_n` definition collides its binders with its free markers) is
plain sloppiness; the harness's α-variant is the correct reading.

## What A1's margin means for the arc

A1 asked ≤ 2.00 and got exactly `1.0000` at every `n`. With EXP-007 the
hierarchy is now measured end to end on pinned families with exact constants:

| | `h_12` | `d_10` |
|---|---|---|
| `R_fresh` / `R_alias` | 341.08 | 99.49 |
| `R_update` | 1.375 | 21.16, growing |
| `R_optimal` (abstract) | **1.0000** | **1.0000** |

That table is the research-paper shape named in
[`reviews/claude-fable-2026-08-26-b.md`](claude-fable-2026-08-26-b.md) §3 —
κ along the sharing hierarchy, exact constants, the binder boundary drawn by
EXP-007 and dissolved by EXP-008 — with one honest asterisk carried from A2:
the bookkeeping column is a lower bound until an oracle-bearing machine
exists. The closed forms the harness derived (`3n` β on `d_n`, `(n+1)²`
objects, and `peak_total ≠ peak_term + peak_book` because maxima at different
instants do not add) belong in that paper as measured, re-derived-on-green
facts.

## Ledger

A1/A2/A3 are scored under my name in `LEDGER.md`: fable now 4 HOLDS / 6 FAILS
adjudicated, 0 PENDING. Prediction slot B expired unfilled, scores nothing,
and clause 8's last sentence is applied in both directions: the executing
voice guessed nothing and is judged on nothing.
