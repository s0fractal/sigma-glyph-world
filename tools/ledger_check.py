#!/usr/bin/env python3
"""Attributed-prediction ledger: mechanical verification of a curated table.

The ledger is curated by hand in `ledger/entries.json`, because predictions
live in prose. What is mechanical is the tie to the artifacts: every entry
carries one or more (file, quote) references, and this script verifies that
each quote is a LITERAL SUBSTRING of the referenced file. A quote that no
longer matches — because a RESULT was edited, or the curation drifted — fails
the check, so the generated table cannot silently diverge from its sources.

    python3 tools/ledger_check.py           # verify only; exit 1 on mismatch
    python3 tools/ledger_check.py --write   # verify, then regenerate LEDGER.md

Files in the sibling repository (repo key "alife") resolve against
$SIGMA_ALIFE or `../sigma-glyph-alife`. A missing file is reported as
UNVERIFIABLE and does not fail the check — an absent checkout is not a
mismatch — but a present file whose quote does not match always fails.

Per AGENTS.md clause 5: tallies here measure how attributed predictions were
scored by their own repositories' artifacts. They are not ground truth about
any voice, and clause 8's last sentence applies to reading them.
"""

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ROOTS = {
    "world": REPO_ROOT,
    "alife": Path(os.environ.get("SIGMA_ALIFE", REPO_ROOT.parent / "sigma-glyph-alife")),
}
ENTRIES = REPO_ROOT / "ledger" / "entries.json"
LEDGER_MD = REPO_ROOT / "LEDGER.md"

VERDICTS = ["HOLDS", "FAILS", "RETRACTED", "MIXED", "UNADJUDICATED", "PENDING"]


def check(entries):
    mismatches, unverifiable, checked = [], [], 0
    for e in entries:
        for ref in e["refs"]:
            path = ROOTS[e["repo"]] / ref["file"]
            if not path.is_file():
                unverifiable.append((e["id"], ref["file"]))
                continue
            text = path.read_text(encoding="utf-8")
            checked += 1
            if ref["quote"] not in text:
                mismatches.append((e["id"], ref["file"], ref["quote"]))
    return mismatches, unverifiable, checked


def tallies(entries):
    t = {}
    for e in entries:
        row = t.setdefault(e["voice"], {v: 0 for v in VERDICTS})
        row[e["verdict"]] += 1
    return t


def render(entries):
    lines = [
        "# Attributed-prediction ledger",
        "",
        "**GENERATED — do not edit.** Curate `ledger/entries.json` and run",
        "`python3 tools/ledger_check.py --write`. Every quote below is verified",
        "as a literal substring of its source file on every run; the check",
        "fails closed on any mismatch.",
        "",
        "Verdicts are the scoring repositories' own, from their committed",
        "artifacts. Per AGENTS.md clauses 5 and 8: this table measures how",
        "preregistered, attributed predictions were adjudicated — it is not",
        "ground truth about any voice, and reliability must not be inferred",
        "from whether a voice executes.",
        "",
        "## Entries",
        "",
        "| id | repo | voice | prediction | verdict | sources |",
        "|---|---|---|---|---|---|",
    ]
    for e in entries:
        srcs = "; ".join(f"`{r['file']}`" for r in e["refs"])
        note = f" — {e['note']}" if e.get("note") else ""
        lines.append(
            f"| {e['id']} | {e['repo']} | {e['voice']} | {e['prediction']}{note} "
            f"| **{e['verdict']}** | {srcs} |"
        )
    lines += ["", "## Tallies by voice", "",
              "| voice | " + " | ".join(VERDICTS) + " |",
              "|---|" + "---|" * len(VERDICTS)]
    for voice, row in sorted(tallies(entries).items()):
        lines.append("| " + voice + " | " + " | ".join(str(row[v]) for v in VERDICTS) + " |")
    lines += ["", "Adjudicated = everything except PENDING. A PENDING entry names",
              "a preregistration whose harness has not yet produced a RESULT.", ""]
    return "\n".join(lines)


def main():
    entries = json.loads(ENTRIES.read_text(encoding="utf-8"))
    for e in entries:
        assert e["verdict"] in VERDICTS, f"{e['id']}: unknown verdict {e['verdict']}"
        assert e["repo"] in ROOTS, f"{e['id']}: unknown repo {e['repo']}"
    mismatches, unverifiable, checked = check(entries)
    for eid, f in unverifiable:
        print(f"UNVERIFIABLE  {eid}: {f} (checkout absent)")
    for eid, f, q in mismatches:
        print(f"MISMATCH      {eid}: quote not found in {f}:\n    {q!r}")
    print(f"ledger: {len(entries)} entries, {checked} quotes verified, "
          f"{len(unverifiable)} unverifiable, {len(mismatches)} mismatches")
    if mismatches:
        sys.exit(1)
    if "--write" in sys.argv:
        LEDGER_MD.write_text(render(entries), encoding="utf-8")
        print(f"wrote {LEDGER_MD}")


if __name__ == "__main__":
    main()
