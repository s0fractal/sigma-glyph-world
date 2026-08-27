# EML-EXP-002 — result

**Status: `H-EML-Q` refuted. `H-EML-BUDGET` refuted. Precision does not behave
like a budget here, because the thing that decides whether a construction
evaluates at all is not how many bits it has — it is whether one particular
subexpression rounds to exactly zero.**

## Abstract, with the counts the preregistration requires in it

`FACT`. The basis holds 32 constructions. **10** are Euler-essential and are
excluded by name — `pi, cos, sin, tan, arsinh, arcosh, arccos, artanh,
arcsin, arctan`. **9** are purely real and are included fully — `e, exp, ln,
neg1, two, minus, sigma, cosh, sinh`. **13** are argument-dependent and are
included per grid point — `sub, add, inv, mul, sqr, div, half, avg, sqrt,
pow, logb, hypot, tanh`. Included total: **22**.

`FACT`, per-point exclusions. The preregistered grid gives **603** points
across the 22. The complex-routing check (mpmath, 50 digits, real-route iff
`max|Im|` along the whole route `< 1e-40`) removes **198** of them; **8** more
are out of domain (`logb` at base `x = 1`). **397** points remain. No
construction is left with zero real-route points, so nothing is reported
`EXCLUDED (no real-route points)`. The gate is not a footnote: it removes
**39 of 64** points from `pow`, **48 of 64** from `logb`, **40 of 64** from
`hypot`, and **6 of 8** from `sqrt`, which is left evaluable at `x = 3` and
`x = 5` only.

`FACT`, the headline. Under the literal preregistered evaluator with
round-to-nearest-even, **14 of the 22** included constructions never reach
relative error `1e-3` at any `n` in `{8, 12, 16, 20, 24, 32, 40}`. There is no
`n <= 20` at which all 22 reach it — there is no such `n` at all. `H-EML-Q`
is false.

## The mechanism, and it is not precision

`FACT`. Odrzywołek builds the additive inverse as `neg(x) = ln(1) - x`. Expanded
to pure EML, that evaluates `ln(ln 1) = ln(0) = -infinity`, and then `exp` of
that infinity, before returning to a finite number. mpmath's extended reals
absorb this, which is why the corpus's own transcription control passes at
`1e-30`. A signed 64-bit integer has no `-infinity`.

`FACT`. In Q arithmetic the inner `ln 1` is not computed symbolically; it is
computed as `e - ln(e^e)`, and whether that lands on exactly `0` is decided by
rounding. Measured, strict configuration, round-to-nearest-even:

| n | 8 | 12 | 16 | 20 | 24 | 32 | 40 |
|---|---|---|---|---|---|---|---|
| every construction whose route passes through `neg` | `DOMAIN` | **evaluates** | `DOMAIN` | `DOMAIN` | `DOMAIN` | `OVERFLOW` | `DOMAIN` |

`DERIVATION`. Eighteen of the 22 included constructions route through `neg`
(all but `e`, `exp`, `ln`, `sub`). Fifteen of those eighteen produce a number
at exactly one precision in the preregistered list, `n = 12`, and trap at the
other six; the remaining three (`hypot`, `sinh`, `tanh`) trap at `n = 12` as
well and never produce a number at all. More bits do not help and are not the variable: `n = 40` fails
where `n = 12` succeeds. Whatever `n*` measures on this basis, it is not a
budget.

## `n*` under the preregistered primary configuration

`FACT`. Strict ln-domain, round-to-nearest-even, `epsilon = 1e-3`:

| construction | depth | nodes | `n*` | | construction | depth | nodes | `n*` |
|---|---:|---:|---:|---|---|---:|---:|---:|
| `e` | 2 | 1 | **8** | | `avg` | 24 | 58 | NONE |
| `exp` | 2 | 1 | **12** | | `sqrt` | 25 | 49 | **12** |
| `ln` | 4 | 3 | **12** | | `pow` | 13 | 24 | NONE |
| `sub` | 5 | 5 | **16** | | `logb` | 18 | 38 | NONE |
| `neg1` | 8 | 8 | **12** | | `hypot` | 27 | 102 | NONE |
| `two` | 10 | 13 | **12** | | `sigma` | 16 | 30 | NONE |
| `minus` | 8 | 8 | **12** | | `cosh` | 24 | 68 | NONE |
| `add` | 10 | 13 | NONE | | `sinh` | 26 | 70 | NONE |
| `inv` | 9 | 12 | NONE | | `tanh` | 38 | 170 | NONE |
| `mul` | 11 | 20 | NONE | | `sqr` | 11 | 20 | NONE |
| `div` | 17 | 32 | NONE | | `half` | 24 | 45 | NONE |

`FACT`. Spearman `rho(depth, n*) = 0.276` over the 8 finite `n*`, permutation
`p = 0.327` (1000 permutations). Excluding `e`, `exp`, `ln` as floor outliers
it is `rho = -0.725` over 5. `H-EML-BUDGET` is refuted: four depth-ordered
pairs invert, the shallowest inversion being `sub` (depth 5, `n* = 16`)
against `minus` (depth 8, `n* = 12`).

`FACT`, `cost_proxy(f, n) = nodes(f) * n` is recorded per evaluated cell in
`measurements.json`. It is a **bit-serial proxy** and nothing else; it is not
ATP, and no claim about Book I follows from it.

## Truncation is not worse — it is better, and for a reason

`FACT`. Under truncation, `10 of the 22` constructions have a *finite* `n*`
where round-to-nearest-even has none: `add, inv, mul, sqr, div, half, pow,
logb, sigma, cosh`. Truncation rounds toward zero, so `e - ln(e^e)` lands on a
small nonzero residue instead of exactly zero, `ln` of it is a large finite
negative, and the construction limps to an answer. Round-to-nearest-even lands
on zero and traps.

`DERIVATION`. The rounding mode is not adjusting an error term here. It is
deciding whether a subexpression is representable at all. That is why
`P-draft-3`, which predicted truncation strictly worse, fails in the opposite
direction.

## The secondary configuration, and why it exists

`FACT`. The preregistered evaluator specification is silent on `ln` at zero.
The harness therefore ran a second, clearly labelled configuration
(`extended`) with two infinity sentinels under mpmath's own conventions —
`ln(0) = -inf`, `exp(-inf) = 0`, `exp(+inf) = +inf`, `ln(+inf) = +inf`,
`inf - inf` a trap. In that configuration the evaluator differs from the
reference **only** in precision, which is the comparison `H-EML-Q` and
`H-EML-BUDGET` were written about.

`FACT`, extended, round-to-nearest-even: **4 of 22** have `n* > 20` or NONE
(`avg` at 24, and `hypot`, `sinh`, `tanh` at NONE); Spearman
`rho(depth, n*) = 0.576`, permutation `p = 0.009`. `H-EML-Q` is still false —
no `n <= 20` serves every construction — but the budget picture is entirely
different. Both configurations are in `measurements.json`; predictions are
scored on the primary, with the secondary printed beside every one it moves.

## Predictions, scored by name

`FACT`. Primary configuration. The secondary's verdict is given where it
differs.

| prediction | voice | claim | measured | verdict |
|---|---|---|---|---|
| `H-EML-Q` | — | some `n <= 20` serves all | no `n` at all does | **refuted** |
| `H-EML-BUDGET` | — | `n*` monotone in depth | 4 inversions, `rho = 0.276` | **refuted** |
| `P-draft-1` | claude-fable (draft) | `H-EML-Q` false; some `n* > 20`; some NONE by `exp` overflow at every `n` | 14 of 22 never reach `1e-3`; **0** have a finite `n* > 20`; **0** fail by `exp` overflow at every `n` | **HELD on its stated falsifier; both stated mechanisms false** |
| `P-draft-2` | claude-fable (draft) | `rho >= 0.5`, `p < 0.05` | `rho = 0.276`, `p = 0.327` | **FAILED** (secondary: `0.576`, `p = 0.009` — would have held) |
| `P-draft-3` | claude-fable (draft) | truncation `>=` rounding everywhere, strictly `>` for `>= 1/4` | truncation needs **fewer** bits for 10 of 22; strictly more for 3 | **FAILED, in the opposite direction** |
| `P-fable-F4` | claude-fable (session) | `>= half` have `n* > 20` or NONE | **14 of 22** | **HELD** (secondary: 4 of 22 — would have failed) |
| `P-fable-F5` | claude-fable (session) | `e, exp, ln` reach `1e-3` at `n <= 16` | `8, 12, 12` | **HELD** |
| `kimi-A5` | kimi | **exactly 6** have `n* > 20` or NONE | **14** | **FAILED** |
| `kimi-A6` | kimi | `e, exp, ln` at `n <= 8` | `8, 12, 12` — `exp` and `ln` need 12 | **FAILED** |
| `kimi-A7` | kimi | `rho >= 0.55` excluding the floor | `rho = -0.725` over 5 | **FAILED** |

`FACT`, on `kimi-A5`. The prediction was a knife edge — "fewer than 6 or more
than 6" falsifies it — and it is scored exactly: 14, not 6, under the primary;
4, not 6, under the secondary. It fails on both readings, and it fails in
opposite directions on them, which is a more informative outcome than either
number alone.

`FACT`, on `P-draft-1`. Its stated falsifier ("every included construction
reaches `1e-3` at some `n <= 20`") is not met, so the prediction stands. Both
of the mechanisms it named are nevertheless false: no construction has a
*finite* `n*` above 20, and the failures are `DOMAIN` traps on `ln(0)`, not
`exp` overflows. Clause 8 says a preregistered prediction is useful however
badly it fares; this one was right about the verdict and wrong about the
reason, and the reason is the finding.

## Controls

| # | control | outcome |
|---|---|---|
| 1 | integer `exp`/`ln` at `n = 40` match mpmath to `1e-9` on the grid | **PASS** — worst `exp` `1.33e-12`, worst `ln` `2.16e-12` |
| 2 (D5) | byte-identical `measurements.json` across two Python minor versions | **PASS** — 3.14.7 and 3.9.6, both mpmath 1.4.1, identical body digest `20e3b93b…` |
| 3 | transcription control re-run, corpus digest re-checked | **PASS** — 32/32, digest `14853489…` unmoved |
| 4 | `exp(exp(exp(1)))` MUST `OVERFLOW` at `n = 8` | **FAILS AS PREREGISTERED** — see deviation D4 |
| 5 | `x*y` in EML form vs. the direct product MUST differ | **PASS** — 103 cells where both are numbers and differ |
| 6 | `sqrt` at `x = 0.5` MUST be excluded by the routing gate | **PASS** — `max|Im| = 4.759` along the route, gate `1e-40` |
| — | no `float` in the evaluation path, grepped | **PASS** — `validate.py` tokenizes `qeval.py` and the marked region of `measure.py` and rejects any non-integer NUMBER token or the names `float`/`complex` |
| — | pinned `ln 2` constant against mpmath at 50 digits | **PASS** |
| — | SATURATED constructions (`> 1e6` evaluation steps) | none; the largest included construction is `tanh` at 170 nodes |

## Deviations and preregistration defects, named

**D1 — the relative-error denominator.** The preregistration says "relative
error" but several targets are zero somewhere on the grid (`sub` at `x = y`,
`ln` at `x = 1`, `minus`). The harness uses
`|got - want| / max(|want|, 1)`, the same unit-floored criterion the corpus's
own committed transcription control uses. Away from the zeros this is exactly
relative error.

**D2 — `ln`'s domain is unspecified, and the basis needs it.** *Erratum
candidate E4.* The preregistered evaluator names only overflow. `ln(0)` is not
an overflow; it is an operation the specification does not define, and the
basis reaches it at every construction downstream of step 5. The harness
reports it as a distinct `DOMAIN` outcome, counts it as failure at that `n`
exactly as `OVERFLOW` would be counted, and never turns it into a number.

**D3 — the `extended` configuration is a harness addition.** *Named, not
absorbed.* It is not preregistered. It is reported in full, it is never the
primary, and no prediction is scored on it alone.

**D4 — control 4's witness cannot fire.** *Erratum candidate E5.*
`exp(exp(exp(1))) = e^(e^e) = 3814279.105`, and `Q(55).8` represents up to
`3.602879702e16`. The preregistered witness returns a number at every `n` in
the list — `4358144.0` at `n = 8`, `3814279.1` at `n = 40`. The control cannot
pass as written; the defect is in the witness, not in the trap. The harness
adds `exp(exp(exp(exp(1)))) = e^3814279`, which `OVERFLOW`s at every `n`, and
reports it as a supplementary witness. The trap is live.

**D5 — no construction was SATURATED.** The `10^6`-step cap is in the code and
is reported, but the included set tops out at 170 `eml` nodes, so it never
binds. The four constructions that would have needed it (`arccos`, `artanh`,
`arcsin`, `arctan`, up to 504554 nodes) are Euler-excluded by name.

## Provenance — every choice the preregistration left open

| # | choice | what was pinned, and why |
|---|---|---|
| C1 | `exp` algorithm | Range reduction by powers of two: `k = round(a / ln2)` in the configured mode, `r = a - k*ln2`, `exp(a) = 2^k * sum_{i<=T} r^i / i!`. Scaling by `2^k` is an exact left shift (a rounded right shift for `k < 0`). |
| C2 | `ln` algorithm | Binary normalization `b = 2^e * m`, `m` in `[1,2)`; `ln(b) = e*ln2 + 2*sum_{j<T} z^(2j+1)/(2j+1)`, `z = (m-1)/(m+1)` in `[0, 1/3]`. |
| C3 | term count | `T(n) = n//2 + 6`: `10, 12, 14, 16, 18, 22, 26` for `n = 8 … 40`. Fixed in `qeval.py`, never varied. Series-truncation bound at `T = 10` is `2^-27` for `exp` and `2^-34` for `ln`, below one ulp at every `n` in the list, so truncation of the series is never the binding error. |
| C4 | `ln 2` | One pinned integer, `floor(ln2 * 2^192)`, rounded to `Q(63-n).n` by round-to-nearest-even. A constant is not an operation, so it does not follow the configured mode; control `constants_agree` checks it against mpmath. |
| C5 | rounding of the reduction index | The configured mode, like every other operation — the two configurations are never mixed. |
| C6 | grid coordinates | Entered as exact rationals (`Fraction`) and correctly rounded into `Q(63-n).n` under the configured mode. No decimal literal is ever parsed as a float. |
| C7 | truncation's meaning | Round toward zero, the standard fixed-point sense, not floor. |
| C8 | trap granularity | A trap at any usable grid point makes `err(f, n)` a failure for the whole `(f, n)` cell, as the preregistration's `OVERFLOW = failure at that n` requires. |
| C9 | memoization | Evaluation is memoized on DAG node identity, which for a hash-consed tree is memoization on subterm content, in the configuration `(n, mode, ln-domain)`. `eml` is a deterministic function of its arguments in Q arithmetic, so this returns the number the fully expanded tree gives. |
| C10 | permutation seed | `sha256("EML-EXP-002/permutation/{label}")[:16]` big-endian into `random.Random`; 1000 permutations; `p = (count + 1)/(N + 1)`. |
| C11 | domain intersection | The grid is entirely positive, so the only out-of-domain points are `logb` at base `x = 1`. Recorded explicitly rather than discovered. |

## What this does not establish

- Nothing about Book I. No term was evaluated by the Σ-GLYPH oracle here, and
  `cost_proxy` is not ATP.
- Nothing about the 10 Euler-essential constructions. A fixed-point *complex*
  evaluator is out of scope and was named out of scope by the preregistration.
- Nothing about EML as a grammar. The paper's constructions are correct in
  extended real arithmetic; the corpus's own control says so at `1e-30`. What
  fails here is their evaluation in a format without infinities, and the
  failure is representational before it is numerical.
- Nothing about rational or interval evaluation, which the preregistration
  lists as a successor's problem.

## Reproduction

```
python3 experiments/eml-exp-002/measure.py --check     # re-measures, byte-compares
python3 experiments/eml-exp-002/validate.py            # scores every prediction
```

`mpmath` is required; without it both report `SKIPPED (mpmath absent)`, which
is never a pass. `measurements.json` was frozen by
`EML_ALT_PYTHON=<python3.9 with mpmath> python3 experiments/eml-exp-002/measure.py --collect`;
without `EML_ALT_PYTHON` the second half of control 2 records
`not performed` honestly rather than claiming a version it did not run.
