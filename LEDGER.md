# Attributed-prediction ledger

**GENERATED — do not edit.** Curate `ledger/entries.json` and run
`python3 tools/ledger_check.py --write`. Every quote below is verified
as a literal substring of its source file on every run; the check
fails closed on any mismatch.

Verdicts are the scoring repositories' own, from their committed
artifacts. Per AGENTS.md clauses 5 and 8: this table measures how
preregistered, attributed predictions were adjudicated — it is not
ground truth about any voice, and reliability must not be inferred
from whether a voice executes.

## Entries

| id | repo | voice | prediction | verdict | sources |
|---|---|---|---|---|---|
| W1 | world | claude-fable | H-SHARING: structural sharing makes peak linear in n | **FAILS** | `reviews/response-to-claude-fable-2026-08-26.md` |
| W2 | world | claude-fable | a strategy-insensitivity constant exists (Track A invariant) | **FAILS** | `reviews/response-to-claude-fable-2026-08-26.md` |
| W3 | world | world-repository | peak = 4·2^n − 3 for both strategies (EXP-001 prereg) — wrong for S_out by a constant 8; printed as DEVIATION on every green run | **FAILS** | `reviews/response-to-claude-fable-2026-08-26.md` |
| W4 | world | world-repository | EXP-001 machine is an explicit syntax tree with no sharing — false of its own implementation; found by Codex | **FAILS** | `reviews/response-to-claude-fable-2026-08-26.md` |
| W5 | world | world-repository | κ ≤ 1 under C_size presented as a finding — a theorem, not a measurement | **RETRACTED** | `reviews/response-to-claude-fable-2026-08-26.md` |
| W6 | world | world-repository | the EXP-001 successor question — trivial in both directions | **RETRACTED** | `reviews/response-to-claude-fable-2026-08-26.md` |
| W7 | world | world-repository | g_{n,k} spread bounded, hand-derived (EXP-003 prereg) — it grows | **FAILS** | `reviews/response-to-claude-fable-2026-08-26.md` |
| W8 | world | world-repository | spread(g_{14,8}) > 100, driven by n, k ruled out (EXP-005 prereg) — measured 10.23; saturates in n; k is the driver — wrong in both directions | **FAILS** | `reviews/response-to-claude-fable-2026-08-26.md` |
| W9 | world | world-repository | no materialization-charging cost model removes the separation (universal claim) — universally quantified over a class of which two members were studied | **RETRACTED** | `reviews/response-to-claude-fable-2026-08-26.md` |
| W10 | world | claude-fable | EXP-007 A.1: on h_n the separation disappears under R_update | **HOLDS** | `experiments/kappa-exp-007/RESULT.md` |
| W11 | world | claude-fable | EXP-007 A.2: under a binder the separation returns | **HOLDS** | `experiments/kappa-exp-007/RESULT.md` |
| W12 | world | world-repository | EXP-007 B.1: separation exactly 1.00 on h_n, identical trajectories — right for the objects metric, wrong for occurrence size — quantity named without its metric | **FAILS** | `experiments/kappa-exp-007/RESULT.md` |
| W13 | world | world-repository | EXP-007 B.2: distinct_objects is Θ(n) for both strategies | **HOLDS** | `experiments/kappa-exp-007/RESULT.md` |
| W14 | world | world-repository | EXP-007 B.3: on d_n the separation returns attenuated, below R_fresh | **HOLDS** | `experiments/kappa-exp-007/RESULT.md` |
| A1 | alife | alife-founding-proposal | anastomosis: sharing factor grows super-linearly with population density | **FAILS** | `experiments/alife-exp-001/RESULT.md` |
| A2 | alife | alife-repository | EXP-004 attack: the sharing decline is an alphabet artifact — the attacked sentence survived, 10/10 seeds at every alphabet fraction | **FAILS** | `experiments/alife-exp-004/RESULT.md`; `experiments/alife-exp-004/RESULT.md` |
| A3 | alife | alife-exp-005-prereg-author (model not named in artifact) | EXP-005 H1: the sharing discount is large and concentrated | **FAILS** | `experiments/alife-exp-005/RESULT.md` |
| A4 | alife | alife-exp-005-prereg-author (model not named in artifact) | EXP-005 H2: enforced copy pricing materially reduces settled agents — budget chosen so everyone settles; H2 could not have been true — design defect recorded | **FAILS** | `experiments/alife-exp-005/RESULT.md` |
| A5 | alife | alife-exp-005-prereg-author (model not named in artifact) | EXP-005 H3: dup largest, drop uniquely smallest, gap ≥ 2× | **FAILS** | `experiments/alife-exp-005/RESULT.md` |
| A6 | alife | alife-repository | EXP-006 H1: observable-state policy beats even split by ≥ 8 agents | **FAILS** | `experiments/alife-exp-006/RESULT.md` |
| A7 | alife | alife-repository | EXP-006 H2: resumption worth ≥ 8 agents against best restarting arm | **HOLDS** | `experiments/alife-exp-006/RESULT.md` |
| A8 | alife | alife-repository | EXP-006 H3: the premium grows with pulse granularity, doubling 2→32 | **FAILS** | `experiments/alife-exp-006/RESULT.md` |
| A9 | alife | alife-repository | EXP-007 H1–H3: organizations form (closure, L1-core, budget-dependence) — criteria met; nulls — written post hoc, defect D50 — kill the interpretation | **MIXED** | `experiments/alife-exp-007/RESULT.md` |
| A10 | alife | alife-repository | EXP-008 H1: a self-maintaining set ≥ 3 while the shuffled-graph null is empty | **MIXED** | `experiments/alife-exp-008/RESULT.md` |
| A11 | alife | alife-repository | EXP-008 H2: the history-core is ≥ 5× the persisting set | **FAILS** | `experiments/alife-exp-008/RESULT.md` |
| A12 | alife | alife-repository | EXP-008 H3: sustaining reactions are ≥ 30% cheaper | **UNADJUDICATED** | `experiments/alife-exp-008/RESULT.md` |
| A13 | alife | alife-repository | EXP-009 H1: ≥ 30 agents recovered at delivery spread 1.0 | **HOLDS** | `experiments/alife-exp-009/RESULT.md` |
| A14 | alife | alife-repository | EXP-009 H2: spread 4.0 recovers ≤ 50% of spread 1.0 | **HOLDS** | `experiments/alife-exp-009/RESULT.md` |
| A15 | alife | alife-repository | EXP-009 H3: 0 ATP while waiting, 100% answers unchanged | **HOLDS** | `experiments/alife-exp-009/RESULT.md` |
| A16 | alife | claude-fable | EXP-010 H1: the currencies pick different colonies (Jaccard < 0.5, 2/3 seeds) — uninformative by post-hoc baseline: E-vs-E across seeds is also ~0; the threshold measures turnover, not the manipulation | **HOLDS** | `experiments/alife-exp-010/RESULT.md`; `experiments/alife-exp-010/RESULT.md` |
| A17 | alife | claude-fable | EXP-010 H2: matter-pricing cannibalizes (smaller census 3/3, fewer hashes 2/3) — the named falsifier fired; the RESULT's initial mechanism ('eating a duplicate spends redundancy') was later refuted by its own mediation statistic — 74.7%/77.2%/90.3% of consumptions removed the LAST living body of that hash; cause of Arm M's higher distinctness is unidentified | **FAILS** | `experiments/alife-exp-010/RESULT.md` |
| A18 | alife | claude-fable | EXP-010 H3: the self-pricing-out curve bends (M exceeds E by >= 10 pts, 2/3 seeds) — sign reversed in two seeds; the RESULT's 0.8%-7.0% share was later corrected by Codex review — verified R-S shares of actual spend are 1.23%/0.62%/2.04%, counterfactual price savings 0.77%/0.40%/1.39% | **FAILS** | `experiments/alife-exp-010/RESULT.md` |
| W15 | world | claude-fable | EXP-008 A1: on d_n the schedule separation under R_optimal is bounded (<= 2.00, non-growing) — by more than the margin asked: exactly 1.0000 at every n — schedule-internal to the abstract sharing graph; the cross-representation reading is blocked by the unpriced-readback boundary (codex-2026-08-26-current-state.md) | **HOLDS** | `experiments/kappa-exp-008/RESULT.md` |
| W16 | world | claude-fable | EXP-008 A2: peak_book/peak_term >= 10 at the top of e_n, rising; <= 2 on h_n — 1.792 at ungated e_4 (0.74 at gated e_3 — verdict robust); metric itself ill-posed as max/max per the prereg author's erratum; no directional bound for full optimal reduction is established | **FAILS** | `experiments/kappa-exp-008/RESULT.md` |
| W17 | world | claude-fable | EXP-008 A3: interaction-minimising schedule differs from peak-minimising at >= half of pooled n >= 6 points — 0 of 12 — and unfalsifiable as posed (E2): strong confluence makes interaction count schedule-invariant, a fact sigma-glyph EXP-004 H3 had already measured | **FAILS** | `experiments/kappa-exp-008/RESULT.md` |
| W18 | world | claude-fable | EML-001 P-draft 1-3 (draft sub-voice): union beats min N1/N2; >= half fail N1 per-function; ratio <= 0.35 — 3/3 — the draft voice, reasoning WITHOUT the corpus facts, beat both session voices on the per-function question | **HOLDS** | `experiments/eml-exp-001/RESULT.md` |
| W22 | world | claude-fable | EML-001 F1/F2/F3/F6 (session sub-voice) — F1, F6 held; F2 failed badly (22 fail, predicted < 8) and F3 narrowly (0.4574) — knowing the chain-expansion facts made the session voice over-index on reuse | **MIXED** | `experiments/eml-exp-001/RESULT.md` |
| W19 | world | kimi | EML-001 A1-A4 — A1 held (paper-decided); A2/A3/A4 failed — A3 wrong on the count (10, not >= 25) yet exactly right on the mechanism: the ten that beat N1 are precisely the ten largest, threshold 134 nodes | **MIXED** | `experiments/eml-exp-001/RESULT.md` |
| W20 | world | claude-fable | EML-002 P-draft 1-3 (draft sub-voice) — P-draft-1 held on its stated falsifier with both stated mechanisms false (DOMAIN traps on ln(0), not exp overflow); P-draft-2 failed (rho 0.276); P-draft-3 failed in the OPPOSITE direction — truncation needs fewer bits for 10 of 22 | **MIXED** | `experiments/eml-exp-002/RESULT.md`; `experiments/eml-exp-002/RESULT.md` |
| W23 | world | claude-fable | EML-002 F4/F5 (session sub-voice): >= half fail n<=20; e/exp/ln at n<=16 — 2/2 — 14 of 22, and 8/12/12 | **HOLDS** | `experiments/eml-exp-002/RESULT.md` |
| W21 | world | kimi | EML-002 A5-A7 (incl. the knife-edge 'exactly 6') — 0/3 — A5 measured 14; A6: exp and ln need 12; A7 refuted with the opposite sign (rho = -0.725) | **FAILS** | `experiments/eml-exp-002/RESULT.md` |
| A19 | alife | chatgpt | EXP-011 H1-is-false: under the default schedule a fed starving agent never fires again (the feed-then-bury analysis) — exactly as analyzed — 0.0% survival across arms (a)/(b), all seeds; the finding entered the ledger the way it entered the codebase: by reading the phase order, then measuring it | **HOLDS** | `experiments/alife-exp-011/RESULT.md` |
| A20 | alife | claude-fable | EXP-011 H2: fed-then-buried ATP exceeds 10% of ATP granted to starving agents — the threshold was absurdly conservative: 100.0% — every granted unit was collected back the same tick | **HOLDS** | `experiments/alife-exp-011/RESULT.md` |
| A21 | alife | claude-fable | EXP-011 H3: with a cull-free window, survival is 100% and answers match the oracle — 90/90 fired, 66/66 settled survivors hit the whole-run answer — resumption_bound's machinery, used as control-by-contrast | **HOLDS** | `experiments/alife-exp-011/RESULT.md` |
| A22 | alife | claude-fable | EXP-012c XC1: the corpus chooses the phase, not the currency (0 discordant seeds of 5) — 4 of 5 seeds discordant — filed under declared partial contamination that pointed the WRONG way; per-arm producing counts (BF 0/5, FF 3/5) suggest the price axis, unclaimed pending a null (successor 012d) | **FAILS** | `experiments/alife-exp-012c/RESULT.md` |
| A23 | alife | claude-fable | EXP-012c XC2: the conditional factorial (X1-X3) over producing seeds — 0 concordantly producing seeds — the base is empty BECAUSE XC1 failed; the prereg's warning sentence was written for the wrong world and the RESULT says so | **UNADJUDICATED** | `experiments/alife-exp-012c/RESULT.md` |
| A24 | alife | claude-fable | EXP-012c XC3: collapse timing is currency-independent — within-seed spread 1255 > across-seed 856.5; seed 20260827: all four arms die, Book-priced ~3x earlier — 'the more interesting world' of the prereg's own falsifier | **FAILS** | `experiments/alife-exp-012c/RESULT.md` |

## Tallies by voice

| voice | HOLDS | FAILS | RETRACTED | MIXED | UNADJUDICATED | PENDING |
|---|---|---|---|---|---|---|
| alife-exp-005-prereg-author (model not named in artifact) | 0 | 3 | 0 | 0 | 0 | 0 |
| alife-founding-proposal | 0 | 1 | 0 | 0 | 0 | 0 |
| alife-repository | 4 | 4 | 0 | 2 | 1 | 0 |
| chatgpt | 1 | 0 | 0 | 0 | 0 | 0 |
| claude-fable | 8 | 8 | 0 | 2 | 1 | 0 |
| kimi | 0 | 1 | 0 | 1 | 0 | 0 |
| world-repository | 2 | 5 | 3 | 0 | 0 | 0 |

Adjudicated = everything except PENDING. A PENDING entry names
a preregistration whose harness has not yet produced a RESULT.
