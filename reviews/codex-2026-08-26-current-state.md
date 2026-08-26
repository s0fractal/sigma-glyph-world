# Adversarial scientific review — current state

**Reviewer:** Codex  
**Reviewed commit:** `f9d6e5b0d9c5144f7a1bee97c63055eeb6ca6188` (`main`)  
**Date:** 2026-08-26  
**Verdict:** **CHANGES REQUESTED**

This review targets the current claims, not the earlier state reviewed in
`codex-2026-08-26.md`. Several earlier defects were corrected well: KAPPA-EXP-005
now checks exact recurrences with a mutation, KAPPA-EXP-006 separates fresh
allocation from aliasing, and SCOPE-PILOT-003 preserves its failed frame while
retracting the changed-estimand conclusion. KAPPA-EXP-008 introduces a new and
more fundamental accounting boundary problem.

## Findings

### [BLOCKER] The cross-representation resource comparison externalises readback

`experiments/kappa-exp-008/measure.py:64-74` computes `peak_total`, interactions,
and both κ values during graph normalisation, then calls `om.readback(net)` only
after the measured run has ended. The readback materialises the explicit normal
form used by G1 and by the headline examples, but none of its allocations, work,
or peak live state is priced.

The result explicitly relies on this exclusion: `RESULT.md:61-71` says the
sharing graph never expands the context because readback does, then compares a
52-node peak and 121 interactions with a readback of `s^65536 z`. This is a
change of semantic boundary, not yet a resource improvement on a common task.

There are only two coherent contracts:

1. **The outcome is the compact graph normal form.** Then compare machines that
   all produce an observationally equivalent compact interface and do not use an
   unpriced tree readback as their semantic certificate.
2. **The outcome is the explicit normal form.** Then include readback time,
   allocations, and peak live nodes in the graph machine's cost and peak.

Under the second contract, `e_4` must expose at least the 131073-occurrence output
somewhere, so “peak 52” cannot describe the end-to-end task. Under the first,
`R_fresh` and `R_update` are being penalised for delivering a stronger output
representation.

**Required correction:** preregister a semantic interface and an end-to-end
resource boundary before further cross-representation κ claims. Report reducer-
internal and readback-inclusive costs separately. The schedule-to-schedule result
inside the same graph representation may remain; the representation hierarchy
does not survive as stated.

### [BLOCKER] The strongest `e_4` observation is outside G1/G2 on a known-unsound machine

The harness deliberately shrinks the gated `e` range to `[1, 3]`
(`measure.py:41-47`), while `e_4` is reported throughout and supplies the most
spectacular “121 interactions, peak 52, readback `s^65536 z`” observation. The
machine is already known to disagree with the reference calculus. At `e_4` there
is no independent reference normal form; the readback is checked only for its
expected Church numeral shape.

Calling the arithmetic value a `FACT` (`RESULT.md:207-208`) is defensible as a
property of the returned tree, but not as evidence that this unsound reducer
correctly normalised the source or achieved the stated resource collapse. The
same implementation produces a plausible-looking but nonterminating readback on
the named counterexample.

**Required correction:** move all `e_4` resource claims to `HYPOTHESIS` or
`UNGATED OBSERVATION`, exclude them from scorecards and headline evidence, and
add an independent semantic oracle capable of handling that point before using
it as confirmation. Saturation of the tree oracle is not permission to promote
an unverified graph answer.

### [MAJOR] The abstract unsound reducer does not establish lower bounds for full Lamping/lambdascope

The implementation is candidly “labelled fans and no bracket/croissant oracle”
and is not one of the two implementations permitted by the preregistration
(`RESULT.md:129-149`). It then derives that its `peak_book` and `interactions` are
lower bounds on a full reducer (`RESULT.md:166-173`). That monotonicity does not
follow.

An unsound abstract rewrite system is not necessarily a subtrace of the full
algorithm. Control nodes can change which interactions occur, their order,
garbage collection, and the live graph; fixing wrong fan annihilations may remove
work as well as add it. A node-set inclusion intuition is insufficient for a
peak or interaction-count lower bound.

**Required correction:** rename this representation to `R_abstract` and limit
claims to its gated fragment. Prove a simulation/cost monotonicity theorem before
calling its measurements lower bounds for another machine. Otherwise label A2
simply untested, without a directional bound.

### [MAJOR] The soundness rate has an invalid denominator and the green check does not replay it

`soundness.py:54-84` silently returns `None` when the reference exceeds its step
limit or raises one of several exceptions, and skips saturated optimal runs. Yet
`sweep()` increments `terms_checked` unconditionally (`soundness.py:87-101`). A
fresh classification of the same frozen 1500 samples found:

```text
reference eligible:   1493
fully comparable:     1493
reference unsettled:     6
reference exception:     1
disagreements:            1
```

The evidence therefore supports 1/1493 comparable samples, with seven excluded,
not 1/1500 tested samples. This small numeric change matters because the script
purports to measure the boundary of a known-unsound machine.

More seriously, `soundness.py --check` recomputes only 120 samples. Its condition
at lines 137-141 can never reject a mismatch while the frozen disagreement count
is 1: the final conjunct requires that count to be zero. The command then prints
the frozen 1/1500 claim even though it replays only the hand-written witness. The
statement in `RESULT.md:242-244` accurately says it replays the counterexample,
but the controls section and terminal output make the frozen sweep look freshly
verified.

**Required correction:** emit explicit outcome categories and use
`disagreements/comparable` as the rate. On a full release check, regenerate all
1500 categorical outcomes or freeze the generated terms and compare an exact
per-term verdict vector/digest. Add mutations to disagreement count, exclusion
count, and one verdict.

### [MAJOR] `peak_book / peak_term` is not a bookkeeping share at any instant

The result correctly observes that term and bookkeeping peaks occur at different
times (`RESULT.md:54-59`). Nevertheless `measure.py:71` divides the two separate
marginal maxima and A2 interprets the ratio as where the cost “moves”. A ratio of
maxima from different states is not the bookkeeping composition of any state and
is not a share of `peak_total`.

This can reverse comparisons: a schedule can have a large term peak early and a
large book peak late while never holding much of both. The experiment already
records enough live-state information to define coherent alternatives.

**Required correction:** choose one before rerunning A2: bookkeeping fraction at
the time of total peak, `max_t(book_t / total_t)`, integral node-time share, or a
two-dimensional Pareto trace. Do not call `max(book)/max(term)` a share.

### [MODERATE] “Optimal” is certified by a necessary sanity check, not an optimality criterion

G2 requires `beta_interactions <= min(tree steps)` and exactly `n` on `h_n`.
Together with local readback equivalence, that shows sharing and local semantic
agreement. It does not establish Lévy optimality or membership in a correctly
implemented Lamping/lambdascope algorithm. The result admits this at
`RESULT.md:221-228`, but identifiers, tables, and headline claims still present
the implementation as `R_optimal`.

Names are part of the scientific interface. Rename it `R_abstract` until there is
an oracle, residual-family criterion, or formal simulation adequate to the word
“optimal”.

### [MODERATE] The SCOPE-PILOT-003 erratum has not propagated to the repository-level claims

The current screening erratum retracts the claim that resolution sampling is the
unique successor and marks the frame-versus-instrument attribution contested.
The README still says the four near misses “locate the real scarcity” in success
contracts (`README.md:37-41`) and that the result argues the successor “must
sample resolutions rather than symptoms” (`README.md:141-145`). Those sentences
restore the conclusion the erratum removed.

**Required correction:** make the README use the corrected status: the pilot
demonstrates failure of this frame-plus-instrument combination; resolution
sampling is one calibration or evidence-augmentation option, not an identified
successor or causal diagnosis.

### [MODERATE] The release documentation understates its mutation set

`README.md:114-118` says the release gate rejects 37 mutations. The current
manifest has 17 frozen and 20 required artifacts; the mutation runner exercises
17 frozen deletions + 20 required deletions + 17 digest corruptions = **54**.
This is documentation drift in the exact section meant to define release
semantics.

**Required correction:** derive the count in generated output or omit the literal
number from the README. Add a check that any literal count agrees with the
manifest if it remains user-facing.

## Verification performed

Commands were run from the reviewed worktree:

```sh
tools/test-all.sh
tools/test-release.sh
python3 tools/mutation-test.py
```

`tools/test-all.sh` completed successfully. The release and mutation results are
also green: the gate rejected all **54** mutations (17 frozen-artifact deletions,
20 required-artifact deletions, and 17 digest corruptions). These checks establish
reproduction and fail-closed artifact coverage, not the validity of the measured
resource boundary.

I also replayed the soundness sample generator with explicit categorical
accounting rather than changing the committed harness. That produced the
1493/6/1 partition above and the same one disagreement. No research artifact was
modified.

## Proposed next experiment: KAPPA-EXP-009

The scientifically useful next question is not whether another graph can produce
a smaller internal peak. It is whether the ordering survives a common semantic
interface.

Preregister:

1. one output contract: compact graph with a fixed observer API, or explicit
   normal form;
2. reducer-internal and end-to-end work/peak, with readback separately itemised;
3. a sound full Lamping/lambdascope implementation or an independently validated
   bounded fragment;
4. comparable/excluded/error categories for every generated term;
5. pointwise live term/book/total traces and a coherent composition estimand;
6. an adversarial family where the observer must inspect the full output, plus a
   family where compact observation is genuinely sufficient.

The prediction worth risking is then crisp: does `R_abstract`'s ordering persist
under readback-inclusive cost, or was the apparent collapse produced by moving
materialisation across the measurement boundary?

## Scientific disposition

KAPPA-EXP-008 supports a bounded and interesting result: on the gated families,
two schedules of this particular abstract sharing graph have equal internal
interaction counts and, on `h_n` and `d_n`, equal internal peak totals. It does
not yet establish a cross-representation resource hierarchy, end-to-end κ,
correctness at `e_4`, or a lower bound for full optimal reduction.

That narrower claim is still worth keeping. The boundary failure is precisely
the next research object.
