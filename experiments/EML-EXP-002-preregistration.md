# EML-EXP-002 — does EML's universality survive fixed-point integers, and does precision behave like a budget?

**Preregistration. Non-normative. Committed before its measurement harness
exists.** Split from the draft at `418038a` with review deltas D1–D5 and the
transcription facts at `9ad4e40` applied. Draft text carried verbatim where
not marked **Delta**. Prediction slots stay open until the harness first
runs.

## Corpus, pinned

As EML-EXP-001: `basis.json` at `d6b97d2`, 32 constructions verified 32/32,
source arXiv:2603.21852 **v2**, SHA-256
`2a3b4219a7784d8fd0b3ffe6e7d3dd570cf73d60f8cf368459122fe78e1421db`.

## Hypotheses under attack — verbatim from the draft

`H-EML-Q`: there exists a fractional-bit count `n ≤ 20` at which every
real-domain basis construction, evaluated by an integer-only Q-format
evaluator, matches its target to relative error ≤ 1e-3 on the test grid.

`H-EML-BUDGET`: the minimal fractional bits `n*(f)` needed to reach 1e-3 is
monotone in construction depth across the basis.

## The included set — Delta (D7/D8), replacing the draft's exclusion rule

The draft excluded "every construction whose paper form routes through `i`".
Transcription measured the routing (`complex_route` per entry) and the
draft's rule is too blunt: **23** of 32 route through `i` somewhere, but only
**10** are Euler-essential (complex at every point); **13** are
argument-dependent (measured `max|Im|` exactly 0 on all-positive windows);
**9** are purely real. The preregistered inclusion rule:

- **Excluded by name (10, Euler-essential):** `pi, cos, sin, tan, arsinh,
  arcosh, arccos, artanh, arcsin, arctan`. This also disposes of the four
  T1-restricted constructions — all are in this list, so the paper defect
  found in transcription does not touch this experiment's set.
- **Included, fully (9, purely real):** `e, exp, ln, neg1, two, minus,
  sigma, cosh, sinh`.
- **Included, per-point gated (13, argument-dependent):** `sub, add, inv,
  mul, sqr, div, half, avg, sqrt, pow, logb, hypot, tanh`. Before any Q
  evaluation, a routing check evaluates each construction's route in complex
  `mpmath` at 50 digits at every grid point; a point is *real-route* iff
  `max|Im|` along the route < 1e-40. Only real-route points enter the error
  grid; excluded points are counted per `(f, point)` and reported. A
  construction with zero real-route grid points is reported `EXCLUDED
  (no real-route points)` as a FACT, not silently dropped.

Included count: **22**, gated as above. The 10-versus-13-versus-9 split and
the per-point exclusions are FACT lines in RESULT's abstract, per the
draft's own worthlessness rule about the complex exclusion.

## Evaluator, grid, measured quantities — verbatim from the draft

Signed 64-bit; `Q(63−n).n`, `n ∈ {8, 12, 16, 20, 24, 32, 40}`; integer-only
`exp`/`ln` (pinned algorithm, term count a function of `n` fixed in
advance); round-to-nearest-even, truncation as a second configuration never
mixed; **overflow traps** (`OVERFLOW` = failure at that `n`; no saturation,
no wraparound); `eml(a,b) = exp(a) − ln(b)` evaluated exactly as the tree
says, no simplification; reference `mpmath` at 50 digits. Grid fixed as
drafted: `x, y ∈ {0.1, 0.25, 0.5, 1, 1.5, 2, 3, 5}` intersected with target
domains; out-of-domain points skipped and counted. `err(f,n)`, `n*(f)`,
`depth(f)`, `nodes(f)`, `cost_proxy(f,n) = nodes(f)·n` labelled a bit-serial
proxy; `ε = 1e-3` fixed. The ATP link ends at the draft's `DERIVATION`
sentence, verbatim.

## Predictions

**P-draft — Claude (chat), from `418038a`, verbatim** (ledger voice
`claude-fable`, sub-attributed *draft*):

1. `H-EML-Q` is **false** for `n ≤ 20`: at least one real-domain
   construction has `n*(f) > 20`, and at least one has `n*(f) = NONE`
   because an intermediate `exp` overflows at every `n` tested. Falsifier:
   every included construction reaches 1e-3 at some `n ≤ 20`.
2. `n*(f)` correlates with `depth(f)`, Spearman ρ ≥ 0.5 over constructions
   with finite `n*`; null: 1000 permutations, p < 0.05.
3. Truncation is strictly worse than round-to-nearest: `n*` under truncation
   ≥ under rounding everywhere, strictly greater for ≥ a quarter.

**P-fable — Claude Fable 5 (session), filed at this commit** (same ledger
voice, sub-attributed *session*):

- **F4.** At least **half** of the 22 included constructions have
  `n*(f) > 20` or `NONE` — sharpening P-draft-1's "at least one": the
  chains' depth (up to hundreds of `eml` nodes even in the included set)
  accumulates rounding past 1e-3 long before bits run out, and `exp` towers
  trip the trap.
- **F5.** All of `e, exp, ln` (the three shallowest purely-real
  constructions) reach 1e-3 at `n ≤ 16` under round-to-nearest — the floor
  of the budget curve is low even though its ceiling is unreachable.

**Open slot** — any other voice, dated addendum before the harness first
runs; later filings score nothing (clause 8).

## Controls — verbatim from the draft, with two deltas

1. Reference agreement: integer `exp`/`ln` at `n = 40` match `mpmath` to
   1e-9 on the grid, else nothing is reported.
2. **Delta (D5):** determinism = byte-identical `measurements.json` across
   **two Python minor versions** on this machine; a second-machine replay is
   recorded `not performed` unless it happened.
3. Transcription control passed (32/32 at `503efe3`; harness re-checks the
   corpus digest).
4. Trap coverage: the preregistered overflow witness `exp(exp(exp(1)))`
   MUST produce `OVERFLOW` at `n = 8`.
5. No simplification: the preregistered pair (`x·y` in EML form vs. direct
   product) MUST differ in `err` at some `n`.
6. **Delta:** the routing check (per-point gate above) is itself controlled:
   one preregistered witness point where `sqrt` routes complex (`x = 0.5`,
   below the measured `x < e` threshold from T2) MUST be excluded by the
   gate; if the gate admits it, the gate is broken.

## What would make this experiment worthless — verbatim from the draft

No `float` in the evaluation path (grepped); no post-hoc `ε`/grid/`n`-list
changes; trapping never saturation; `cost_proxy` never reported as ATP; no
tree simplification; the complex exclusion counted in RESULT's abstract.

## Deliverables, dependency rule, role separation

`experiments/eml-exp-002/{qeval.py, measure.py, validate.py,
measurements.json, RESULT.md}`; `validate.py` prints every `PREDICTION
FAILED` and `DEVIATION` line on every green run; `mpmath` dependency behind
the same `SKIPPED (mpmath absent)` rule as EML-EXP-001. This document's
authors do not write the harness; the harness author works from the
committed documents and corpus only and scores every prediction by name.
