# EML basis — transcription log

Corpus for EML-EXP-001 and EML-EXP-002, built before either harness exists,
under section 1.1 of
[`experiments/EML-EXP-001-002-preregistration-draft.md`](../EML-EXP-001-002-preregistration-draft.md)
(committed verbatim at `418038a`) and deltas D1 and D4 of
[`reviews/claude-fable-2026-08-27-eml-draft.md`](../../reviews/claude-fable-2026-08-27-eml-draft.md).

Nothing here is a measurement. No hypothesis is scored, no null model is drawn,
no `measure.py` exists in this directory. This file records what was fetched,
what was transcribed, and every change made to a transcription between the
first run of the control and the green one.

## 1. Source pin (D1)

`FACT` — the external input was fetched once, on 2026-08-27, as follows.

| field | value |
|---|---|
| paper | Andrzej Odrzywołek, *All elementary functions from a single operator* |
| arXiv id | 2603.21852 |
| version pinned | **v2**, 2026-04-04 (v1 was 2026-03-23) |
| requested URL | `https://arxiv.org/e-print/2603.21852v2` |
| resolved URL | `https://arxiv.org/src/2603.21852v2` |
| **format used** | **TeX e-print source tarball (gzip)** — the PDF fallback was *not* needed |
| bytes | 1274423 |
| **SHA-256** | **`2a3b4219a7784d8fd0b3ffe6e7d3dd570cf73d60f8cf368459122fe78e1421db`** |

`FACT` — the digest covers exactly the bytes returned by that fetch: the gzipped
tar containing `EML.tex`, `EML.bib`, `00README.json`, `Fig1_graph_spiral.pdf`,
`Fig2_trees.pdf` and `anc/SupplementaryInformation.pdf`. The Supplementary
Information is *inside* the pinned tarball, so it is covered by the same digest;
no second fetch was made and no follow-up literature was consulted.

`FACT` — the operator, main text Eq. (3): `eml(x, y) = exp(x) − ln(y)`, with the
constant `1`, evaluated internally over ℂ on the principal branch.

## 2. What was transcribed, and from where

`FACT` — the paper's table of goal operations with their EML constructions is
**Supplementary Information, Table S2 (p. 6), "Complete EML bootstrapping
chain", steps 1–32**. The main text contains no such table: main-text Table 1
is the *starting list* of primitives, Table 2 is the reduction sequence, and
Table 4 gives LeafCounts without expressions. Only three constructions appear in
the main text at all (`e`, `exp`, `ln`).

`FACT` — Table S2 states each witness over *previously discovered* primitives,
not in pure EML. `basis.json` therefore carries three levels per entry, and the
relation between them is mechanical substitution, never simplification:

- `witness_paper` — the Table S2 row, verbatim (e.g. `arsinh(1/tan(arccos(x)))`);
- `chain_sexpr` — the same expression with the paper's primitive names;
- `eml_sexpr` — the expansion down to `{eml, 1, x, y}`, which is what the
  draft's §"Encoding" requires.

`FACT` — totals across the 32 expansions: 692375 `eml` nodes, 692407 leaves,
maximum depth 260. The largest single construction is `artanh` at 504554 nodes;
the smallest are `e` and `exp` at 1.

### 2.1 Cross-checks that the expansion is the paper's own

`FACT` — three independent anchors in the paper agree with the expansion
produced here:

- `ln` expands to `(eml 1 (eml (eml 1 x) 1))`, which is main-text Eq. (4)
  character for character, and its RPN serialisation is `11xE1EE` with
  LeafCount 7 — both stated in main text Sect. 4.1.
- `x × y` expands to 20 `eml` nodes, LeafCount 41; main-text Table 4 gives the
  EML compiler 41 for `x × y`.
- `half(1) = 1/2` expands to 45 nodes, LeafCount 91; main-text Table 4 gives the
  EML compiler 91 for the constant `1/2`.

`CONTESTED` — most other Table 4 EML-compiler LeafCounts do *not* match the
chain expansion (e.g. `−x`: chain 17, compiler 57; `x − y`: chain 11, compiler
83; `π`: chain 199, compiler 193). This is expected rather than alarming: the
paper calls the compiler an "unoptimized prototype" and reports its numbers
separately from direct search. It does mean **Table 4 cannot be used as a
checksum on this transcription**, and it is not used as one. Nothing in
`basis.json` was adjusted to make a Table 4 number come out.

## 3. Control (draft §1.1)

`FACT` — `transcription_check.py` implements §1.1: 200 pseudo-random points per
construction, `mpmath` at `mp.dps = 50`, agreement required to
`|eml − target| ≤ 1e-30 · max(|target|, 1)`. The unit floor is stated in the
script and is needed because `sin`, `artanh`, `arsinh` and others have zeros
inside their domains, where a purely relative criterion is undefined; away from
those zeros the criterion is exactly "1e-30 relative".

`FACT` — the point set is derived, not drawn from a stateful PRNG, so it is
reproducible across Python versions and languages:

```
seed = "EML-EXP-001-002/transcription-control/v1"
u(id, var, k, d) = int.from_bytes(sha256(f"{seed}|{id}|{var}|{k}|{d}")[:16], "big") / 2**128
```

with `k` the 0-based point index and `d` the 0-based draw index (`d > 0` only
where a rejection sampler redraws an excluded interval). `u` is then mapped
through the sampler recorded in that construction's `domain` block in
`basis.json`. Both the seed and the derivation are constants in the script.

`FACT` — `mpmath` was not present. Installed for this user only:
`pip3 install --user --break-system-packages mpmath` → **mpmath 1.4.1**, into
`~/Library/Python/3.14/lib/python/site-packages`. The `--break-system-packages`
flag was required by PEP 668 on this Homebrew Python; it does not change where
the package lands, which is still the per-user site directory. Python 3.14.7.

`FACT` — final run: **PASS, 32 of 32**. Worst deviation anywhere over the whole
basis is `2.54e-48`, eighteen orders of magnitude inside the `1e-30` gate. The
largest imaginary part surviving at any root is `4.26e-47`.

## 4. Changes made between the first run and the green run

Two changes. Neither edits a construction.

### T1 — four constructions do not compute their target on the negative half of its domain

**First run:** `FAIL 4 of 32` — `arccos`, `artanh`, `arcsin`, `arctan`. Every
failure was at a negative argument; every positive argument passed at `~1e-49`.
First reported deviation: `arccos` at `x = −0.4126536009398481`.

**What was checked first.** Whether this was a transcription error. The Table S2
rows were re-read from a 600 dpi render of SI p. 6 before anything else was
changed. They read, verbatim:

```
27  arsinh(x)  6  ln(x + hypot(-1, x))
28  arcosh(x)  5  arsinh(hypot(x, sqrt(-1)))
29  arccos(x)  4  arcosh(cos(arcosh(x)))
30  artanh(x)  5  arsinh(1/ tan(arccos(x)))
31  arcsin(x)  5  pi/2 - arccos(x)
32  arctan(x)  4  arcsin(tanh(arsinh(x)))
```

That is exactly what was transcribed. **No transcription error was found, and
nothing in the transcription was changed.**

**What the paper's construction actually computes.** `FACT`, measured at 50
digits: each of the four returns the target evaluated at `|x|`, exactly.

| x | construction | `arccos(x)` | `arccos(|x|)` |
|---|---|---|---|
| `+0.4126536009398481` | `1.1454309781988448267` | `1.1454309781988448267` | `1.1454309781988448267` |
| `−0.4126536009398481` | `1.1454309781988448267` | `1.9961616753909484118` | `1.1454309781988448267` |

`DERIVATION` — the mechanism. Step 28's witness reaches `x` only through
`hypot`, and `hypot(a, b) = sqrt(a² + b²)` squares it, so the EML `arcosh` is an
even function of `x`. On `x ≥ 1`, `arcosh`'s own real domain, that is harmless,
and step 28 verifies on the full domain. Step 29 applies `arcosh` at `|x| < 1`,
*off* that domain, where the discarded sign cannot be recovered; the EML
`arccos` therefore computes `arccos(|x|)`. Steps 30, 31 and 32 all reach `x`
through step 29 and inherit it. Agreement with the target at `|x|` to all 50
digits identifies the mechanism rather than a numerical accident.

`CONTESTED` — SI Sect. 1.3 describes precisely this failure mode as a rejection
criterion. It reports that the candidate `arcsin(x) = arccos(sin(arccos(x)))`
was discarded as a "flaky witness" because it "passes at `x = γ` but fails
(wrong sign) at `x = −γ`". The accepted step-29 witness
`arccos(x) = arcosh(cos(arcosh(x)))` has the same shape and the same defect, and
was not discarded. This is a defect in the paper, not in the transcription, and
it is recorded here rather than repaired.

**Change made.** The construction is unchanged. The §1.1 control now samples the
sub-domain on which the paper's construction computes the target, and every
affected entry carries a `domain_restriction` block in `basis.json` naming the
full target domain, the checked sub-domain, the mechanism and a counterexample.
`transcription_check.py` prints a `RESTRICT` marker for those rows and lists
them under a "checked on a RESTRICTED sub-domain" heading on every green run, so
the restriction cannot be read past.

| id | target's real domain | checked on |
|---|---|---|
| `eml_arccos` | `\|x\| ≤ 1` | `0 ≤ x ≤ 1` |
| `eml_artanh` | `\|x\| < 1` | `0 ≤ x < 1` |
| `eml_arcsin` | `\|x\| ≤ 1` | `0 ≤ x ≤ 1` |
| `eml_arctan` | `x ∈ ℝ` | `x ≥ 0` |

`UNKNOWN` — whether the paper's `rust_verify` accepts these four because its
probe constants γ ≈ 0.577 and A ≈ 1.282 are positive, or for some other reason.
SI Sect. 1.3 says sign-flipped probes were added as safeguard (ii) in the Rust
version; that safeguard should have caught step 29. Not investigated further:
that is a question about the paper's tool, not about this corpus.

### T2 — `complex_reason` for `sqrt` and `log_x y` was wrong about *when*

**Was:** "`ln(ln x)` is complex whenever `0 < x < 1`" (`eml_sqrt`), and "ln of a
negative argument inside the quotient" (`eml_logb`).

**Measured:** both still show `max|Im| = π` on a window of `[1.5, 2.5]`, where
every argument exceeds 1, and both are purely real (`max|Im| = 0` exactly) on
`[4, 20]`. The threshold is `e`, not `1`: the halving and the quotient take `ln`
of `ln x`, which is negative for `x < e`.

**Change made:** the two `complex_reason` strings, only. No construction and no
domain changed; the entries were flagged `complex: true` before and after.

### Not a change, recorded for completeness

`FACT` — the `complex` flag asserted in `basis.json` matched the measured
imaginary parts for all 32 constructions on the first run. The control fails a
construction whose flag contradicts what it measures, so the flag EML-EXP-002
excludes by is itself under control rather than being taken on trust.

## 5. `FACT` lines required by the task and by D4

`FACT` — **32 goal operations were transcribed.** Every one of them is a row of
SI Table S2, steps 1 through 32.

`FACT` — **the paper's "36" is not the number of goal operations, and the paper
says so itself.** Main-text Sect. 3 claims the procedure "re-generates all 36
elementary operations from Table 1", and main-text Table 1 does list 36
primitives (8 constants/variables + 20 unary functions + 8 binary operations).
But the caption of SI Table S2 states: *"Four missing from 36 entries listed in
Table 1 of main text are: two variables `x, y`, constant `1`, and imaginary
unit."* The two variables and the constant `1` are the grammar's terminals, not
things to construct; the imaginary unit is simply not reconstructed by the
chain. **32, not 36, is the count.** D4 is upheld: 36 was a claim, it was
checked, and it does not match. The main text's "all 36" and the SI's "32
remaining primitives ... four missing" are inconsistent with each other inside
the same version, v2.

`FACT` — **complex/real split, over the 32 transcribed constructions:**

| class | count | ids |
|---|---|---|
| `complex` (routes through `i`) — all of them `real_via_complex` | **23** | see the two rows below |
| — of those, route via **Euler** (complex at *every* point of the domain) | 10 | `pi`, `cos`, `sin`, `tan`, `arsinh`, `arcosh`, `arccos`, `artanh`, `arcsin`, `arctan` |
| — of those, **argument-dependent** (complex only for some arguments) | 13 | `sub`, `add`, `inv`, `mul`, `sqr`, `div`, `half`, `avg`, `sqrt`, `pow`, `logb`, `hypot`, `tanh` |
| purely **real** (`max\|Im\|` exactly `0` at every sampled point) | **9** | `e`, `exp`, `ln`, `neg1`, `two`, `minus`, `sigma`, `cosh`, `sinh` |
| **complex-valued targets** | **0** | — the imaginary unit is one of the four Table-1 entries the chain does not reconstruct |

`FACT` — because no target is complex-valued, `complex == true` and
`evaluation_class == "real_via_complex"` coincide exactly on this basis: all 23
flagged constructions are real-target constructions with complex intermediates,
verified to return a vanishing imaginary part (largest surviving `|Im|` at any
root over the whole basis: `4.26e-47`).

`FACT` — measured, not assumed: on a window where every argument is `≥ e`, all
thirteen `argument_dependent` constructions evaluate with `max|Im|` exactly `0`,
and all ten `euler` constructions do not. The distinction is recorded per entry
as `complex_route` in `basis.json`.

`DERIVATION` — for EML-EXP-002, whose exclusion rule is "anything routed through
`i`" and whose grid `x ∈ {0.1, 0.25, 0.5, 1, 1.5, 2, 3, 5}` is entirely
positive: the 10 `euler` constructions are excluded by name unconditionally, and
the 13 `argument_dependent` ones are complex or not depending on where the grid
sits relative to `e` — six of the eight grid values are below it. That is a
sentence about which names the split preregistration must list, not a
measurement; the draft's own §"Basis subset" wording ("trigonometry via Euler,
and anything derived from it") maps onto the 10, not the 23.

## 6. Files

| file | what it is |
|---|---|
| `basis.json` | the corpus: 32 constructions, source pin, per-entry domain and flags |
| `build_basis.py` | the transcription instrument: Table S2 chain → pure EML. `--check` verifies `basis.json` is what it builds |
| `transcription_check.py` | the §1.1 control. Exits non-zero on any FAIL |
| `TRANSCRIPTION_LOG.md` | this file |

No `measure.py` exists here and none should: EML-EXP-001 and EML-EXP-002 are
preregistered separately and their harnesses live in their own directories.
`tools/test-all.sh` is deliberately left untouched — wiring the control into it
would add the repository's first third-party dependency, and that belongs to the
preregistration split, not to the corpus.
