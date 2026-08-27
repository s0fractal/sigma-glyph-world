#!/usr/bin/env python3
"""Three machines, two families, two strategies -- under write-through CAS.

The machines are KAPPA-EXP-007's, called through its own `tree_run` and
`graph_run` so that control 1 is satisfied by reuse rather than by
re-implementation. `cas.Instrumentation` patches them for the duration of one
run and restores them afterwards.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent
EXP007 = BASE.parent / "kappa-exp-007"
sys.path.insert(0, str(BASE))

import cas  # noqa: E402

_spec = importlib.util.spec_from_file_location("kappa_exp_007_measure", EXP007 / "measure.py")
exp007 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(exp007)

MEASUREMENTS = BASE / "measurements.json"
EXP007_MEASUREMENTS = EXP007 / "measurements.json"
H_RANGE = list(range(1, 13))
D_RANGE = list(range(1, 11))
MACHINES = ("R_alias", "R_fresh", "R_update")
STRATEGIES = ("S_out", "S_in")
CHECK_UPTO = 6


def instrumented(family: str, n: int, machine: str, strategy: str) -> dict[str, Any]:
    """One run with the CAS live. Returns KAPPA-EXP-007's receipt plus the store."""
    instrument = cas.Instrumentation()
    instrument.install()
    try:
        if machine == "R_update":
            run = exp007.graph_run(family, n, strategy)
        else:
            run = exp007.tree_run(family, n, strategy, machine == "R_fresh")
        trajectory_writes = instrument.store.resident
        readback_new = instrument.readback_writes(instrument.last_seen, machine == "R_update")
    finally:
        instrument.remove()
    return {
        "receipt": run,
        "live_peak": instrument.live_peak,
        "cas_unique_ever": trajectory_writes,
        "cas_unique_ever_with_readback": instrument.store.resident,
        "cas_unique_ever_readback": readback_new,
        "cas_resident_end": instrument.store.resident,
        "cas_resident_trace": list(instrument.store.trace),
        "live_trace": list(instrument.live_trace),
        "put_calls": instrument.store.writes,
        "completeness_misses": instrument.completeness_misses,
        "ratio_ever_over_live": trajectory_writes / instrument.live_peak,
    }


def measure(h_range=None, d_range=None) -> dict[str, Any]:
    h_range = H_RANGE if h_range is None else h_range
    d_range = D_RANGE if d_range is None else d_range
    controls = {
        "reproduces_kappa_exp_007": True,
        "write_through_complete": True,
        "no_gc_identity": True,
        "determinism": True,
        "readback_reported_separately": True,
        "live_peak_is_distinct_hashes": True,
    }
    failures: list[str] = []
    frozen007 = (json.loads(EXP007_MEASUREMENTS.read_text(encoding="utf-8"))["rows"]
                 if EXP007_MEASUREMENTS.exists() else {})
    rows: dict[str, list[dict[str, Any]]] = {}

    for family, indices in (("h", h_range), ("d", d_range)):
        rows[family] = []
        for n in indices:
            row: dict[str, Any] = {"n": n}
            for machine in MACHINES:
                for strategy in STRATEGIES:
                    result = instrumented(family, n, machine, strategy)
                    receipt = result.pop("receipt")
                    receipt.pop("normal_form", None)

                    # Control 1: the instrumentation changed no trajectory.
                    prior = next((item for item in frozen007.get(family, [])
                                  if item["n"] == n), None)
                    if prior is not None:
                        theirs = prior[f"{machine}.{strategy}"]
                        for field, value in theirs.items():
                            if field in receipt and receipt[field] != value:
                                controls["reproduces_kappa_exp_007"] = False
                                failures.append(
                                    f"{family}_{n} {machine}.{strategy}.{field}: "
                                    f"{receipt[field]} != {value} with instrumentation on")
                    # Control 2.
                    if result["completeness_misses"] != 0:
                        controls["write_through_complete"] = False
                        failures.append(f"{family}_{n} {machine}.{strategy}: "
                                        f"{result['completeness_misses']} live hashes never written")
                    # Control 3.
                    if result["cas_resident_end"] != result["cas_unique_ever_with_readback"]:
                        controls["no_gc_identity"] = False
                        failures.append(f"{family}_{n} {machine}.{strategy}: resident(end) != unique_ever")
                    # Control 6: live_peak is exactly what KAPPA-EXP-006/007 called the store.
                    if result["live_peak"] != receipt["peak_distinct_hashes"]:
                        controls["live_peak_is_distinct_hashes"] = False
                        failures.append(f"{family}_{n} {machine}.{strategy}: live_peak "
                                        f"{result['live_peak']} != peak_distinct_hashes "
                                        f"{receipt['peak_distinct_hashes']}")
                    # Control 5.
                    if "cas_unique_ever_readback" not in result:
                        controls["readback_reported_separately"] = False
                    # Control 4.
                    again = instrumented(family, n, machine, strategy)
                    again.pop("receipt")
                    if again != result:
                        controls["determinism"] = False
                        failures.append(f"{family}_{n} {machine}.{strategy}: not deterministic")
                    row[f"{machine}.{strategy}"] = {**result, "receipt": receipt}
            rows[family].append(row)

    return {
        "experiment": "WORLD-CAS-001",
        "policy": {
            "write_through": "every materialized content is put; in-place update path-copies",
            "gc": "none, by preregistration; WORLD-CAS-002 is the named successor for GC",
            "readback": "counted separately, never merged into the trajectory count",
            "digest": "blake2b-128 over (kind, name, child digests)",
        },
        "machines": {name: "verbatim from KAPPA-EXP-007, patched only to observe"
                     for name in MACHINES},
        "ranges": {"h": [h_range[0], h_range[-1]], "d": [d_range[0], d_range[-1]]},
        "controls": controls,
        "control_failures": failures,
        "rows": rows,
    }


def collect() -> int:
    if MEASUREMENTS.exists():
        print("refusing to overwrite frozen measurements", file=sys.stderr)
        return 1
    document = measure()
    temporary = MEASUREMENTS.with_name(f".{MEASUREMENTS.name}.tmp")
    temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, MEASUREMENTS)
    print(f"froze {sum(len(group) for group in document['rows'].values())} rows; "
          f"controls {document['controls']}")
    return 0


def check() -> int:
    if not MEASUREMENTS.exists():
        print("PASS: WORLD-CAS-001 not measured yet")
        return 0
    frozen = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    prefix = list(range(1, CHECK_UPTO + 1))
    recomputed = measure(prefix, prefix)
    for family in ("h", "d"):
        for row in recomputed["rows"][family]:
            prior = next(item for item in frozen["rows"][family] if item["n"] == row["n"])
            if row != prior:
                differing = [k for k in set(row) | set(prior) if row.get(k) != prior.get(k)]
                print(f"FAIL: {family}_{row['n']} differs on recomputation: {differing}", file=sys.stderr)
                return 1
    failed = [name for name, ok in frozen["controls"].items() if not ok]
    if failed:
        print(f"FAIL: preregistered controls failed: {failed}", file=sys.stderr)
        return 1
    top_h = frozen["rows"]["h"][-1]
    print(f"PASS: WORLD-CAS-001 reproduced n<={CHECK_UPTO}; controls ok; on h_{top_h['n']} under "
          f"R_fresh/S_out the live peak is {top_h['R_fresh.S_out']['live_peak']} hashes while the "
          f"store ever holds {top_h['R_fresh.S_out']['cas_unique_ever']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collect", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.collect == args.check:
        parser.error("choose exactly one of --collect or --check")
    sys.setrecursionlimit(200_000)
    return collect() if args.collect else check()


if __name__ == "__main__":
    raise SystemExit(main())
