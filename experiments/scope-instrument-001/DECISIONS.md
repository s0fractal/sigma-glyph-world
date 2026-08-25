# SCOPE-INSTRUMENT-001 decisions

These decisions are induced by the retired SCOPE-PILOT-001 corpus. They do not
retroactively change its codebook or classifications.

## D001 — component identity follows interfaces

`DECISION`: remove `TOOL_BLIND_SPOT` and `HARNESS_ORCHESTRATION_DEFECT` from the
successor vocabulary. Localize the breach to `checker`, `adapter`, or `gate` by
the first violated input/output contract, regardless of package boundaries.

`RATIONALE`: the same result-normalization code can be called a tool, wrapper,
CLI, plugin, or harness without changing behavior.

## D002 — split audited object from scope authority

`DECISION`: record both objects and their authority relation. A repository path
alone does not imply self-selection.

`RATIONALE`: a policy, test manifest, workflow, build graph, and external CLI
argument may live near one another while belonging to different control
authorities.

## D003 — require an independently evidenced success contract

`DECISION`: reporter expectation and reproducibility establish behavior, not the
meaning of success. T4-only contract claims are `DISPUTED` and fail admission.

`RATIONALE`: otherwise any surprising but documented no-op can be promoted into
a false acceptance by restating the reporter's desired semantics.

## D004 — name the governing signal

`DECISION`: every topology identifies the exact process status, required check,
report field, or UI state that governed acceptance.

`RATIONALE`: “failed with exit code 0” inside a UI that still marks the test
failed is misleading text, not a false acceptance.

## D005 — stop forcing a primary label through prose

`DECISION`: use sufficient repair-site interventions. Multiple sufficient sites
produce `MULTICAUSAL`; lack of a contract produces a contract status, not a
guessed mechanism.

`RATIONALE`: “earliest causal link” depends on narrative ordering and can turn
the defect-bearing product input into the alleged verification defect.

## D006 — empty scope is a modifier

`DECISION`: retain empty-scope success as an observable structural label while
also localizing the breach that allowed it to govern acceptance.

`RATIONALE`: zero tests can arise from a selector, checker convention, adapter,
or gate. The count alone does not locate the failure.
