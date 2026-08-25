# SCOPE-PILOT-002 — codebook v1

**Frozen before candidate search.** This codebook operationalizes
SCOPE-INSTRUMENT-001 and applies only to a fresh pilot corpus.

## 1. Admission

Return `ADMIT` only when the packet establishes:

- an automated verification control;
- one exact governing success signal;
- observed acceptance or omission;
- an `ESTABLISHED` or `SUPPORTED` success contract;
- a causal connection inside selector, checker, adapter, gate, statement,
  provenance, or trusted-core boundaries.

Return `CONTRACT_DISPUTED` when behavior is reproducible but the relevant
meaning of success has only reporter expectation, an unmerged proposed fix, or
conflicting sources. Return `INSUFFICIENT_EVIDENCE` when behavior or component
interfaces are not established. Return `OUT_OF_SCOPE` when the named governing
gate rejected, the check failed closed, or only the product under test was
defective.

Do not assign mechanism labels unless admission is `ADMIT`.

## 2. Governing signal and contract

The governing signal is the exact process status, required check, report field,
or UI state relied on for acceptance. Diagnostic text that does not govern the
outcome is evidence but not the gate.

Contract evidence tiers:

- `T1_NORMATIVE`: version-pinned official specification or documentation;
- `T2_EXECUTABLE`: existing assertion or merged regression test encoding the
  relevant pass/fail boundary;
- `T3_ADJUDICATED`: maintainer adjudication tied to reproduced behavior;
- `T4_REPORTED`: reporter expectation or unmerged proposed fix;
- `NONE`: no evidence states the relevant boundary.

Derive contract status:

- consistent T1 or T2 -> `ESTABLISHED`;
- consistent T3 -> `SUPPORTED`;
- T4 only or conflicting tiers -> `DISPUTED`;
- NONE -> `UNKNOWN`.

Higher-tier evidence controls only the contract it actually states. A generic
promise such as “reports errors” does not establish whether completeness is
per-path, per-file, or over a union.

## 3. Component topology

Identify components by interfaces, not packages:

| role | input | output |
|---|---|---|
| `selector` | claimed universe and selection configuration | actual target set |
| `checker` | target plus statement | raw outcome |
| `adapter` | raw outcomes | gate vocabulary/result object |
| `gate` | adapted result and governing policy | accept/reject signal |

For each role code `breach = yes/no/unknown`, cite evidence identifiers, and
state whether restoring that component's local contract while holding other
observed links fixed would change the gate to reject.

## 4. Scope authority

Name:

- `audited_object`: what the success signal claims about;
- `scope_authority_object`: what chooses selector scope;
- `authority_relation`: `same`, `independent`, `shared`, or `unknown`;
- `selected_scope`: `empty`, `incomplete`, `complete`, or `unknown`;
- `completeness_fence`: `independent`, `self_owned`, `none`, or `unknown`.

Derive `scope_self_selection = yes` only when relation is `same` or `shared`,
scope is empty or incomplete, and the fence is none or self-owned. Derive `no`
when relation is independent or an independent fence rejects omission.
Otherwise return `unknown`.

Version-control location alone does not establish authority. A self-owned floor
or manifest does not become independent merely because it is a separate file.

## 5. Mechanism labels

- `UNFENCED_SCOPE_SELF_SELECTION`: the scope derivation is `yes`.
- `EMPTY_SCOPE_SUCCESS`: an established non-empty contract governs an empty
  effective scope that accepts.
- `CHECKER_MISSED_CONDITION`: intended target and statement reach the checker,
  but its raw outcome violates the checker contract.
- `ADAPTER_MISREPRESENTED_RESULT`: the adapter receives a raw outcome and emits
  a contrary gate-vocabulary result.
- `GATE_OMITTED_OR_IGNORED_RESULT`: the gate receives or should invoke an
  adequate result but does not await, propagate, or enforce it.
- `CLAIM_WEAKENED`: the established checked statement does not entail the
  property named by success.
- `PROVENANCE_IDENTITY_MISMATCH`: result and governed artifact differ in
  revision, configuration, environment, or identity.
- `TRUSTED_CORE_INVALID_ACCEPTANCE`: a named trusted validation boundary accepts
  an invalid witness after receiving the intended target and statement.

Assign every evidenced label. `EMPTY_SCOPE_SUCCESS` is structural and normally
co-occurs with a localized breach.

## 6. Primary outcome

For each breached component, test a local contract-restoring intervention.

- one sufficient repair site -> choose its mechanism label;
- several sufficient sites -> `MULTICAUSAL`;
- no localizable site -> `INSUFFICIENT_EVIDENCE`.

Do not use narrative order, package ownership, or the historical fix choice to
break a tie. A historical fix proves one sufficient site; it does not prove
other sites insufficient.

## 7. Required counterclassification

Name the strongest alternative admission, scope, or component result. State one
specific fact which, if added or contradicted, would change your coding. “No
alternative” is invalid.

## 8. Epistemic discipline

Use only the packet. Keep observed evidence separate from derivation. Repository
familiarity, likely documentation, and assumptions about common tool behavior
are not evidence. When a required interface or contract is absent, return the
appropriate disputed or insufficient value.
