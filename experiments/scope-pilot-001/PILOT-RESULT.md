# SCOPE-PILOT-001 — corpus-construction result

**Status: `CONTESTED` codebook; corpus frozen; independent coding not run.**

This is a result about the measurement instrument before inter-rater numbers.
It is not a result about the prevalence hypothesis `H-SCOPE`.

## Outcome first

`DERIVATION`: codebook v0 is not yet precise enough for confirmatory sampling.
Corpus construction exposed three decisions that can change a primary label
without changing the incident evidence:

1. **Tool versus harness boundary.** A wrapper, reporter, importer, and aggregate
   task can all receive the relevant result and still emit success. The current
   boundary between `TOOL_BLIND_SPOT` and `HARNESS_ORCHESTRATION_DEFECT` depends
   on which component the researcher calls “the tool,” not on an operational
   test in the codebook.
2. **Identity of the audited artifact.** A policy selector, build graph, workflow
   path list, and test platform annotation may each choose scope. The current
   `SCOPE_SELF_SELECTED` rule does not say whether the audited object is the
   product artifact, the verification manifest, or the whole repository.
3. **Success contract.** An empty or partial run is a false acceptance only
   relative to a claimed gate. For options such as “error when no files are
   found,” issue evidence can demonstrate behavior while leaving `CONTESTED`
   whether the promise is per declared path or over their union. The admission
   gate needs a hierarchy for normative documentation, maintainer statements,
   executable behavior, and reporter expectation.

These are pre-coding construct ambiguities. Running several models now would
measure how their implicit component boundaries happen to align, not only how
clearly they apply the frozen taxonomy.

## What was frozen before search

`FACT`: preregistration and codebook v0 were committed as
`099077757d8b27426cc6c1d9debcf0ed62299ab4` before candidate packets were
written.

The frozen documents are:

- [`../SCOPE-PILOT-001-preregistration.md`](../SCOPE-PILOT-001-preregistration.md)
- [`CODEBOOK.md`](CODEBOOK.md)

No codebook clause was edited after evidence collection began. Proposed changes
below apply only to a successor pilot and a fresh corpus.

## Construction receipts

`FACT`:

- search stopped at the preregistered first boundary: 12 admissible incidents;
- 20 candidates were screened and 8 were rejected with retained reasons;
- admitted packets cover 12 unrelated repositories and 4 control kinds;
- researcher sampling metadata marks 7 external-scope negative controls and 7
  expected multilabel cases;
- 10 packets are `VERIFIED` and 2 are `SUPPORTED` under codebook v0;
- every packet has a public primary-source URL, causal chain, reproducer status,
  counterclassification, and separate facts, derivations, and unknowns;
- deterministic blinded renders exclude repository URLs and researcher labels.

The counts above are construction checks, not prevalence estimates and not
coder-agreement measures. The sample was deliberately enriched for mechanisms
likely to attack the codebook.

Artifacts:

- [`candidates.json`](candidates.json) — queries, admissions, and rejections;
- [`incident.schema.json`](incident.schema.json) — packet shape;
- [`packets/`](packets/) — sourced researcher packets;
- [`blind/`](blind/) — deterministic evidence-only renders;
- [`render_blind.py`](render_blind.py) — identity-reduction transform;
- [`validate.py`](validate.py) — preregistered sampling and provenance checks.

Run from the repository root:

```sh
tools/test-all.sh
```

Green execution means only that the checked corpus is internally consistent and
the blinded files reproduce. It is not review, adoption, or evidence for
`H-SCOPE`.

## Researcher assessment is not a coder result

`FACT`: packet authorship and preliminary classification were performed in the
same research context. The `researcher_assessment` field exists to verify the
purposive sampling controls and to record where ambiguity was noticed. It is
removed from blinded renders.

`DERIVATION`: recoding those renders in the same context would not be blind or
independent. Therefore this repository reports no exact agreement, Jaccard,
alpha, or scope-agreement number. Missing numbers here are a preserved boundary,
not an incomplete calculation.

## Decisions for a successor codebook

These decisions are proposals, not retroactive repairs:

1. Define a component graph for every incident: `selector -> checker -> result
   adapter -> governing gate`. Assign `TOOL_BLIND_SPOT` only inside the checker;
   assign `HARNESS_ORCHESTRATION_DEFECT` after the checker boundary.
2. Name the audited object and the scope-authority object separately. Code
   self-selection only when they share an authority domain and no independently
   owned completeness fence exists.
3. Add `CLAIMED_SUCCESS_CONTRACT` to each packet, with evidence priority:
   version-pinned normative documentation, accepted regression test, maintainer
   adjudication, then reporter expectation. Reporter expectation alone cannot
   promote a disputed contract above `CONTESTED`.
4. Replace “earliest causal link” with a minimal-cut question: which smallest
   evidenced set of links must change to prevent false success? Select a primary
   only if exactly one codebook mechanism covers every minimal cut.
5. Add a separate field for the governing signal (`process_status`, required
   check, report summary, UI state, or another named oracle). Misleading text
   inside an already failing gate is not a false acceptance.

Because these changes were induced by this corpus, the 12 packets are retired
for instrument development after coding. They cannot become the confirmatory
sample for `H-SCOPE`.

## What remains unknown

- `UNKNOWN`: whether independent coders can agree after the successor boundaries
  are operationalized.
- `UNKNOWN`: whether repository identity can be removed sufficiently; minimized
  causal details may still fingerprint a famous incident.
- `UNKNOWN`: the prevalence of scope-self-selected incidents relative to a
  matched ordinary-CI baseline.
- `UNKNOWN`: whether the eventual taxonomy generalizes beyond GitHub issues and
  exit-status-heavy search language.

## Deviations

No sampling stop, repository cap, control-kind minimum, confidence gate, or
provenance requirement was relaxed. Independent coding was intentionally not
run because no independent coding contexts were authorized in this work session.
This document records that boundary instead of manufacturing agreement from one
researcher.
