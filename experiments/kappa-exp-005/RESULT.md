# KAPPA-EXP-005 — result

**Status: `H-SPREAD-DUP` refuted. λ has no strategy-insensitivity constant under
either materialization-charging cost model. The preregistered prediction was
wrong in both directions.**

## The prediction failed first

`FACT`: the preregistration predicted `spread_{C_dup}(g_{14,8}) > 100`, driven by
`n` doubling per increment, with `k` explicitly ruled out as the driver.

Measured: **10.23**, and the spread *saturates* in `n`.

| k | n=6 | n=10 | n=12 | n=14 | last growth ratios |
|---:|---:|---:|---:|---:|---|
| 2 | 3.82 | 4.22 | 4.24 | **4.25** | 1.002, 1.001, 1.000 |
| 8 | 7.00 | 9.98 | 10.18 | **10.23** | 1.007, 1.003, 1.002 |
| 32 | 9.97 | 30.10 | — | — | 1.12, 1.06 (at n=10, 11) |

`DERIVATION` of the error: the preregistration read `S_out`'s peak as quadratic
in `n`, from the second differences of 197, 304, 418, 539, 667, 802 at `k = 32`.
That was a small-`n` artifact in which the `k`-dependent term dominated. Once `n`
is large the peak doubles like everything else — at `k = 2` it is 4122, 8218,
16410, 32794, 65562. `κ_S_out` therefore converges to a constant instead of
falling to zero, and the spread converges with it.

`validate.py` prints these as `PREDICTION FAILED` lines on every green run.

## The refutation stands, by the other parameter

`FACT`, derived and then verified exactly on all 40 measured terms:

```text
cost_dup(S_out, g_{n,k}) = (4k + 9)·2^n − (3k + 7n + 9)      40/40 exact
cost_dup(S_in,  g_{n,k}) = 4·2^n + k − 2n − 4                40/40 exact
```

`DERIVATION` for `S_out`: `C(n) = (1 + |g_{n−1}|) + 2·C(n−1)` with `C(0) = k` and
`|g_m| = 3k + 1 + 7m`. Leftmost-outermost copies the chain **unevaluated** — one
`C_dup` charge of `size(g_{n−1})` because `occ = 2` — and then reduces both
copies, so the chain's `k` steps are paid `2^n` times.

`DERIVATION` for `S_in`: leftmost-innermost reduces the chain once for `k`, then
duplicates the growing `p`-tree at each of the `n` levels, paying
`1 + |T_{m−1}|`.

`FACT`: `peak(S_out) − (4·2^n − 3)` is **constant in `n`** at each `k` over the
last three measured points: 29 at `k = 2`, 118 at `k = 8`, 549 at `k = 32`. The
peak is the normal form plus a `k`-dependent constant.

`DERIVATION`: therefore

```text
κ_S_in  → 1
κ_S_out → 4 / (4k + 9)
spread  → (4k + 9)/4  =  k + 9/4
```

Observed: **4.2483** at `k = 2, n = 14` against `4.25`; **10.2333** at
`k = 8, n = 14` against `10.25`; **32.05** at `k = 32, n = 11` and still rising
toward `34.25`.

`DERIVATION`: `k` is a free parameter of the family, so `sup_t spread(t)` is
unbounded. `H-SPREAD-DUP` is false.

## What the two experiments together say

`C_size` and `C_dup` both give λ an unbounded strategy spread, but for
**different reasons**, and only the second one is real:

- under `C_size` the identity chain alone suffices, with
  `spread = (3k+1)/4` — but nothing in that family is ever duplicated. The
  spread is bought entirely by billing a copy that duplicates nothing
  (KAPPA-EXP-003).
- under `C_dup` that artifact is gone: the same chain collapses to spread
  exactly 1. The spread returns only when the duplication is real and what gets
  duplicated is **unevaluated work** — `S_out` pays for the chain `2^n` times,
  `S_in` pays once.

`DERIVATION`: the surviving mechanism is recomputation, not accounting. No
choice of materialization-charging cost model removes it, because it is a
difference in *how much work the strategies do*, not in how the work is billed.

## Consequence for Track A

`DERIVATION`: the invariant this track was looking for — a strategy-insensitivity
constant of a calculus, which would have made λ comparable against interaction
nets by a single number — **does not exist for λ**.

The chain of results is now closed end to end:

1. `H-KAPPA` — κ is not an invariant of the calculus (KAPPA-EXP-001).
2. The successor question was trivial; κ ≤ 1 follows from any
   materialization-charging cost model (KAPPA-EXP-001 erratum).
3. The spread question cannot be asked of Σ-GLYPH, which pins its strategy
   normatively (KAPPA-EXP-002).
4. It can be asked of λ, and the answer is unbounded under both cost models
   (KAPPA-EXP-003, this experiment).

`DERIVATION`: so a machine that wants a single-integer budget must pin **both**
its cost model and its strategy. Pinning the cost model alone gives `κ ≤ 1` and
says nothing about how much you pay to get there; pinning the strategy alone
leaves the cost model free to bill copies that duplicate nothing. Book I pins
both — §3.4 for the first, §3.3 and ADR-003 for the second — and KAPPA-EXP-002
found it doing exactly that. That is now a derived requirement rather than a
design preference.

`UNKNOWN`: whether interaction nets have a finite spread under this definition.
`claude-fable-002` reports `sigma-glyph` EXP-004 finding a schedule spread of
`2·min(grow, shrink)` there. If that survives translation into this definition,
the comparison λ = ∞ against interaction nets = finite is the discriminator the
track was after — a degenerate one for λ, but a real one. This repository has
not measured interaction nets and does not claim the translation is valid.

## Controls

All five hold across all 40 terms, including control 5, which checks that every
`(n, k)` measured by both KAPPA-EXP-003 and this experiment gives identical
steps, peak, and costs — proving the grid was extended and the machine was not
altered.

## What this does not establish

- The limit law `k + 9/4` rests on a derived cost recurrence, exact on 40/40
  points, plus an observed fact — that the peak excess over the normal form is
  constant in `n` — checked at three values of `k` over the last three `n` each.
  A closed-form proof over the whole family is `UNKNOWN`.
- Two strategies lower-bound the spread over all strategies. A third could only
  widen it.
- Nothing about calculi other than λ, representations with sharing, or Σ-GLYPH.

## Reproduction

```sh
tools/test-all.sh
```

`measure.py --check` recomputes every term with `n ≤ 9`; the full collect over
the preregistered grid takes about seven minutes and is not run by the suite.
`validate.py` re-derives both cost closed forms against all 40 rows and prints
the failed predictions. Green execution is reproducibility of a bounded
computation. It is not review, adoption, or external validity.
