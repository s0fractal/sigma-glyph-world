# EML-EXP-001 / EML-EXP-002 — what content addressing and a single integer buy for a single-operator grammar of elementary functions

**Draft preregistration, for review and splitting into two committed files.
Non-normative. To be committed before either measurement harness exists.**

Author of the draft: Claude (chat), 2026-08-27, from a conversation with
s0fractal. Prior record of this author in this repository: three predictions
stated this week (H-SHARING, a strategy-insensitivity constant for λ, the
foreign-data design of H-SCOPE), three refuted. Predictions below are stated
so that they can be refuted cleanly, not so that they will be believed.

## 0. Scope guard

- Does not modify `s0fractal/sigma-glyph`, Book I reduction, §3.4 pricing,
  serialization, hashing, or the bound `size ≤ spent + 1`.
- Does not use Book II, phase, `interfere()`, Mass, pins, CP-24, or any
  coordinate annotation. Phase is out of scope for both experiments.
- Does not interpret `eml` inside the Book I oracle. In EML-EXP-001 `eml` is an
  **uninterpreted** head literal; every EML tree is a Book I normal form.
- EML-EXP-002 runs **outside** the oracle, on a separate integer-only evaluator
  with its own explicitly labelled cost proxy. Any sentence linking that proxy
  to ATP is `DERIVATION`, never `FACT`.
- No claim about holography, fractals, mipmaps, "worlds", or symbolic
  regression. Those words do not appear in the harness or the result.
- Complex-domain constructions (anything routed through `i`) are out of scope
  for EML-EXP-002 and are listed by name as excluded.

## 1. External input, pinned

- Odrzywołek, *All elementary functions from a single binary operator*,
  arXiv:2603.21852. Pin the exact version (`v1`, `v2`, …) and the SHA-256 of
  the downloaded PDF/TeX source in `measurements.json`.
- The basis: the paper's table of goal operations (the paper says 36; the
  harness records the actual count it transcribes, and any discrepancy is a
  `FACT` line) with their EML constructions, transcribed into
  `basis.json` as S-expressions over the alphabet `{eml, 1, x, y}`.
- Follow-up literature is **not** an input: Stachowiak (algebraic structure),
  Erez (biological ODEs), EML-CD are cited in RESULT only if a finding needs
  them.

### 1.1 Transcription control (mandatory, runs before anything else)

Every construction in `basis.json` MUST be verified against its target
function numerically: evaluate both at ≥ 200 pseudo-random points of the
target's domain in `mpmath` at 50 significant digits (complex points for
complex-domain constructions) and require agreement to 1e-30 relative. A
construction that fails is a transcription error and is fixed **before** any
measurement is taken; the fix is logged. No measurement below is valid over a
basis that has not passed this control. Record the seed and the point set.

---

# EML-EXP-001 — does a content-addressed store compress the EML basis beyond chance?

## Hypothesis under attack

From the fusion notes (Grok/Gemini, 2026-08-26): "any elementary function
becomes a hashed term" and "content addressing helps with tree size".

The first clause is false by Richardson's theorem and is not tested: an EML
tree is *one* of infinitely many trees for a function, and equality of such
trees is undecidable. What is tested is the second clause, made precise:

`H-EML-SHARE`: over the Odrzywołek basis encoded as Book I normal forms, the
ratio `size_dag / size_tree` is smaller than under every null model below —
i.e. the basis shares subterms because its constructions **reuse derived
sub-constructions**, not merely because a two-symbol alphabet makes small
subtrees coincide.

The alphabet danger is exactly ALIFE-EXP-004's: with an alphabet of `{eml, 1,
x, y}`, tiny subtrees such as `eml(1,x)` coincide by chance, and a naive ratio
cannot tell reuse from a small alphabet. The nulls exist for that reason.

## Encoding

```text
E   := LITERAL(sha256("EML"))
ONE := LITERAL(sha256("ONE"))
X   := LITERAL(sha256("X"))
Y   := LITERAL(sha256("Y"))
eml(a, b) := APPLY(APPLY(E, a), b)
```

`E` at the head with arguments is a normal form in Book I (as `p x x` was in
KAPPA-EXP-002). Every node is written to a `Store` before any call.

Oracle: local checkout of `s0fractal/sigma-glyph`; pin HEAD, and SHA-256 of
`impl/sigma_glyph.py` and `spec/book-1-truth.en.md` exactly as
KAPPA-EXP-002 does. Imported at run time, never vendored. Missing checkout or
digest → `SKIPPED`, never a pass.

## Measured quantities

Per construction `f` and for the union `U` of all constructions in one shared
store:

- `size_tree(f)` — `impl.size` of the term (one count per occurrence);
- `size_dag(f)` — number of distinct node hashes in the term;
- `size_dag(U)` — distinct hashes across the whole basis in one store;
- `size_tree(U)` — sum of `size_tree(f)`;
- `ratio(f) = size_dag(f) / size_tree(f)`, `ratio(U)` likewise;
- `depth(f)` — tree depth; `nodes(f)` — number of `eml` nodes;
- `cross_only(U)` — distinct hashes that appear in ≥ 2 constructions.

## Null models (all mandatory, 100 draws each, same seed list, worst-case
statistic reported alongside mean, as ALIFE-EXP-008 requires)

- **N1, size-matched random trees.** For each `f`, a uniformly random binary
  tree with the same number of `eml` nodes and the same leaf multiset
  (`ONE`/`X`/`Y` counts preserved). Tests whether the alphabet alone produces
  the sharing.
- **N2, leaf-shuffled real trees.** The real tree shapes, leaves permuted
  among leaf positions. Tests whether sharing comes from shape or from which
  leaf sits where.
- **N3, subtree-shuffled union.** The real constructions, but with the
  sub-constructions re-derived independently per function (no cross-function
  reuse of the same derived term); concretely, each function's tree is
  regenerated from the paper's *primitive* construction rules rather than
  from shared intermediate definitions. If the paper only gives one form per
  function, N3 is `not constructible` and is reported as such, not silently
  dropped.

Statistic per null: the null's `ratio` (per `f` and for `U`), mean and
minimum over 100 draws. `H-EML-SHARE` holds for a level (`f` or `U`) only if
the observed ratio is below the **minimum** null ratio at that level.

## Preregistered predictions

`HYPOTHESIS`:

1. At the union level, `ratio(U)` is below the minimum of N1 and N2 —
   cross-function reuse of `eml(1,x)`, `exp`, `ln` and product
   sub-constructions is real.
2. At the per-function level, for at least half of the constructions
   `ratio(f)` does **not** beat N1's minimum — inside one tree, the small
   alphabet produces as much coincidence as the construction does.
3. `size_dag(U) / size_tree(U) ≤ 0.35`.

Falsifiers: (1) fails if `ratio(U) ≥ min N1` or `≥ min N2`; (2) fails if more
than half the constructions beat N1's minimum; (3) fails on its number.

## Controls

1. **Normal form.** `eval_hash(f, budget)` returns `f`'s own hash with
   `spent = 0` for every construction. A non-zero spend means `E` at the head
   is not a normal form at this digest, and the encoding must change before
   measuring.
2. **Hash agreement.** The harness's own `size_dag` counting agrees with the
   store's key count for a single-construction store, for every `f`.
3. **Transcription control** (§1.1) has passed before this experiment runs.
4. **Alphabet sanity.** A construction with `nodes(f) ≤ 2` is reported but
   excluded from per-function statistics (its ratio is degenerate).

## What would make this experiment worthless

- Dropping or weakening a null after seeing the data.
- Reporting mean-null only; the minimum over draws is the gate.
- Reading a low `ratio` as "the basis is compressed" without N1: a two-symbol
  alphabet compresses anything.
- Any mention of a theorem, ATP, or the bound in RESULT — nothing is evaluated
  here; `spent` is zero by control 1.

---

# EML-EXP-002 — does EML's universality survive fixed-point integers, and does precision behave like a budget?

## Hypothesis under attack

From the Q-format note (Grok, 2026-08-26): Q10–Q20 fixed point "leaves the
system integer-only" while keeping EML universality with "known, reproducible
precision".

Stachowiak's note on the operator's algebraic structure observes that the
recovery of elementary functions from EML relies on cancellations — `ln 1 =
0`, additive inverses through subtraction — and on the addition law of `exp`.
None of these is exact in fixed point, and Odrzywołek's constructions pass
through large intermediates (his `ln x` is `e − ln(e^e / x)`).

`H-EML-Q`: there exists a fractional-bit count `n ≤ 20` at which every
real-domain basis construction, evaluated by an integer-only Q-format
evaluator, matches its target to relative error ≤ 1e-3 on the test grid.

`H-EML-BUDGET`: the minimal fractional bits `n*(f)` needed to reach 1e-3 is
monotone in construction depth across the basis.

## Evaluator, pinned

- Signed 64-bit integers; formats `Q(63−n).n` for
  `n ∈ {8, 12, 16, 20, 24, 32, 40}`.
- `exp` and `ln` implemented as **integer-only** deterministic algorithms
  (range reduction by powers of two, then a fixed-term series or CORDIC; the
  choice is pinned and the term count is a function of `n` fixed in advance).
  No `float` anywhere in the evaluation path; the harness greps for it and
  fails if found.
- Rounding: round-to-nearest-even at every operation; truncation is a second
  configuration, run for comparison, never mixed.
- Overflow: **trap**. Any intermediate outside the representable range marks
  `(f, n)` as `OVERFLOW`, which counts as failure at that `n`. Saturation and
  wraparound are not used, because they would silently produce numbers.
- `eml(a, b) = exp(a) − ln(b)` evaluated left to right, exactly as the tree
  says; no algebraic simplification of the tree before evaluation (that would
  test the simplifier, not EML).
- Reference: `mpmath` at 50 digits.

## Basis subset

Real-domain constructions only. Every construction whose paper form routes
through `i` (trigonometry via Euler, and anything derived from it) is
**excluded by name** in `basis.json` with reason `complex`. The count of
included and excluded constructions is a `FACT` line.

## Test grid

Fixed now: `x ∈ {0.1, 0.25, 0.5, 1, 1.5, 2, 3, 5}`, `y` over the same set for
binary constructions, restricted to each target's domain (e.g. `ln` at `x >
0`, `sqrt` at `x ≥ 0`). Points outside the domain are skipped and counted.
The grid is not enlarged or shrunk after the first run.

## Measured quantities

Per `(f, n)`:

- `err(f, n)` — maximum relative error over the grid, or `OVERFLOW`;
- `n*(f)` — the least `n` in the list with `err(f, n) ≤ 1e-3`, or `NONE`;
- `depth(f)`, `nodes(f)` — from EML-EXP-001's `basis.json`;
- `cost_proxy(f, n) = nodes(f) · n` — a bit-serial proxy, labelled as such.

`ε = 1e-3` is fixed here and not revisited.

## Preregistered predictions

`HYPOTHESIS`:

1. `H-EML-Q` is **false** for `n ≤ 20`: at least one real-domain construction
   has `n*(f) > 20`, and at least one has `n*(f) = NONE` because an
   intermediate `exp` overflows at every `n` tested (the trap fires before
   precision can help). Falsifier: every included construction reaches 1e-3
   at some `n ≤ 20`.
2. The failing constructions are the deep ones: `n*(f)` correlates with
   `depth(f)`, Spearman ρ ≥ 0.5 over constructions with finite `n*`.
   Null: 1000 permutations of `n*` across constructions; report the
   permutation p-value. Falsifier: ρ < 0.5 or p ≥ 0.05.
3. Truncation is strictly worse than round-to-nearest: `n*` under truncation
   is ≥ `n*` under rounding for every construction, and strictly greater for
   at least a quarter of them. Falsifier: any construction where truncation
   needs fewer bits.

`DERIVATION`, not measured: if (1) holds, then EML in fixed point is not a
universal grammar but an **approximation grammar whose error grows with
depth**, and the only universality that survives integer-only evaluation is
the symbolic one measured in EML-EXP-001. If (2) holds, `n*` behaves like a
budget — a deeper term needs more of it — and `cost_proxy` is the shape a
materialization-charging price for a hypothetical Q-arithmetic primitive would
have to take. That sentence is where the ATP link ends in this experiment.

## Controls

1. **Reference agreement.** For `exp` and `ln` alone, the integer evaluator at
   `n = 40` matches `mpmath` to 1e-9 on the grid. If not, the evaluator is
   wrong, not EML, and nothing is reported until it is fixed.
2. **Determinism.** Two runs on two machines (or two Python versions) produce
   byte-identical `measurements.json`. A difference is a `float` leak or an
   unpinned algorithm.
3. **Transcription control** (§1.1) has passed.
4. **Trap coverage.** A synthetic construction known to overflow at `n = 8`
   (e.g. `exp(exp(exp(1)))`) MUST produce `OVERFLOW`; if it produces a
   number, the trap is broken.
5. **No simplification.** A construction and its algebraically simplified
   equivalent (one pair, chosen now: `x·y` in EML form vs. the direct product)
   are evaluated separately; they MUST differ in `err` at some `n`, proving
   the evaluator follows the tree.

## What would make this experiment worthless

- Any `float` in the evaluation path.
- Choosing `ε`, the grid, or the `n` list after seeing errors.
- Using saturation instead of trapping, which turns overflow into a wrong
  number that then "converges".
- Reporting `cost_proxy` as ATP, or claiming anything about Book I from it.
- Simplifying trees before evaluation.
- Treating the complex-domain exclusion as a footnote: it is at least a third
  of the basis and must be counted in the abstract of RESULT.

---

## Deliverables (both experiments)

```text
experiments/EML-EXP-001-preregistration.md      (this part, split out)
experiments/EML-EXP-002-preregistration.md      (this part, split out)
experiments/eml-basis/basis.json                 transcribed constructions + targets
experiments/eml-basis/transcription_check.py     §1.1 control
experiments/eml-exp-001/measure.py, validate.py, measurements.json, RESULT.md
experiments/eml-exp-002/qeval.py, measure.py, validate.py, measurements.json, RESULT.md
```

`validate.py` in each prints every `PREDICTION FAILED` and `DEVIATION` line on
every green run, as KAPPA-EXP-005 does. `tools/test-all.sh` reports
`SKIPPED` when the oracle checkout is absent (EML-EXP-001) and never for
EML-EXP-002, which has no external dependency beyond `mpmath`.

## Order of work

1. Pin the paper version; transcribe `basis.json`; run §1.1 until green.
2. Commit both preregistrations **before** `measure.py` exists in either
   directory (two commits, in that order, as KAPPA-EXP-001 did).
3. EML-EXP-001 first — it is minutes of compute and needs no numerics.
4. EML-EXP-002 second.
5. RESULT.md for each, judged against the preregistration, with errata in
   place rather than edits to the reviewed text.

## Out of scope, explicitly, for successors to pick up

- Complex-domain constructions under a fixed-point complex evaluator.
- Exact-rational interval evaluation (RFC-0003's preferred representation)
  as the third configuration.
- A priced `eml` primitive inside a Σ-GLYPH-like machine with a §3.4-style
  cost row — only after EML-EXP-002 has said what shape the price must have.
- Anything involving phase.
