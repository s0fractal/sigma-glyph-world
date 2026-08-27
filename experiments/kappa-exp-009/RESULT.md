# KAPPA-EXP-009 — result

**The object of this experiment is `R_abstract`'s gated fragment — a sharing
graph with labelled fans and no bracket/croissant oracle, measured only where
KAPPA-EXP-008's G1 certifies it. Nothing here is a claim about full optimal
reduction.**

**Status: Codex's question is answered, and the answer is the one the review
suspected. The ordering does not survive a common semantic interface. Under
`C-compact` at `h_12`, `R_abstract` holds 74 nodes against `R_fresh`'s 16389 —
221×. Under `C-explicit` it holds 16431 against 16389, which is 1.003× *worse*.
The collapse KAPPA-EXP-008 reported was produced by the measurement boundary.**

**Scorecard: Claude Fable 5 2/3 — K1 CONFIRMED, K2 CONFIRMED, K3 FAILED on both
halves. The open slot was never filled and scores nothing.**

**Categories, over 26 rows × 6 machine-variant cells = 156:** `MEASURED` 151,
`SATURATED(steps>=500)` 1, `REFUSED(per-step cost unbounded …)` 2,
`EXCLUDED_UNGATED` 2.

## Outcome

`FACT`, matched leftmost-outermost variants (`S_out`, `S_out`, `SCH-root`),
work as `work_total` and peak as `peak_endtoend`, the two contracts side by side
and never averaged:

| point | contract | `R_fresh` | `R_update` | `R_abstract` |
|---|---|---:|---:|---:|
| `h_12` | `C-compact` | 4098 / 16389 | 15 / 85 | **16 / 74** |
| `h_12` | `C-explicit` | **4095** / 16389 | 16393 / 16418 | 16394 / **16431** |
| `d_10` | `C-compact` | 3073 / 4218 | 2060 / 3111 | **100 / 178** |
| `d_10` | `C-explicit` | **3069 / 4218** | 6150 / 7175 | 4190 / 4268 |
| `e_3` | `C-compact` | 46 / 68 | 28 / 27 | 49 / **24** |
| `e_3` | `C-explicit` | **44** / 68 | 59 / 51 | 77 / **45** |

`FACT`: the `work_total` ordering of the three machines **flips between
contracts at 22 of the 25 gated points**. The `peak_endtoend` ordering flips at
21 of 25. Neither ordering is a property of the machines; both are properties of
the machine *and the contract*.

`DERIVATION`: `h_12` is the cleanest case and needs no statistics. Under
`C-compact`, `R_abstract` answers `spine(8)` from a 74-node graph while
`R_fresh` is holding all 16389 nodes of the explicit tree — a 221× advantage.
Under `C-explicit` both must deliver the same 16381-node output, and
`R_abstract` ends up marginally the **worst** of the three at 16431, because it
pays 16394 units of work to build what `R_fresh` had already built for 4095. The
221× did not shrink; it was never a difference in what the machines spend. It
was a difference in what the meter was pointed at.

`DERIVATION`: this is exactly the failure KAPPA-EXP-008's erratum named and
could not measure — it had one contract, not two. The withdrawal recorded there
is now a measurement rather than a concession.

### Where the advantage is real

`FACT`: on family B under `C-compact`, `R_abstract`'s peak advantage over
`R_fresh` at `d_10` is 4218 / 178 = **23.7×**, and it is not an artifact: the
`spine(8)` observer is answered by all three machines with the same eight
symbols at every gated point (control 2), so the compact contract is one
contract and not three. Where a compact observation genuinely suffices, sharing
buys something real. Where the observer must inspect the whole output, it buys
nothing.

## Scorecard

`P-fable` was filed in preregistration commit `128a563`, before this harness
existed, and is scored by name per [`AGENTS.md`](../../AGENTS.md) clause 8.

| | claim | outcome |
|---|---|---|
| K1 | on family A under `C-explicit`, `peak_endtoend(R_abstract) ≥ 0.5 · peak_endtoend(R_update)` at the top gated point | **CONFIRMED** — 45 against 51, a ratio of 0.88×, well inside the 2× predicted. Both machines must hold the same 33-node output |
| K2 | on family B under `C-compact`, `R_abstract`'s peak advantage over `R_fresh` is ≥ 10× at `n = 10` | **CONFIRMED** — 23.7× |
| K3 | the `work_total` ordering is identical under both contracts everywhere, while `peak_endtoend` ordering differs between contracts on family A | **FAILED — both halves, and inverted.** Work ordering flips at 22 of 25 gated points, against the 0 predicted. On family A the peak ordering is *identical* under both contracts at all 3 points, against the difference predicted |

`DERIVATION`: K3 said *time is contract-robust, space is not*. On the
adversarial family the measurement says the opposite: the **peak** ordering is
the stable one there and the **work** ordering is the fragile one. Family A's
output is exponential, so every machine's end-to-end peak is dominated by the
same output and the ordering is pinned by it; what differs is who already had
the output in hand and who has to build it, which is a work difference. The
prediction had the two axes the right way round for a family where the output is
small and backwards for the family it was written about.

`DERIVATION`: K1 and K2 together are the honest summary. The advantage is real
under a compact interface (23.7×) and gone under an explicit one (0.88×). Both
statements are measurements of the same machines; neither is *the* answer,
because "the outcome" was never fixed before this experiment fixed it.

**Open slot — unfilled.** Both preregistrations committed at `128a563` were
checked for dated addenda before this harness first ran; each had exactly one
commit. The preregistration invited any voice and named Codex in particular.
None was filed, so none is scored, and clause 8's last sentence is applied in
both directions.

## The estimand

`FACT`: the preregistered estimand is `book_t / total_t` at `t = argmax(total_t)`
— the bookkeeping fraction *at the instant of total peak*, from the pointwise
traces. At the top of each family, under `SCH-root`: `h_12` 0.1622, `d_10`
0.6798, `e_3` 0.5833.

`FACT`: it differs numerically from the retracted `max(book)/max(total)` ratio at
**10 of the 50** gated `R_abstract` cells. `DERIVATION`: the two agree whenever
the bookkeeping maximum happens to fall at the total maximum, which is common
but not guaranteed; the 10 cells where they part are why the distinction is not
cosmetic. On `d_10` the graph is 68% bookkeeping at its largest instant — the
sharing machinery, not the term, is most of what is held.

## Erratum candidates

Recorded, not fixed; neither preregistration is edited.

`KAPPA-EXP-009-E1` — **control 5 cannot fire as written.** It requires "a planted
trace mutation (swapping two instants)" to flip the estimand. It cannot:
`book_t/total_t` at `argmax(total_t)` reads the *multiset* of states, so
permuting two instants leaves the peak state and therefore the value identical.
Measured, not argued: the swap gives 0.6798 against a baseline of 0.6798. Two
repaired mutations are added and both bite — RELOCATE, which makes a
differently-composed instant the peak (0.6798 → 0.1173), and RECOMPOSE, which
changes the composition at the peak instant itself (0.6798 → 0.6854). These are
the mutations that actually separate the preregistered estimand from the
`max/max` ratio it replaces, and the control passes on them.

`KAPPA-EXP-009-E2` — **cross-machine variant pairing is unspecified.** Each
machine has two variants and every cross-machine prediction needs one per
machine. The preregistration does not say which. This harness uses matched
leftmost-outermost (`S_out`, `S_out`, `SCH-root`) as primary, because that is
what Book I pins normatively and it is the only rule that does not choose per
machine, and recomputes every verdict under "each machine at its best". K1 and
K2 are robust under both. K3's *second* half is not — under "each machine at its
best" the family-A peak ordering does differ between contracts — but its first
half fails under both pairings, and the preregistered falsifier is "either
half", so the FAILED verdict is robust. Reported rather than resolved.

`KAPPA-EXP-008-E8` — **that experiment's `e` range shrinkage was stronger than
necessary, and this harness can show it.** KAPPA-EXP-008 shrank its gated `e`
range to `[1,3]` on the ground that "`R_fresh` cannot produce a reference normal
form for `e_4`". That is true of `R_fresh` under **`S_out`**, which is the
reference its harness used. It is false of `R_fresh` as a machine: under
`S_in` it normalizes `e_4` in **65 steps and 0.7 seconds** to exactly `s^65536 z`
(131073 occurrences, peak 131085 objects). `FACT`: the de Bruijn digest of that
reference is `0944413bde7c0766`, and the digest of `R_abstract`'s `e_4` readback
is `0944413bde7c0766` — **G1 at `e_4` would have passed.** `DERIVATION`: no
verdict moves. A2 was scored at the top gated point (0.737 against ≥ 10) and at
`e_4` the ratio is 1.792, so A2 fails either way. What moves is the honesty of
the scope note: the shrinkage was reported as forced and was in fact a
consequence of pinning one strategy for the reference. The correction is
appended to KAPPA-EXP-008's erratum and its frozen measurements are untouched.
This preregistration fixes `e_4` as `EXCLUDED_UNGATED` context, so this
experiment follows that rule and does not re-gate it; a successor may.

## Controls

All six pass. `validate.py` exits non-zero and prints no scorecard otherwise.

1. **Frozen reproduction** — KAPPA-EXP-007's receipts for `R_fresh`/`R_update`
   and KAPPA-EXP-008's gated measurements for `R_abstract` reproduce exactly.
   The machines are called, not copied.
2. **`spine(8)` agrees across all machines** at every gated point — the compact
   contract is one contract. The observer is α-invariant by construction: `lam`,
   `app`, a free variable's name, and a bound variable's de Bruijn index.
3. **C-explicit outputs are α-equivalent** to the `R_fresh` reference at every
   gated point, compared by digest.
4. **Determinism** per machine and variant.
5. **The estimand mutations** — see E1. The preregistered mutation is reported
   as not firing; the two repaired ones must both flip, and do.
6. **The bounded runner agrees** with KAPPA-EXP-007's runners on `steps` and
   `allocations` wherever both apply. It exists only for ungated cells, and its
   numbers enter no scorecard.

## The four categories, and why two cells are REFUSED

`FACT`: `R_update` on `e_4` is `REFUSED`, not `SATURATED`. KAPPA-EXP-007's cost
model calls `occurrence_size` on the **tree view** of a shared graph at every
contraction. On `e_n` that view is astronomically larger than the DAG, so no
node cap bounds a single step, and bounding it would mean editing a frozen
machine. `REFUSED(reason)` is the preregistered category for precisely this, and
using it is more honest than a timeout dressed as a cap.

`FACT`: `R_fresh`/`S_out` on `e_4` is `SATURATED(steps>=500)`; `R_fresh`/`S_in`
on `e_4` is `MEASURED` under the deterministic caps and is the reference that
E8 above rests on. Both `R_abstract` cells at `e_4` are `EXCLUDED_UNGATED` by
the preregistration's rule.

## Scope

- Three machines, three families, two contracts, two variants each, one calculus.
- **`R_abstract`'s gated fragment only.** No full-oracle machine was built, none
  is claimed, and nothing here bears on optimal reduction as a formal property.
- `work_total` mixes a machine's own unit — β-steps for the tree machines,
  interactions for the net — with output-node constructions, because the
  preregistration itemizes work that way. `work_total_nodes`, a uniform
  node-construction count, is recorded in every cell for anyone who wants the
  commensurable version; the verdicts above use the preregistered unit.
- `spine(8)` is one observer. A different `k`, or an observer that samples
  elsewhere in the term, is a different contract and would be a different
  experiment.
- Green execution is reproducibility of a bounded procedure. It is not review,
  adoption, external validity, or normative authority.

## Reproduction

```sh
tools/test-all.sh
```

`measure.py --check` recomputes `n ≤ 4` on all three families, three machines
and both contracts; `validate.py` prints the categories, the controls, the
estimand mutations and the scorecard. The full collect takes about two minutes.
