# Dialogue provenance

This repository currently contains model dialogue artifacts supplied by the
repository owner:

| artifact | attributed voice | role in the dialogue |
|---|---|---|
| `talks/gemini-001.md` | Gemini | generates physical and cosmological correspondences |
| `talks/claude-fable-001.md` | Claude Fable | separates scientific hypotheses from speculation and proposes tests |
| `INTENTIONS.md` | Codex | records the intended research boundaries after critique and counter-critique |
| `talks/claude-fable-002.md` | Claude Fable | attacks the successor question of KAPPA-EXP-001 as trivial, proposes the strategy-spread reframing, and reports the Σ-GLYPH accounting model |

`talks/claude-fable-002.md` carries the header format described below, with
`UNKNOWN` in every field the repository cannot establish. Its claim about the
Σ-GLYPH accounting model was independently checked against
`spec/book-1-truth.en.md` §3.4 and `spec/appendix-a-complexity.md` §1 before
being used; see the erratum in `experiments/kappa-exp-001/RESULT.md`. Nothing
else in it has been verified.

The exact prompts, platform receipts, model versions, sampling parameters, and
generation transcripts are not present. Therefore these files establish the
text and its local attribution only. They do not establish independent review,
priority, authorship in a legal sense, or validation of any scientific claim.

Future dialogue artifacts should be append-only and numbered. When available,
their header should record:

- attributed model and exact version;
- date and platform;
- prompt or a digest/link to it;
- whether earlier answers were visible;
- whether tools or web search were available;
- whether the file is verbatim or edited.

Corrections belong in a later artifact or an explicit erratum. Silent edits
would destroy the disagreements this repository exists to preserve.

