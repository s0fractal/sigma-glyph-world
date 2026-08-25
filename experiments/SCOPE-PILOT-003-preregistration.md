# SCOPE-PILOT-003 — canonical-frame retry

**Preregistration. Non-normative. No P003 search request has been made.**

SCOPE-PILOT-002 failed during sampling because its frame treated `coq/coq` and
`rocq-prover/rocq` as different repositories even though both resolve to the
same GitHub repository ID. No P002 candidate artifact was frozen and no
screening or coding occurred.

P003 repeats the P002 instrument question with only two sampling-substrate
changes:

1. the repository frame is pinned by canonical GitHub repository ID, and the
   duplicate alias is replaced by `agda/agda` in the same proofs/build stratum;
2. every query response or failure receives an append-only checkpoint before
   sampling proceeds.

## Reused frozen instrument

The following P002 artifacts are reused without modification:

- codebook SHA-256:
  `3c9261450ffe3553a984788e5f764cc4f829624155b53b5272ae4ebc3f7f8e01`;
- coder prompt SHA-256:
  `9b4c3c277b263d350d8dd22bac8f7d4444e98134f1b1e7a64fc6b1f3e174abf1`;
- `experiments/scope-pilot-002/coding.schema.json`;
- the four P002 authored controls and `control-key.json`.

They were committed before P002 search, were not exposed to coders, and did not
cause the sampling failure. P003 coder receipts continue to use their exact
digests.

## Question and admission

The question, component topology, contract tiers, admission gate, controls,
coder isolation, measures, and continuation thresholds are exactly those in
[`SCOPE-PILOT-002-preregistration.md`](SCOPE-PILOT-002-preregistration.md).
`H-SCOPE` remains out of scope.

## Sampling frame

The machine-readable frame is
[`scope-pilot-003/sampling-frame.json`](scope-pilot-003/sampling-frame.json).
It retains:

- issue creation window `2020-01-01..2025-12-31`;
- closed issues only;
- the seven exact P002 query terms;
- at most 100 results per repository/term, sorted by creation time ascending;
- ordering by `sha256("SCOPE-PILOT-003\n" + canonical_issue_url)`;
- stop at 12 admitted or 60 screened;
- at most 2 admitted incidents per repository, at least 3 control kinds, and at
  least 2 expected selector, adapter, and gate cases;
- sampling failure if fewer than 8 incidents survive 60 screens.

The 24 repository names, canonical names, numeric GitHub IDs, archive states,
and URLs were resolved before P003 search and are frozen in
[`scope-pilot-003/repository-identities.json`](scope-pilot-003/repository-identities.json).
All IDs must be unique and every requested name must equal its canonical name.

## Append-only query protocol

There are exactly 168 ordered repository/term requests. For each request:

1. verify its expected index, query text, repository ID, and frame digest;
2. if a valid success checkpoint exists, do not query again;
3. otherwise make the read-only GitHub Search request;
4. on success, atomically write one immutable checkpoint containing minimized
   returned items, counts, retrieval time, and raw-response SHA-256;
5. on failure, atomically append a failure receipt and stop without deleting
   successful checkpoints.

A later run may resume after a transient failure by skipping valid checkpoints.
Failure receipts remain. An identity mismatch, changed query, or changed frame
requires a new pilot rather than resume.

Only after all 168 success checkpoints exist may the sampler write
`candidate-order.json` and `query-receipts.json`. Those final files are derived
deterministically from checkpoints and may not overwrite existing files.

P002 live responses are not checkpoints and are not reused.

## Search and coding stop rules

Candidate screening follows the frozen hash order. All decisions and reasons are
retained. Search stops at the same P002 limits. No packet construction or coder
execution starts unless the minimum sample and stratum conditions hold.

Any change to the frame, canonical identities, queries, ordering, admission,
codebook, controls, prompt, or schemas after the first P003 request creates a
new pilot and fresh sample.
