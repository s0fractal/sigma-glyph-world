# KAPPA-EXP-006 — result

**Status: `H-REPR` refuted. The phenomenon survives the separation — and the
separation shows exactly which representations it holds for.**

[Codex's review](../../reviews/codex-2026-08-26.md) closed with the question this
experiment answers:

> whether the claimed phenomenon survives when "tree," "sharing," "materialized
> state," and "actual work" are four separately measured quantities rather than
> four names for one cached `size` field.

They are four different quantities. The answer is yes, on the representations
that materialize per occurrence, and no on the ones that alias.

## Outcome

`FACT`, at `n = 12`, `S_in` / `S_out` separation of `κ = (peak − 1)/cost` under
`C_unit`:

| representation | by occurrence size | by materialized objects |
|---|---:|---:|
| `R_fresh` — every written node is new | **341×** | **341×** |
| `R_alias` — substitution reuses the argument object | 341× | **1.21×** |

`DERIVATION`: `H-KAPPA` is refuted on a machine that genuinely does not share,
where the metric and the materialization coincide. The same counterexample
**dissolves** on the aliasing machine once materialization rather than occurrence
count is the metric. `H-REPR` — that the refutation was an artifact of the
conflation — is false; what was an artifact was the claim that KAPPA-EXP-001's
machine demonstrated the physical version.

## The four names were four quantities

`FACT`, `S_in` at `n = 12`:

| quantity | `R_fresh` | `R_alias` | growth |
|---|---:|---:|---|
| occurrence size ("tree") | 16381 | 16381 | `4·2^n − 3`, both |
| distinct objects ("materialized state") | 16381 | **30** | `Θ(2^n)` vs `Θ(n)` |
| distinct content hashes ("sharing") | 29 | **29** | `Θ(n)`, both |
| cumulative allocations ("actual work") | 32790 | **90** | `Θ(2^n)` vs `Θ(n)` |

`FACT`: the same four for `S_out` at `n = 12` are 16389, 8196, 60, and 139080 on
`R_fresh`; 16389, 8196, 60, and 69633 on `R_alias`.

`DERIVATION`: **aliasing helps exactly one strategy.** Leftmost-innermost
duplicates an argument that is already in normal form, so the copies stay
identical forever and one object serves both positions — 30 objects and 90
allocations for a term of occurrence size 16381. Leftmost-outermost duplicates
*before* reducing, so the two copies immediately diverge and must be
materialized separately: 8196 objects even on the aliasing machine, `Θ(2^n)`.

`DERIVATION`: content addressing is `Θ(n)` under **both** representations and
both strategies. A store never sees the explosion. This is KAPPA-EXP-002's
finding reproduced in a second machine: there the Book I oracle's store held
`2n + 2` nodes while the evaluator materialized `4·2^n − 3` objects.

## Which machines the refutation applies to

`DERIVATION`: `H-KAPPA` falls for a machine iff its representation materializes
duplicated subterms per occurrence. That class is not empty and is not exotic:

- `R_fresh` here, by construction;
- the **Σ-GLYPH Book I reference implementation**, checked at object level in
  [KAPPA-EXP-002](../kappa-exp-002/RESULT.md#checked-at-object-level): 1021
  distinct Python objects for `size_tree = 1021` at `n = 8`, because `R-S`
  aliases a thunk but each copy is forced independently afterwards.

`DERIVATION`: it does **not** apply to a machine that shares reduction — one
where contracting a redex updates every occurrence at once. Such a machine is
`R_alias`-like for every strategy, not only for the innermost one, and the
separation collapses.

`DERIVATION`: therefore κ is a function of **(representation, size functional,
strategy, cost model)**. The KAPPA-EXP-001 erratum said (strategy, cost model);
that was two axes short, and the two it missed were exactly the two the review
found entangled in one cached field.

## Controls

All six hold across all 12 values of `n`:

- `reproduces_kappa_exp_001` — `R_alias` under the occurrence functional
  reproduces KAPPA-EXP-001's frozen `steps`, `peak`, `cost_unit` and `cost_size`
  exactly. This experiment is measuring that machine, so the comparison is
  licensed.
- `no_aliasing_on_R_fresh` — every term on every `R_fresh` trajectory is
  traversed and the harness raises if any node is reachable by two paths.
- `aliasing_present_on_R_alias` — the other direction, so the two
  representations are demonstrably different rather than accidentally the same.
- `same_normal_form` — all four machines reach α-equivalent normal forms.
- `no_renaming` — capture-avoiding substitution never α-renamed.
- `metric_ordering` — `hashes ≤ objects ≤ occurrences` at every measured point.

## What this does not establish

- `allocations` and `peak_live` are counted in this harness's object model. They
  are a proxy for materialization in *this* implementation, not bytes, and no
  claim is made about any other runtime.
- One family, one calculus, two representations, two strategies, `n ≤ 12`.
- KAPPA-EXP-001, 003 and 005 remain measurements of the occurrence metric. This
  experiment does not reinterpret their numbers; their errata state what they
  are.
- Nothing about a machine that shares *reduction* rather than storage. That
  machine is described above and was not built.

## Reproduction

```sh
tools/test-all.sh
```

`measure.py --check` recomputes `n ≤ 8` on all four machines. The full collect
over the preregistered range takes about twenty seconds. Green execution is
reproducibility of a bounded computation. It is not review, adoption, or
external validity.
