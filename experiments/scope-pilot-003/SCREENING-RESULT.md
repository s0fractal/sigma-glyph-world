# SCOPE-PILOT-003 — screening result

**Status: `SAMPLING_FAILURE`. 60 candidates screened, 1 admitted, minimum to
code is 8. No packet was constructed and no coder was run.**

> **See the [erratum](#erratum-2026-08-26) before reading §"Why candidates
> failed" and §"Disposition".** [Codex's review](../../reviews/codex-2026-08-26.md)
> found that the evidence behind the 60 decisions was not committed, that the
> causal attribution "frame failure, not instrument failure" is unidentified,
> that two threads were silently truncated at 100 comments, and that the
> control-kind diversity requirement was satisfied by construction. All four are
> accepted.

The preregistration is explicit: *"If fewer than 8 incidents survive the
60-candidate limit, report sampling failure and do not run coders."* That
condition is met, so P003 stops here. No agreement number exists and `H-SCOPE`
remains untested.

## Outcome

`FACT`: screening followed the frozen hash order from position 1 to position 60
without skipping, and every decision and reason is retained in
[`screening-log.json`](screening-log.json). `screen.py --check` enforces that
the log is a contiguous prefix of `candidate-order.json`, that each entry's
identity matches the frozen candidate, and that the preregistered caps hold.

| constraint | required | observed |
|---|---|---|
| admitted incidents | >= 8 | **1** |
| control kinds among admitted | >= 3 | **1** |
| expected selector cases | >= 2 | **1** |
| expected adapter cases | >= 2 | **0** |
| expected gate cases | >= 2 | **0** |
| candidates screened | <= 60 | 60 |
| admitted per repository | <= 2 | max 1 |

`FACT`: the 60 screened candidates span 18 of the 24 frame repositories and all
four strata (lint/static analysis 22, tests 16, proofs/build completeness 11,
artifact/conformance 11). The repository cap never bound; no candidate was
recorded as `CAPPED`.

## Why candidates failed

`FACT`: rejection reasons, in the order they occur:

| reason | n | what it means here |
|---|---|---|
| `NO_PRIMARY_EVIDENCE` | 20 | behavior unreproduced or withdrawn, or the evidenced direction is over-reporting rather than acceptance or omission |
| `NO_AUTOMATED_CONTROL` | 15 | feature request, policy thread, install or runtime defect; no control and no governing signal |
| `PRODUCT_DEFECT_NOT_CONTROL` | 9 | the artifact under test was defective and the control reported it |
| `CONTRACT_DISPUTED` | 8 | reproducible behavior whose meaning of success rests on reporter expectation or is under live maintainer disagreement |
| `OUT_OF_SCOPE_GATE_REJECTED` | 7 | the named governing gate rejected; the check failed closed |
| `ADMITTED` | 1 | — |

`DERIVATION`: the dominant failure is not that verification-scope incidents are
rare. It is that the seven frozen query terms — `exit code`, `no tests`,
`false positive`, `not run`, `ignored`, `reports success`, `zero issues` — select
for *any* issue whose text mentions a tool outcome. `false positive` and
`ignored` in particular select the direction opposite to the one codebook v1
admits: a tool reporting **too much** rather than accepting too little. Nine of
the twenty `NO_PRIMARY_EVIDENCE` rejections — positions 6, 15, 22, 32, 35, 37,
42, 57, and 58 — are over-reporting cases that are reproducible, often
maintainer-confirmed and fixed, and simply not about false acceptance. Four of
those nine matched on `false positive` and three on `ignored`.

`FACT`: across the 60 screened candidates, `reports success` — the term closest
to the mechanism under study — matched exactly one candidate, while `not run`
matched 19, `exit code` 18, `ignored` 13, `no tests` 9, and `false positive` 7.
`zero issues` matched none.

`DERIVATION`: a second, sharper constraint is admission gate 3. Several
candidates carry exactly the mechanism shape the pilot is built to study and
still fail, because a public issue thread rarely establishes the success
contract at tier T1, T2, or T3:

- **position 29**, `golangci-lint` 1.36.0 reports a ruleguard diagnostic while
  1.37.0 and later print nothing and exit 0. A member could not reproduce it,
  the ruleguard author acknowledged only a general go-critic problem, and the
  reporter finally attributed it to their own module setup. Codebook v1 does not
  count a prior release's observed behavior as a T2 assertion, so the tiers
  conflict and the contract is `DISPUTED`.
- **position 46**, `semgrep` generic mode silently does not match inside a file
  that is one very long line, and a maintainer confirmed the engine refuses
  files without indentation structure in order to bound parsing cost. The
  target's own formatting decides whether it is audited, with no independent
  fence — but the adjudication establishes the omission as *intended*, so no
  contract is breached.
- **position 28**, a `semgrep` scan prints an undescribed error span for a file
  it cannot analyze and still exits 0, with the same output documenting that
  `--strict` is required for a non-zero exit. The completeness fence exists but
  is self-owned and opt-in, and the documented default establishes that the run
  passes.
- **position 31**, Jest prints `Done in 0.72s.` with no test results and no
  failure — the empty-scope-success shape — but a maintainer closed it as a
  support question, leaving no cause and no component boundary.

`DERIVATION`: these four are the pilot's most useful output. They show that the
binding scarcity for `H-SCOPE` archaeology is **adjudicated contracts**, not
candidate incidents. A confirmatory corpus will have to sample where the
contract is written down — merged regression tests, changelog entries,
version-pinned documentation — rather than where the symptom is described.

## The single admitted incident

`FACT`: position 40, `leanprover/lean4` issue 1371, stratum
proofs/build completeness.

Lean 4 accepted a `match`-syntax definition whose second and third alternatives
are unreachable. The quotation match compiler silently dropped them, so their
bodies were never elaborated and the conflicting result types `1`, `true`, and
`"hello"` never produced an error. The fix commit adds unused-alternative
checking, a merged regression test (`tests/lean/1371.lean` and its expected
output), and a `RELEASES.md` entry stating that match-syntax notation now checks
for unused alternatives — a T2 executable contract, hence `ESTABLISHED`.

`FACT`: one admitted packet cannot be coded. Agreement is undefined on a single
observation, the control-kind and component minima are unmet, and codebook v1
forbids scoring a hypothesis on the corpus that shaped it. This incident is
retained as a seed for a successor frame, not as a result.

## What did not happen

- No incident packet was constructed and no blinded render exists.
- No coder was run; no model receipt exists.
- No agreement, Jaccard, alpha, or control pass rate was computed.
- The four authored P002 controls were not exposed to anyone.
- `H-SCOPE` remains untested.

## Disposition

`DERIVATION`: this is a frame failure, not an instrument failure. The codebook,
coder prompt, coding schema, and four authored controls were never exposed to a
coder and did not cause the outcome; their digests remain
`3c9261450ffe3553a984788e5f764cc4f829624155b53b5272ae4ebc3f7f8e01` and
`9b4c3c277b263d350d8dd22bac8f7d4444e98134f1b1e7a64fc6b1f3e174abf1`. Under the
preregistration, any change to the frame, queries, or ordering after the first
P003 request creates a new pilot and a fresh sample. Therefore P003 is retired
and a successor must change the *sampling substrate*:

1. **Sample from resolutions, not symptoms.** Search merged commits, changelog
   entries, and regression-test additions whose text asserts a restored
   completeness or acceptance boundary, then walk back to the issue. This
   attacks admission gate 3 directly, which is where 8 `CONTRACT_DISPUTED` and
   much of `NO_PRIMARY_EVIDENCE` were lost.
2. **Drop or invert the over-reporting terms.** `false positive` and `ignored`
   supplied a large share of rejections in the direction codebook v1 excludes.
3. **Decide, before the next preregistration, whether codebook v1 should admit
   an intended-but-unfenced omission.** Positions 28 and 46 are refused only
   because a maintainer called the omission deliberate. If self-selected scope
   is the object of study, a designed, undisclosed, self-owned fence may be the
   most important case class rather than an excluded one. Changing this is a
   codebook change and requires a new codebook version and a fresh corpus.

`UNKNOWN`: whether the prevalence question is answerable from public issue
records at all, or whether it requires corpora where the success contract is
version-pinned by construction.

## Reproduction

```sh
tools/test-all.sh
```

`python3 experiments/scope-pilot-003/screen.py --status` prints the terminal
state and every unmet constraint. Green execution means the screening log is a
faithful, constraint-checked prefix of the frozen candidate order. It is not
review, external validity, or evidence for any mechanism claim.

---

## Erratum, 2026-08-26

From [`reviews/codex-2026-08-26.md`](../../reviews/codex-2026-08-26.md),
findings 5, 6, 8 and 9.

### Finding 5 — the decisions were ordered but not auditable

`FACT`: the 168 search checkpoints were committed; the evidence behind the 60
screening decisions was not. `evidence-cache/` is ignored, the screening log
carried response digests with nothing to compare them against, and the sole
admitted incident's contract rested on two commit URLs with no digest at all.

Now committed:

- [`evidence-manifest.json`](evidence-manifest.json) — one entry per screened
  position, built from the evidence used at screening time so every
  `retrieved_at` and digest is the original. Bodies are clipped to 900
  characters and comments to 400, with `sha256` and `chars` covering the
  untruncated text, so a decision can be audited without republishing 60
  third-party threads in full.
- [`cited-artifacts.json`](cited-artifacts.json) — the admitted incident's
  out-of-thread evidence: both commits with API-response and message digests and
  per-file patch digests, the merged regression test and its expected output with
  git blob SHA and content, and the release-note line, each content-addressed.

`FACT`: the frozen regression test reads

```lean
def f (stx : Lean.Syntax) :=
  match stx with
  | `($f $a)  => 1
  | `($_)     => 2
  | `($f $b)  => 3
  | _         => "hello"
```

with expected output `error: redundant alternative #3` and `#4`. That is the
`T2_EXECUTABLE` contract the admission claimed, now auditable rather than
asserted.

`FACT`: `screen.py --check` now fails if any screened position is absent from the
manifest, or if the manifest's url, issue digest, or reason disagrees with the
log. It still does **not** validate the substance of any reason, and the review
is right that it cannot. Researcher judgment stays judgment.

### Finding 8 — two threads were truncated at 100 comments

`FACT`: `fetch_evidence.py` requested `per_page=100` without paginating and
recorded `comment_count` as the number of items fetched, so a thread with more
than 100 comments was indistinguishable from a complete one. Positions 44
(`astral-sh/ruff#1904`) and 59 (`rocq-prover/rocq#12487`) were affected.

The tool now pages to exhaustion and records `comments_pages`,
`comments_complete`, `declared_comment_total`, and a digest per page.

`FACT`, from the audit, recorded in the manifest rather than backdated: position
44 was missing 1 comment of 101, position 59 was missing 10 of 110.

`DERIVATION`: neither changes its decision. The comment missed at 44 is an aside
about Black's default in a design thread that contains no incident; the ten
missed at 59 are memory-profiling discussion ending in a maintainer closing the
issue because the consumption was no longer reproducible — which reinforces
`NO_PRIMARY_EVIDENCE` rather than disturbing it.

`FACT`: the review's narrower point stands regardless. The claim that all 60
decisions used complete primary threads was false when written, and was true only
by luck for these two.

### Finding 9 — the diversity requirement was satisfied by construction

`FACT`: `screen.py` requires an admitted entry's `sampling_assessment.control_kind`
to equal the frozen repository stratum. The later "at least 3 control kinds"
minimum therefore ranged over **sampling strata**, a frame label, not over
independently observed incident kinds.

The field is renamed in the harness output and status
(`sampling_strata_of_admitted`) so it no longer claims to be an observation. The
frozen log is not rewritten.

`DERIVATION`: a successor must carry `sampling_stratum` and
`observed_control_kind` as separate fields and permit them to disagree, so that
misclassification is data. Diversity minima then apply either to strata, and are
called strata, or to adjudicated incident kinds — never to a field forced equal
to the frame.

### Finding 6 — "frame failure, not instrument failure" is retracted

`FACT`: this document attributed the outcome to the sampling frame rather than
the instrument. That attribution is not identified. The admission gate is part
of the instrument, eight candidates were rejected specifically because codebook
v1's contract tier was unmet, and this document's own conclusion is that the
binding scarcity is adjudicated contracts. There was no comparison frame, no
relaxed-admission arm, and no independent adjudication.

**Corrected status: `CONTESTED`.** Two live interpretations, both consistent with
the evidence: the seven query terms have poor directional precision, *and*
codebook v1 demands evidence that issue threads rarely carry. Separating them
requires a design that varies one while holding the other.

`FACT`: the successor this document proposed — sampling from merged regressions,
changelogs and fixes — conditions inclusion on resolution, maintenance and public
documentation. That is a different estimand. It measures mechanisms among
**documented fixed incidents**, not prevalence among verification-infrastructure
incidents, and cannot answer `H-SCOPE`'s population comparison without a
selection model.

`DERIVATION`, replacing the proposal in §"Disposition":

1. Name the estimand before P004, in the preregistration.
2. Use a resolution-derived corpus for **instrument calibration and evidence
   augmentation only**, never silently for prevalence.
3. For prevalence, keep an incident-based probability sample and retrieve
   resolution evidence **after** selection; record unresolved or missing
   contracts as outcomes rather than as exclusions.
4. If the public record cannot support that estimand, retire the prevalence
   question explicitly instead of answering a resolution-conditioned replacement
   and calling it `H-SCOPE`.
