# SCOPE-PILOT-001 — incident codebook v0

**Frozen for pilot sampling.** This version is expected to fail. Revisions are
recorded in `PILOT-RESULT.md` and apply only to a future corpus.

## Admission gate

Code a packet only if all are true:

1. an automated verification control was intended to inspect an artifact or
   property;
2. the control produced a false acceptance, omission, or materially false
   success signal;
3. public evidence supports a causal connection between mechanism and false
   acceptance;
4. the defect belongs to the control, harness, statement, or trusted checker —
   not merely to the product being checked;
5. at least one stable report URL exists.

Otherwise return `OUT_OF_SCOPE` or `INSUFFICIENT_EVIDENCE`.

## Mechanism labels

Labels are multilabel. Assign every evidenced mechanism, then choose one primary
mechanism: the earliest evidenced link in the causal chain whose removal would
have prevented the false acceptance. If two links are independently sufficient,
primary is `CONTESTED` and the ambiguity must be explained.

### `SCOPE_SELF_SELECTED`

The artifact or repository being audited controls which relevant artifacts,
paths, targets, rules, or cases the control inspects.

Include when changing an in-repository manifest, discovery pattern, ignore list,
path filter, generated target list, or equivalent can exclude the defect-bearing
surface while the control still reports success.

Do not include merely because configuration is version-controlled. The causal
test is whether the audited side can remove relevant scope without an external
completeness check noticing.

### `VACUOUS_ACCEPTANCE`

The invoked control checks an empty or semantically empty set and still reports
success indistinguishably from a non-empty pass.

Examples include zero collected tests accepted as green, a theorem quantified
over an uninhabited type, or a conformance runner with zero discovered vectors.
An incomplete but non-empty scope is not automatically vacuous.

### `STATEMENT_WEAKENED`

The checked statement, oracle, schema, or test assertion no longer entails the
property claimed in the success signal.

This includes gutted definitions and assertions that cannot fail. It does not
include an adequate statement applied to the wrong or incomplete target; that is
scope.

### `TOOL_BLIND_SPOT`

The intended target and statement reach the tool, but the analyzer, compiler,
runner, or integration fails to observe a relevant condition within its claimed
operating envelope.

Known documented limitations are included only when the surrounding success
signal failed to disclose that the property was not checked.

### `TRUSTED_CORE_DEFECT`

The trusted checker, proof kernel, validator core, or result-verification logic
accepts an invalid witness despite receiving the intended target and statement.

Compiler or elaborator bugs are not kernel defects unless invalid acceptance
crosses the stated trusted boundary.

### `PROVENANCE_STALE_OR_MISMATCHED`

The evidence or success signal was valid for a different revision, artifact,
configuration, or environment than the one it was used to justify.

This label concerns identity and freshness, not missing scope within the same
revision.

### `HARNESS_ORCHESTRATION_DEFECT`

The intended check exists and is adequate, but orchestration fails to invoke it,
propagate its exit status, await it, or attach its result to the governing gate.

Use `SCOPE_SELF_SELECTED` as well when the omission is controlled by an audited
manifest or filter. Use only this label when the omitted invocation is fixed by
external orchestration.

## Scope-control ternary

Answer `yes` only when the causal evidence shows that the audited artifact or
repository could influence relevant target selection without an independent
completeness fence.

Answer `no` when the failed control’s scope was fixed externally or the mechanism
occurred after complete target selection. Answer `unknown` when the available
evidence does not establish where target selection lived.

This field is not derived mechanically from the primary label. A tool blind spot
may coexist with self-selected scope; a scope defect may be introduced by an
external CI service and therefore answer `no`.

## Evidence confidence

- `VERIFIED`: executable reproducer, regression test, or fixing change proves
  the failure boundary.
- `SUPPORTED`: primary-source maintainer evidence states the cause and fix, but
  the packet lacks an executable boundary.
- `TENTATIVE`: inference from incomplete primary evidence or secondary sources.

Only `VERIFIED` and `SUPPORTED` packets enter blinded coding.

## Required counterclassification

Every coding answer must name the strongest competing primary label and one
specific missing or contrary fact that would make that competitor primary. “No
alternative” is invalid. The purpose is to expose where the codebook forces a
choice the evidence does not.

