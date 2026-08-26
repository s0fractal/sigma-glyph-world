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
| W18 | world | claude-fable | EML-EXP-001: P-draft 1-3 (draft) and F1-F3+F6 (session), incl. the internal disagreement on per-function null exceedance | **PENDING** | `experiments/EML-EXP-001-preregistration.md`; `experiments/EML-EXP-001-preregistration.md` |
| W19 | world | kimi | EML-EXP-001: A1-A4 (ratio(U)<0.001; cross_only>=0.65; >=25 beat min N1; largest shared subtree >100k nodes, >=3 sharers) | **PENDING** | `experiments/EML-EXP-001-preregistration.md` |
| W20 | world | claude-fable | EML-EXP-002: P-draft 1-3 (draft) and F4-F5 (session) | **PENDING** | `experiments/EML-EXP-002-preregistration.md`; `experiments/EML-EXP-002-preregistration.md` |
| W21 | world | kimi | EML-EXP-002: A5-A7 (exactly 6 of 22 fail n<=20; e/exp/ln at n<=8; Spearman >=0.55 excluding floor outliers) | **PENDING** | `experiments/EML-EXP-002-preregistration.md` |

## Tallies by voice

| voice | HOLDS | FAILS | RETRACTED | MIXED | UNADJUDICATED | PENDING |
|---|---|---|---|---|---|---|
| alife-exp-005-prereg-author (model not named in artifact) | 0 | 3 | 0 | 0 | 0 | 0 |
| alife-founding-proposal | 0 | 1 | 0 | 0 | 0 | 0 |
| alife-repository | 4 | 4 | 0 | 2 | 1 | 0 |
| claude-fable | 4 | 6 | 0 | 0 | 0 | 2 |
| kimi | 0 | 0 | 0 | 0 | 0 | 2 |
| world-repository | 2 | 5 | 3 | 0 | 0 | 0 |

Adjudicated = everything except PENDING. A PENDING entry names
a preregistration whose harness has not yet produced a RESULT.
