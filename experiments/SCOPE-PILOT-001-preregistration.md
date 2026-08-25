# SCOPE-PILOT-001 — can verification-scope incidents be coded reproducibly?

**Preregistration for a codebook pilot. Non-normative. No incident has been
sampled for this pilot.**

## Why this pilot exists

The future confirmatory hypothesis is:

> `H-SCOPE`: among verification-infrastructure incidents, failures whose causal
> chain includes “the audited artifact controls the scope of its own audit” are
> more prevalent than in a repository- and time-matched baseline of ordinary CI
> infrastructure incidents.

This pilot does **not** test `H-SCOPE`. Its question is prior:

> Can independent coders apply the proposed incident taxonomy from minimized
> public evidence packets without silently inventing the missing causal chain?

A pilot that changes its own codebook cannot also validate that codebook. The
pilot corpus will therefore be retired after revision. Any prevalence claim
requires a new, mechanically sampled confirmatory corpus and a frozen successor
codebook.

## Unit of analysis

One unit is an **incident**, not an issue or commit. An incident is one causal
chain in which an intended automated control accepted, omitted, or misclassified
an artifact it was expected to check. Several links may evidence one incident;
one issue containing two independent causes becomes two incidents.

Build failures that fail closed, feature requests without an observed false
acceptance, and defects in the product under test rather than its control are
out of scope.

## Pilot sample

The pilot is purposive because its purpose is to break the taxonomy, not estimate
prevalence.

- target: 8–12 admissible incidents;
- at least 3 unrelated public repositories;
- at least 3 verification-control kinds among tests, proofs, static analysis,
  lint/type checks, and artifact/conformance validation;
- at least 2 negative controls where the audited artifact does **not** choose the
  scope;
- at least 2 candidates expected to require multiple labels;
- no more than 4 incidents from one repository.

Search queries, rejected candidates, and rejection reasons are retained. Search
stops at 12 admissible packets or when 40 candidates have been screened,
whichever comes first. Convenient or famous incidents may be included, but the
pilot must label that selection and may make no frequency claim.

## Evidence packet

Every packet must contain:

1. repository and incident date or bounded date range;
2. stable public URLs for the report and, where available, the fixing change;
3. the intended control and the false acceptance it produced;
4. a paraphrased causal chain grounded in the linked evidence;
5. a minimized reproducer, or an explicit statement that none is available;
6. a counterclassification: the strongest plausible competing primary label;
7. evidence confidence: `VERIFIED`, `SUPPORTED`, or `TENTATIVE`;
8. `FACT`, `DERIVATION`, and `UNKNOWN` fields kept separate.

`VERIFIED` requires either an executable reproducer or a fixing change whose
tests demonstrate the failure boundary. A maintainer explanation without that
boundary is `SUPPORTED`. Search snippets and third-party summaries alone are
`TENTATIVE` and cannot enter the blinded coding set.

## Coding procedure

The codebook is committed before sampling. Each admissible packet is then
rendered without repository fame signals where removal does not destroy causal
evidence. Coders receive the same packet and frozen prompt in isolated contexts;
they do not see other coders’ answers.

Each coder returns:

- zero or more mechanism labels;
- exactly one primary label, or `INSUFFICIENT_EVIDENCE`;
- `scope_controlled_by_audited_artifact`: `yes`, `no`, or `unknown`;
- evidence identifiers supporting each label;
- one counterexample that would change the primary label;
- confidence: `high`, `medium`, or `low`.

Model names, exact versions, prompt digests, tool access, and whether web access
was enabled are receipt fields. Model agreement is prompt-conditioned inter-rater
agreement, not truth and not independent review.

## Pilot measures

The pilot reports, without testing `H-SCOPE`:

- admissible / screened candidates and rejection reasons;
- missing evidence fields by packet;
- exact agreement on primary label;
- exact agreement on the scope-control ternary;
- pairwise Jaccard agreement on multilabel sets;
- Krippendorff’s alpha for nominal primary labels if at least 3 coders and the
  sample size make the computation non-vacuous;
- every disagreement, not only the aggregate score;
- codebook clauses revised as a consequence.

No threshold will be called “validated.” As an engineering continuation rule,
alpha below 0.67 or exact scope agreement below 70% means the current taxonomy
is too ambiguous for confirmatory sampling. Passing that rule merely permits a
new preregistration; it does not establish validity.

## Controls

1. **Empty-evidence control:** a packet containing only a claim must yield
   `INSUFFICIENT_EVIDENCE`, not a mechanism label.
2. **Fail-closed control:** an ordinary failing check is rejected as not an
   incident unless a false acceptance is evidenced.
3. **External-scope negative control:** at least two admitted packets must permit
   `scope_controlled_by_audited_artifact = no`.
4. **Multilabel control:** the format must preserve co-occurring mechanisms; the
   primary label may not erase secondary evidence.
5. **Provenance control:** a packet without stable source URLs or source digests
   is excluded from blinded coding.

## What would make the pilot worthless

- Selecting only incidents already described with the codebook’s vocabulary.
- Treating coder agreement as evidence that the assigned cause is true.
- Repairing ambiguous packets after seeing which answer would improve agreement.
- Using pilot prevalence to support or reject `H-SCOPE`.
- Letting repository identity substitute for incident evidence.
- Quietly discarding disagreements or rejected candidates.

## Outputs

- `experiments/scope-pilot-001/CODEBOOK.md`
- `experiments/scope-pilot-001/candidates.json`
- `experiments/scope-pilot-001/packets/*.json`
- `experiments/scope-pilot-001/validate.py`
- `experiments/scope-pilot-001/PILOT-RESULT.md`

Only the codebook exists at preregistration time. All other outputs come later
and must name any deviations from this document.

