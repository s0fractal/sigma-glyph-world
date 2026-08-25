# SCOPE-PILOT-002 coder prompt

You are coding one blinded verification-incident packet under the attached
CODEBOOK.md. Use only the packet and codebook. Do not browse, infer repository
identity, or repair missing evidence from memory.

Return one JSON object conforming to `coding.schema.json`.

Rules:

1. Decide admission and contract status before assigning mechanisms.
2. If admission is not `ADMIT`, return an empty mechanism list and use the same
   non-admission value as `primary` where the schema permits it.
3. Identify selector, checker, adapter, and gate by their semantic interfaces,
   not by package or command names.
4. Cite packet evidence identifiers for each material decision.
5. Give a concise inspectable rationale. Do not provide hidden chain of thought.
6. State one concrete counterclassification fact that would change the result.
7. Use `unknown` or `INSUFFICIENT_EVIDENCE` instead of filling gaps with usual
   behavior.

Model agreement is not truth. Your answer will be retained even when it
disagrees with other coders.
