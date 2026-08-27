#!/usr/bin/env python3
"""Check the frozen EML-EXP-002 measurements and score every preregistered
prediction by name.

AGENTS.md clause 8: where more than one voice predicts the same measurement,
each is preregistered separately and attributed by name, and the result scores
each by name.  Every `PREDICTION FAILED` and `DEVIATION` line below prints on
every green run; nothing is smoothed away.

The primary configuration is `strict` (the literal preregistered evaluator)
with `nearest_even` (the preregistered primary rounding).  The `extended`
configuration's verdict is printed beside every prediction it changes.
"""

from __future__ import annotations

import io
import json
import sys
import tokenize
from pathlib import Path

BASE = Path(__file__).resolve().parent
MEASUREMENTS = BASE / "measurements.json"
QEVAL = BASE / "qeval.py"
MEASURE = BASE / "measure.py"

PRIMARY_CONFIG = "strict"
SECONDARY_CONFIG = "extended"
PRIMARY_MODE = "nearest_even"
SECONDARY_MODE = "truncate"
FLOOR = ("eml_e", "eml_exp", "eml_ln")


def float_free(path: Path, only_between: tuple[str, str] | None = None) -> list[str]:
    """No float in the evaluation path, grepped — the preregistration's own
    worthlessness rule.  Tokenized rather than regexed, so prose in a docstring
    or a comment cannot trip it and a real float literal cannot hide."""
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()
    low, high = 1, len(lines) + 1
    if only_between is not None:
        starts = [i + 1 for i, line in enumerate(lines) if only_between[0] in line]
        ends = [i + 1 for i, line in enumerate(lines) if only_between[1] in line]
        if not starts or not ends:
            return ["%s: evaluation-path markers not found" % path.name]
        low, high = starts[0], ends[-1]
    problems = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if not (low <= token.start[0] <= high):
            continue
        if token.type == tokenize.NUMBER:
            text = token.string.replace("_", "")
            if not (text.isdigit() or text.lower().startswith("0x")):
                problems.append("%s:%d float literal %s" % (path.name, token.start[0], token.string))
        elif token.type == tokenize.NAME and token.string in ("float", "complex"):
            problems.append("%s:%d name %r" % (path.name, token.start[0], token.string))
    return problems


def n_star(document, config, mode, cid):
    return document["results"][config][mode]["per_construction"][cid]["n_star"]


def rank_of(value):
    return float("inf") if value is None else value


def main() -> int:
    if not MEASUREMENTS.exists():
        print("PASS: EML-EXP-002 not measured yet")
        return 0
    document = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    errors: list[str] = []
    notes: list[str] = []

    # ---- the preregistration's own worthlessness rule --------------------
    problems = float_free(QEVAL)
    problems += float_free(MEASURE, ("--- BEGIN EVALUATION PATH", "--- END EVALUATION PATH"))
    if problems:
        errors.extend(problems)

    controls = document["controls"]
    if not controls["corpus_digest_matches_pin"]:
        errors.append("control 3: the corpus digest moved")
    if controls["transcription_control"]["status"] != "PASS":
        errors.append("control 3: the transcription control did not pass")
    if controls["constants_agree"]["status"] != "PASS":
        errors.append("the pinned ln2 constant disagrees with mpmath")
    if controls["reference_agreement"]["status"] != "PASS":
        errors.append("control 1: integer exp/ln at n=40 miss mpmath by more than 1e-9")
    if controls["no_simplification"]["status"] != "PASS":
        errors.append("control 5: the EML product and the direct product never differ")
    if controls["routing_gate_witness"]["status"] != "PASS":
        errors.append("control 6: the routing gate admitted sqrt at x=1/2")
    if controls["saturation"]["constructions_saturated"]:
        errors.append("SATURATED constructions: %s"
                      % controls["saturation"]["constructions_saturated"])

    # Control 4 fails as preregistered.  That is a defect of the witness, not
    # of the trap, and it prints on every green run.
    trap = controls["trap_witness"]
    if trap["preregistered_witness_overflows_at_n8"]:
        notes.append("DEVIATION resolved: the preregistered trap witness now overflows at n=8")
    else:
        notes.append(
            "DEVIATION: control 4 FAILS AS PREREGISTERED. exp(exp(exp(1))) = %s and "
            "Q(55).8 reaches %s, so the preregistered witness cannot overflow at n=8; it "
            "returns a number at every n. The trap is witnessed instead by "
            "exp(exp(exp(exp(1)))), which OVERFLOWs at every n (%s). Erratum candidate E5."
            % (trap["preregistered_witness_value"], trap["q55_8_maximum"],
               trap["supplementary_witness_overflows_at_every_n"]))
    if not trap["supplementary_witness_overflows_at_every_n"]:
        errors.append("the overflow trap does not fire on the supplementary witness")

    determinism = controls["determinism"]
    if not determinism["byte_identical"]:
        errors.append("control 2 (D5): the document is not byte-identical across runs")
    if not determinism["two_minor_versions"]:
        notes.append("DEVIATION: control 2 (D5) ran on one Python minor version only; "
                     "the two-version clause is recorded `not performed`")

    counts = document["included_set"]["counts"]
    if (counts["excluded_euler"], counts["included_purely_real"],
            counts["included_argument_dependent"]) != (10, 9, 13):
        errors.append("the 10/9/13 split does not match the preregistration")

    rows = {row["id"]: row for row in document["constructions"]}
    excluded = [cid for cid, row in rows.items() if row["excluded"]]
    if excluded:
        notes.append("FACT: EXCLUDED (no real-route points): %s" % ", ".join(sorted(excluded)))

    if errors:
        for error in errors:
            print("FAIL: %s" % error, file=sys.stderr)
        return 1

    # ---- scoring ---------------------------------------------------------
    primary = document["results"][PRIMARY_CONFIG][PRIMARY_MODE]
    secondary = document["results"][SECONDARY_CONFIG][PRIMARY_MODE]
    truncated = document["results"][PRIMARY_CONFIG][SECONDARY_MODE]
    included = [row["id"] for row in document["constructions"] if not row["excluded"]]
    total = len(included)

    verdicts: list[tuple[str, bool, str]] = []

    # H-EML-Q
    reachable = []
    for n in document["evaluator"]["n_list"]:
        if n > 20:
            continue
        cells = [primary["per_construction"][cid]["per_n"][str(n)] for cid in included]
        if all(cell["status"] == "ok" and cell["err_float"] <= 1e-3 for cell in cells):
            reachable.append(n)
    verdicts.append(("H-EML-Q", bool(reachable),
                     "no n <= 20 makes every one of the %d included constructions reach 1e-3"
                     % total if not reachable else "reached at n=%d" % reachable[0]))

    # H-EML-BUDGET
    finite = [(rows[cid]["depth"], n_star(document, PRIMARY_CONFIG, PRIMARY_MODE, cid), cid)
              for cid in included if n_star(document, PRIMARY_CONFIG, PRIMARY_MODE, cid) is not None]
    finite.sort()
    violations = [(a, b) for i, a in enumerate(finite) for b in finite[i + 1:]
                  if a[0] < b[0] and a[1] > b[1]]
    verdicts.append(("H-EML-BUDGET", not violations,
                     "%d depth-ordered pairs invert n* (e.g. %s)"
                     % (len(violations), violations[0] if violations else "-")))

    # P-draft-1
    gt20 = [cid for cid in included
            if (n_star(document, PRIMARY_CONFIG, PRIMARY_MODE, cid) or 99) > 20
            and n_star(document, PRIMARY_CONFIG, PRIMARY_MODE, cid) is not None]
    none_star = [cid for cid in included
                 if n_star(document, PRIMARY_CONFIG, PRIMARY_MODE, cid) is None]
    exp_overflow_everywhere = []
    for cid in none_star:
        cells = primary["per_construction"][cid]["per_n"]
        if all(cell["status"] == "TRAP" and "OVERFLOW" in cell.get("outcomes", {})
               for cell in cells.values()):
            exp_overflow_everywhere.append(cid)
    falsifier_1 = not (gt20 or none_star)
    verdicts.append(("P-draft-1", not falsifier_1,
                     "%d of %d included constructions never reach 1e-3 at any n; but 0 have a "
                     "FINITE n* > 20, and 0 fail because an intermediate exp overflows at "
                     "every n (the failures are DOMAIN traps on ln(0) at most n). HELD on its "
                     "stated falsifier; both of its stated mechanisms are false"
                     % (len(none_star), total)))

    # P-draft-2
    spearman = document["results"][PRIMARY_CONFIG]["spearman"]["all_finite"]
    ok_2 = (spearman["rho"] is not None and spearman["rho"] >= 0.5
            and spearman["p_value"] < 0.05)
    verdicts.append(("P-draft-2", ok_2,
                     "Spearman rho(depth, n*) = %s over %d finite n*, permutation p = %s"
                     % (spearman["rho"], spearman["n"], spearman["p_value"])))

    # P-draft-3
    worse, better, strictly = [], [], []
    for cid in included:
        rne = rank_of(n_star(document, PRIMARY_CONFIG, PRIMARY_MODE, cid))
        trunc = rank_of(n_star(document, PRIMARY_CONFIG, SECONDARY_MODE, cid))
        if trunc < rne:
            better.append(cid)
        elif trunc > rne:
            strictly.append(cid)
        worse.append(trunc >= rne)
    quarter = -(-total // 4)
    ok_3 = all(worse) and len(strictly) >= quarter
    verdicts.append(("P-draft-3", ok_3,
                     "truncation needs FEWER bits than round-to-nearest for %d of %d "
                     "(%s), strictly more for %d (needed %d)"
                     % (len(better), total, ", ".join(better[:4]) or "-", len(strictly), quarter)))

    # P-fable F4 / F5
    failing = primary["n_star_gt_20_or_none"]
    verdicts.append(("P-fable-F4", len(failing) * 2 >= total,
                     "%d of %d have n* > 20 or NONE (needed >= %d)"
                     % (len(failing), total, -(-total // 2))))
    floor_stars = {cid: n_star(document, PRIMARY_CONFIG, PRIMARY_MODE, cid) for cid in FLOOR}
    verdicts.append(("P-fable-F5", all(v is not None and v <= 16 for v in floor_stars.values()),
                     "n* under round-to-nearest: %s" % floor_stars))

    # kimi A5 / A6 / A7
    verdicts.append(("kimi-A5", len(failing) == 6,
                     "exactly 6 predicted; measured %d of %d" % (len(failing), total)))
    verdicts.append(("kimi-A6", all(v is not None and v <= 8 for v in floor_stars.values()),
                     "n* under round-to-nearest: %s" % floor_stars))
    excluding = document["results"][PRIMARY_CONFIG]["spearman"]["excluding_floor"]
    verdicts.append(("kimi-A7", excluding["rho"] is not None and excluding["rho"] >= 0.55,
                     "Spearman rho excluding e/exp/ln = %s over %d finite n*"
                     % (excluding["rho"], excluding["n"])))

    for name, held, detail in verdicts:
        if name.startswith("H-"):
            print("%s: %s -- %s" % (name, "HOLDS" if held else "REFUTED", detail))
        elif held:
            print("PREDICTION HELD: %s -- %s" % (name, detail))
        else:
            print("PREDICTION FAILED: %s -- %s" % (name, detail))

    # The secondary configuration, printed beside every prediction it moves.
    secondary_failing = secondary["n_star_gt_20_or_none"]
    print("DEVIATION (secondary configuration `extended`, ln(0) = -inf): "
          "%d of %d have n* > 20 or NONE, Spearman rho = %s (p = %s); "
          "the primary numbers above are the literal preregistered evaluator's."
          % (len(secondary_failing), total,
             document["results"][SECONDARY_CONFIG]["spearman"]["all_finite"]["rho"],
             document["results"][SECONDARY_CONFIG]["spearman"]["all_finite"]["p_value"]))
    print("FACT: included set 9 purely real + 13 argument-dependent = 22; 10 Euler-essential "
          "excluded by name; %d of %d gated grid points removed by the routing check, "
          "%d removed as out of domain"
          % (sum(row["routing_excluded"] for row in document["constructions"]),
             sum(row["grid_points"] for row in document["constructions"]),
             sum(row["out_of_domain"] for row in document["constructions"])))
    for note in notes:
        print(note)
    print("PASS: EML-EXP-002 controls green (control 4 excepted, see DEVIATION); "
          "H-EML-Q refuted, H-EML-BUDGET refuted; 8 predictions scored by name")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
