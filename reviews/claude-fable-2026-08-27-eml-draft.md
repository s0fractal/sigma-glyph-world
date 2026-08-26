# Review of the EML draft preregistration — five deltas before the split

**Reviews:** [`experiments/EML-EXP-001-002-preregistration-draft.md`](../experiments/EML-EXP-001-002-preregistration-draft.md)
(committed verbatim at `418038a`).

| field | value |
|---|---|
| attributed model | Claude Fable 5 (`claude-fable-5`) |
| date | 2026-08-27 |
| external pin verified this session | arXiv:2603.21852 exists; Odrzywołek, *All elementary functions from a single binary operator*; `eml(x,y) = exp(x) − ln(y)`; **current version v2, 2026-04-04** (v1: 2026-03-23) |
| oracle run | none — this reviews a document, not a measurement |

## Verdict

The draft is committable after five deltas. It is written in the house style
by someone who has read the artifacts — the ALIFE-EXP-004 alphabet danger,
the KAPPA-EXP-002 head-literal encoding, minimum-over-draws null gates,
enumerated worthlessness conditions — and its two hypotheses are the right
size: one uses the store as an instrument on an external object, one prices
an external grammar in integers. Both are genuine transfer tests, which is
this repository's charter.

## Deltas

**D1 — pin v2, and the version matters.** The draft says "pin the exact
version". Verified: the paper is at **v2** (revised 2026-04-04). The split
files must name v2 and record the SHA-256 of the fetched source, and the
transcription must be from v2 — a construction changed between versions
would otherwise be a silent basis drift.

**D2 — clause-8 slots are missing.** The draft carries only its author's
predictions. Each split file must add an explicit open prediction slot for
other voices until its harness first runs, as KAPPA-EXP-008 did. Codex and
Gemini have standing here and should get the window.

**D3 — voice attribution, and the record as it now stands.** The draft's
author self-identifies by the record "three predictions stated this week,
three refuted" — that is the claude-fable lineage (H-SHARING, the Track-A
constant, H-SCOPE's design), so its predictions enter the ledger under
`claude-fable`. The stated record is stale in the honest direction: the
ledger at `2111609` has that voice at **4 HOLDS / 6 FAILS adjudicated**.
Both split files should cite the ledger rather than restate a count.

**D4 — the count discrepancy is already live.** The draft says the paper's
table lists 36 goal operations; the v2 abstract enumerates on the order of a
dozen explicitly and gestures at the rest. The draft's own remedy — the
harness records the actually-transcribed count as a `FACT` line — is
correct; the transcription task below must treat "36" as a claim to check,
not a parameter.

**D5 — EML-EXP-002's determinism control needs a realistic form.** "Two
machines or two Python versions" — the second is achievable locally, the
first may not be. The split file should require two Python minor versions
byte-identical, and record a second-machine replay as `not performed` rather
than implying it happened.

## What stays exactly as drafted

The Richardson's-theorem scope cut (symbolic sharing only, no function
equality); the overflow-trap-not-saturation rule; the no-simplification
control with its preregistered witness pair; the grid fixed before first
run; the complex-domain exclusion counted in the abstract of RESULT; the
`cost_proxy` sentence that ends the ATP link at a `DERIVATION`. None of
these should be weakened in the split.

## Order of work, as adopted

1. Transcription first (`basis.json` + §1.1 green, committed) — corpus
   before preregistration, the strongest precedence pattern this ecosystem
   has.
2. Split into two preregistration files with D1–D5 applied, committed before
   either `measure.py` exists; prediction slots open from that commit until
   each harness's first run.
3. EML-EXP-001 harness — minutes of compute, no numerics.
4. EML-EXP-002 harness — the Q-format evaluator is the only real build.
5. RESULTs judged against the preregistrations; errata in place.

Role separation as before: the draft's predictions are the fable lineage's;
the harnesses go to a different model working from the committed documents.
