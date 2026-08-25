# SCOPE-INSTRUMENT-001 — operational component model

**Instrument-development exercise. Non-normative. Does not score `H-SCOPE`.**

This instrument responds to the construct ambiguities found in
[`../scope-pilot-001/PILOT-RESULT.md`](../scope-pilot-001/PILOT-RESULT.md). It
uses retired pilot packets only as calibration attacks. No calibration output
may be reported as independent coding or moved into a confirmatory corpus.

## Unit of localization

Packaging is not a component boundary. A command, plugin, action, or service may
contain several components; several packages may jointly implement one.
Components are identified by semantic interfaces:

1. `selector`: maps a claimed universe to the targets actually presented for
   checking;
2. `checker`: evaluates the claimed property on each presented target and emits
   raw outcomes;
3. `adapter`: converts raw outcomes into the result vocabulary consumed by the
   governing gate;
4. `gate`: produces the actual accept/reject signal relied on by the named
   automation context.

Every topology names all four. A component not implicated in the incident is
still present with `breach = no`; an unobserved boundary uses `unknown`.

## Two objects, not one

Each incident names separately:

- `audited_object`: the object about which the governing success signal makes a
  claim;
- `scope_authority_object`: the configuration, manifest, annotation, graph, or
  caller input that determines the selector's universe.

Their `authority_relation` is one of:

- `same`: both are mutable under the same authority domain;
- `independent`: scope is fixed by an authority independent of the audited
  object;
- `shared`: either side can change effective scope;
- `unknown`: public evidence does not establish ownership.

Version control location is not sufficient evidence of authority.

## Completeness fence

A completeness fence is a control that compares selected targets with an
independently owned inventory or fails on a missing/empty selection before the
checker result can govern acceptance.

Allowed values are `independent`, `self_owned`, `none`, and `unknown`.
Self-owned assertions may improve visibility but do not break self-selection.

`scope_self_selection = yes` is derived only when:

1. `authority_relation` is `same` or `shared`;
2. selected scope is `empty` or `incomplete`; and
3. the completeness fence is `none` or `self_owned`.

It is `no` when authority is independent or an independent fence rejects the
omission. Otherwise it is `unknown`.

## Claimed success contract

Observed behavior alone does not establish what success claims. Each topology
names the `governing_signal` and records contract evidence:

| tier | evidence |
|---|---|
| `T1_NORMATIVE` | version-pinned official documentation or specification |
| `T2_EXECUTABLE` | an existing assertion or merged regression test that encodes the boundary |
| `T3_ADJUDICATED` | maintainer adjudication tied to the reproduced behavior |
| `T4_REPORTED` | reporter expectation or an unmerged proposed fix |
| `NONE` | no source states the claimed boundary |

Contract status is:

- `ESTABLISHED` for consistent T1 or T2 evidence;
- `SUPPORTED` for consistent T3 evidence;
- `DISPUTED` for conflicting evidence or T4-only evidence;
- `UNKNOWN` for `NONE`.

Only `ESTABLISHED` and `SUPPORTED` contracts may enter a future incident corpus.
`DISPUTED` remains useful calibration data but cannot establish false
acceptance.

## Mechanism labels v1

- `UNFENCED_SCOPE_SELF_SELECTION`: the derived scope condition above is `yes`.
- `EMPTY_SCOPE_SUCCESS`: the effective selected scope is empty and the
  governing gate accepts under an established or supported non-empty contract.
- `CHECKER_MISSED_CONDITION`: the checker receives the intended target and
  statement but emits a raw outcome contrary to its contract.
- `ADAPTER_MISREPRESENTED_RESULT`: the adapter receives a raw outcome but emits
  a governing vocabulary value contrary to its contract.
- `GATE_OMITTED_OR_IGNORED_RESULT`: the gate has an adequate adapted result but
  does not invoke, await, propagate, or enforce it.
- `CLAIM_WEAKENED`: the established checked statement does not entail the
  property named by the governing success signal.
- `PROVENANCE_IDENTITY_MISMATCH`: the result and governed artifact differ in
  revision, configuration, environment, or identity.
- `TRUSTED_CORE_INVALID_ACCEPTANCE`: a named trusted validation boundary accepts
  an invalid witness after receiving the intended target and statement.

`EMPTY_SCOPE_SUCCESS` is a structural condition, not a substitute for locating
the component breach. It normally co-occurs with another label unless the
checker's own established contract explicitly treats the empty set as passing.

## Primary mechanism

For every breached component, record one local intervention that restores its
contract while holding other observed links fixed. A component is a sufficient
repair site if that intervention changes the governing outcome to reject.

- exactly one sufficient repair site: its label may be primary;
- more than one sufficient repair site: `MULTICAUSAL`;
- no admissible success contract: `CONTRACT_DISPUTED` or `CONTRACT_UNKNOWN`;
- evidence cannot localize a repair site: `INSUFFICIENT_EVIDENCE`.

This is not a claim that the chosen repair is the historical root cause. It is
an operational statement about the supplied causal topology.
