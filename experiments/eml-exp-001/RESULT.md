# EML-EXP-001 — result

**Status: `H-EML-SHARE-revised` holds, on both clauses of Amendment 1's
scoring rule — and the per-function picture is the opposite of what three of
the four voices expected. The basis beats the nulls only where it is big.**

## Outcome

`FACT`, union of all 32 constructions in one content-addressed store, in
**Book I nodes** (an EML tree of `n` operator nodes encodes to `4n + 1`):

| quantity | value |
|---|---:|
| `size_tree(U)` | 2 769 532 |
| `size_dag(U)` | **1 290** |
| `ratio(U)` | 4.658e-4 |
| savings `size_tree(U) − size_dag(U)` | 2 768 242 |
| `cross_only(U)` | 590 (45.74 % of `size_dag(U)`) |
| distinct EML subterms across the basis | 849 |

`FACT`, the nulls at the union level, 100 draws each, minimum gating:

| null | role | mean `ratio(U)` | **minimum** `ratio(U)` |
|---|---|---:|---:|
| **N4** grammar-matched independent trees | **primary** (Amendment A1.2) | 0.070311 | **0.070076** |
| N1 size-matched uniform random trees | descriptive | 0.137407 | 0.136711 |
| N2 leaf-shuffled real trees | descriptive | 0.042648 | 0.042109 |
| N3 subtree-shuffled union | — | `not constructible (CAS identity)` | — |
| N5 chain-topology content permutation | — | `not run` (see D3) | — |

`FACT`, Amendment 1's two-part scoring rule for `H-EML-SHARE-revised`:

1. `ratio(U) = 4.658e-4` is below N4's minimum `0.070076` — by a factor of
   150. **Holds.**
2. **99.82 %** of the union savings are attributable to shared subtrees of
   `>= 100` Book I nodes; the rule requires `>= 50 %`. **Holds.**

`H-EML-SHARE-revised` **holds**.

## What is not a finding, and is printed anyway

`FACT`. `ratio(U) <= 0.35` and `ratio(U) < 0.01` and `ratio(U) < 0.001` are
all true. The preregistration's worthlessness list says so in advance: the
basis entries are mechanical expansions of the paper's chain over previously
discovered primitives, so massive deduplication is **paper-decided
arithmetic**, not a measurement. `P-draft-3`, `P-fable-F1` and `kimi-A1` are
scored below because clause 8 requires it. None of them is the finding, and
none is headlined.

## The finding: sharing lives at the top of the basis, and only there

`FACT`, per-function. A construction "beats" a null only if its `ratio(f)` is
strictly below that null's **minimum** over 100 draws.

| null | constructions beaten, of 32 |
|---|---:|
| N1 | **10** |
| N2 | 9 |
| N4 | 9 |

`FACT`. The 10 that beat N1's minimum are **exactly the 10 largest by node
count** — `arsinh` (134 nodes), `tanh` (170), `cos` (222), `arcosh` (782),
`sin` (818), `tan` (1072), `arccos` (20882), `arcsin` (21031), `arctan`
(141991), `artanh` (504554). Every one of the 22 smaller constructions loses
to a random tree of its own size and leaf multiset. `arsinh` beats N1 but not
N4, which is why N4's count is 9.

`DERIVATION`. Over an alphabet of `{eml, 1, x, y}`, a random tree of 8 to 100
nodes collides with itself more than the paper's chain does. The chain's reuse
does not become visible against chance until a construction is large enough
that whole earlier primitives are embedded in it — and on this basis that
threshold sits somewhere between 102 nodes (`hypot`, which loses) and 134
(`arsinh`, which wins). This is the reviewer's own alphabet-coincidence
warning, confirmed at the per-function level and against their expectation of
its magnitude.

## The size spectrum (Amendment A1.4)

`FACT`. 1 032 of the 1 290 distinct stored nodes occur at least twice in the
union tree expansion; 590 occur in at least two different constructions.
Attribution: a memoized depth-first walk of the union tree expansion,
constructions in basis order, left child before right; a hit on an
already-stored hash prunes an entire subtree occurrence of `s(h)` nodes, and
those `s(h)` node occurrences are exactly what content addressing removes. The
attributed total is 2 768 242, which is the savings exactly.

| threshold (Book I nodes) | share of union savings |
|---|---:|
| `>= 100` | **99.82 %** |
| `>= 1000` | **99.26 %** |

| shared-subtree size | share of the 1 032 shared nodes below it |
|---|---:|
| `< 10` | 1.8 % |
| `< 100` | 11.2 % |
| `< 1 000` | 34.7 % |
| `< 10 000` | 58.2 % |
| `< 100 000` | 82.6 % |

`FACT`. The largest shared subtree is **672 575 Book I nodes** (168 143 EML
nodes), occurring twice — both times **inside `artanh` alone**. It is the
auxiliary `APPLY(E, T(u))` node above `u = inv(tan(arccos x))`, which `arsinh`
embeds twice when it expands `arsinh(u) = ln(u + hypot(-1, u))`. The largest
subtree shared **across** constructions is **83 529 Book I nodes** (20 882 EML
nodes), the whole of `arccos`, occurring 26 times across `arccos`, `artanh`
and `arcsin`.

`DERIVATION`, and it is a derivation, not a finding: a content-addressed store
is provenance-agnostic, so no null can see *why* two subtrees have one
address. The spectrum is diagnostic, not probative — 99 % of the savings
coming from subtrees above 1 000 nodes is not something independent random
generation from a 3-leaf alphabet produces at any appreciable rate, and the
reader may draw the inference. The harness does not draw it.

## Predictions, scored by name

`FACT`, per AGENTS.md clause 8. Every line below prints on every green
`validate.py` run.

| prediction | voice | claim | measured | verdict |
|---|---|---|---|---|
| `H-EML-SHARE-revised` | — | `ratio(U) < min N4` **and** `>= 50 %` of savings from subtrees `>= 100` | 4.658e-4 vs 0.070076; 99.82 % | **HOLDS** |
| `P-draft-1` | claude-fable (draft) | `ratio(U)` below the minimum of N1 and N2 | 4.658e-4 vs 0.136711 and 0.042109 | **HELD** |
| `P-draft-2` | claude-fable (draft) | at least half do **not** beat N1's minimum | **22 of 32** do not (needed `>= 16`) | **HELD** |
| `P-draft-3` | claude-fable (draft) | `ratio(U) <= 0.35` | 4.658e-4 | **HELD** — paper-decided, not a finding |
| `P-fable-F1` | claude-fable (session) | `ratio(U) < 0.01` | 4.658e-4 | **HELD** — likewise |
| `P-fable-F2` | claude-fable (session) | fewer than a quarter (`< 8`) fail to beat N1 | **22** fail | **FAILED** |
| `P-fable-F3` | claude-fable (session) | `cross_only(U) >= 0.5 · size_dag(U)` | 0.4574 | **FAILED**, narrowly |
| `P-fable-F6` | claude-fable (session) | `>= 95 %` of savings from subtrees `>= 1000` | 99.26 % | **HELD** |
| `kimi-A1` | kimi | `ratio(U) < 0.001` | 4.658e-4 | **HELD** — paper-decided |
| `kimi-A2` | kimi | `cross_only(U) >= 0.65 · size_dag(U)` | 0.4574 | **FAILED** |
| `kimi-A3` | kimi | `>= 25` of 32 beat N1's minimum, the failures being exactly the smallest | **10** beat; the failures **are** exactly the smallest | **FAILED on the count, right on the mechanism** |
| `kimi-A4` | kimi | largest shared subtree `> 100 000` nodes **and** shared by `>= 3` constructions | 672 575 nodes but inside **1** construction; the largest cross-construction one is 83 529 nodes in **3** | **FAILED on either reading of "shared"** |

`FACT`, on `kimi-A3`. The structural half of the prediction is exactly right:
the constructions that fail to beat N1 are precisely the smallest, with a
clean threshold and no interleaving. Only the threshold's location is wrong —
kimi placed it near 10 nodes, and it sits at 134. A prediction that names a
mechanism and misses a number is worth more than one that names neither; the
mechanism here is now measured.

`FACT`, on `kimi-A4`. Both clauses were tested on both readings of "shared"
(occurring twice anywhere, and occurring in two different constructions), and
the prediction fails on each: the biggest shared subtree is bigger than
predicted but lives inside one construction, and the biggest cross-construction
one is shared by exactly the predicted three but is smaller than predicted.

`FACT`, on `P-fable-F3` and `kimi-A2`. Both are about `cross_only`, and both
overestimated it. Under 46 % of distinct stored nodes appear in more than one
construction. Sharing on this basis is predominantly **within** a construction
— `arsinh` embedding its argument twice, `sqr(x) = mul(x, x)` — not across
constructions, which is the opposite of the "chains build on shared
primitives" story both predictions rested on.

## Controls

| # | control | outcome |
|---|---|---|
| 1 | normal form: `eval_hash(f)` returns `f`'s hash with `spent = 0` | **FAILS AS PREREGISTERED**; the property it exists for is established three ways — see D1 |
| 2 | harness `size_dag` = store key count on single-`f` stores | **PASS**, all 32 |
| 3 | transcription control re-run; corpus digest re-checked | **PASS** — 32/32; `basis.json` at `14853489…`, arXiv source at `2a3b4219…`, both unmoved |
| 4 | alphabet sanity: `nodes(f) <= 2` reported and excluded from per-function statistics | **PASS** — `eml_e`, `eml_exp` excluded |
| 5 | determinism: two runs produce a byte-identical `measurements.json` | **PASS**, and also byte-identical across CPython 3.14.7 and 3.9.6 — after one correction, see D5 |
| — | fast `size_dag` identity used for the nulls vs. real SHA-256 hashing | **PASS**, per construction and for the union |
| — | oracle pinned | `HEAD c78e8664…`, `impl/sigma_glyph.py 413d1f98…`, `spec/book-1-truth.en.md cc8c41bb…`, all matching the pin |

`FACT`, the encoding actually measured:
`E = 12c08231…`, `ONE = df559d2c…`, `X = 8785b7dd…`, `Y = 8ee7e3ec…`,
`eml(a,b) = APPLY(APPLY(E,a),b)`.

## Deviations and preregistration defects, named

**D1 — control 1's `spent = 0` is unreachable under the pinned oracle.**
*Erratum candidate E1.* Book I v0.5 prices every materialization: a root handed
to `eval_hash` as a hash costs `8n + 1` for an EML tree of `n` operator nodes,
and can never cost zero. The number in the preregistration describes a machine
that charges only for reduction. The property the control exists for — that
`E` at the head is a normal form and the encoding is not evaluated — is
established three ways, all recorded per construction in `measurements.json`:

- the term returned by `eval_hash` hashes to the root hash, for all 28 driven
  constructions;
- `spent` equals the closed form `8n + 1` **exactly**, for all 28. That number
  is pure materialization: `3` per `APPLY`, `1` per `LITERAL`, no contraction;
- no literal in the store is glyph-equal to `I`, `K` or `S`, so `step5` cannot
  fire a contraction anywhere in the basis. This argument is complete and
  covers all 32.

No ATP or theorem claim is made anywhere in this result, which is what the
worthlessness rule was protecting.

**D2 — four constructions were not driven through the oracle.** *Choice C2.*
The oracle's leftmost-outermost search is `O(size)` per step, so driving a term
of `size_tree` nodes costs `O(size^2)`; `artanh` at 2 018 217 Book I nodes is
out of reach by orders of magnitude, and `tan` at 4 289 already takes about
three seconds. The cap is `size_tree <= 5 000` Book I nodes, fixed before the
run, and covers 28 of 32. For `arccos`, `artanh`, `arcsin` and `arctan` the
normal-form claim rests on the structural argument in D1, which is complete,
and control 2 on them compares the store's key count against the harness's
`size_dag` using the harness's own serializer, tied to the oracle's by the
`encoding_agrees_with_oracle` control.

**D3 — N5 is `not run`, with a reason.** *Erratum candidate E2.* The review's
draw procedure builds the permutation pool `P(f)` from size proximity alone and
places no constraint on arity, so step 4 ("replace each occurrence of `d` in
`f`'s `chain_sexpr` with a uniform draw from `P(f)`") is undefined: for
`f = sigma`, the only constructions within 10 % of `inv`'s 12 nodes are `two`
(arity 0) and `add` (arity 2), and neither can replace a unary primitive.
Adding an arity filter would be a design choice made after the preregistration
closed. Amendment A1.3 makes N5 optional and non-gating; it is reported
`not run`.

**D4 — N4's stated uniformity does not match its own procedure.** *Erratum
candidate E3.* The review's step 3 says the tree is drawn "uniformly from the
set of such trees", but its step 4 specifies choosing the split of internal
nodes uniformly from the `k` valid splits and recursing, which is **not**
uniform over binary trees — it favours balanced shapes. Amendment A1.2 adopts
"the recursive uniform-split procedure specified in the review", so the
procedure governs and is implemented verbatim. The draft's N1, which says
"uniformly random binary tree", is implemented by **Rémy's algorithm**, which
*is* exactly uniform over the Catalan set. The two nulls therefore differ in
their draw distribution rather than being duplicates, and N4's minimum
(0.070076) sits between N2's and N1's, as a more balanced ensemble should.

**D5 — the cross-interpreter determinism run, and one correction it forced.**
*Correction C11, named not absorbed.* The preregistered control 5 asks for two
runs; the harness also ran the whole measurement under a second Python minor
version. The first freeze was byte-identical on the same interpreter but
**not** across versions: two null `ratio_mean` values differed by one ULP,
because CPython 3.12 gave `builtins.sum` a compensated (Neumaier) summation
for floats and 3.9 sums naively. No measured quantity that any hypothesis or
prediction depends on was affected — every minimum, maximum, ratio, count and
hash was identical — but a harness whose output depends on the interpreter
version is not reproducible. The means are now computed with `math.fsum`,
which is exactly rounded and has been stable since Python 2.6, and the
measurement was re-frozen. The re-freeze changed exactly those two digits;
it was not a response to any measured value, and no prediction, null, gate or
threshold moved. Control 5 now passes on both runs: body digest
`f1631b0b…` under CPython 3.14.7 and CPython 3.9.6 alike, both with
mpmath 1.4.1.

## Provenance — every choice the preregistration left open

| # | choice | what was pinned, and why |
|---|---|---|
| C1 | unit of `size_tree`/`size_dag` | Book I nodes, the unit the store actually holds. `4n + 1` per EML tree of `n` operator nodes. EML-node counts are reported alongside where a prediction could be read either way. |
| C2 | oracle drive cap | `size_tree <= 5 000` Book I nodes; see D2. |
| C3 | `size_dag` identity for the nulls | `1 + |distinct EML subterms| + |distinct left children|`, derived from the encoding and checked against real SHA-256 hashing on the real basis at every level before any null is drawn. Hashing 69 million null nodes per null would have added nothing. |
| C4 | N4 seed material | `sha256("EML-EXP-001/N4/{id}/{draw}")[:16]` big-endian, with `{id}` the `basis.json` construction id (`eml_artanh`, …), into `random.Random`. The same scheme with `N1`/`N2` substituted supplies the other two nulls, which the draft asked to share a seed list. |
| C5 | N4 leaf assignment | The review's base case — leaves drawn from `L(f)` without replacement into the leaf positions in left-to-right order — which is exactly a uniform permutation of the multiset, and which makes its step-3 multiset split hypergeometric rather than uniform-over-sub-multisets. |
| C6 | N1 shape | Rémy's algorithm; see D4. |
| C7 | savings attribution | Memoized DFS over the union tree expansion, constructions in basis order, left child before right; a pruned hit at `h` attributes `s(h)`. The total is `size_tree(U) − size_dag(U)` under any visit order; the split across size classes is order-dependent, so the order is fixed here and recorded. |
| C8 | "shared" and "sharers" | Shared = a distinct stored node with `>= 2` occurrences in the union tree expansion. Sharers = the number of distinct constructions containing it. Both readings are computed and both are used to score `kimi-A4`. |
| C9 | ATP budget for control 1 | `2^40`, never binding: the largest driven `spent` is 8 577. |
| C10 | determinism method | A second run in a fresh interpreter with a different `PYTHONHASHSEED`, which is what can catch a set- or dict-ordering leak; a second run inside one process cannot. A third run under a second Python minor version is taken when `EML_ALT_PYTHON` names one. |
| C11 | float summation | `math.fsum`, not `builtins.sum`, for every mean over draws. See D5. |

## What this does not establish

- Nothing causal. A content-addressed store cannot see why two subtrees share
  an address; the review says so and Amendment 1 removed the causal clause
  before the harness existed. The size spectrum is diagnostic.
- Nothing about ATP, theorems, or the `size <= spent + 1` bound. No contraction
  fired anywhere in this experiment.
- Nothing about EML as a grammar for elementary functions. This measures one
  transcription of one paper's chain under one encoding.
- Nothing about compression in general. A different encoding of the same basis
  — for instance one that gave `eml` its own opcode instead of an `APPLY`
  spine — would move every number in the union table, though not the null
  comparison, which is scale-free.

## Reproduction

```
python3 experiments/eml-exp-001/measure.py --check     # cheap re-derivation
python3 experiments/eml-exp-001/validate.py            # scores every prediction
```

`measurements.json` was frozen by
`EML_ALT_PYTHON=<python3.9 with mpmath> python3 experiments/eml-exp-001/measure.py --collect`,
about six minutes of measurement plus two verification re-runs. The oracle is
read from `$SIGMA_GLYPH_IMPL` or `~/Projects/sigma-glyph/impl/sigma_glyph.py`;
without it controls 1 and 2 report `SKIPPED`, which is never a pass. The
transcription control needs `mpmath`; without it control 3 reports
`SKIPPED (mpmath absent)`.
