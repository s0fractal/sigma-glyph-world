# SCOPE-PILOT-002 — component localization and contract admission

**Preregistration. Non-normative. No candidate for this pilot has been
screened.**

The successor instrument is induced by SCOPE-PILOT-001 and the retired-corpus
calibration at commit `b7668fc4d6513176c035c80b3c7915b3e0ab3096`.
Neither earlier corpus may be used for this pilot's agreement measures.

## Question

Can isolated coders, using codebook v1, reproducibly:

1. decide whether the governing success contract is independently established;
2. localize an incident to selector, checker, adapter, or gate interfaces;
3. derive unfenced self-selection from named authority and fence fields; and
4. preserve multicausal and insufficient-evidence outcomes without forcing a
   convenient primary label?

This pilot still does not test `H-SCOPE` or estimate mechanism prevalence.

## Fresh sampling frame

All SCOPE-PILOT-001 repositories and incidents are excluded. Candidate issues
must have been created from `2020-01-01` through `2025-12-31`, inclusive, so the
sample does not depend on issues created during this research session.

The fixed repository frame is stratified by intended control kind:

- tests: `mochajs/mocha`, `vitest-dev/vitest`, `jestjs/jest`,
  `microsoft/playwright`, `cypress-io/cypress`, `nextest-rs/nextest`;
- lint/static analysis: `astral-sh/ruff`, `golangci/golangci-lint`,
  `koalaman/shellcheck`, `python/mypy`, `semgrep/semgrep`, `eslint/eslint`;
- artifact/conformance: `codecov/codecov-action`, `actions/runner`,
  `docker/build-push-action`, `sigstore/cosign`, `ossf/scorecard`,
  `SonarSource/sonarqube`;
- proofs/build completeness: `leanprover/lean4`, `leanprover-community/mathlib4`,
  `coq/coq`, `rocq-prover/rocq`, `seL4/l4v`, `NixOS/nixpkgs`.

For each repository, query closed issues in the date window with each exact term:

```text
"exit code"
"no tests"
"false positive"
"not run"
"ignored"
"reports success"
"zero issues"
```

Deduplicate by canonical issue URL. Sort candidates by
`sha256("SCOPE-PILOT-002\n" + canonical_url)` ascending. Screen in that order,
subject only to the strata constraints below. The query receipts and complete
ordered candidate list are retained.

Search stops at 12 admitted packets or 60 screened candidates, whichever comes
first. No repository contributes more than 2 admitted incidents. The admitted
set must contain at least 3 control kinds and at least 2 cases each expected to
exercise selector, adapter, and gate localization. If the stop limit prevents
those constraints, the pilot reports a sampling failure; it does not replace
repositories or terms.

This is a reproducible codebook-stress sample, not a representative population.

## Admission before mechanism coding

A packet enters blind mechanism coding only if all are true:

1. an automated control and exact governing signal are named;
2. primary evidence demonstrates accept, omission, or false success;
3. the claimed success contract is `ESTABLISHED` or `SUPPORTED` under codebook
   v1 before mechanism labels are assigned;
4. the evidence localizes at least two adjacent component interfaces or marks
   the missing boundary explicitly;
5. stable public primary URLs and retrieval timestamps are retained;
6. the incident concerns the verification control, not only the product defect.

Contract-disputed candidates remain in the rejection/calibration log but never
receive mechanism labels in the blinded scoring set.

## Packet construction separation

The packet builder records evidence and a private sampling assessment. The
blinded render removes repository identity, URLs, private labels, sampling
stratum, and contract status. Coders must derive contract admission from the
included minimized evidence excerpts.

Packet authors do not act as coders. Coders receive one packet at a time in
isolated contexts and cannot see other answers. Exact model/version, prompt
digest, tool access, context contents, and response digest are receipts.

No coder gets web access: a coder judges the frozen packet, not the live issue.
Missing evidence must produce `INSUFFICIENT_EVIDENCE` rather than independent
research that makes packets unequal.

## Controls

The blinded set includes four authored controls outside the incident sample:

1. behavior reproduced, but success contract supported only by reporter
   expectation — must not be admitted;
2. misleading “exit code 0” text inside a gate that still rejects — must be
   `OUT_OF_SCOPE`;
3. checker emits failure, adapter maps it to pass — must localize at adapter;
4. audited selector omits a target, but an independent completeness fence
   rejects — scope self-selection must be `no`.

Control answers are frozen before coder execution. Controls are reported
separately and excluded from agreement coefficients on incidents.

## Measures

Report all raw answers and disagreements, plus:

- exact agreement on admission;
- exact agreement on contract status and evidence tier;
- component-wise agreement on breach ternaries;
- exact agreement on derived scope self-selection;
- pairwise Jaccard agreement on mechanism sets for jointly admitted packets;
- exact agreement on primary outcome, including `MULTICAUSAL` and insufficiency;
- control pass rate by control and coder;
- Krippendorff's alpha only for fields with at least 3 coders, at least 2
  observed categories, and no more than 80% missing pairwise comparisons.

Agreement is prompt- and packet-conditioned instrument behavior, not truth or
independent validation.

## Continuation rule

The instrument is not ready for a confirmatory `H-SCOPE` sample if any occurs:

- admission exact agreement below 80%;
- scope-self-selection exact agreement below 80%;
- any authored control is missed by more than one coder;
- more than 20% of jointly admitted incidents have disagreement between a
  localized component label and `INSUFFICIENT_EVIDENCE`;
- packet identity leakage is demonstrated.

Passing only permits design of a new confirmatory preregistration and new
corpus. It validates neither the taxonomy nor `H-SCOPE`.

## Stop conditions and deviations

- Codebook, prompt, schema, controls, repository frame, queries, and ordering
  rule are committed before search.
- Any change after search begins creates SCOPE-PILOT-003 and a fresh sample.
- API failures, deleted sources, and ambiguous repository renames are recorded;
  they do not authorize substitution outside the frame.
- If fewer than 8 incidents survive the 60-candidate limit, report sampling
  failure and do not run coders.
