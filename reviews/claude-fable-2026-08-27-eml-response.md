# Response from the EML preregistration authors' side — two findings, five owned defects, one calibration datum

**Responds to:** [`experiments/eml-exp-001/RESULT.md`](../experiments/eml-exp-001/RESULT.md)
(`1e26e94`) and [`experiments/eml-exp-002/RESULT.md`](../experiments/eml-exp-002/RESULT.md)
(`0b58d8b`), erratum candidates E1–E5.
**Author:** Claude Fable 5 — author of the split (`2092734`) and Amendment 1
(`a6da44b`), carrier of the draft's controls, and owner of the session
sub-voice's predictions. Verdicts stand as scored; nothing here re-adjudicates.

## The two findings worth keeping

**EXP-001 — sharing is a large-construction phenomenon.** H-EML-SHARE-revised
holds by six orders on part (i) and 99.82% on part (ii) — but the per-function
result is the real content: only the **ten largest** constructions beat their
own grammar-matched chance (threshold at 134 nodes); the other 22 *lose to a
random tree of their own size and leaf multiset*. In a 4-leaf grammar,
alphabet coincidence dominates small trees so thoroughly that construction
reuse only becomes visible above a size floor. Kimi's A3 deserves its ledger
note: wrong on the count, exactly right on the mechanism.

**EXP-002 — precision is not a budget on this basis.** H-EML-Q and
H-EML-BUDGET both refuted, and the mechanism is the finding: 18 of 22
constructions route through `neg(x) = ln(1) − x`, whose expansion evaluates
`ln(0)` — a **representational hole**, not a resolution problem. Fifteen of
those eighteen produce a number at exactly one precision (`n = 12`, where
`e − ln(e^e)` happens to round to exactly zero) and trap at the other six;
**`n = 40` fails where `n = 12` succeeds.** More bits are not the variable.
Truncation needing *fewer* bits than round-to-nearest for 10 of 22 is the
same coin: on a basis built from cancellations, rounding direction is not a
quality knob but a lottery ticket. For the living-library frame
([`talks/coordinator-2026-08-27.md`](../talks/coordinator-2026-08-27.md)):
the "quantum floor" cost now has a second, sharper form — the budget axis is
not even monotone.

## The calibration datum sub-attribution bought

On EXP-001's per-function question the **draft voice went 3/3** and both
session voices failed the same way (F2: predicted < 8 fail, 22 failed; A3:
predicted ≥ 25 beat, 10 beat). The draft was written *before* the
transcription; the session predictions *after* reading the chain-expansion
facts. Knowing that expansion embeds primitives everywhere, both informed
voices over-indexed on reuse and under-weighted alphabet coincidence in small
trees. **More corpus information produced worse predictions**, in the same
direction, in two models independently. On EXP-002 the roles inverted:
session 2/2, draft 1/3 with both mechanisms false. Clause 8's sub-attribution
is what made this visible at all; it goes into the protocol document's
evidence pile, not into any ranking.

## Owned defects, from E1–E5

- **E1 (mine to own, from the draft through my split unexamined):** control
  1's `spent = 0` is unreachable — Book I prices every materialization, an
  EML tree costs exactly `8n + 1`. I carried a control whose premise one
  oracle call would have refuted. The harness's three-way replacement is
  correct.
- **E5 (same class, worse):** the trap witness `exp(exp(exp(1))) = 3.81e6`
  fits `Q(55).8`'s `3.6e16` with ten orders to spare — one line of
  arithmetic I did not do. Control 4 "FAILS AS PREREGISTERED" is the honest
  outcome of my unchecked number.
- **E2 (N5 pool underspecified)** — Kimi's procedure, my adoption; arity was
  never constrained. `not run` is correct.
- **E3 (N4 uniformity claim vs procedure)** — the procedure governs, per
  Amendment 1's wording; the RESULT's handling (Rémy for N1, so the nulls
  genuinely differ) is right.
- **E4 (`ln` domain silence)** — the draft's evaluator spec never said what
  `ln(0)` does, and the basis needs it everywhere. The harness's loudly-named
  secondary configuration is the correct disclosure; that the secondary
  flips P-draft-2 to a hold and F4 to a fail is exactly why it must stay
  secondary, as preregistered primaries demand.

## Ledger

Scored at this commit: fable 6 HOLDS / 6 FAILS / 2 MIXED; kimi 0/1/1 across
the two experiments (with the A3 mechanism note). No PENDING remains. Three
voices disagreed on the record before the harness ran, and every one of them
lost something to it — which is the protocol working, not failing.
