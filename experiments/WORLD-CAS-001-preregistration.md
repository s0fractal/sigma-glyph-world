# WORLD-CAS-001 — does the live-DAG bound survive persistent storage history?

**Preregistration. Non-normative. Committed before its measurement harness
exists.** Named and posed by ChatGPT's review
([`reviews/chatgpt-2026-08-27.md`](../reviews/chatgpt-2026-08-27.md)), which
found — verified by code reading before that file was committed — that every
"store" number in the κ arc counts **live reachable hashes of the current
term**, while the `Store` is pre-filled before evaluation and never written
during it. `content-addressable ≠ content-stored`. This experiment splits
the conflated quantities and measures which of the arc's Θ(n) sentences
survive an actual persistence policy.

## The three quantities, defined now

Under a **write-through policy** — every node the machine materializes is
`put` into the CAS at the moment of materialization — measure, per run:

- `live_peak` — max over ticks of distinct hashes reachable from the
  current term (what KAPPA-EXP-002/006 actually measured);
- `cas_resident(t)` — objects in the store at tick t under **no GC**
  (monotone by construction);
- `cas_unique_ever` — distinct hashes ever written across the whole
  trajectory, readback included and counted separately
  (`cas_unique_ever_readback`).

## What is decided on paper, and will not be claimed as a finding

`cas_unique_ever ≥ live_peak` always; under no-GC,
`cas_resident(end) = cas_unique_ever` — that identity is a **control**, not
a result. What is genuinely open is growth: whether any machine-family pair
keeps `cas_unique_ever` linear when the store must remember the trajectory
and not just the survivor.

## Machines, families, reuse

`R_fresh`, `R_alias`, `R_update` verbatim from KAPPA-EXP-007 (gate: their
frozen numbers reproduce exactly — the instrumentation must not change one
trajectory). Families `h_n` (n ∈ [1,12]) and `d_n` (n ∈ [1,10]) verbatim.
`R_abstract` is out of scope here (its boundary questions belong to
KAPPA-EXP-009); a scope line in the RESULT must say so.

## Predictions

**P-fable — Claude Fable 5, filed at this commit:**

- **C1.** On `h_n` under `R_update`, `cas_unique_ever ≤ 12·n` at every
  measured n — the trajectory stays linear even cumulatively; in-place
  update touches O(1) new content per level. Falsifier: any n where it
  exceeds `12·n`.
- **C2.** On `h_n` under `R_fresh` with `S_out`, `cas_unique_ever` grows
  Θ(2^n): last-three growth ratios ≥ 1.8. KAPPA-EXP-006's sentence "a
  store never sees the explosion" is then **false under write-through** —
  the store sees exactly the explosion; what never saw it was the live
  window. Falsifier: growth ratios < 1.8.
- **C3.** `cas_unique_ever / live_peak` diverges with n (last-three ratios
  increasing) on at least one machine-family pair — i.e. the live-DAG
  bound does **not** survive persistence history in general. Falsifier:
  the ratio is bounded (non-increasing tail) on every pair.

**Open slot** — any voice, dated addendum before the harness first runs.

## Controls

1. **Reproduction.** All KAPPA-EXP-007 frozen numbers reproduce with
   instrumentation on.
2. **Write-through completeness.** Every hash in any live set at any tick
   is in the ever-written set; a single miss invalidates the policy.
3. **No-GC identity.** `cas_resident(end) = cas_unique_ever`, exactly.
4. **Determinism.** Two runs, identical receipts.
5. **Separation of readback.** `cas_unique_ever` is reported with and
   without readback writes; both appear in every table.

## What would make this experiment worthless

Reporting `live_peak` under any storage-flavored name; mixing readback
writes into the trajectory count without the split; GC of any kind (that
is a successor's policy axis, named now: WORLD-CAS-002); treating the
paper-decided identity as a finding.

## Role separation

The prereg author does not write the harness; the harness author records
open choices in the RESULT's provenance and scores C1–C3 by name.
