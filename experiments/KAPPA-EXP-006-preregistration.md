# KAPPA-EXP-006 — seven quantities, not one cached field

**Preregistration. Non-normative. Committed before its measurement harness
exists.**

## Why this exists

[Codex's review](../reviews/codex-2026-08-26.md), finding 1, showed that the
KAPPA-EXP-001 machine pins "explicit syntax tree, no sharing" and does not have
that representation: `substitute` returns the same object at every occurrence,
so the object graph is a persistent DAG while `Term.size` counts occurrences. At
`n = 8`, `S_in` reports `size = 1021` over **18** distinct objects.

The [erratum](kappa-exp-001/RESULT.md#erratum-2-2026-08-26--representation-and-signature)
took the review's second option: rename the model honestly and retract the
physical reading. This experiment takes the first option as well, and answers
the review's closing question directly:

> whether the claimed phenomenon survives when "tree", "sharing", "materialized
> state", and "actual work" are four separately measured quantities rather than
> four names for one cached `size` field.

## Hypothesis

`H-REPR`: the KAPPA-EXP-001 refutation of `H-KAPPA` is an artifact of conflating
an occurrence-weighted metric with materialization, and dissolves once the
quantities are separated.

**Predicted outcome: false — with the sharper statement that the refutation
holds for exactly those representations that materialize once per occurrence,
and dissolves for those that do not.** `H-KAPPA` was always a claim about a
machine tuple in which representation is a component; this measures that
component instead of assuming it.

## Two representations, one calculus

Both over the same untyped λ, the same two strategies (`S_out` leftmost-outermost,
`S_in` leftmost-innermost), and the same family `h_0 = y`,
`h_{n+1} = (λx. p x x) h_n`. Range `n ∈ [1, 12]`.

- **`R_alias`** — substitution returns the argument object at every occurrence
  and returns a subterm unchanged when the bound name is absent. This is
  KAPPA-EXP-001's actual representation.
- **`R_fresh`** — substitution allocates a new node for every node it writes, so
  no two positions in a term ever share an object. This is the representation
  KAPPA-EXP-001 *said* it had.

## Seven measured quantities

Recorded independently, never derived from one another:

1. `occurrence_size` — the occurrence-weighted tree size, KAPPA-EXP-001's `size`;
2. `distinct_objects` — reachable objects by identity;
3. `distinct_hashes` — reachable subterms by structural content, the DAG size a
   content-addressed store would hold;
4. `allocations` — cumulative node constructions over the whole run;
5. `peak_live` — maximum `distinct_objects` over the trajectory;
6. `steps` — β-contractions;
7. `cost` — under `C_unit`, `C_size`, `C_dup`.

Peaks are taken over the trajectory for 1, 2, 3 and 5.

## Preregistered predictions

`DERIVATION`:

| quantity | `R_fresh` `S_out` | `R_fresh` `S_in` | `R_alias` `S_out` | `R_alias` `S_in` |
|---|---|---|---|---|
| `occurrence_size` peak | `Θ(2^n)` | `Θ(2^n)` | `Θ(2^n)` | `Θ(2^n)` |
| `distinct_objects` peak | `Θ(2^n)` | `Θ(2^n)` | `Θ(2^n)` | `Θ(n)` |
| `distinct_hashes` peak | `Θ(n)` | `Θ(n)` | `Θ(n)` | `Θ(n)` |
| `steps` | `2^n − 1` | `n` | `2^n − 1` | `n` |

So:

- on `R_fresh`, `distinct_objects` equals `occurrence_size` for both strategies,
  `S_in` genuinely materializes `Θ(2^n)` objects in `n` steps, and
  `κ = peak/cost` under `C_unit` still diverges as `Θ(2^n/n)` against a bounded
  `S_out`. **`H-KAPPA` is refuted on a machine that really does not share.**
- on `R_alias` measured by `distinct_objects` rather than `occurrence_size`,
  `S_in`'s peak is linear and its κ is bounded. **The same counterexample
  dissolves.**
- `distinct_hashes` is `Θ(n)` everywhere, so a content-addressed store never sees
  the explosion under either representation — consistent with KAPPA-EXP-002,
  where the Book I oracle's store held `2n + 2` nodes while it materialized
  `4·2^n − 3` objects.

`DERIVATION`: therefore κ is not merely a function of (strategy, cost model) as
the KAPPA-EXP-001 erratum said, but of (representation, strategy, cost model,
size functional), and the last two axes were previously entangled.

## Controls

1. **Reproduction of the frozen machine.** `R_alias` with the `occurrence_size`
   functional MUST reproduce KAPPA-EXP-001's frozen `steps`, `peak`, `cost_unit`
   and `cost_size` exactly at every `n`. Otherwise this experiment is measuring a
   different machine and no comparison with it is valid.
2. **Aliasing control.** On `R_fresh`, no two distinct positions of any term on
   any trajectory may share object identity; the harness fails if they do. On
   `R_alias`, duplicated positions MUST share identity — the two representations
   must be demonstrably different, not accidentally the same.
3. **Same outcome.** All four machines reach α-equivalent normal forms.
4. **No renaming.** Capture-avoiding substitution never α-renames.
5. **Metric consistency.** `distinct_hashes ≤ distinct_objects ≤ occurrence_size`
   at every measured point, for every machine.

## Falsifiers

- On `R_fresh`, `distinct_objects` for `S_in` grows sub-exponentially: then the
  explosion was an artifact of the metric after all and `H-REPR` holds.
- On `R_alias` measured by `distinct_objects`, `S_in`'s κ is *not* bounded: then
  the aliasing does not do what finding 1 says it does.
- Control 1 fails: no comparison with KAPPA-EXP-001 is licensed.
- Control 2 fails in either direction.

## Scope

- One family, one calculus, two representations, two strategies, `n ≤ 12`.
- `allocations` and `peak_live` are counted in the harness's own object model.
  They are a proxy for physical materialization in *this* implementation, not a
  measurement of memory in bytes, and no claim is made about any other runtime.
- KAPPA-EXP-001, 003 and 005 numbers remain measurements of the occurrence
  metric. This experiment does not retroactively reinterpret them; the errata
  already state what they are.
- Any change to representations, family, range, strategies, or measured
  quantities after the harness first runs creates KAPPA-EXP-007.
