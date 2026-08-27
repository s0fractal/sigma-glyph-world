#!/usr/bin/env python3
"""EML-EXP-002 measurement harness — EML under fixed-point integers.

Preregistration: `experiments/EML-EXP-002-preregistration.md` (with its
2026-08-27 addendum) at `a6da44b`, committed before this file existed.  The
harness author did not write it and does not edit it; open choices are
recorded in `RESULT.md`'s provenance section and deviations are named there.

THE INCLUDED SET, as preregistered (D7/D8):
    10 Euler-essential constructions excluded BY NAME;
    9 purely-real constructions included fully;
    13 argument-dependent constructions included per-point, gated by a
    complex-routing check in mpmath at 50 digits: a point is real-route iff
    max|Im| along the whole route is < 1e-40.  Excluded points are counted
    per (f, point).  A construction with no real-route grid point is reported
    EXCLUDED (no real-route points), never silently dropped.

Run:  python3 measure.py --collect
      python3 measure.py --check
      python3 measure.py --body-digest
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qeval                                          # noqa: E402
from qeval import MODES, NEAREST, N_LIST, Q, Saturated, TRUNCATE, Trap   # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
BASIS = REPO / "experiments" / "eml-basis" / "basis.json"
TRANSCRIPTION = REPO / "experiments" / "eml-basis" / "transcription_check.py"
MEASUREMENTS = HERE / "measurements.json"

BASIS_SHA256 = "14853489bf3701e276d67e6f6fe6e007ebb507c7dad527b9fe0f4ffd6cdf5475"
SOURCE_SHA256 = "2a3b4219a7784d8fd0b3ffe6e7d3dd570cf73d60f8cf368459122fe78e1421db"

DPS = 50
IMAG_GATE = "1e-40"          # preregistered real-route threshold
EPSILON = "1e-3"             # preregistered, fixed, never revisited
REFERENCE_GATE = "1e-9"      # control 1
PERMUTATIONS = 1000          # P-draft-2's null

# The preregistered grid, as exact rationals so no float enters anywhere.
GRID = (Fraction(1, 10), Fraction(1, 4), Fraction(1, 2), Fraction(1),
        Fraction(3, 2), Fraction(2), Fraction(3), Fraction(5))

EULER_EXCLUDED = ("eml_pi", "eml_cos", "eml_sin", "eml_tan", "eml_arsinh",
                  "eml_arcosh", "eml_arccos", "eml_artanh", "eml_arcsin", "eml_arctan")
PURELY_REAL = ("eml_e", "eml_exp", "eml_ln", "eml_neg1", "eml_two", "eml_minus",
               "eml_sigma", "eml_cosh", "eml_sinh")
ARGUMENT_DEPENDENT = ("eml_sub", "eml_add", "eml_inv", "eml_mul", "eml_sqr", "eml_div",
                      "eml_half", "eml_avg", "eml_sqrt", "eml_pow", "eml_logb",
                      "eml_hypot", "eml_tanh")

# Target-domain restrictions of the preregistered grid.  The grid is entirely
# positive, so the only construction with an out-of-domain grid point is the
# logarithm base, which is undefined at base 1.
DOMAIN_EXCLUSION = {"eml_logb": lambda x, y: x == 1}

CONFIGURATIONS = (("strict", False), ("extended", True))


# ---------------------------------------------------------------------------
# --- BEGIN EVALUATION PATH -------------------------------------------------
# Everything between these markers is integer-only; `validate.py` greps it,
# together with the whole of qeval.py, for floats.
# ---------------------------------------------------------------------------

def parse_dag(text):
    """`(eml A B)` over {eml,1,x,y} into an interned node table plus a
    topological order of the nodes reachable from the root."""
    kinds, lefts, rights, syms = [], [], [], []
    interned = {}

    def leaf(sym):
        key = ("L", sym)
        got = interned.get(key)
        if got is None:
            got = len(kinds)
            kinds.append(0); lefts.append(-1); rights.append(-1); syms.append(sym)
            interned[key] = got
        return got

    def node(a, b):
        key = (a, b)
        got = interned.get(key)
        if got is None:
            got = len(kinds)
            kinds.append(1); lefts.append(a); rights.append(b); syms.append(None)
            interned[key] = got
        return got

    stack, root, i, n = [], None, 0, len(text)
    while i < n:
        c = text[i]
        if c == "(":
            if text[i:i + 5] != "(eml ":
                raise ValueError("malformed S-expression at %d" % i)
            stack.append([]); i += 5
        elif c == ")":
            kids = stack.pop()
            nid = node(kids[0], kids[1])
            if stack:
                stack[-1].append(nid)
            else:
                root = nid
            i += 1
        elif c == " ":
            i += 1
        else:
            nid = leaf(c)
            if stack:
                stack[-1].append(nid)
            else:
                root = nid
            i += 1
    order = [i for i in range(len(kinds))]      # interning already topologically orders ids
    return kinds, lefts, rights, syms, order, root


def q_environment(point, n, mode):
    """The grid coordinates as Q(63-n).n integers, from exact rationals."""
    env = {}
    for name, value in point.items():
        env[name] = qeval.from_fraction(value.numerator, value.denominator, n, mode)
    return env


def evaluate_point(program, point, n, mode, extended):
    """One (construction, point, n, mode, ln-domain) evaluation.

    Returns (kind, payload): ("value", int) | ("OVERFLOW", detail) |
    ("DOMAIN", detail) | ("SATURATED", steps) | ("INFINITE", sign)."""
    kinds, lefts, rights, syms, order, root = program
    q = Q(n, mode, extended)
    try:
        env = q_environment(point, n, mode)
        value, steps = qeval.evaluate(kinds, lefts, rights, syms, order, root, env, q)
    except Trap as trap:
        return (trap.kind, trap.detail, 0)
    except Saturated as sat:
        return ("SATURATED", "cap %d" % qeval.MAX_STEPS, sat.steps)
    if isinstance(value, qeval.Infinity):
        return ("INFINITE", repr(value), steps)
    return ("value", value, steps)


# ---------------------------------------------------------------------------
# --- END EVALUATION PATH ---------------------------------------------------
# ---------------------------------------------------------------------------


def targets(mp, mpf):
    return {
        "eml_e": lambda x, y: mp.e,
        "eml_exp": lambda x, y: mp.exp(x),
        "eml_ln": lambda x, y: mp.log(x),
        "eml_sub": lambda x, y: x - y,
        "eml_neg1": lambda x, y: mpf(-1),
        "eml_two": lambda x, y: mpf(2),
        "eml_minus": lambda x, y: -x,
        "eml_add": lambda x, y: x + y,
        "eml_inv": lambda x, y: mpf(1) / x,
        "eml_mul": lambda x, y: x * y,
        "eml_sqr": lambda x, y: x ** 2,
        "eml_div": lambda x, y: x / y,
        "eml_half": lambda x, y: x / 2,
        "eml_avg": lambda x, y: (x + y) / 2,
        "eml_sqrt": lambda x, y: mp.sqrt(x),
        "eml_pow": lambda x, y: x ** y,
        "eml_logb": lambda x, y: mp.log(y) / mp.log(x),
        "eml_sigma": lambda x, y: mpf(1) / (mpf(1) + mp.exp(-x)),
        "eml_cosh": lambda x, y: mp.cosh(x),
        "eml_sinh": lambda x, y: mp.sinh(x),
        "eml_tanh": lambda x, y: mp.tanh(x),
        "eml_hypot": lambda x, y: mp.sqrt(x ** 2 + y ** 2),
    }


def route_imaginary(program, env, mp, mpf, mpc):
    """max |Im| over every node of the route, in complex mpmath at 50 digits."""
    kinds, lefts, rights, syms, order, root = program
    values = {}
    worst = mpf(0)
    for i in order:
        if kinds[i] == 0:
            value = mpf(1) if syms[i] == "1" else env[syms[i]]
        else:
            value = mp.exp(values[lefts[i]]) - mp.log(values[rights[i]])
        values[i] = value
        if isinstance(value, mpc):
            magnitude = abs(value.imag)
            if magnitude > worst:
                worst = magnitude
    return values[root], worst


def grid_points(arity):
    if arity == 0:
        return [{}]
    if arity == 1:
        return [{"x": x} for x in GRID]
    return [{"x": x, "y": y} for x in GRID for y in GRID]


def measure() -> dict:
    started = time.time()
    from mpmath import mp, mpc, mpf
    import mpmath
    mp.dps = DPS
    gate = mpf(IMAG_GATE)
    epsilon = mpf(EPSILON)

    raw = BASIS.read_bytes()
    basis_digest = hashlib.sha256(raw).hexdigest()
    doc = json.loads(raw.decode("ascii"))
    by_id = {c["id"]: c for c in doc["constructions"]}
    target_table = targets(mp, mpf)

    included = list(PURELY_REAL) + list(ARGUMENT_DEPENDENT)
    included.sort(key=lambda cid: by_id[cid]["step"])

    programs = {cid: parse_dag(by_id[cid]["eml_sexpr"]) for cid in included}

    # ---- routing gate and reference values -------------------------------
    rows = []
    for cid in included:
        entry = by_id[cid]
        program = programs[cid]
        gated = cid in ARGUMENT_DEPENDENT
        points = []
        for point in grid_points(entry["arity"]):
            x = mpf(point["x"].numerator) / mpf(point["x"].denominator) if "x" in point else mpf(0)
            y = mpf(point["y"].numerator) / mpf(point["y"].denominator) if "y" in point else mpf(0)
            label = "|".join("%s=%s" % (k, point[k]) for k in sorted(point)) or "(constant)"
            rule = DOMAIN_EXCLUSION.get(cid)
            if rule is not None and rule(point.get("x"), point.get("y")):
                points.append({"point": label, "status": "out of domain"})
                continue
            env = {"x": x, "y": y}
            value, imaginary = route_imaginary(program, env, mp, mpf, mpc)
            real_route = imaginary < gate
            want = target_table[cid](x, y)
            record = {
                "point": label,
                "max_abs_im": mp.nstr(imaginary, 6),
                "real_route": bool(real_route),
                "reference": mp.nstr(want, 25),
            }
            if gated and not real_route:
                record["status"] = "excluded by the routing gate"
            else:
                record["status"] = "included"
                record["_want"] = want
                record["_point"] = point
            points.append(record)
        usable = [p for p in points if p.get("status") == "included"]
        rows.append({
            "id": cid,
            "step": entry["step"],
            "target": entry["target_name"],
            "arity": entry["arity"],
            "class": "purely real" if cid in PURELY_REAL else "argument-dependent",
            "nodes": entry["eml_nodes"],
            "depth": entry["eml_depth"],
            "grid_points": len(points),
            "out_of_domain": sum(1 for p in points if p.get("status") == "out of domain"),
            "routing_excluded": sum(1 for p in points
                                    if p.get("status") == "excluded by the routing gate"),
            "usable_points": len(usable),
            "excluded": len(usable) == 0,
            "points": points,
        })

    # ---- the Q sweep ------------------------------------------------------
    results = {}
    for configuration, extended in CONFIGURATIONS:
        for mode in MODES:
            for row in rows:
                cid = row["id"]
                program = programs[cid]
                per_n = {}
                for n in N_LIST:
                    worst = None
                    worst_point = None
                    outcomes = {}
                    for record in row["points"]:
                        if record.get("status") != "included":
                            continue
                        kind, payload, _steps = evaluate_point(
                            program, record["_point"], n, mode, extended)
                        if kind != "value":
                            outcomes[kind] = outcomes.get(kind, 0) + 1
                            if worst is None or worst is not False:
                                worst = False
                                worst_point = "%s: %s (%s)" % (record["point"], kind, payload)
                            continue
                        got = mpf(payload) / (mpf(2) ** n)
                        want = record["_want"]
                        scale = abs(want) if abs(want) > 1 else mpf(1)
                        deviation = abs(got - want) / scale
                        if worst is False:
                            continue
                        if worst is None or deviation > worst:
                            worst = deviation
                            worst_point = record["point"]
                    if row["excluded"]:
                        per_n[str(n)] = {"err": None, "status": "no usable points"}
                    elif worst is False:
                        per_n[str(n)] = {"err": None, "status": "TRAP",
                                         "outcomes": dict(sorted(outcomes.items())),
                                         "first": worst_point}
                    else:
                        per_n[str(n)] = {"err": mp.nstr(worst, 8),
                                         "err_float": float(worst),
                                         "status": "ok", "worst_point": worst_point,
                                         "cost_proxy": row["nodes"] * n}
                best = None
                for n in N_LIST:
                    cell = per_n[str(n)]
                    if cell["status"] == "ok" and mpf(cell["err"]) <= epsilon:
                        best = n
                        break
                results[(configuration, mode, cid)] = {"per_n": per_n, "n_star": best}

    # ---- controls ---------------------------------------------------------
    controls = {}
    controls["corpus_digest_matches_pin"] = basis_digest == BASIS_SHA256
    controls["source_digest_matches_pin"] = doc["source"]["sha256"] == SOURCE_SHA256
    controls["transcription_control"] = run_transcription_control()
    controls["constants_agree"] = constants_control(mp, mpf)
    controls["reference_agreement"] = reference_control(mp, mpf)
    controls["trap_witness"] = trap_witness_control(mp, mpf)
    controls["no_simplification"] = no_simplification_control(rows, programs, mp, mpf)
    controls["routing_gate_witness"] = routing_witness(rows)
    controls["saturation"] = {"cap": qeval.MAX_STEPS, "constructions_saturated": sorted(
        {cid for (_c, _m, cid), value in results.items()
         if any(cell.get("status") == "SATURATED" for cell in value["per_n"].values())})}

    # ---- assemble ---------------------------------------------------------
    for row in rows:
        for record in row["points"]:
            record.pop("_want", None)
            record.pop("_point", None)

    per_configuration = {}
    for configuration, _extended in CONFIGURATIONS:
        modes = {}
        for mode in MODES:
            entries = {}
            for row in rows:
                entries[row["id"]] = {
                    "n_star": results[(configuration, mode, row["id"])]["n_star"],
                    "per_n": results[(configuration, mode, row["id"])]["per_n"],
                }
            modes[mode] = {
                "per_construction": entries,
                "n_star_gt_20_or_none": sorted(
                    row["id"] for row in rows if not row["excluded"]
                    and (entries[row["id"]]["n_star"] is None or entries[row["id"]]["n_star"] > 20)),
                "finite_n_star": sorted(
                    row["id"] for row in rows if entries[row["id"]]["n_star"] is not None),
            }
        modes["spearman"] = spearman_block(rows, modes[NEAREST]["per_construction"])
        per_configuration[configuration] = modes

    return {
        "experiment": "EML-EXP-002",
        "preregistration": "experiments/EML-EXP-002-preregistration.md at a6da44b "
                           "(addendum included)",
        "corpus": {"path": "experiments/eml-basis/basis.json", "sha256": basis_digest,
                   "arxiv": "%s%s" % (doc["source"]["arxiv_id"], doc["source"]["version"]),
                   "source_sha256": doc["source"]["sha256"]},
        "included_set": {
            "euler_excluded_by_name": list(EULER_EXCLUDED),
            "purely_real_included_fully": list(PURELY_REAL),
            "argument_dependent_gated": list(ARGUMENT_DEPENDENT),
            "counts": {"excluded_euler": len(EULER_EXCLUDED),
                       "included_purely_real": len(PURELY_REAL),
                       "included_argument_dependent": len(ARGUMENT_DEPENDENT),
                       "included_total": len(included)},
        },
        "evaluator": {
            "format": "signed 64-bit, Q(63-n).n",
            "n_list": list(N_LIST),
            "rounding": list(MODES),
            "term_count": {str(n): qeval.term_count(n) for n in N_LIST},
            "exp": "range reduction by powers of two: k = round(a/ln2), "
                   "exp(a) = 2^k * sum_{i<=T} r^i/i!, r = a - k*ln2",
            "ln": "binary normalization: b = 2^e*m, m in [1,2), "
                  "ln(b) = e*ln2 + 2*sum_{j<T} z^(2j+1)/(2j+1), z = (m-1)/(m+1)",
            "overflow": "trap; no saturation, no wraparound",
            "ln_domain_configurations": {
                "strict": "PRIMARY, the literal preregistered evaluator: ln of a "
                          "non-positive representable is a DOMAIN trap",
                "extended": "SECONDARY, added by the harness: two infinity sentinels "
                            "with mpmath's conventions, so that the precision question "
                            "is askable on constructions whose route passes through "
                            "ln(0) = -inf (see RESULT deviation D2)"},
            "epsilon": EPSILON,
            "reference": "mpmath at %d digits" % DPS,
            "mpmath": mpmath.__version__,
        },
        "grid": {"values": [str(v) for v in GRID],
                 "domain_exclusions": {"eml_logb": "x != 1 (log base 1 is undefined)"}},
        "routing": {"gate": IMAG_GATE, "dps": DPS,
                    "rule": "a point is real-route iff max|Im| along the whole route < gate"},
        "controls": controls,
        "constructions": rows,
        "results": per_configuration,
        "elapsed_seconds_excluded_from_digest": round(time.time() - started, 1),
    }


# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------

def run_transcription_control() -> dict:
    proc = subprocess.run([sys.executable, str(TRANSCRIPTION)],
                          capture_output=True, text=True, cwd=str(REPO))
    tail = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    return {"status": "PASS" if proc.returncode == 0 else "FAIL",
            "returncode": proc.returncode, "last_line": tail}


def constants_control(mp, mpf) -> dict:
    """The pinned ln2 constant against mpmath at 50 digits, and its Q(n) roundings."""
    exact = mp.log(2)
    pinned = mpf(qeval.LN2_Q192) / (mpf(2) ** qeval.LN2_SCALE)
    worst = abs(pinned - exact)
    per_n = {}
    ok = worst < mpf(2) ** (-qeval.LN2_SCALE + 1)
    for n in N_LIST:
        approximate = mpf(qeval.ln2_at(n)) / (mpf(2) ** n)
        deviation = abs(approximate - exact)
        per_n[str(n)] = mp.nstr(deviation, 6)
        if deviation > mpf(2) ** (-n - 1):
            ok = False
    return {"status": "PASS" if ok else "FAIL",
            "ln2_q192_deviation": mp.nstr(worst, 6), "per_n_deviation": per_n}


def reference_control(mp, mpf) -> dict:
    """Preregistered control 1: integer exp and ln at n = 40 match mpmath to 1e-9
    on the grid.  Nothing is reported if this fails."""
    gate = mpf(REFERENCE_GATE)
    q = Q(40, NEAREST, False)
    worst_exp = mpf(0)
    worst_ln = mpf(0)
    detail = []
    for value in GRID:
        exact = mpf(value.numerator) / mpf(value.denominator)
        argument = qeval.from_fraction(value.numerator, value.denominator, 40, NEAREST)
        got_exp = mpf(q.exp(argument)) / (mpf(2) ** 40)
        want_exp = mp.exp(exact)
        deviation_exp = abs(got_exp - want_exp) / (abs(want_exp) if abs(want_exp) > 1 else mpf(1))
        got_ln = mpf(q.ln(argument)) / (mpf(2) ** 40)
        want_ln = mp.log(exact)
        deviation_ln = abs(got_ln - want_ln) / (abs(want_ln) if abs(want_ln) > 1 else mpf(1))
        worst_exp = max(worst_exp, deviation_exp)
        worst_ln = max(worst_ln, deviation_ln)
        detail.append({"x": str(value), "exp_dev": mp.nstr(deviation_exp, 6),
                       "ln_dev": mp.nstr(deviation_ln, 6)})
    ok = worst_exp <= gate and worst_ln <= gate
    return {"status": "PASS" if ok else "FAIL", "gate": REFERENCE_GATE,
            "worst_exp": mp.nstr(worst_exp, 6), "worst_ln": mp.nstr(worst_ln, 6),
            "per_point": detail}


def trap_witness_control(mp, mpf) -> dict:
    """Preregistered control 4 and the harness's supplementary witness.

    The preregistered witness is exp(exp(exp(1))), which in EML is
    eml(eml(eml(1,1),1),1) and denotes e^(e^e) = 3.81e6.  Q(55).8 represents
    up to 3.6e16, so the preregistered witness CANNOT overflow at n = 8, and
    the control fails as written.  It is reported as failed and named as a
    preregistration defect; the trap itself is then witnessed by
    exp(exp(exp(exp(1)))) = e^(3.81e6), which no Q(63-n).n can hold, at every
    n in the list.  See RESULT deviation D4.
    """
    preregistered = "(eml (eml (eml 1 1) 1) 1)"
    supplementary = "(eml (eml (eml (eml 1 1) 1) 1) 1)"
    out = {}
    for label, text in (("preregistered exp(exp(exp(1)))", preregistered),
                        ("supplementary exp(exp(exp(exp(1))))", supplementary)):
        program = parse_dag(text)
        per_n = {}
        for n in N_LIST:
            kind, payload, _steps = evaluate_point(program, {}, n, NEAREST, False)
            per_n[str(n)] = kind if kind != "value" else "value %s" % (
                mp.nstr(mpf(payload) / (mpf(2) ** n), 8))
        out[label] = per_n
    exact = mp.exp(mp.exp(mp.e))
    return {
        "status": "FAIL (as preregistered) / PASS (supplementary witness)",
        "preregistered_witness_overflows_at_n8": out["preregistered exp(exp(exp(1)))"]["8"] == "OVERFLOW",
        "preregistered_witness_value": mp.nstr(exact, 10),
        "q55_8_maximum": mp.nstr(mpf(2 ** 63 - 1) / mpf(2 ** 8), 10),
        "supplementary_witness_overflows_at_every_n": all(
            v == "OVERFLOW" for v in out["supplementary exp(exp(exp(exp(1))))"].values()),
        "outcomes": out,
    }


def no_simplification_control(rows, programs, mp, mpf) -> dict:
    """Preregistered control 5: `x*y` in EML form against the direct product.

    If the evaluator simplified the tree the two would agree everywhere."""
    row = next(r for r in rows if r["id"] == "eml_mul")
    program = programs["eml_mul"]
    differs = []
    both_values_differ = 0
    for n in N_LIST:
        for record in row["points"]:
            if record.get("status") != "included":
                continue
            kind, payload, _steps = evaluate_point(program, record["_point"], n, NEAREST, True)
            point = record["_point"]
            q = Q(n, NEAREST, True)
            direct = q.mul(qeval.from_fraction(point["x"].numerator, point["x"].denominator, n, NEAREST),
                           qeval.from_fraction(point["y"].numerator, point["y"].denominator, n, NEAREST))
            if kind != "value" or payload != direct:
                differs.append({"n": n, "point": record["point"],
                                "tree": kind if kind != "value" else str(payload),
                                "direct": str(direct)})
                if kind == "value":
                    both_values_differ += 1
    return {"status": "PASS" if both_values_differ else "FAIL",
            "configuration": "extended/nearest -- the strict configuration traps on eml_mul "
                             "everywhere (ln(0) in the additive inverse), so the comparison "
                             "would be vacuous there",
            "cells_where_both_are_numbers_and_differ": both_values_differ,
            "differing_cells": len(differs), "first_five": differs[:5]}


def routing_witness(rows) -> dict:
    """Preregistered control 6: sqrt at x = 0.5 MUST be excluded by the gate."""
    row = next(r for r in rows if r["id"] == "eml_sqrt")
    record = next(p for p in row["points"] if p["point"] == "x=1/2")
    excluded = record.get("status") == "excluded by the routing gate"
    return {"status": "PASS" if excluded else "FAIL",
            "witness": "eml_sqrt at x=1/2", "max_abs_im": record.get("max_abs_im"),
            "gate_excluded_it": excluded}


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def ranks(values):
    """Average ranks, exactly, as Fractions."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = [Fraction(0)] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        average = Fraction(sum(range(i, j + 1)), j - i + 1) + 1
        for k in range(i, j + 1):
            out[order[k]] = average
        i = j + 1
    return out


def pearson(a, b):
    n = len(a)
    if n < 2:
        return None
    mean_a = sum(a, Fraction(0)) / n
    mean_b = sum(b, Fraction(0)) / n
    covariance = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
    va = sum((x - mean_a) ** 2 for x in a)
    vb = sum((y - mean_b) ** 2 for y in b)
    if va == 0 or vb == 0:
        return None
    from mpmath import mpf, sqrt
    return covariance / (sqrt(mpf(va.numerator) / mpf(va.denominator))
                         * sqrt(mpf(vb.numerator) / mpf(vb.denominator)))


def spearman(depths, stars):
    return pearson(ranks(depths), ranks(stars))


def spearman_block(rows, per_construction) -> dict:
    """Spearman rho(depth, n*) over finite n*, with the preregistered
    1000-permutation null.  Reported both over all finite n* (P-draft-2) and
    with e, exp, ln removed as floor outliers (kimi A7)."""
    import random
    out = {}
    for label, drop in (("all_finite", ()), ("excluding_floor", ("eml_e", "eml_exp", "eml_ln"))):
        pairs = [(row["depth"], per_construction[row["id"]]["n_star"])
                 for row in rows
                 if per_construction[row["id"]]["n_star"] is not None and row["id"] not in drop]
        if len(pairs) < 3:
            out[label] = {"n": len(pairs), "rho": None,
                          "status": "not computable (fewer than 3 finite n*)"}
            continue
        depths = [p[0] for p in pairs]
        stars = [p[1] for p in pairs]
        rho = spearman(depths, stars)
        if rho is None:
            out[label] = {"n": len(pairs), "rho": None, "status": "degenerate (zero variance)"}
            continue
        seed = int.from_bytes(hashlib.sha256(
            ("EML-EXP-002/permutation/%s" % label).encode("ascii")).digest()[:16], "big")
        rng = random.Random(seed)
        atleast = 0
        for _ in range(PERMUTATIONS):
            shuffled = list(stars)
            rng.shuffle(shuffled)
            candidate = spearman(depths, shuffled)
            if candidate is not None and candidate >= rho:
                atleast += 1
        out[label] = {"n": len(pairs), "rho": float(rho),
                      "permutations": PERMUTATIONS,
                      "p_value": (atleast + 1) / (PERMUTATIONS + 1),
                      "pairs": [[row["id"], per_construction[row["id"]]["n_star"], row["depth"]]
                                for row in rows
                                if per_construction[row["id"]]["n_star"] is not None
                                and row["id"] not in drop]}
    return out


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def body(document: dict) -> str:
    volatile = dict(document)
    volatile.pop("elapsed_seconds_excluded_from_digest", None)
    return json.dumps(volatile, indent=2) + "\n"


def determinism_control(document: dict) -> dict:
    """Preregistered control 2 (D5): byte-identical `measurements.json` across
    two Python minor versions on this machine."""
    expected = hashlib.sha256(body(document).encode()).hexdigest()
    alternate = os.environ.get("EML_ALT_PYTHON")
    runs = []
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "1"
    for label, interpreter in (("same minor version, PYTHONHASHSEED=1", sys.executable),
                               ("second Python minor version", alternate)):
        if not interpreter:
            runs.append({"run": label,
                         "status": "not performed (no second Python minor version with "
                                   "mpmath on this machine; set EML_ALT_PYTHON to one)"})
            continue
        version = subprocess.run([interpreter, "-c", "import sys;print(sys.version.split()[0])"],
                                 capture_output=True, text=True).stdout.strip()
        proc = subprocess.run([interpreter, str(Path(__file__).resolve()), "--body-digest"],
                              capture_output=True, text=True, env=env)
        got = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
        runs.append({"run": label, "interpreter": version, "body_sha256": got,
                     "byte_identical": got == expected})
    performed = [r for r in runs if "byte_identical" in r]
    return {"body_sha256": expected, "runs": runs,
            "two_minor_versions": len({r["interpreter"] for r in performed}) >= 2,
            "byte_identical": bool(performed) and all(r["byte_identical"] for r in performed)}


def collect() -> int:
    if MEASUREMENTS.exists():
        print("refusing to overwrite frozen measurements", file=sys.stderr)
        return 1
    document = measure()
    document["controls"]["determinism"] = determinism_control(document)
    MEASUREMENTS.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    strict = document["results"]["strict"][NEAREST]
    print("froze %d included constructions; strict/nearest: %d with n* > 20 or NONE"
          % (document["included_set"]["counts"]["included_total"],
             len(strict["n_star_gt_20_or_none"])))
    return 0


def check() -> int:
    """Cheap re-derivation for tools/test-all.sh: the corpus digest, the
    evaluator's own controls, and the frozen n* table re-derived from scratch."""
    if not MEASUREMENTS.exists():
        print("PASS: EML-EXP-002 not measured yet")
        return 0
    try:
        import mpmath  # noqa: F401
    except ImportError:
        print("SKIPPED (mpmath absent): EML-EXP-002")
        return 0
    frozen = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    digest = hashlib.sha256(BASIS.read_bytes()).hexdigest()
    if digest != frozen["corpus"]["sha256"]:
        print("FAIL: corpus digest moved", file=sys.stderr)
        return 1
    document = measure()
    frozen["controls"].pop("determinism", None)      # added after the body is sealed
    if body(document) != body(frozen):
        print("FAIL: re-measurement differs from the frozen document", file=sys.stderr)
        return 1
    print("PASS: EML-EXP-002 re-measured byte-identically (%d included constructions)"
          % frozen["included_set"]["counts"]["included_total"])
    return 0


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--collect", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--body-digest", action="store_true")
    args = parser.parse_args()
    if args.body_digest:
        print(hashlib.sha256(body(measure()).encode()).hexdigest())
        return 0
    if args.collect == args.check:
        parser.error("choose exactly one of --collect or --check")
    return collect() if args.collect else check()


if __name__ == "__main__":
    raise SystemExit(main())
