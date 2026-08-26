# KAPPA-EXP-005 — result

**Status: `H-SPREAD-DUP` refuted over the occurrence-weighted metric. The
preregistered prediction was wrong in both directions.**

> **See the [erratum](#erratum-2026-08-26) before reading §"Consequence for
> Track A".** [Codex's review](../../reviews/codex-2026-08-26.md) found the
> asymptotic claim rested on three tail observations rather than a derivation,
> and the Track A conclusion over-generalised. The first is now supplied as a
> derivation in [`theorem.py`](theorem.py); the second is retracted and
> replaced.

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

---

## Erratum, 2026-08-26

From [`reviews/codex-2026-08-26.md`](../../reviews/codex-2026-08-26.md),
findings 2 and 3. One is answered by supplying what was missing; one is a
retraction.

### Finding 2 — the peak asymptotics were inferred, not derived. Now derived.

`FACT`: the review is right about what the validator did. It proved the two
cost formulae on 40 rows, then checked that the peak excess was *equal on the
last three `n` per `k`* and printed `refuted`. Three equal tail observations do
not establish an all-`n`, all-`k` limit, and `spread` contains both strategies'
peaks, so exact cost recurrences alone are insufficient.

`DERIVATION`, now supplied in [`theorem.py`](theorem.py), from the structure of
the two trajectories rather than from the tail:

```text
peak_out(n,k) = 3 + peak_out(n-1,k) + max(|g_{n-1}|, |T_{n-1}|),  peak_out(0,k) = |c_k|
peak_in (n,k) = max(|g_n|, |T_n|)
cost_out(n,k) = (4k + 9)·2^n − (3k + 7n + 9)
cost_in (n,k) = 4·2^n + k − 2n − 4
```

After the outer contraction the term is `APPLY(APPLY(p, g_{n−1}), g_{n−1})`,
contributing 3 nodes. Leftmost-outermost then has two phases — the left copy
reduces while the right is still `g_{n−1}`, then the right reduces while the
left is fixed at `T_{n−1}` — so each phase's maximum is `3 + peak(n−1)` plus the
other side's fixed size, and the trajectory maximum takes the larger fixed side.
Leftmost-innermost shrinks the chain before growing the tree, so it never
exceeds its endpoints.

`FACT`: all four forms are exact on **all 58** frozen rows of KAPPA-EXP-003 and
KAPPA-EXP-005 together. `theorem.py --check` also runs the mutation the review
asked for: perturbing the *earliest* row of each `k` while leaving the last
three untouched is caught, so the check cannot be satisfied by a doctored tail.

`DERIVATION`: past the crossover where `|T_{n−1}|` overtakes `|g_{n−1}|`, the
recurrence becomes `peak_out(n) = peak_out(n−1) + 4·2^{n−1}`, hence
`peak_out = 4·2^n + C(k)`. With `κ_S_in → 1` and `κ_S_out → 4/(4k+9)`,
`spread → k + 9/4` for every `k`, and `k` is a free parameter of the family.

`FACT`: these are hand derivations machine-checked on 58 points, not mechanised
proofs. A Lean or Coq statement would be a further step this repository has not
taken.

**Status after the erratum:**

```text
FACT       — the preregistered prediction failed on the frozen grid.
DERIVATION — spread(g_{n,k}) → k + 9/4, from four closed forms exact on 58 rows.
DERIVATION — H-SPREAD-DUP is false over the occurrence-weighted tree metric.
UNKNOWN    — whether it is false over physically materialized state; see the
             KAPPA-EXP-001 erratum on finding 1 and KAPPA-EXP-006.
```

### Finding 3 — "a single-integer budget must pin strategy" is retracted

`FACT`: this document claimed *"no choice of materialization-charging cost model
removes it"* while only two models were studied, and turned strategy pinning
into a *derived requirement* for a single-integer budget.

Both are retracted. The review is correct that the experiments show a difference
in **tightness**, not a failure of **safety**, and that the universal
quantification over cost models is unearned.

`DERIVATION`: the erratum inequality `size ≤ 1 + cost` holds strategy by
strategy under any materialization-charging model. A hard cap is therefore safe
under *either* strategy without pinning anything; a conservative
strategy-agnostic price stays safe while wasting capacity. Unbounded spread does
not distinguish these.

Separating the properties the earlier text conflated:

| property | what these experiments say |
|---|---|
| hard-cap safety | unaffected; follows from `Δsize ≤ cost − 1` alone |
| tightness — paid cost as a constant-factor proxy for materialized state | fails without a pinned strategy, on this family, under both measured models |
| work conservation / utilization | not measured |
| strategy-independent comparability | fails, same evidence as tightness |

**Replacement claim, correctly quantified:** *on the family `g_{n,k}`, under
`C_size` and `C_dup`, no strategy-independent constant-competitive charge
exists.* Whether that extends to a defined class of local cost models is
`UNKNOWN` and would need the class defined and a lower bound proved.

`DERIVATION`: Book I pinning both its cost model and its strategy remains a
coherent design, and KAPPA-EXP-002 observed it doing so. But this repository no
longer claims that as *derived from* these measurements. It is a design choice
that these measurements are consistent with.
