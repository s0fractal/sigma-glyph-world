# EML-EXP-001 — does a content-addressed store compress the EML basis beyond chance?

**Preregistration. Non-normative. Committed before its measurement harness
exists.** Split from the draft at `418038a` with review deltas D1–D5
([`reviews/claude-fable-2026-08-27-eml-draft.md`](../reviews/claude-fable-2026-08-27-eml-draft.md))
and the transcription facts at `9ad4e40` applied. The draft's hypotheses,
predictions, nulls and controls are carried verbatim where not marked
**Delta**. Prediction slots stay open until the harness first runs.

## Corpus, pinned (already committed — corpus precedes this document)

- `experiments/eml-basis/basis.json` at `d6b97d2`, verified 32/32 by
  `transcription_check.py` at `503efe3` (worst deviation 2.54e-48 against a
  1e-30 gate).
- Source: arXiv:2603.21852 **v2**, TeX e-print tarball, SHA-256
  `2a3b4219a7784d8fd0b3ffe6e7d3dd570cf73d60f8cf368459122fe78e1421db`.
- **Delta (D4, resolved):** the basis holds **32** constructions, not 36; the
  paper contradicts itself (main text: "all 36"; SI Table S2 caption: `x`,
  `y`, `1`, `i` are not reconstructed). The FACT lines live in
  `TRANSCRIPTION_LOG.md`.
- Scale facts the draft did not know: 692375 `eml` nodes total across the
  basis, maximum depth 260, `artanh` alone 504554 nodes.

## Hypothesis under attack — verbatim from the draft

`H-EML-SHARE`: over the Odrzywołek basis encoded as Book I normal forms, the
ratio `size_dag / size_tree` is smaller than under every null model below —
i.e. the basis shares subterms because its constructions **reuse derived
sub-constructions**, not merely because a two-symbol alphabet makes small
subtrees coincide.

## What the transcription already decided, and will not be claimed as a finding

**Delta.** The basis entries are mechanical expansions of Table S2 *chains*
over previously discovered primitives (`chain_sexpr` → `eml_sexpr`). Massive
sharing is therefore guaranteed **by construction**: every later step embeds
earlier steps whole, and a content-addressed store deduplicates them by
content. "The union store is much smaller than the union tree" is
paper-decided arithmetic, not a finding. What remains measurable: the
magnitude; the per-function-versus-union split; whether cross-function reuse
(`cross_only`) or within-function repetition carries the sharing; and whether
any of it beats alphabet-coincidence nulls at the per-function level.

**Delta — N3 is not constructible, and the reason is the instrument.** The
draft's N3 (re-derive each function's sub-constructions independently, no
cross-function reuse) is void on a content-addressed store: independent
derivation of the same content yields the same hash, so "no reuse of the same
derived term" cannot be expressed. N3 is reported `not constructible (CAS
identity)` per the draft's own provision; N1 and N2 carry the null burden.

## Encoding, oracle, measured quantities, N1, N2 — verbatim from the draft

As drafted: `E := LITERAL(sha256("EML"))` etc.; `eml(a,b) :=
APPLY(APPLY(E,a),b)`; oracle = local sigma-glyph checkout, HEAD +
`impl/sigma_glyph.py` + Book I digests pinned in `measurements.json`, absent
checkout → `SKIPPED`, never a pass. Quantities: `size_tree`, `size_dag`,
`ratio` per `f` and for the union `U`, `depth`, `nodes`, `cross_only(U)`.
Nulls N1 (size-matched random trees, leaf multiset preserved) and N2
(leaf-shuffled real trees), 100 draws each, same seed list, mean **and
minimum** reported; a level passes only against the **minimum**.

## Predictions

**P-draft — Claude (chat), from `418038a`, verbatim** (ledger voice
`claude-fable`, sub-attributed *draft*):

1. At the union level, `ratio(U)` is below the minimum of N1 and N2.
2. At the per-function level, for at least half of the constructions
   `ratio(f)` does **not** beat N1's minimum.
3. `size_dag(U) / size_tree(U) ≤ 0.35`.

**Delta note on P-draft-3:** after the chain-expansion facts, 0.35 is
expected to hold by a wide, paper-decided margin; its confirmation carries
little evidential weight and must not be headlined as one.

**P-fable — Claude Fable 5 (session), filed at this commit** (same ledger
voice, sub-attributed *session*; where P-fable opposes P-draft, both score):

- **F1.** `ratio(U) < 0.01` — the union store is at least two orders below
  the tree count, not merely below 0.35.
- **F2.** Fewer than a **quarter** of constructions fail to beat N1's
  minimum per-function — directly opposing P-draft-2's "at least half":
  chain expansion puts real reuse *inside* nearly every tree, not only
  across trees.
- **F3.** `cross_only(U) ≥ 0.5 · size_dag(U)` — the majority of distinct
  stored nodes appear in at least two constructions, because chains build on
  shared primitives.

**Open slot** — any other voice, as a dated addendum before the harness
first runs; later filings score nothing (clause 8).

## Controls — verbatim from the draft

1. Normal form: `eval_hash(f, budget)` returns `f`'s hash with `spent = 0`
   for every construction; otherwise the encoding changes before measuring.
2. Hash agreement: harness `size_dag` = store key count on single-`f` stores.
3. Transcription control has passed (it has — 32/32 at `503efe3`; the
   harness re-runs it and fails if the corpus digest moved).
4. Alphabet sanity: `nodes(f) ≤ 2` reported, excluded from per-function
   statistics.
5. **Delta:** determinism — two runs produce byte-identical
   `measurements.json`.

## What would make this experiment worthless — verbatim, plus one

As drafted (no null dropped after data; minimum-gate not mean; no
"compressed" reading without N1; no ATP/theorem talk — `spent` is zero by
control 1), plus: **headlining P-draft-3 or the raw `ratio(U)` as a
discovery** — both are paper-decided; the findings live in the null
comparisons and `cross_only`.

## Deliverables and dependency rule

`experiments/eml-exp-001/{measure.py, validate.py, measurements.json,
RESULT.md}`; `validate.py` prints every `PREDICTION FAILED` and `DEVIATION`
line on every green run. **Delta (dependency):** the transcription control
needs `mpmath`; `tools/test-all.sh` wiring reports `SKIPPED (mpmath absent)`
rather than importing it unconditionally — mirroring the oracle-absent rule,
and keeping the repository's zero-dependency default intact.

## Role separation

This document's authors do not write the harness. The harness author works
from the committed documents and corpus only, records missing choices in the
RESULT's provenance, and scores every prediction above by name.

---

## Amendment 1 — 2026-08-27, pre-harness, caused by [`reviews/kimi-2026-08-27-eml.md`](../reviews/kimi-2026-08-27-eml.md)

Filed before any harness exists; the scope clause ("changes after the harness
first runs create a successor") is not triggered. Nothing below weakens a
gate or drops a measurement; predictions already filed score exactly as
written, because every quantity they reference is still computed.

**A1.1 — the hypothesis is reformulated.** `H-EML-SHARE`'s causal clause
("because its constructions reuse derived sub-constructions, not merely
because a two-symbol alphabet…") is not adjudicable on a content-addressed
store: the instrument is provenance-agnostic, and no null can see the
"because". Replaced, per the review, by:

> **H-EML-SHARE-revised:** the Odrzywołek basis exhibits sharing that
> exceeds independent random generation from the same EML grammar (N4), and
> the excess is concentrated in subtrees larger than any plausible
> alphabet-coincidence threshold.

Scoring rule, fixed now: the revised hypothesis HOLDS iff (i) `ratio(U)` is
below N4's **minimum** at the union level, and (ii) at least **50%** of the
union savings `size_tree(U) − size_dag(U)` is attributable to shared
subtrees of **≥ 100 nodes**. The causal reading is a `DERIVATION` from the
size spectrum, never a scored claim.

**A1.2 — N4 becomes the primary null.** Grammar-matched independent trees:
per construction, a uniformly random binary tree with exactly `n(f)`
internal `eml` nodes and `f`'s exact leaf multiset, drawn by the recursive
uniform-split procedure specified in the review, 100 draws, seeds
`sha256("EML-EXP-001/N4/{f}/{draw_index}")[:16]` big-endian, mean and
minimum reported, minimum gates. **N1 and N2 are demoted to descriptive
baselines** — they establish "more than random / more than leaf-shuffled",
full stop, and are not read as testing any mechanism.

**A1.3 — N5 (chain-topology-preserving content permutation) is admitted as
optional and non-gating**, with the review's draw procedure and its stated
caveat; if implemented it is reported, if not it is listed `not run`.

**A1.4 — the size spectrum is added to the measured quantities.** Per
distinct hash in the union store: its subtree node count. Reported: the
cumulative distribution of shared-subtree sizes; the fraction of union
savings attributable to shared subtrees ≥ 100 and ≥ 1,000 nodes (both
thresholds fixed here); the largest shared subtree and the constructions
sharing it.

**A1.5 — worthlessness list extended** (from the review): headlining the
size spectrum as proof of construction-driven reuse; any size threshold
chosen after data; dropping N4 after seeing the data.

## Addendum — predictions filed 2026-08-27, pre-harness

**kimi** (full text and rationale in
[`reviews/kimi-2026-08-27-eml.md`](../reviews/kimi-2026-08-27-eml.md)):

- **A1.** `ratio(U) < 0.001`. Falsifier: `≥ 0.001`.
- **A2.** `cross_only(U) ≥ 0.65 · size_dag(U)`. Falsifier: below.
- **A3.** At least **25** of 32 constructions have `ratio(f) < min(N1)`
  per-function, the failures being exactly the smallest constructions.
  Falsifier: fewer than 25.
- **A4.** The largest shared subtree has **> 100,000 nodes** and is shared
  by **≥ 3** constructions. Falsifier: ≤ 100,000 nodes or < 3 sharers.

**claude-fable (session), filed at this amendment:**

- **F6.** At least **95%** of the union savings
  `size_tree(U) − size_dag(U)` is attributable to shared subtrees of
  **≥ 1,000 nodes**. Falsifier: < 95%.

The slot remains open for further voices until the harness first runs.
