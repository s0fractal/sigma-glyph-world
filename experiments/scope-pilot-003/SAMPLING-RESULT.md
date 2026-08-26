# SCOPE-PILOT-003 — sampling result

**Status: `SAMPLING_SUCCESS`. Candidate order frozen; no candidate screened,
no packet built, no coder run.**

This document reports that the P003 sampling substrate executed as
preregistered. It is not a result about the codebook, about coder agreement, or
about `H-SCOPE`.

## Outcome

`FACT`: all 168 preregistered repository/term requests returned successfully.

- 168/168 append-only success checkpoints in [`query-checkpoints/`](query-checkpoints/);
- 0 failure receipts; `query-failures/` was never created;
- retrieval window `2026-08-25T23:40:59Z` .. `2026-08-25T23:49:35Z`;
- every checkpoint carries frame digest
  `2ff05360190a83045c6ced5b8a893852fd288986153db3f0bc431b96bfb2976b`;
- `incomplete_results` was false for every response.

`FACT`: the sampler then derived the two final artifacts from those checkpoints
and refuses to overwrite them:

| artifact | SHA-256 |
|---|---|
| `candidate-order.json` | `2e3d00332101e7ce90e4d186584b4b5cb09906f6bf337d869091dd6600f12bfb` |
| `query-receipts.json` | `02ebf6bb3158cf5191125ae23547e397530c6eccc14e15c2fc4db453566aaa75` |
| `sampling-frame.json` | `2ff05360190a83045c6ced5b8a893852fd288986153db3f0bc431b96bfb2976b` |
| `repository-identities.json` | `633b36e87a8848c225e2d5ef6d0f6f2160619f207f725e5a61752f6b1bb774ff` |

`FACT`: 5276 unique canonical issue URLs were frozen, sorted ascending by
`sha256("SCOPE-PILOT-003\n" + canonical_issue_url)`. 610 of them matched more
than one query term.

`FACT`: the preregistration was committed at `12acd5e` on
`2026-08-25T23:40:53Z`, six seconds before the first request. The alias defect
that retired SCOPE-PILOT-002 did not recur: 24 requested names, 24 canonical
names, 24 unique repository IDs, no archived repository.

## The frame is not the search universe

`FACT`: the frame caps each repository/term request at 100 results. 36 of the
168 requests returned exactly 100 items while reporting a larger `total_count`.
Across the whole run GitHub reported 19943 matches and the sampler retained
5952 item records; 13991 matches fall outside the operational frame.

Truncated requests, by repository: `NixOS/nixpkgs` 5; `jestjs/jest`,
`microsoft/playwright`, `cypress-io/cypress`, `eslint/eslint` 4 each;
`vitest-dev/vitest`, `astral-sh/ruff`, `golangci/golangci-lint`, `python/mypy`
3 each; `actions/runner` 2; `semgrep/semgrep` 1.

`DERIVATION`: truncation is not uniform across the frame. It concentrates in
high-volume repositories, so the 5276 candidates under-represent exactly those
repositories relative to their true match counts. Because each request is sorted
by issue creation time ascending, truncation also biases the retained set toward
older issues within those repository/term pairs.

This is the preregistered sampling convention, not a defect, and not a claim
that 5276 is the population. The pilot measures codebook behavior on a
reproducible candidate order; it does not estimate prevalence.

## Candidate distribution

`FACT`: unique candidates by stratum — lint/static analysis 1933, tests 1843,
proofs/build completeness 848, artifact/conformance 652. 41 of the 168 requests
returned zero items. Every repository contributed at least one candidate;
`seL4/l4v` contributed 1 and `leanprover-community/mathlib4` contributed 7.

`DERIVATION`: the first 60 candidates in frozen screening order — the maximum
the preregistration permits screening — span 18 of 24 repositories and all four
strata, but are concentrated: `NixOS/nixpkgs` 8, `eslint/eslint` 6,
`jestjs/jest` 5, `microsoft/playwright` 5.

`DERIVATION`: the admission constraints therefore bind before the screening
budget does. With at most 2 admitted incidents per repository, the 60-candidate
window can supply at most 36 admissible slots even if every candidate were
otherwise admissible. The binding risk for this pilot is a sampling failure on
the `>= 8` minimum or on the `>= 2` selector/adapter/gate expectation, not on
the 60-screen ceiling.

`UNKNOWN`: whether 8 or more candidates in that window satisfy the codebook v1
admission gate. Screening has not started.

## What did not happen

- No candidate was screened, admitted, or rejected.
- No incident packet was constructed and no blinded render exists.
- No coder was run; no model receipt exists.
- No agreement, Jaccard, alpha, or control pass rate was computed.
- `H-SCOPE` remains untested.

## Reproduction

From the repository root:

```sh
tools/test-all.sh
```

`python3 experiments/scope-pilot-003/sample.py --check` re-verifies every
checkpoint against its expected index, query, repository ID, and frame digest,
re-derives every candidate order hash, and confirms the frozen artifacts match
the checkpoint set. Green execution is reproducibility of a bounded procedure.
It is not review, external validity, or evidence for any mechanism claim.
