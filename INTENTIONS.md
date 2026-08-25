# Intentions — 2026-08-25

**DRAFT. Non-normative.** These are intended investigations, not results and not
commitments by Σ-GLYPH.

## The question

The repository will not ask whether Σ-GLYPH “explains the world.” It will ask a
narrower question:

> Which systems admit a single resource potential that bounds both work and
> materialized state, which systems do not, and what breaks when the result is
> transferred?

For deterministic systems the candidate may be a strictly decreasing potential
such as `Φ = size + budget_remaining`. For stochastic systems it may instead be
a supermartingale or a potential with negative expected drift. Neither form is
assumed to exist outside the machine where it was proved.

## Track A — sharing and the price gap

### Current boundary

- `FACT`: ALIFE-EXP-005 measured a small whole-corpus shadow gap at its pinned
  budget and corpus. That result does not establish an unbounded trajectory gap.
- `DERIVATION`: the local `R-S` price gap between hash-leaf pricing and deep-copy
  pricing can grow without bound over a constructed family whose addressed
  argument grows while its thunk remains one hash leaf.
- `CONTESTED`: a quantity called κ is not yet well-defined enough to compare
  machines. “Paid cost / actual work” may normalize away the difference it was
  meant to expose.

### Intent

Define a machine as at least

`M = (calculus, representation, evaluation strategy, primitive cost model)`

and keep three comparisons separate:

1. the price gap at the local duplication action;
2. total cost to the same outcome on the same semantic task;
3. peak materialized state on that trajectory.

Construct a depth-indexed minimal family first. Only after two evaluators agree
on input, outcome, and charged primitives will an external workload such as a
functional benchmark suite be admissible.

### Falsifiers

- The local gap fails to grow under the fixed representations.
- The apparent whole-run gap disappears after all downstream materializations
  are counted.
- The compared evaluators change semantics or strategy in addition to sharing.

## Track B — local prepayment and coordination

### Current boundary

- `FACT`: static local quotas are a zero-message counterexample to the claim
  that every hard global bound needs synchronization at every step.
- `HYPOTHESIS`: preserving a hard cap while remaining work-conserving under
  dynamic demand requires transferable rights or coordination.
- `UNKNOWN`: the minimal communication cost. “Messages per unit of budget” is
  not yet a valid lower-bound measure because one message can transfer an
  arbitrary amount.

### Intent

Specify the fault and timing model before stating a theorem: synchronous or
asynchronous execution, partitions, crashes, message size, ownership of rights,
and the definition of availability. Treat escrow tokens, bounded counters, and
static partitions as first-class candidate protocols rather than exceptions.

The likely measurable object is a trade-off among:

- hard-cap safety;
- availability while global capacity exists;
- utilization/work conservation;
- messages, bits, or coordination rounds per transfer event.

Kubernetes, cgroups, and distributed rate limiters are comparison targets only
after the formal model identifies which resource and boundary each one actually
controls.

### Falsifiers

- A protocol reaches all vertices of the proposed trade-off in the stated fault
  model without hidden coordination.
- The lower bound depends only on an accounting convention, not communication.
- Real comparison systems do not implement the boundary the model attributes to
  them.

## Track C — who chooses the scope of a control

This is the first intended empirical track because it can meet external data
before the repository builds another internal machine.

### Hypothesis

`HYPOTHESIS`: among verification-infrastructure incidents, failures whose root
includes “the audited artifact controls the scope of its own audit” are more
prevalent than in a repository- and time-matched baseline of ordinary CI
infrastructure incidents.

This does not claim scope control is the only failure class. Vacuous statements,
gutted definitions, tool blind spots, and kernel defects remain distinct or
co-occurring mechanisms.

### Pilot intent

1. Freeze a sampling query and inclusion/exclusion rules.
2. Build one evidence packet per incident: issue, change, claimed bypass, exact
   causal evidence, fix, and a counterexample to the assigned class.
3. Use a multilabel codebook plus one explicitly justified primary mechanism.
4. Send identical, blinded packets to multiple models in isolated contexts,
   with fixed model/version and prompt receipts.
5. Measure agreement as codebook clarity, **not** as truth.
6. Use disagreements to revise the codebook.

The pilot will not score the hypothesis. A frozen codebook and a new
confirmatory corpus are required before prevalence is compared with the matched
baseline. Without independent adjudication, the output will be called a
machine-coded pilot, not external validation.

### Falsifiers

- Scope-controlled failures are no more prevalent than the matched baseline.
- Agreement remains poor after the codebook is revised.
- Classification depends on repository fame or model familiarity rather than
  the minimized evidence packet.
- Externally scoped controls fail at the same rate through other mechanisms,
  eliminating the proposed distinction.

## Promotion rule

A speculation moves to hypothesis only when it has:

1. an operational mapping from source system to measured system;
2. a prediction that differs from a named baseline;
3. a minimized counterexample that would make it fail;
4. a frozen measurement protocol and provenance for its inputs;
5. a status statement separating local green execution from external validity.

A strictly decreasing scalar potential is sufficient where it exists, not a
universal admission requirement. Stochastic potentials and other resource
invariants are admissible if they produce a discriminating prediction.

## What I do not intend to claim

- That formal termination removes physical singularities.
- That ATP accounting explains dark energy, quantum uncertainty, biology, or
  consciousness without a separate operational model.
- That model agreement is ground truth or a substitute for independent review.
- That a local `R-S` discount establishes a whole-program asymptotic advantage.
- That this repository has authority to change or interpret the normative
  Σ-GLYPH specification.

