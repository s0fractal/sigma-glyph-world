# WORLD-CAS-001 — result

**Status: the live-DAG `Θ(n)` sentences do not survive persistence. Under a
write-through content-addressable store, the live window on `h_n` holds `5n`
hashes while the store ever holds `3·2^n + 3`. ChatGPT's review was right that
`content-addressable ≠ content-stored`, and the gap is exponential, not
constant.**

**Scorecard: Claude Fable 5 2/3 — C1 FAILED, C2 CONFIRMED, C3 CONFIRMED. The
open slot was never filled and scores nothing.**

## Outcome

`FACT`, at the top of each range, under write-through with no GC:

| family | machine | strategy | `live_peak` | `cas_unique_ever` | ratio |
|---|---|---|---:|---:|---:|
| `h_12` | `R_fresh` = `R_alias` | `S_out` | 60 | **12291** | 204.9 |
| `h_12` | `R_fresh` = `R_alias` | `S_in` | 29 | 108 | 3.7 |
| `h_12` | `R_update` | `S_out` | 29 | 174 | 6.0 |
| `h_12` | `R_update` | `S_in` | 29 | 108 | 3.7 |
| `d_10` | `R_fresh` = `R_alias` | `S_out` | 73 | **21243** | 291.0 |
| `d_10` | `R_update` | `S_out` | 98 | 14497 | 147.9 |

`FACT`, closed forms on `h_n`, exact at every `n ∈ [1, 12]` and re-derived by
`validate.py` on every green run:

```text
cas_unique_ever, R_fresh and R_alias, S_out   = 3·2^n + 3
cas_unique_ever, R_fresh and R_alias, S_in    = (n² + 5n + 12)/2
cas_unique_ever, R_update,            S_out   = n² + 2n + 6
cas_unique_ever, R_update,            S_in    = (n² + 5n + 12)/2
live_peak,       every machine,       S_in    = 2n + 5
live_peak,       R_fresh/R_alias,     S_out   = 5n           (n ≥ 3)
```

`FACT`: on `d_n` no closed form is offered; the measured growth ratios of
`cas_unique_ever` at the top of the range are 2.0428, 2.0269, 2.0166 under
`R_fresh`/`S_out` and 1.9817, 1.9845, 1.9883 under `R_update`/`S_out`. Both are
exponential; only the constant differs.

`DERIVATION`: the explosion was never in the *term*. Under `S_out` the machine
contracts the outermost redex first, so every intermediate state is a distinct
mixture of reduced and unreduced copies — `2^n − 1` of them — and each mixture
has a content no earlier state had. The live window never holds more than `5n`
of those at once, which is exactly what KAPPA-EXP-002 and KAPPA-EXP-006
measured and called "the store". A store that must remember the trajectory
rather than the survivor sees all `3·2^n + 3`.

### Two things the store cannot see

`FACT`: **`R_fresh` and `R_alias` are identical in every CAS quantity** — same
`live_peak`, same `cas_unique_ever`, same `cas_resident_end`, in all 22 rows
and both strategies. At `h_12`/`S_out` their allocation counts differ by 2×
(139080 against 69633) and their materialized-object counts by 2× as well, and
the store records the same 12291 contents either way.

`DERIVATION`: content addressing is blind to aliasing by construction — two
objects with the same content have one address. The axis KAPPA-EXP-006 was
built to separate ("does substitution reuse the argument object?") is exactly
the axis a CAS cannot observe. That is not a defect of either experiment; it is
the price of the addressing scheme, and it means no CAS-based measurement can
ever adjudicate `R_fresh` against `R_alias`.

`FACT`, measured and not assumed: **readback writes nothing new anywhere** —
`cas_unique_ever_readback = 0` in all 132 measured cells. `DERIVATION`: making a
shared normal form explicit duplicates *occurrences*, and every occurrence of a
subterm has the content its siblings have. A content-addressed store already
holds it. Both columns are reported in every table, per control 5, and they are
equal everywhere.

## Scorecard

`P-fable` was filed in the preregistration commit `128a563`, before this harness
existed. It is scored by name per [`AGENTS.md`](../../AGENTS.md) clause 8.
`validate.py` prints all four lines on every green run.

| | claim | outcome |
|---|---|---|
| C1 | on `h_n` under `R_update`, `cas_unique_ever ≤ 12·n` at every measured `n` | **FAILED** — `n² + 2n + 6` under `S_out`, which crosses `12n` at `n = 10` and reaches 174 against 144 at `n = 12`. Three breaches, all under `S_out`; under `S_in` the bound holds at every `n` |
| C2 | on `h_n` under `R_fresh`/`S_out`, `cas_unique_ever` grows `Θ(2^n)`, last-three ratios ≥ 1.8 | **CONFIRMED** — exactly `3·2^n + 3`; ratios 1.9981, 1.9990, 1.9995 |
| C3 | `cas_unique_ever / live_peak` diverges on at least one machine-family pair | **CONFIRMED** — on **all 12** pairs; worst is `R_alias`/`S_out` on `d_n` at 291.0× |

**Open slot — unfilled.** Both preregistrations committed at `128a563` were
checked for dated addenda before this harness first ran; each had exactly one
commit and no addendum. No second voice preregistered on this measurement, so
none is scored, and clause 8's last sentence is applied in both directions.

`DERIVATION`: C1's number failed because C1's *reason* was wrong. It argued that
"in-place update touches O(1) new content per level". Under content addressing
an object's address is a function of its whole subtree, so mutating a node moves
the address of that node **and of every ancestor**. A write-through store must
path-copy, and one contraction therefore writes `Θ(n)` new contents, not `O(1)`
— giving `Θ(n²)` cumulatively where the live DAG stays `Θ(n)`. In-place update
is the one thing a persistent content-addressed store cannot do cheaply, and it
is precisely the mechanism KAPPA-EXP-007 credited for collapsing the separation.

`DERIVATION`: C2 is the sentence-level correction. KAPPA-EXP-006's RESULT says
"a store never sees the explosion". Under write-through that is **false**: the
store sees exactly the explosion — `3·2^n + 3` against a live window of `5n`.
What never saw it was the live window. The earlier sentence was true of the
quantity it measured and false of the quantity its wording implied, which is the
same error KAPPA-EXP-006 and 007 each caught once before, one level up.

## Erratum candidates

Recorded, not fixed; the preregistration is unedited.

`WORLD-CAS-001-E1` — **C1 does not name a strategy.** Every other quantity in
this arc is reported per strategy, and C1's outcome depends on the choice: under
`R_update`/`S_in` the bound `≤ 12n` holds at every measured `n`, and under
`R_update`/`S_out` it fails from `n = 10`. The stated falsifier is "any n where
it exceeds `12·n`", which fires on the `S_out` column, so the verdict is FAILED
and both columns are reported. A successor should quantify the strategy.

`WORLD-CAS-001-E2` — **the write-through policy is underdetermined for a
mutating machine.** The preregistration defines the policy as "every node the
machine materializes is `put` at the moment of materialization". For the
immutable tree machines that is unambiguous: materialization is allocation. For
`R_update`, `become()` replaces a node's content **without allocating**, and it
moves the address of every ancestor as well. Two readings were available:

1. hook allocation only — then control 2 fails by construction on `R_update`,
   because live contents exist that were never written;
2. hook allocation *and* path-copy the reachable closure after each in-place
   update — then control 2 holds, and it holds **by construction** on
   `R_update` while remaining a genuine test of the constructor hook on
   `R_fresh` and `R_alias`.

This harness takes reading 2, because reading 1 makes the machine unmeasurable
rather than making a measurement. The consequence is stated rather than hidden:
control 2 is a real check on two of the three machines and a tautology on the
third. C1's verdict depends on this choice — under reading 1 the question would
not have an answer at all — and a successor that wants a strategy-free C1 must
settle the policy in the preregistration.

## Controls

All six pass. `validate.py` exits non-zero and prints no scorecard otherwise.

1. **Reproduction** — every field of every KAPPA-EXP-007 frozen receipt
   reproduces exactly with the instrumentation live, across all 132 runs. The
   machines are not copied: [`measure.py`](measure.py) calls KAPPA-EXP-007's own
   `tree_run` and `graph_run`, and [`cas.py`](cas.py) patches the constructors,
   `become`, `FINDERS` and `distinct_hashes` at runtime and restores them after
   each run. Not one line of KAPPA-EXP-006's or KAPPA-EXP-007's source is
   modified.
2. **Write-through completeness** — at every tick the live reachable content set
   is recomputed independently and checked against the ever-written set. Zero
   misses. See E2 for where this control is load-bearing and where it is not.
3. **No-GC identity** — `cas_resident(end) = cas_unique_ever` exactly, in every
   cell. This is decided on paper and is reported as a control, never as a
   finding, exactly as the preregistration demands.
4. **Determinism** — every cell is run twice and the full receipt, both traces
   included, must be identical.
5. **Separation of readback** — `cas_unique_ever` and
   `cas_unique_ever_readback` are separate fields in every row; the second is 0
   everywhere and is reported rather than folded in.
6. **`live_peak` is the old quantity** — `live_peak` equals KAPPA-EXP-007's
   frozen `peak_distinct_hashes` in every cell, which is what licenses the claim
   that this experiment splits the arc's conflated quantity rather than
   measuring a new one. `live_peak` is never given a storage-flavoured name.

## Provenance and open choices

- **Digest**: blake2b-128 over `(kind, name, child digests)`. A Merkle address,
  so an object's address is a function of its subtree — the property that forces
  path copying.
- **Policy**: write-through, no GC. GC is named as the successor's axis,
  `WORLD-CAS-002`, and none is implemented here.
- **Readback accounting**: the normal form is walked as a DAG with a memo rather
  than expanded to a tree. A content-addressed `put` is idempotent, so the *set*
  of contents an expanded tree would write is exactly the set the DAG walk
  writes; only the redundant `put` count would differ, and the preregistration
  asks for distinct hashes. `put_calls` is reported separately for anyone who
  wants the redundant count.
- **Tick boundary**: one tick per call of the machine's own `distinct_hashes`,
  which KAPPA-EXP-007's drivers invoke exactly once before the loop and once per
  step. The tick sequence is therefore the machine's, not the instrument's.

## Scope

- Two families, three machines, two strategies, one calculus, one policy.
- **`R_abstract` is out of scope here.** Its boundary questions — what counts as
  in-band, what readback costs — belong to KAPPA-EXP-009, and mixing them into a
  storage-policy experiment would repeat the error KAPPA-EXP-008's erratum
  records.
- No GC, so nothing here bears on any store that reclaims.
- `cas_unique_ever` counts contents, not bytes, and no claim is made about any
  real storage system.
- Green execution is reproducibility of a bounded procedure. It is not review,
  adoption, external validity, or normative authority.

## Reproduction

```sh
tools/test-all.sh
```

`measure.py --check` recomputes `n ≤ 6` on both families and all six
machine-strategy pairs with the instrumentation live; `validate.py` prints the
controls, the closed forms and the scorecard. The full collect takes about two
minutes.
