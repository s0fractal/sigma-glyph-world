#!/usr/bin/env python3
"""Pointwise live (term, book, total) census, for a successor to reason over.

Codex's review of `f9d6e5b` observed that `max(book)/max(term)` is a ratio of
maxima taken at different instants and is therefore not the bookkeeping
composition of any state -- a defect the preregistration author has owned as
his own, since the preregistration defined that statistic. Choosing the
replacement estimand belongs to KAPPA-EXP-009's preregistration, not to this
harness.

So this emits the raw trace and computes nothing from it. One row per
(family, n, schedule), each carrying the live census before the first
interaction and after every one. `--check` re-derives every trace and compares
it exactly. No gate and no prediction reads this file.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

import families as fam  # noqa: E402
import graph_machine as gm  # noqa: E402
import optimal_machine as om  # noqa: E402

TRACES = BASE / "traces.json"
BUILDERS = {"h": gm.family_h, "d": gm.family_d, "e": fam.graph_family_e}


def collect_traces() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for family, indices in fam.RANGES.items():
        for n in indices:
            for schedule in om.SCHEDULES:
                pointwise: list[tuple[int, int, int]] = []
                run = om.normalize(om.encode(BUILDERS[family](n)), schedule, pointwise=pointwise)
                rows.append({
                    "family": family, "n": n, "schedule": schedule,
                    "gated": n in {"h": fam.H_RANGE, "d": fam.D_RANGE, "e": [1, 2, 3]}[family],
                    "interactions": run["interactions"],
                    "live_term_book_total": [list(point) for point in pointwise],
                })
    return {
        "experiment": "KAPPA-EXP-008",
        "what": "raw pointwise live census under R_abstract; no estimand is derived here",
        "why": "Codex review of f9d6e5b: max(book)/max(term) composes maxima from "
               "different instants. The replacement estimand is KAPPA-EXP-009's to "
               "preregister; this file only makes the trace available to it.",
        "columns": ["live_term", "live_book", "live_total"],
        "rows": rows,
    }


def collect() -> int:
    if TRACES.exists():
        print("refusing to overwrite frozen traces", file=sys.stderr)
        return 1
    document = collect_traces()
    temporary = TRACES.with_name(f".{TRACES.name}.tmp")
    temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, TRACES)
    print(f"froze {len(document['rows'])} pointwise traces")
    return 0


def check() -> int:
    if not TRACES.exists():
        print("PASS: KAPPA-EXP-008 traces not collected yet")
        return 0
    frozen = json.loads(TRACES.read_text(encoding="utf-8"))
    replay = collect_traces()
    if frozen["rows"] != replay["rows"]:
        differing = [f"{a['family']}_{a['n']} {a['schedule']}"
                     for a, b in zip(frozen["rows"], replay["rows"]) if a != b]
        print(f"FAIL: pointwise traces do not replay: {differing[:5]}", file=sys.stderr)
        return 1
    points = sum(len(row["live_term_book_total"]) for row in frozen["rows"])
    print(f"PASS: {len(frozen['rows'])} pointwise live traces replay exactly "
          f"({points} states). No estimand is derived from them here")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collect", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.collect == args.check:
        parser.error("choose exactly one of --collect or --check")
    return collect() if args.collect else check()


if __name__ == "__main__":
    raise SystemExit(main())
