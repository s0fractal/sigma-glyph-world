# Σ-GLYPH World

A non-normative research notebook for testing where Σ-GLYPH resource
invariants transfer to other systems — and where the analogy breaks.

This repository does **not** extend the Σ-GLYPH specification and does not speak
for [`s0fractal/sigma-glyph`](https://github.com/s0fractal/sigma-glyph). Its
subject is representativeness: whether a result proved for one abstract machine
survives an explicit mapping to another computational, biological, physical, or
verification system.

## What is here

- [`talks/gemini-001.md`](talks/gemini-001.md) — a generative map of physical
  and cosmological resonances;
- [`talks/claude-fable-001.md`](talks/claude-fable-001.md) — an adversarial
  separation of testable hypotheses from narrative correspondences;
- [`INTENTIONS.md`](INTENTIONS.md) — Codex's current research intent after
  attacking both texts and receiving Claude's counter-attack;
- [`PROVENANCE.md`](PROVENANCE.md) — what the dialogue artifacts establish and
  what they do not;
- [`experiments/SCOPE-PILOT-001-preregistration.md`](experiments/SCOPE-PILOT-001-preregistration.md)
  and [`experiments/scope-pilot-001/PILOT-RESULT.md`](experiments/scope-pilot-001/PILOT-RESULT.md)
  — a preregistered attack on whether verification-scope incidents can be
  coded without inventing their causal chain;
- [`experiments/scope-instrument-001/RESULT.md`](experiments/scope-instrument-001/RESULT.md)
  — a retired-corpus calibration that separates observed behavior from the
  independently evidenced meaning of success;
- [`experiments/SCOPE-PILOT-002-preregistration.md`](experiments/SCOPE-PILOT-002-preregistration.md)
  and [`experiments/scope-pilot-002/PILOT-RESULT.md`](experiments/scope-pilot-002/PILOT-RESULT.md)
  — a fresh-corpus protocol retired when a repository alias made its supposedly
  unique sampling frame invalid before any candidate was frozen;
- [`experiments/SCOPE-PILOT-003-preregistration.md`](experiments/SCOPE-PILOT-003-preregistration.md)
  and [`experiments/scope-pilot-003/SAMPLING-RESULT.md`](experiments/scope-pilot-003/SAMPLING-RESULT.md)
  — the canonical-repository-ID retry with append-only query checkpoints, and
  its frozen candidate order of 5276 issues;
- [`experiments/scope-pilot-003/SCREENING-RESULT.md`](experiments/scope-pilot-003/SCREENING-RESULT.md)
  — the screen of the first 60 candidates in frozen order, retired as a sampling
  failure at 1 admitted incident against a minimum of 8. Its erratum marks the
  attribution `CONTESTED`: what the pilot demonstrates is the failure of this
  **frame-plus-instrument combination**, and whether the seven query terms or
  codebook v1's contract tier is the binding constraint is not identified by a
  design with no comparison arm.
- [`experiments/KAPPA-EXP-001-preregistration.md`](experiments/KAPPA-EXP-001-preregistration.md)
  and [`experiments/kappa-exp-001/RESULT.md`](experiments/kappa-exp-001/RESULT.md)
  — a preregistered refutation of the claim that the overcharge factor κ is an
  invariant of a calculus. One λ family, two strategies, same normal form: κ
  diverges under one and converges to 4 under the other. Two errata: the
  successor question was trivial, and the machine's object graph is a persistent
  DAG while its metric is occurrence-weighted, so `peak` is a tree size and not
  materialized state;
- [`experiments/KAPPA-EXP-002-preregistration.md`](experiments/KAPPA-EXP-002-preregistration.md)
  and [`experiments/kappa-exp-002/RESULT.md`](experiments/kappa-exp-002/RESULT.md)
  — the same family run through the Σ-GLYPH Book I reference oracle at a pinned
  digest. Structural sharing does not make peak linear: the store holds `2n + 2`
  distinct nodes and is fetched `2^(n+3) − 7` times.
- [`experiments/KAPPA-EXP-003-preregistration.md`](experiments/KAPPA-EXP-003-preregistration.md)
  and [`experiments/kappa-exp-003/RESULT.md`](experiments/kappa-exp-003/RESULT.md)
  — the strategy-spread question for λ. Refuted under `C_size` with the closed
  form `(3k+1)/4`, but that refutation is an artifact of a cost model that bills
  a copy which duplicates nothing; under the corrected `C_dup` the question is
  live and unsettled;
- [`experiments/KAPPA-EXP-005-preregistration.md`](experiments/KAPPA-EXP-005-preregistration.md)
  and [`experiments/kappa-exp-005/RESULT.md`](experiments/kappa-exp-005/RESULT.md)
  — the extended grid that settles it. The spread saturates in `n` and is driven
  by `k`, converging to `k + 9/4`. The preregistered prediction was wrong in both
  directions and says so on every green run; an erratum supplies the peak
  recurrences the asymptotic claim was missing and retracts the Track A
  over-generalisation;
- [`experiments/KAPPA-EXP-006-preregistration.md`](experiments/KAPPA-EXP-006-preregistration.md)
  and [`experiments/kappa-exp-006/RESULT.md`](experiments/kappa-exp-006/RESULT.md)
  — the representation audit. "Tree", "sharing", "materialized state" and "actual
  work" turn out to be four different quantities: at `n = 12` and the same
  occurrence size of 16381, the innermost strategy materializes 16381 objects on
  a machine that copies and 30 on one that aliases, while a content-addressed
  store holds 29 under both;
- [`experiments/KAPPA-EXP-007-preregistration.md`](experiments/KAPPA-EXP-007-preregistration.md)
  and [`experiments/kappa-exp-007/RESULT.md`](experiments/kappa-exp-007/RESULT.md)
  — Wadsworth graph reduction. Sharing *reduction* rather than storage collapses
  the 341× separation to exactly `11/8` where duplication is not under a binder,
  and leaves it growing where it is. The first experiment run under
  [`AGENTS.md`](AGENTS.md) clause 8, with two attributed predictions scored by
  name on every green run;
- [`experiments/KAPPA-EXP-008-preregistration.md`](experiments/KAPPA-EXP-008-preregistration.md)
  and [`experiments/kappa-exp-008/RESULT.md`](experiments/kappa-exp-008/RESULT.md)
  — a sharing graph reducer. What survives Codex's boundary review is the
  **schedule-internal** claim: inside one machine the two schedules fire the
  same number of interactions and reach the same peak, so the separation is
  exactly `1.0000` on `h_n` and `d_n`. The cross-representation reading is
  withdrawn — readback is unpriced, so the machines' outputs sit on opposite
  sides of an undefined boundary. The implemented reducer is renamed
  `R_abstract`, its unsoundness is a measured rate over a stated denominator
  (1 of 1493 comparable terms), and `e_4` is an ungated observation;
- [`reviews/`](reviews/) — [Codex's review](reviews/codex-2026-08-26.md), an adversarial
  review of `main` at `d61e6da` with verdict `CHANGES REQUESTED`;
  [Claude Fable's review](reviews/claude-fable-2026-08-26.md) of `9dd7e18`, whose
  synthesis is adopted and whose closing role calibration is
  [disputed on the record](reviews/response-to-claude-fable-2026-08-26.md).
  Findings are answered in errata and successor experiments, never by editing the
  reviewed documents.

The dialogue files are evidence of a conversation, not evidence for the claims
inside it.

- **The EML track** ([`experiments/EML-EXP-001-preregistration.md`](experiments/EML-EXP-001-preregistration.md),
  [`experiments/EML-EXP-002-preregistration.md`](experiments/EML-EXP-002-preregistration.md)) —
  two transfer tests against Odrzywołek's single-operator basis
  (arXiv:2603.21852v2, source-pinned by digest), corpus committed and verified
  before the preregistrations, three voices' predictions filed before the
  harness. Measured: **sharing is a large-construction phenomenon** — only the
  ten largest constructions beat a grammar-matched null (N4), floor at 134
  nodes ([RESULT](experiments/eml-exp-001/RESULT.md)); and **precision is not
  a budget on this basis** — 15 of 18 `neg`-routed constructions evaluate at
  exactly one precision (`n = 12`) and `n = 40` fails where `n = 12` succeeds,
  because the blocker is `ln(0)`, a representational hole
  ([RESULT](experiments/eml-exp-002/RESULT.md)). Transcription found a defect
  in the paper itself (T1, an even-in-`x` `arcosh` witness;
  [`TRANSCRIPTION_LOG.md`](experiments/eml-basis/TRANSCRIPTION_LOG.md)).

## Pipeline state

| pilot | sampling | screening | packets | coding | agreement |
|---|---|---|---|---|---|
| SCOPE-PILOT-001 | done | done | done | not run | not computed |
| SCOPE-PILOT-002 | failed | — | — | — | — |
| SCOPE-PILOT-003 | done | done — sampling failure | not run | not run | not run |

There are two commands, and they answer different questions.

- `tools/test-all.sh` is a **progress reporter**. It passes when a phase has not
  started, when a measurement is absent, and when the external Σ-GLYPH oracle is
  missing, and says so in its output.
- `tools/test-release.sh` is the **gate** for the claims on this page. A missing
  artifact, a changed frozen digest, an absent terminal state, or any skip marker
  is a failure. `tools/mutation-test.py` deletes each manifest artifact and
  corrupts each frozen digest in a throwaway copy, and additionally edits three
  recorded soundness values while re-freezing their digests so that only the
  semantic check can object. It requires the gate to reject all 82 mutations.
  That literal is derived from the manifest by `tools/mutation-test.py`, and
  `tools/check-release.py` fails if this sentence and the manifest disagree.

A green `tools/test-all.sh` reports the state of each phase; it does not assert
that later phases exist. `experiments/scope-pilot-003/screen.py --check` prints
the screening's terminal status, including `SAMPLING_FAILURE`, because a
recorded failure is an outcome of the protocol rather than a harness error.

## Research discipline

Claims use explicit status labels:

- `FACT` — directly supported by a named artifact or observation;
- `DERIVATION` — follows from stated premises;
- `HYPOTHESIS` — falsifiable but not established;
- `SPECULATION` — generative analogy without an operational test;
- `CONTESTED` — more than one live interpretation;
- `UNKNOWN` — the repository does not know.

A hypothesis is written before its measurement harness. A pilot may improve a
codebook or protocol, but it may not score the hypothesis it helped define.
Green checks establish reproducibility of what ran, not truth, review,
adoption, or normative authority.

## Current direction

Verification-scope archaeology on public, third-party incident records
(Track C) is retired at SCOPE-PILOT-003 as a sampling failure of the
frame-plus-instrument combination. Its screening erratum retracts the claim that
a resolution-sampled successor follows: conditioning inclusion on resolution
changes the estimand, so resolution-derived corpora are one option for
instrument calibration and evidence augmentation, not an identified successor
and not a causal diagnosis. No successor is identified.

Track A produced its first two measurements. KAPPA-EXP-001 refutes κ as a
property of a calculus and relocates it to the pair (strategy, cost model); its
erratum retracts the successor question as trivial and adopts instead the
*spread* of κ between strategies on one term. KAPPA-EXP-002 refutes the
prediction that structural sharing dissolves that counterexample, and finds the
real reason it does not transfer to Σ-GLYPH: the strategy is pinned normatively,
so there is no second strategy to diverge. KAPPA-EXP-003 and KAPPA-EXP-005 ask the
spread question of λ, where the strategy is free, and answer it: unbounded under
both materialization-charging cost models, for different reasons, only the
second of which is real. Over the occurrence-weighted tree metric, the
invariant the track set out to find does not exist for λ. KAPPA-EXP-006 then
separates the metric from the materialization and finds the refutation holds for
representations that materialize duplicated subterms per occurrence — including
the Σ-GLYPH reference implementation — and dissolves for those that alias.
KAPPA-EXP-007 moves the boundary once more: a machine that shares *reduction*
collapses the separation to a residual `11/8` where duplication is not under a
binder, and fails to collapse it where it is. The standing statement is that
unbounded strategy separation belongs to machines that do not share reduction
under a binder — Wadsworth 1971 for the first half, Lévy's non-optimality of
call-by-need for the second. What survives is
narrower than first claimed: on the measured family and under the two measured
cost models, no strategy-independent constant-competitive charge exists. Hard-cap
safety is unaffected and needs no pinned strategy; the earlier "derived
requirement" is retracted.

The distributed-prepayment track (Track B) remains formalization work until its
fault model and comparison metric stop moving.

No license has been selected yet. In particular, publication of attributed
dialogue records does not silently assign them the licensing terms of adjacent
Σ-GLYPH repositories.
