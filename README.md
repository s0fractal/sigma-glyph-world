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
  failure at 1 admitted incident against a minimum of 8, with the four
  near-miss cases that locate the real scarcity in adjudicated success
  contracts rather than in candidate incidents.
- [`experiments/KAPPA-EXP-001-preregistration.md`](experiments/KAPPA-EXP-001-preregistration.md)
  and [`experiments/kappa-exp-001/RESULT.md`](experiments/kappa-exp-001/RESULT.md)
  — a preregistered refutation of the claim that the overcharge factor κ is an
  invariant of a calculus. One λ family, two strategies, same normal form: κ
  diverges under one and converges to 4 under the other.
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
  live and unsettled.

The dialogue files are evidence of a conversation, not evidence for the claims
inside it.

## Pipeline state

| pilot | sampling | screening | packets | coding | agreement |
|---|---|---|---|---|---|
| SCOPE-PILOT-001 | done | done | done | not run | not computed |
| SCOPE-PILOT-002 | failed | — | — | — | — |
| SCOPE-PILOT-003 | done | done — sampling failure | not run | not run | not run |

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
(Track C) is retired at SCOPE-PILOT-003 as a sampling failure; its screening
result argues the successor must sample resolutions rather than symptoms.

Track A produced its first two measurements. KAPPA-EXP-001 refutes κ as a
property of a calculus and relocates it to the pair (strategy, cost model); its
erratum retracts the successor question as trivial and adopts instead the
*spread* of κ between strategies on one term. KAPPA-EXP-002 refutes the
prediction that structural sharing dissolves that counterexample, and finds the
real reason it does not transfer to Σ-GLYPH: the strategy is pinned normatively,
so there is no second strategy to diverge. KAPPA-EXP-003 asks the spread
question of λ, where the strategy is free, and refutes it under `C_size` while
leaving it open under the corrected `C_dup`, where the measurement is still
rising at the edge of its preregistered grid. KAPPA-EXP-005 will extend that
grid; the range cannot be changed inside KAPPA-EXP-003.

The distributed-prepayment track (Track B) remains formalization work until its
fault model and comparison metric stop moving.

No license has been selected yet. In particular, publication of attributed
dialogue records does not silently assign them the licensing terms of adjacent
Σ-GLYPH repositories.
