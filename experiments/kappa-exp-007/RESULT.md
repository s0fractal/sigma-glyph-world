# KAPPA-EXP-007 — result

**Status: `H-UPDATE` holds for duplication that is not under a binder and fails
under one. The class boundary is the binder, exactly as
[`claude-fable-2026-08-26`](../../reviews/claude-fable-2026-08-26.md) predicted.**

**Scorecard: claude-fable 2/2, this repository 2/3.**

## Outcome

`FACT`: separation of `κ = (peak − 1)/cost` between `S_out` and `S_in`, under
`C_unit`, at the top of each range:

| family | duplication | `R_fresh` | `R_alias` | `R_update` |
|---|---|---:|---:|---:|
| `h_12` | not under a binder | 341.08 | 341.08 | **1.375** |
| `d_10` | under a binder | 99.49 | 99.49 | **21.16**, still growing |

`FACT`, closed forms on `h_n` under `R_update`, exact at every `n`:

```text
steps            = n                      for both strategies
peak S_in        = 4·2^n − 3
peak S_out       = 11·2^(n−1) − 3
distinct objects = 7n + 1                 for both strategies
separation       → 11/8 = 1.375
```

`DERIVATION`: sharing reduction removes the **step** difference completely — both
strategies take exactly `n` — and collapses materialization from `Θ(2^n)` to
`7n + 1`. What it does not remove is a **bounded residual**: leftmost-outermost
expands the `p`-spine above the shared node before contracting it, so its peak is
`11·2^(n−1)` against `8·2^(n−1)`. Graph reduction turns an unbounded separation
into exactly `11/8`.

`DERIVATION`: under a binder it does not even do that. In `d_n` the two calls
`x w` and `x (q w)` share the *function* node but have different arguments, so
one contraction cannot serve both, and the separation returns — attenuated by
4.70× at `n = 10` but growing at roughly the same rate as on `R_fresh`.

## Scorecard

Both predictions were preregistered separately and attributed, per
[`AGENTS.md`](../../AGENTS.md) clause 8, which this experiment is the first to
exercise. `validate.py` prints all five lines on every green run.

**Prediction A — `reviews/claude-fable-2026-08-26.md`: 2/2**

| | claim | outcome |
|---|---|---|
| A.1 | on `h_n` the separation disappears under `R_update` (Wadsworth 1971) | **CONFIRMED** — 341.08 → 1.375 |
| A.2 | under a λ-abstraction it returns, because updating a thunk does not help when the copies are instantiated differently (Lévy) | **CONFIRMED** — 21.16 at `n = 10`, growing |

**Prediction B — this repository: 2/3**

| | claim | outcome |
|---|---|---|
| B.1 | the separation is **exactly 1.00** because both strategies traverse identical trajectories | **FAILED** — 1.3751 by occurrence, and the trajectories are not identical: peaks 22525 against 16381. Exactly 1.00 holds only by the objects metric, which the prediction did not name |
| B.2 | `distinct_objects` is `Θ(n)` for both strategies | **CONFIRMED** — exactly `7n + 1` |
| B.3 | on `d_n` the separation returns **attenuated**, strictly below `R_fresh` at every `n ≥ 4` | **CONFIRMED** — 99.49 → 21.16, an attenuation of 4.70× |

`FACT`: B.1 failed in the same way KAPPA-EXP-006 was wrong — by naming a
quantity without naming its metric. The number 1.00 was right for materialized
objects and wrong for occurrence size, and the stated *reason* was wrong for
both.

`DERIVATION`: this round the prose voice went 2/2 and the executing voice 2/3.
Both were preregistered, both were scored, and the difference showed up in the
harness rather than in an argument. That is the mechanism
[the response document](../../reviews/response-to-claude-fable-2026-08-26.md)
proposed, working — it argued that the calibration is about preregistration
rather than about which voice runs the oracle, and one round in which the
non-executing voice scores higher is exactly what that claim predicts is
possible.

## What neither prediction anticipated

`FACT`: the residual `11/8`. Prediction A said the separation disappears;
prediction B said it becomes exactly 1. It becomes a constant strictly between
them, and that constant is stable to four decimal places from `n = 8` onward.

`DERIVATION`: full sharing of reduction equalises *work* between strategies and
does not equalise *space*. The remaining gap is the cost of expanding a context
before reducing what sits inside it, which no amount of node sharing addresses
because the expanded context is not a duplicate of anything.

## The class boundary, restated

`DERIVATION`, replacing KAPPA-EXP-006's formulation:

- `H-KAPPA` — unbounded strategy separation — holds for machines that do **not
  share reduction**, whatever their storage does. That class contains the
  Σ-GLYPH Book I reference implementation, checked at object level in
  [KAPPA-EXP-002](../kappa-exp-002/RESULT.md#checked-at-object-level).
- On machines that **do** share reduction, it survives only where the
  duplication sits **under a binder**, because sharing a node cannot share a
  redex whose argument differs at each instantiation.
- So the boundary is *"does not share reduction under a binder"*, which is what
  the review proposed and what the prior art says: Wadsworth 1971 for the first
  half, Lévy's non-optimality of call-by-need for the second. Removing the
  second half is what Lamping's optimal reduction is for; Asperti and Guerrini's
  book is the standing treatment.

`FACT`: optimal reduction is **not** implemented here. That the separation
persists on `d_n` is consistent with the prior art and is not a measurement of
it.

## Controls

All six hold across all 22 measured terms:

- `reproduces_kappa_exp_006` — `R_alias` and `R_fresh` reproduce KAPPA-EXP-006's
  frozen steps, three peaks, two costs and allocations on `h_n` exactly;
- `update_actually_updates` — at least one contraction on `h_n` removes more than
  one **occurrence**-redex, so reduction is genuinely shared. The first version
  of this control counted redexes by object identity and always read zero, which
  made sharing invisible by construction; that was a defect in the control, not
  in the machine, and it was found and fixed before the measurement;
- `same_normal_form` — all six machines agree on both families;
- `no_renaming`, `metric_ordering`, `root_identity_preserved` — the last
  asserting that `R_update` mutates the root rather than replacing it, so
  in-place update is what was measured.

## What this does not establish

- Two families, three representations, two strategies, one calculus.
- `d_n` is one family with duplication under a binder. It witnesses that the
  separation can survive there; it does not characterise when it must.
- Nothing about optimal reduction, which was not built.
- Nothing about Σ-GLYPH's own machine beyond what KAPPA-EXP-002 measured.

## Reproduction

```sh
tools/test-all.sh
```

`measure.py --check` recomputes `n ≤ 6` on all six machines. The full collect
takes about thirty seconds.
