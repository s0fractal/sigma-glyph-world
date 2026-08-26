# KAPPA-EXP-002 — does structural sharing dissolve the H-KAPPA counterexample?

**Preregistration. Non-normative. Committed before its measurement harness
exists.** This experiment reads and executes a local checkout of
`s0fractal/sigma-glyph`. It does not modify that repository, does not speak for
it, and does not extend the Σ-GLYPH specification.

## Hypothesis under attack

From [`talks/claude-fable-002.md`](../talks/claude-fable-002.md):

> Сім'я h_n експлодує лише без шарингу — «дерево, без шарингу» записано явно. У
> Σ-GLYPH шаринг структурний: дублікат x — одна адреса, не k вузлів. Тож через
> профіль C1 (λ→SKI) та ж сім'я в оракулі Book I має дати peak лінійний у n, не
> експоненційний, і обидві стратегії — обмежену і близьку κ.

`H-SHARING`: under Σ-GLYPH's hash-thunk representation, `peak` for the
KAPPA-EXP-001 family is linear in `n` rather than `Θ(2^n)`.

**Predicted outcome: `H-SHARING` is false, for a reason the prediction did not
consider.** Predictions and their falsifiers are stated below before the harness
exists.

## The oracle, pinned

- repository: local checkout of `s0fractal/sigma-glyph`
- HEAD: `c78e866420f016adf706f3806593cebc05e47dd0` (`v0.6.7-105-gc78e866`)
- `impl/sigma_glyph.py` SHA-256:
  `413d1f9805cdbdf42f13d967a17be26eb959c692eeb067e7146203ed9cebe64d`
- `spec/book-1-truth.en.md` SHA-256:
  `cc8c41bbe7cd27c3bca51c7a0636d2de8239c91334f230af4d6044b454d7bcd3`

The oracle is imported at run time from that path. Its code is **not** vendored
into this repository: no license has been selected here, and copying another
repository's implementation into an unlicensed notebook would be an outward act
of the kind `AGENTS.md` clause 7 reserves for explicit authorization. If the
checkout or the digest is absent, the harness reports `SKIPPED`, never a pass.

Unlike KAPPA-EXP-001, the strategy is **not a free parameter**: Book I fixes
leftmost-outermost with lazy left-spine resolution normatively (§3.3, ADR-003).
There is therefore no second strategy to vary, and `spread` is undefined on this
machine. That is itself a finding to record, not an obstacle to route around.

## The family, compiled

`h_0 = y`, `h_{n+1} = (λx. p x x) h_n`, identical to KAPPA-EXP-001, with the two
free variables instantiated as non-glyph literals so the terms are closed and
`p x x` is a normal form:

```text
p := LITERAL(sha256("P"))
y := LITERAL(sha256("Y"))
```

Compiled by the normative profile C1 (`spec/book-1-truth.en.md` §6) via
`impl/sigma_glyph.c1`, giving `D := S (S (K P) I) I` and
`h_n := APPLY(D, APPLY(D, … APPLY(D, Y)))`. Every node is written to a `Store`
before evaluation, so no evaluation may end in Unresolved Reference.

Measured range: `n ∈ [1, 12]`, matching KAPPA-EXP-001.

## Measured quantities

Per `n`, under §3.4 pricing:

- `spent` — ATP actually charged;
- `size_tree` — `impl.size` of the normal form, the quantity §3.4's bound is
  about, which counts every materialized node once per occurrence;
- `size_dag` — the number of **distinct** node hashes in the normal form, the
  quantity a content-addressed store holds;
- `peak_tree` — maximum `impl.size` over the trajectory;
- `kappa = (peak_tree − 1) / spent`.

## Preregistered predictions

`DERIVATION`, from reading `step5`, `_step_application`, `_head_reduction` and
`size` at the pinned digest:

1. `size` is a tree recursion (`1 + size(left) + size(right)`) with no
   deduplication, and `_step_application` descends into the argument once the
   function is in normal form. So the whole normal form is materialized, once
   per occurrence.
2. `R-S` prices `1 + size(z)` with `z` in its *current* materialization, and a
   thunk has size 1. So duplication itself is cheap — but it duplicates a thunk,
   and each copy is forced independently afterwards.

Therefore:

| quantity | predicted |
|---|---|
| `size_tree(nf)` | `Θ(2^n)` |
| `size_dag(nf)` | `Θ(n)` |
| `peak_tree` | `Θ(2^n)` |
| `spent` | `Θ(2^n)` |
| `kappa` | `≤ 1` at every `n` |

`DERIVATION`: if these hold, `H-SHARING` is false, and the reason is that
hash-leaf sharing is a property of the **store**, not of the materialized term.
A duplicated subterm shares one address and one hash, but is materialized once
per occurrence, so both `size` and ATP scale with the tree while the store holds
the DAG. The predicted `size_tree / size_dag` gap is exponential.

`DERIVATION`: the counterexample of KAPPA-EXP-001 nonetheless does not transfer
to Σ-GLYPH, for two reasons neither of which is sharing — the strategy is pinned
normatively so no second strategy exists to diverge from, and §3.4 is
materialization-charging so `κ ≤ 1` holds by the theorem in the KAPPA-EXP-001
erratum.

## Controls

1. **Driver equivalence.** `peak` is not observable through `eval_hash`, so the
   harness runs its own loop over the oracle's `step5`. That loop MUST reproduce
   `eval_hash`'s `(result_hash, spent)` exactly for every `n`, or the
   measurement is void rather than reported.
2. **Normal form agreement.** The oracle's normal form MUST have the same hash
   as the C1 compilation of the KAPPA-EXP-001 normal form for the same `n`.
   A mismatch means the two experiments are not measuring the same computation.
3. **Normative bound.** `size(t) − 1 ≤ spent` MUST hold at **every** step, not
   only at the end. This is an independent check of a normative Book I claim on
   a family the spec's own conformance vectors do not cover. A violation is a
   conformance finding and MUST be reported as such, not smoothed.
4. **Digest.** The oracle file's SHA-256 MUST equal the pinned value, or the
   harness reports `SKIPPED`.
5. **No writes.** The harness MUST NOT write to the `sigma-glyph` checkout.

## Falsifiers of the predicted outcome

- `peak_tree` or `size_tree` grows linearly in `n`. Then `H-SHARING` holds, this
  preregistration is wrong, and the KAPPA-EXP-001 counterexample is confined to
  machines without structural sharing.
- `size_dag` grows exponentially. Then the store does not share either, and the
  tree/DAG gap this experiment claims to measure does not exist.
- `kappa > 1` at any `n`. Then §3.4's memory bound does not hold on this family
  in this implementation, which would be a conformance finding about the oracle
  and outranks everything else in this document.

## Scope

- One family, one machine, one pinned digest. Nothing here generalizes to other
  Σ-GLYPH versions, to `impl-rs`, or to `impl-go`.
- Nothing here is a defect claim against Book I. `size` counting a tree rather
  than a DAG is a representation choice, and the bound §3.4 asserts is about
  that same quantity, so a large `size_tree` is not a violation of anything the
  specification promises.
- Any change to the family, the range, the oracle digest, or the measured
  quantities after the harness first runs creates KAPPA-EXP-004 and a fresh
  measurement.
