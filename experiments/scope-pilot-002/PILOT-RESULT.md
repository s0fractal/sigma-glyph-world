# SCOPE-PILOT-002 — sampling result

**Status: `SAMPLING_FAILURE`. No candidate corpus, screening, or coding.**

## Outcome

The sampler completed 140 of 168 read-only GitHub Search requests and stopped on
the first query for literal repository name `coq/coq`:

```text
gh: Validation Failed (HTTP 422)
```

The sampler wrote neither `candidate-order.json` nor `query-receipts.json`, as
required by its all-or-nothing implementation. No partial query result is being
treated as a frozen sample.

## Cause

`FACT`: the GitHub repository endpoint for `coq/coq` resolves to canonical
repository `rocq-prover/rocq`, which was also independently listed in the fixed
frame. GitHub issue search rejects the old literal in a `repo:` qualifier.

`DERIVATION`: protocol validation checked uniqueness of repository strings, not
uniqueness of resolved repository identities. Therefore the allegedly fresh
24-repository frame contained 23 canonical repositories and one duplicate alias.

This is a harness/frame defect, not evidence about the incident codebook.

## Disposition

The preregistration states that any harness or frame change after search begins
creates a new pilot and fresh sample. Therefore:

- SCOPE-PILOT-002 is retired as a sampling failure;
- completed live queries are not reused as frozen P003 responses;
- codebook v1, coder prompt, schema, and authored controls may be reused by exact
  digest because they did not cause the failure and no coder saw them;
- the successor frame must pin canonical repository IDs before search;
- the successor sampler must retain an append-only per-query checkpoint so an
  API failure is inspectable without promoting a partial sample.

## What did not happen

- No candidate was screened or admitted.
- No incident packet was constructed.
- No coder was run.
- No agreement number exists.
- `H-SCOPE` remains untested.

The absence of a partial artifact is useful fail-closed behavior, but the lack
of a durable failure receipt is a second sampler weakness to correct in P003.
