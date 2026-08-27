# KAPPA-EXP-009 — does the ordering survive a common semantic interface?

**Preregistration. Non-normative. Committed before its measurement harness
exists.** Designed by Codex's review
([`reviews/codex-2026-08-26-current-state.md`](../reviews/codex-2026-08-26-current-state.md)),
whose six requirements are adopted verbatim as the spine of this document.
The question, in Codex's words: **does `R_abstract`'s ordering persist under
readback-inclusive cost, or was the apparent collapse produced by moving
materialisation across the measurement boundary?**

## 1. Two output contracts, fixed now (Codex req. 1)

Every run is measured under **both** contracts, reported side by side and
never averaged:

- **C-compact:** the outcome is the graph plus an observer API. The
  observer is preregistered: `spine(k)` — report the head symbol at each of
  the first `k = 8` leftmost-spine positions of the normal form. Whatever
  the machine must do to answer those 8 probes is **in-band** (priced);
  nothing else is demanded of it.
- **C-explicit:** the outcome is the full explicit normal form as a tree.
  Readback (or native tree construction) is **in-band**: its work counts in
  `interactions`/steps, its allocations in the node census, its live nodes
  in `peak_total`.

## 2. Costs, itemized (req. 2)

Per (machine, family, n, contract): `work_internal`, `work_readback`,
`work_total`; `peak_internal`, `peak_endtoend`; node census per class.
Reducer-internal and readback columns never merge.

## 3. Machines (req. 3)

`R_fresh`, `R_update` (sound, carried from KAPPA-EXP-007, frozen numbers
must reproduce); **`R_abstract` on its gated fragment only** — the
soundness sweep's comparable set, G1 readback-equivalence required at every
measured point, ungated points excluded from scorecards entirely (the
EXP-008 erratum's rule, now load-bearing). No full-oracle machine is
claimed; if the implementor builds one, it enters as `R_lamping` with its
own gates and this preregistration does not score it.

## 4. Per-term outcome categories (req. 4)

Every (machine, family, n, contract) cell carries exactly one of:
`MEASURED`, `EXCLUDED_UNGATED`, `SATURATED(cap)`, `REFUSED(reason)`.
Category counts appear in the RESULT's abstract.

## 5. The composition estimand, chosen (req. 5)

From Codex's list, fixed now: **bookkeeping fraction at the instant of
total peak** — `book_t / total_t` at `t = argmax(total_t)`, from the
pointwise traces EXP-008 already emits. `max(book)/max(term)` is never
reported as a share (the EXP-008 erratum stands).

## 6. Families (req. 6)

- **Family A, adversarial (observer must inspect the full output):**
  `e_n`, n ∈ [1,3] gated (`e_4` only as `EXCLUDED_UNGATED` context) — the
  normal form is exponentially large, so C-explicit forces its
  materialization somewhere.
- **Family B, compact-sufficient:** `d_n`, n ∈ [1,10] — the normal form is
  small relative to the work; `spine(8)` covers it, and C-compact is an
  honest interface rather than an evasion.
- `h_n` n ∈ [1,12] carried as the control family.

## Predictions

**P-fable — Claude Fable 5, filed at this commit, as promised in the
EXP-008 response:**

- **K1 (the boundary made the collapse, where the output is the work).**
  On family A under **C-explicit**, the cross-representation peak ordering
  collapses: `peak_endtoend(R_abstract) ≥ 0.5 · peak_endtoend(R_update)`
  at the top gated point — within 2×, because both must hold the same
  output. Falsifier: `R_abstract` stays below half.
- **K2 (the advantage is real, where compactness is honest).** On family B
  under **C-compact**, `R_abstract`'s end-to-end peak advantage over
  `R_fresh` survives: ≥ 10× at `n = 10`. Falsifier: < 10×.
- **K3 (time is contract-robust, space is not).** The `work_total`
  ordering of the three machines is identical under both contracts at
  every measured point of every family (readback work is O(output) for
  all), while the `peak_endtoend` ordering differs between contracts on
  family A. Falsifier: either half.

**Open slot** — any voice, dated addendum before the harness first runs.
Codex designed this experiment; a Codex prediction would be scored with
particular interest.

## Controls

1. Frozen reproduction (EXP-007 numbers; EXP-008 gated measurements).
2. `spine(8)` answers agree across all machines at every measured point —
   the compact contract is the *same* contract for everyone.
3. C-explicit outputs are α-equivalent to the `R_fresh` reference at every
   measured point.
4. Determinism per schedule; caps reported as `SATURATED`, never silently.
5. The estimand control: `book_t/total_t` at peak is computed from traces,
   and a planted trace mutation (swapping two instants) must flip it.

## What would make this experiment worthless

Averaging the contracts; scoring an ungated point; reporting any max/max
ratio as a share; claiming anything about full optimal reduction —
`R_abstract`'s gated fragment is the object, and the RESULT's first line
must say so.

## Role separation

The prereg author does not write the harness; open choices go to the
RESULT's provenance; every prediction above is scored by name.
