# KAPPA-EXP-007 — does sharing *reduction* remove the separation?

**Preregistration. Non-normative. Committed before its measurement harness
exists.** Two predictions are recorded, attributed separately, per
[`AGENTS.md`](../AGENTS.md) clause 8. The result scores each by name.

## The question

[KAPPA-EXP-002](kappa-exp-002/RESULT.md) left an untested `HYPOTHESIS`: an
evaluator that shares *reduction* rather than only storage would collapse
`peak` to `size_dag` and with it the `S_out`/`S_in` separation.
[KAPPA-EXP-006](kappa-exp-006/RESULT.md) sharpened the class boundary to
"materializes duplicated subterms per occurrence" and noted that a machine which
shares reduction was not built.

[`reviews/claude-fable-2026-08-26.md`](../reviews/claude-fable-2026-08-26.md)
observes that Book I normatively pins leftmost-outermost — the strategy for
which thunk aliasing is powerless, since it duplicates *before* reducing — so
only sharing reduction can help it, and proposes this experiment.

`H-UPDATE`: on a machine that updates a redex in place so every occurrence sees
the result, the `S_out`/`S_in` separation of κ disappears.

## The third representation

Added to the two of KAPPA-EXP-006:

- **`R_update`** — call-by-need graph reduction. Substitution aliases the
  argument, as in `R_alias`, and contraction **mutates the redex node in place**,
  so every reference to that node observes the contracted term. This is
  Wadsworth's 1971 graph reduction.

`R_alias` and `R_fresh` are carried over unchanged and must reproduce
KAPPA-EXP-006's frozen numbers exactly.

## Two families

1. **`h_n`** — duplication **not** under a binder, from KAPPA-EXP-001.
   `h_0 = y`, `h_{n+1} = (λx. p x x) h_n`. Range `n ∈ [1, 12]`.
2. **`d_n`** — duplication **under a binder**, with the two calls given different
   arguments so their results cannot coincide:
   ```text
   D    = λx. λw. p (x w) (x (q w))
   d_0  = λw. y
   d_{n+1} = D d_n
   ```
   Range `n ∈ [1, 10]`.

`FACT`: `d_n` was selected as an instrument **before** this preregistration by
probing it on the already-published `R_fresh` machine only, never on `R_update`.
It shows a growing separation there — 1.96 at `n = 4`, 8.13 at `n = 6`, 15.58 at
`n = 7` — so it can witness a collapse. That probe is instrument selection, not
a test of `H-UPDATE`, and its numbers are recorded here rather than discovered
later.

## Prediction A — attributed to `reviews/claude-fable-2026-08-26.md`

1. On `h_n`, the separation **disappears** for both strategies under `R_update`.
   Wadsworth 1971; graph reduction was invented for exactly this.
2. On a family whose duplication sits **under a λ-abstraction**, the separation
   **returns**, because updating a thunk does not help when the copies are
   instantiated differently. Lévy: call-by-need is not optimal; only Lamping's
   optimal reduction removes it.
3. If 2 holds, the class boundary for `H-KAPPA` becomes *"does not share
   reduction under a binder"* rather than *"materializes per occurrence"*.

## Prediction B — attributed to this repository

Sharper on 1, and differing from A on 2:

1. On `h_n`, the separation is **exactly 1.00** at every `n`, because both
   strategies traverse identical trajectories once the duplicated node is
   updated in place — not merely "small".
2. On `h_n` under `R_update`, `distinct_objects` is `Θ(n)` for **both**
   strategies, where KAPPA-EXP-006 measured `Θ(2^n)` for `S_out` even on
   `R_alias`.
3. On `d_n` the separation **persists and grows in `n`**, agreeing with A — but
   it is **strictly smaller than on `R_fresh` at every `n ≥ 4`**, because the
   shared `D`-application at each level is contracted once instead of twice even
   though the two instantiations are not shareable. A says the separation
   returns; B says it returns *attenuated*, and the difference is measurable.

`FACT`: this repository's last seven preregistered predictions include one wrong
in both directions at once. Prediction B is offered under that record, not
against it.

## Controls

1. **Reproduction.** `R_alias` and `R_fresh` reproduce KAPPA-EXP-006's frozen
   `steps`, peaks and costs on `h_n` exactly. Otherwise no comparison is valid.
2. **Update actually updates.** On `R_update` there must exist at least one step
   where contracting one redex reduces the reachable redex count by more than
   one, and the harness fails if no such step occurs on `h_n` — otherwise the
   machine is `R_alias` under another name.
3. **Same outcome.** All six machines reach α-equivalent normal forms on both
   families.
4. **No renaming.** Capture-avoiding substitution never α-renames.
5. **Metric ordering.** `hashes ≤ objects ≤ occurrences` everywhere.
6. **Root identity.** Under `R_update` the root object is never replaced, only
   mutated, so in-place update is what is being measured.

## Falsifiers

- `h_n` separation under `R_update` is not 1.00 → B.1 fails; if it is also large,
  A.1 fails and `H-UPDATE` survives nothing.
- `d_n` separation under `R_update` collapses to ≈1 → A.2 and B.3 both fail,
  `H-UPDATE` holds, and the class boundary is *not* about binders.
- `d_n` separation under `R_update` is **not** smaller than on `R_fresh` → B.3
  fails while A.2 stands.
- Control 2 fails → the third representation is not a third representation.

## Scope

- Two families, three representations, two strategies, one calculus.
- Optimal reduction (Lamping; Asperti and Guerrini) is **not** implemented. If
  the separation persists on `d_n`, that is consistent with the prior art and is
  not a measurement of it.
- Any change to representations, families, ranges, strategies, or measured
  quantities after the harness first runs creates KAPPA-EXP-008.
