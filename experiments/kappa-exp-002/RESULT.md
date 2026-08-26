# KAPPA-EXP-002 — result

**Status: `H-SHARING` refuted. Structural sharing does not make `peak` linear —
it is a property of the store, not of the materialized term.**

The prediction under test, from [`talks/claude-fable-002.md`](../../talks/claude-fable-002.md),
is that the KAPPA-EXP-001 family evaluated through Σ-GLYPH's hash-thunk machine
gives `peak` linear in `n`, because "дублікат x — одна адреса, не k вузлів".

The address is indeed one. The materialization is not.

## Outcome

`FACT`, from [`measurements.json`](measurements.json), oracle
`impl/sigma_glyph.py` at SHA-256 `413d1f98…`, `s0fractal/sigma-glyph` HEAD
`c78e866`, family compiled by normative profile C1:

| n | `spent` | `peak_tree` | `size_tree(nf)` | `size_dag(nf)` | tree/dag | κ | store fetches |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 406 | 69 | 61 | 10 | 6.1 | 0.167 | 121 |
| 6 | 1702 | 261 | 253 | 14 | 18.1 | 0.153 | 505 |
| 8 | 6886 | 1029 | 1021 | 18 | 56.7 | 0.149 | 2041 |
| 10 | 27622 | 4101 | 4093 | 22 | 186.0 | 0.148 | 8185 |
| 12 | 110566 | 16389 | 16381 | 26 | **630.0** | 0.148 | 32761 |

`FACT`: every preregistered quantity matched a closed form exactly at every `n`
in range:

```text
size_tree(nf) = 4·2^n − 3      size_dag(nf) = 2n + 2
peak_tree     = 4·2^n + 5      spent        = 27·2^n − 26
fetches       = 2^(n+3) − 7    κ            → 4/27 ≈ 0.1481
```

`DERIVATION`: `peak` and `spent` are `Θ(2^n)`; only `size_dag` is linear.
`H-SHARING` is false.

The sharpest statement of the mechanism is the last column. At `n = 12` the
store holds **26 distinct nodes** and is fetched **32761 times** — about 1260
fetches per distinct node. `R-S` duplicates a size-1 thunk for `1 + 1 = 2` ATP,
so duplication is genuinely cheap; but the two copies are independent thunks
over the same hash, and `_step_application` forces each one separately when the
leftmost-outermost search demands it. Content addressing collapses the *storage*
of the normal form from `4·2^n − 3` to `2n + 2`; it does not collapse the
*materialization*, and `size` in §3.4 is a tree recursion over what is
materialized.

## This is not a defect claim against Book I

`FACT`: `size(t) − 1 ≤ spent` held at **every step** of all twelve evaluations.
Zero violations. κ never exceeded 1.

The bound §3.4 asserts is about `size_tree`, the same quantity that is
exponential here, and it holds. Nothing in Book I promises that a term whose
normal form is an exponential tree will materialize in linear space. The
prediction under test was an inference from "structural sharing", not a claim
the specification makes.

`FACT`: this is an independent check of a normative claim on a family the
spec's own conformance vectors do not cover. It passed.

## Why the KAPPA-EXP-001 counterexample does not transfer — and it is not sharing

`FACT`: Book I fixes leftmost-outermost with lazy left-spine resolution
normatively (§3.3, ADR-003). The strategy is not a free parameter of this
machine.

`DERIVATION`: KAPPA-EXP-001's counterexample needs two strategies on one
calculus to diverge. Σ-GLYPH admits one. `spread` is undefined here — not
large, not small, undefined. That is the first reason the counterexample cannot
be constructed against this machine.

`DERIVATION`: the second is the theorem in the KAPPA-EXP-001 erratum. §3.4 is
materialization-charging, so `κ ≤ 1 + (size_0 − 1)/spent`, and evaluation begins
from a single hash with `size_0 = 1`, giving `κ ≤ 1` outright. The measured
0.148 sits well inside it.

Neither reason is structural sharing. Sharing changes what the store holds; it
changed nothing about `peak`, `spent`, or κ on this family.

## Cross-check against KAPPA-EXP-001

Two independently written machines, one in this repository over a tree of Python
objects with β as its only rule, one the Σ-GLYPH reference oracle over SKI with
hash thunks and §3.4 pricing:

- `FACT`: the oracle's normal form hash equals the C1 compilation of
  KAPPA-EXP-001's normal form, checked for every `n ≤ 8` (control 2);
- `FACT`: `size_tree(nf) = 4·2^n − 3` in both;
- `FACT`: `peak_tree = 4·2^n + 5` in the oracle, identical to KAPPA-EXP-001's
  `S_out` peak — including the additive 8 that experiment recorded as a
  deviation from its own predicted closed form.

The deviation KAPPA-EXP-001 reported rather than smoothed turns out to reproduce
exactly on a different machine, through a different compiler, in a different
calculus. That is what reporting it bought.

## Controls

All four hold for every `n` in range:

- `driver_equivalence` — `peak` is not observable through `eval_hash`, so this
  harness runs its own loop over the oracle's `step5`. It reproduces
  `eval_hash`'s result hash and `spent` exactly at every `n`.
- `normative_bound` — `size(t) − 1 ≤ spent` at every step, zero violations.
- `memo_size_agrees` — `size` is memoized on object identity, a pure harness
  optimization, because recomputing it per step costs `O(4^n)` and does not
  reach the preregistered range. For `n ≤ 7` the whole trajectory is re-driven
  with the oracle's own `sg.size` and every measured quantity compared; beyond
  that the final term is cross-checked. No measured number depends on the memo.
- `no_oracle_writes` — the harness imports the oracle at run time from a pinned
  path and digest. It never vendors the code and never writes to that checkout.

## Harness notes, not scope changes

- `oracle.py --check` re-drives only `n ≤ 8`, about 0.7 s. The oracle's
  leftmost-outermost search is `O(size)` per step, so a full re-drive of the
  preregistered range costs minutes. The rows beyond 8 are checked against the
  closed forms above by `validate.py`. The measured range is the preregistered
  `[1, 12]`; only the re-verification cadence is partial.
- If the pinned checkout or digest is absent, both scripts print `SKIPPED` and
  exit 0. They never print `PASS` without having run the oracle.

## What this does not establish

- Nothing about `impl-rs`, `impl-go`, or any Σ-GLYPH version other than the
  pinned digest.
- Nothing about families other than this one. A family whose normal form is
  linear would materialize linearly; the exponential gap here comes from the
  term, not from the machine.
- No claim that a hash-consed *evaluator* would behave this way. This measured
  the reference implementation, which represents terms as trees. An evaluator
  that deduplicated materialized nodes by hash would plausibly show
  `peak = size_dag`, and that is untested here.
- Nothing about `H-SCOPE` or Track B.

## Consequence for Track A

`DERIVATION`: the spread question raised in `claude-fable-002` and adopted in
the KAPPA-EXP-001 erratum cannot be asked of Σ-GLYPH, because Σ-GLYPH pins its
strategy normatively. It is a question about λ, where the strategy is free. That
is KAPPA-EXP-003.

`HYPOTHESIS`, untested here: an evaluator that deduplicates materialized nodes
by hash — sharing reduction, not only storage — would collapse `peak` to
`size_dag` and with it the `S_out`/`S_in` separation of KAPPA-EXP-001. If so,
the H-KAPPA counterexample is confined to machines that materialize per
occurrence, which is a much narrower class than "machines without sharing", and
the Σ-GLYPH reference implementation is inside it rather than outside.

## Reproduction

```sh
tools/test-all.sh
```

Requires a checkout of `s0fractal/sigma-glyph` at HEAD `c78e866` with
`impl/sigma_glyph.py` at SHA-256 `413d1f98…`, found at `~/Projects/sigma-glyph`
or at `$SIGMA_GLYPH_IMPL`. Without it the experiment reports `SKIPPED`.
Green execution is reproducibility of a bounded computation. It is not review,
adoption, or external validity, and it is not an endorsement by the Σ-GLYPH
project.
