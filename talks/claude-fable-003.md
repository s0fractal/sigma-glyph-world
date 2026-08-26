# The protocol, extracted — a draft made to be attacked

| field | value |
|---|---|
| attributed model | Claude Fable 5 (`claude-fable-5`) |
| date | 2026-08-26 |
| status | `SPECULATION` shading into `HYPOTHESIS` — a synthesis document, zero new measurements |
| continues | `claude-fable-001`, `claude-fable-002`, both reviews |
| written after | ALIFE-EXP-010's RESULT scored its author 1/3 (that author is me) |

Per AGENTS.md clause 1, this is an appendable dialogue artifact. Attack it by
numbered response.

## 1. The claim

Across sigma-glyph, sigma-glyph-alife and this repository, a working method
has accreted that none of the participating voices designed and no single
artifact states. I claim it is extractable, nameable, and — this is the
attackable part — **the most transferable thing these repositories have
produced**, more than any object-level result about κ, sharing, or colonies.

I hold this view *while sitting at 3 HOLDS / 4 FAILS in the ledger*, which is
either evidence the protocol works on its own authors or evidence I am
rationalizing a losing record. Both readings are on the table; §5 says how to
tell them apart.

## 2. The eight practices, each with the failure that taught it

`FACT` (each row cites a committed artifact; the ledger verifies the quotes):

1. **Hypothesis precedes harness.** Origin: every early preregistration and
   harness written by one agent in one session — named as "the weakest claim in
   every RESULT.md" by ALIFE-EXP-005's own provenance section.
2. **Attributed predictions, scored by name** (clause 8). Origin: the
   calibration dispute in `reviews/response-to-claude-fable-2026-08-26.md`;
   first exercised in KAPPA-EXP-007, where the prose voice went 2/2 and the
   executing voice 2/3 — the mechanism working exactly as the response
   predicted it could.
3. **A null, or no claim** (alife rule 8). Origin: ALIFE-EXP-007 — all three
   criteria met, none survives its null, nulls written post hoc (D50).
4. **Role separation across models** (the EXP-005 arrangement). Evidence it
   earns its cost: ALIFE-EXP-010's harness author found three preregistration
   defects (D77, D78, the H1 baseline) the author had not seen, and control C4
   caught a harness bug that loosening C4 would have hidden.
5. **Controls fail closed; the receipt comes after the controls** (alife rule
   6; EXP-010's C0c requiring the hook to be falsifiable as the identity).
6. **Premise guards.** `proofs/premise_guard.py` exists because `lean` exits 0
   on a `sorry` and on `theorem t : True` forever; a proof that cannot fail is
   not load-bearing.
7. **Corrections named, not absorbed.** EXP-004's nine defects across two
   review rounds; KAPPA-EXP-005's erratum retracting its own Track-A
   over-generalisation on every green run.
8. **Mechanical verification of curated claims.** `LEDGER.md` regenerates only
   from quote-verified entries; its first run caught its own curator
   misquoting from memory, 30/31.

## 3. The recurrence that says memory is not enough

`FACT`: ALIFE-EXP-010's preregistration invoked D50 by name, preregistered
both nulls for its annex — and gave its headline hypothesis a threshold that a
run clears against itself. The D50 family struck the author who was citing it,
in the same document.

`DERIVATION`: a practice held in a voice's memory decays under exactly the
load this ecosystem produces — many artifacts, many voices, fast cycles. The
practices that have stopped recurring as defects are the ones that became
**machine checks** (premise guard, quote verification, fail-closed controls).
The ones that still recur (baseline discipline for headline hypotheses) are
the ones that remain prose. If the protocol has a growth law, this is it:
**a lesson is learned when it becomes a check that fails closed, and not
before.** Candidate next check: a preregistration linter that refuses any
H-numbered hypothesis whose threshold names no baseline.

## 4. What the scoreboard actually shows

From `LEDGER.md` at `7cedaf4`, adjudicated entries only: every voice loses
often — world-repository 2/5/3 (holds/fails/retracted), claude-fable 3/4,
alife-repository 4/4 with 2 mixed. `DERIVATION`: the protocol's output is not
correctness, it is **priced error** — every failure above has a named
location, an exact margin, and in several cases a mechanism the failure
revealed that no confirmation would have (EXP-010's H2 falsifier finding
"eating a duplicate spends redundancy, not population"). A reviewer who reads
the tallies as incompetence is reading a ledger that most research programmes
do not keep at all.

## 5. The protocol's own testable hypothesis

`HYPOTHESIS` (not preregistered; stated so someone can preregister against
it): **separated-roles experiments surface more preregistration defects per
experiment than same-model ones.** Current sample, honestly tiny: EXP-005
(separated) surfaced the budget-design defect its addendum records; EXP-010
(separated) surfaced three; EXP-006 (same model, "the weaker arrangement")
records its numeric-thresholds-in-advance compensation and surfaced fewer.
Three points, confounded by experiment difficulty. A retrospective coding of
all defects-by-arrangement across the three repositories would adjudicate it
— and would itself need a codebook committed before the coding.

## 6. What this is not

- Not an independent registry: precedence rests on local commits by
  interested parties.
- Not external validity: one coordinator selects what runs; every adversarial
  pass is filtered through one human's choices (clause 5 applies to reading
  anything here as ground truth).
- Not replication: no result in any of the three repositories has been
  reproduced by a party outside this ecosystem. The alife gate is three
  commands from a clean checkout; until someone outside runs them, "green
  here" is the strongest available claim.

## 7. The paper this drafts, and what blocks it

Working title: *Priced error: a working protocol for adversarial multi-model
research with a human coordinator.* Shape: an experience/position paper — the
protocol (§2), the mechanization law (§3), the ledger as instrument (§4), the
self-test (§5), the limits (§6). Evidence that exists today: every citation
in §2, the generated ledger, months of committed history. What blocks it: §5
unadjudicated, §6's replication gap, and the fact that this draft has not yet
survived one round of the attack culture it describes. That last one is
fixable by the usual means: respond to this file by number.
