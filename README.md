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

The first intended empirical track is verification-scope archaeology on public,
third-party incident records. The κ and distributed-prepayment tracks remain
formalization work until their machines and comparison metrics stop moving.

No license has been selected yet. In particular, publication of attributed
dialogue records does not silently assign them the licensing terms of adjacent
Σ-GLYPH repositories.
