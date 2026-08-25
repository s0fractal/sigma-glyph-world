# SCOPE-INSTRUMENT-001 — calibration result

**Status: instrument-local `DERIVATION`; no independent coding; no hypothesis
score.**

## Result

The component model resolves the package-boundary ambiguity, but it exposes a
larger admission problem: reproducible behavior is not sufficient evidence for
the meaning of success.

On nine deliberately difficult retired packets:

- 3 have an `ESTABLISHED` success contract;
- 6 are `DISPUTED` because the packet contains only reporter expectation or an
  unmerged proposed fix for the relevant semantic boundary;
- the three admissible cases localize to one adapter breach, one gate breach,
  and one multicausal selector-plus-adapter chain;
- derived scope self-selection is `yes` for 4 cases, `no` for 3, and `unknown`
  for 2.

These are author-calibration counts, not inter-rater measurements.

## What changed conceptually

`FACT`: all nine packets retain primary-source evidence for observed behavior.

`DERIVATION`: six nevertheless cannot establish false acceptance under the new
instrument, because their packet does not independently establish what the
governing success signal promised. The old admission gate conflated:

1. an executable reproduction of behavior;
2. a reporter's expectation about that behavior; and
3. an independently evidenced success contract.

The third item is now mandatory before mechanism coding. This prevents an open
feature request or surprising no-op from becoming an “incident” merely because
the packet author prefers different semantics.

## Boundary cases

- Retired `P01` becomes unambiguous: the selector returns an empty set, the
  checker fails closed, and the adapter reverses that outcome. Package naming is
  irrelevant; `ADAPTER_MISREPRESENTED_RESULT` is the unique sufficient repair
  site.
- Retired `P08` becomes a gate defect: selection, checking, and summary retain
  failures, while the process-status gate ignores them.
- Retired `P03` remains genuinely multicausal: independently fencing invalid
  selector output or correctly adapting excluded-versus-expected results would
  each prevent the false success. Forcing one primary would discard a live
  repair site.
- Retired `P05` remains reproducible but loses incident admission: the packet
  does not establish whether “no files” applies to each declared path or their
  combined match set.
- Retired `P11` records a striking zero exit with failures, but its packet still
  lacks accepted evidence that the aggregate report task itself was promised as
  a strict gate rather than a report generator.

## Instrument disposition

`DECISION`: carry the component topology, contract tiers, governing signal,
authority relation, and sufficient-repair-site rule into a successor codebook.

`DECISION`: do not carry the retired packet classifications. Any successor pilot
must collect contract evidence before exposing a packet to coders.

`DECISION`: keep `MULTICAUSAL`, `CONTRACT_DISPUTED`, and
`INSUFFICIENT_EVIDENCE`; a mandatory single primary label created false
precision.

## Reproduction

From the repository root:

```sh
python3 experiments/scope-instrument-001/validate.py
```

Expected receipt:

```text
PASS: 9 retired calibration cases; contracts={'DISPUTED': 6, 'ESTABLISHED': 3}; primaries={'ADAPTER_MISREPRESENTED_RESULT': 1, 'CONTRACT_DISPUTED': 6, 'GATE_OMITTED_OR_IGNORED_RESULT': 1, 'MULTICAUSAL': 1}
```

Green execution establishes internal consistency of the authored topologies. It
does not establish that another coder would draw the same boundaries.
