#!/usr/bin/env python3
"""EML-EXP-001/002 section 1.1 -- transcription control over `basis.json`.

This is a CONTROL, not a measurement harness.  It answers exactly one
question: does every EML S-expression transcribed from arXiv:2603.21852v2
compute the target function it is labelled with?  It reports no hypothesis,
no null model and no statistic, and it writes no measurements file.

The preregistration draft, section 1.1, fixes the protocol:

    Every construction in basis.json MUST be verified against its target
    function numerically: evaluate both at >= 200 pseudo-random points of the
    target's domain in mpmath at 50 significant digits (complex points for
    complex-domain constructions) and require agreement to 1e-30 relative.
    ... Record the seed and the point set.

Implemented as follows.

POINT SET.  Points are derived, not drawn from a stateful PRNG, so the point
set is reproducible across Python versions, platforms and languages:

    u(cid, var, k, d) = int.from_bytes(sha256(f"{SEED}|{cid}|{var}|{k}|{d}"
                                              .encode("ascii")).digest()[:16],
                                       "big") / 2**128            in [0, 1)

with SEED the string constant below, `cid` the construction id, `var` the
variable name, `k` the 0-based point index and `d` the 0-based draw index
(d > 0 only when a rejection sampler redraws).  u is then mapped through the
sampler recorded in that construction's `domain` block in basis.json.  The
division is exact at 50 dps (2**128 is representable), so u is a function of
the digest alone.

ARITHMETIC.  mp.dps = 50 throughout.  Leaves are mpf; the EML operator is
evaluated as written, eml(a, b) = mp.exp(a) - mp.log(b), with mpmath's own
principal branch, which promotes to mpc exactly when the paper's operator
does ("eml(x,y) internally operates over C using the principal branch", main
text Sect. 2).  ln(0) = -inf and exp(-inf) = 0 are mpmath's native extended
reals, which is the behaviour the paper's constructions for -1 and -x rely on
(main text Sect. 4.1).  Every node of the S-expression is evaluated; equal
subterms are evaluated once (the operator is a deterministic function of its
two arguments, so this is the same number the full tree gives).

COMPLEX POINTS.  No construction in this basis has a complex-valued target:
SI Table S2's caption states that the imaginary unit is one of the four
Table-1 entries the chain does not reconstruct.  What the basis does contain
is real-target constructions with complex INTERMEDIATES.  Those are sampled
at real points of the real domain, evaluated in complex mpmath, and required
to return a vanishing imaginary part; they are flagged `real_via_complex`.
The check also verifies each construction's `complex` flag in basis.json
against the imaginary parts it actually measures, so the flag EML-EXP-002
excludes by is itself under control.

AGREEMENT.  |v_eml - v_target| <= TOL * max(|v_target|, 1), with TOL = 1e-30.
The unit floor is necessary because targets such as sin and artanh have zeros
inside their domain, where a purely relative criterion is undefined; away
from those zeros the criterion is exactly "1e-30 relative".

Exit status is non-zero if any construction fails.
"""

import argparse
import hashlib
import json
import os
import sys

try:
    from mpmath import mp, mpf, mpc
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "mpmath is required. Install it for this user only:\n"
        "    pip3 install --user mpmath\n"
        "(on a PEP 668 'externally managed' Python, add --break-system-packages;\n"
        " it still installs into the per-user site directory only)\n")
    raise

import mpmath

HERE = os.path.dirname(os.path.abspath(__file__))
BASIS = os.path.join(HERE, "basis.json")

SEED = "EML-EXP-001-002/transcription-control/v1"
POINTS = 200
DPS = 50
TOL = "1e-30"
MAX_REDRAWS = 64

# ---------------------------------------------------------------------------
# Point set
# ---------------------------------------------------------------------------


def unit_draw(cid, var, k, d):
    """u in [0, 1), derived from sha256. See the module docstring."""
    msg = "%s|%s|%s|%d|%d" % (SEED, cid, var, k, d)
    digest = hashlib.sha256(msg.encode("ascii")).digest()[:16]
    return mpf(int.from_bytes(digest, "big")) / mpf(2) ** 128


def _map(spec, u, usign):
    s = spec["sampler"]
    if s == "uniform":
        lo, hi = mpf(spec["lo"]), mpf(spec["hi"])
        return lo + u * (hi - lo)
    if s == "loguniform":
        lo, hi = mpf(spec["lo"]), mpf(spec["hi"])
        return mp.exp(mp.log(lo) + u * (mp.log(hi) - mp.log(lo)))
    if s == "signed_loguniform":
        lo, hi = mpf(spec["lo"]), mpf(spec["hi"])
        mag = mp.exp(mp.log(lo) + u * (mp.log(hi) - mp.log(lo)))
        return -mag if usign < mpf("0.5") else mag
    if s == "shifted_loguniform":
        base, lo, hi = mpf(spec["base"]), mpf(spec["lo"]), mpf(spec["hi"])
        return base + mp.exp(mp.log(lo) + u * (mp.log(hi) - mp.log(lo)))
    raise ValueError("unknown sampler %r" % s)


def sample(cid, var, spec, k):
    """The k-th point for `var`, with rejection of any excluded interval."""
    excl = [(mpf(a), mpf(b)) for a, b in spec.get("exclude", [])]
    for d in range(MAX_REDRAWS):
        u = unit_draw(cid, var, k, d)
        usign = unit_draw(cid, var + "#sign", k, d)
        v = _map(spec, u, usign)
        if not any(a <= v <= b for a, b in excl):
            return v
    raise RuntimeError("rejection sampler exhausted for %s/%s point %d" % (cid, var, k))


# ---------------------------------------------------------------------------
# S-expression -> evaluable node table
# ---------------------------------------------------------------------------


def parse_sexpr(text):
    """Parse `(eml A B)` over {eml, 1, x, y} into a node table in topological
    order.  Returns (kinds, lefts, rights, syms, root) where kind 0 is a leaf
    with symbol syms[i] and kind 1 is eml(lefts[i], rights[i]).  Structurally
    equal subterms are shared; see the module docstring."""
    kinds, lefts, rights, syms = [], [], [], []
    interned = {}

    def leaf(sym):
        key = ("L", sym)
        got = interned.get(key)
        if got is None:
            got = len(kinds)
            kinds.append(0)
            lefts.append(-1)
            rights.append(-1)
            syms.append(sym)
            interned[key] = got
        return got

    def node(a, b):
        key = (a, b)
        got = interned.get(key)
        if got is None:
            got = len(kinds)
            kinds.append(1)
            lefts.append(a)
            rights.append(b)
            syms.append(None)
            interned[key] = got
        return got

    stack = []
    root = None
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "(":
            if text[i:i + 5] != "(eml ":
                raise ValueError("malformed S-expression at %d" % i)
            stack.append([])
            i += 5
        elif c == ")":
            kids = stack.pop()
            if len(kids) != 2:
                raise ValueError("eml is binary; got %d arguments" % len(kids))
            nid = node(kids[0], kids[1])
            if stack:
                stack[-1].append(nid)
            else:
                root = nid
            i += 1
        elif c == " ":
            i += 1
        elif c in ("1", "x", "y"):
            nid = leaf(c)
            if stack:
                stack[-1].append(nid)
            else:
                root = nid
            i += 1
        else:
            raise ValueError("symbol %r outside the alphabet {eml,1,x,y} at %d" % (c, i))
    if stack or root is None:
        raise ValueError("unbalanced S-expression")
    return kinds, lefts, rights, syms, root


def evaluate(prog, env):
    """Evaluate the node table at one point.  Returns (root value, max |Im|
    over every node evaluated)."""
    kinds, lefts, rights, syms, root = prog
    vals = [None] * len(kinds)
    im_max = mpf(0)
    for i in range(len(kinds)):
        if kinds[i] == 0:
            v = mpf(1) if syms[i] == "1" else env[syms[i]]
        else:
            a = vals[lefts[i]]
            b = vals[rights[i]]
            v = mp.exp(a) - mp.log(b)          # eml(a, b), exactly as written
        vals[i] = v
        if isinstance(v, mpc):
            m = abs(v.imag)
            if m > im_max:
                im_max = m
    return vals[root], im_max


# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------

TARGETS = {
    "eml_e":      lambda x, y: mp.e,
    "eml_exp":    lambda x, y: mp.exp(x),
    "eml_ln":     lambda x, y: mp.log(x),
    "eml_sub":    lambda x, y: x - y,
    "eml_neg1":   lambda x, y: mpf(-1),
    "eml_two":    lambda x, y: mpf(2),
    "eml_minus":  lambda x, y: -x,
    "eml_add":    lambda x, y: x + y,
    "eml_inv":    lambda x, y: mpf(1) / x,
    "eml_mul":    lambda x, y: x * y,
    "eml_sqr":    lambda x, y: x ** 2,
    "eml_div":    lambda x, y: x / y,
    "eml_half":   lambda x, y: x / 2,
    "eml_avg":    lambda x, y: (x + y) / 2,
    "eml_sqrt":   lambda x, y: mp.sqrt(x),
    "eml_pow":    lambda x, y: x ** y,
    "eml_logb":   lambda x, y: mp.log(y) / mp.log(x),
    "eml_pi":     lambda x, y: mp.pi,
    "eml_hypot":  lambda x, y: mp.sqrt(x ** 2 + y ** 2),
    "eml_sigma":  lambda x, y: mpf(1) / (mpf(1) + mp.exp(-x)),
    "eml_cosh":   lambda x, y: mp.cosh(x),
    "eml_sinh":   lambda x, y: mp.sinh(x),
    "eml_tanh":   lambda x, y: mp.tanh(x),
    "eml_cos":    lambda x, y: mp.cos(x),
    "eml_sin":    lambda x, y: mp.sin(x),
    "eml_tan":    lambda x, y: mp.tan(x),
    "eml_arsinh": lambda x, y: mp.asinh(x),
    "eml_arcosh": lambda x, y: mp.acosh(x),
    "eml_arccos": lambda x, y: mp.acos(x),
    "eml_artanh": lambda x, y: mp.atanh(x),
    "eml_arcsin": lambda x, y: mp.asin(x),
    "eml_arctan": lambda x, y: mp.atan(x),
}


# ---------------------------------------------------------------------------


def check_one(entry, points, tol):
    cid = entry["id"]
    prog = parse_sexpr(entry["eml_sexpr"])
    dom = entry["domain"]["vars"]
    target = TARGETS[cid]

    worst = mpf(0)
    worst_pt = None
    im_max = mpf(0)
    im_root = mpf(0)
    failures = 0
    first_failure = None

    for k in range(points):
        env = {}
        for var, spec in dom.items():
            env[var] = sample(cid, var, spec, k)
        env.setdefault("x", mpf(0))
        env.setdefault("y", mpf(0))

        try:
            got, im = evaluate(prog, env)
        except Exception as exc:                       # noqa: BLE001
            failures += 1
            if first_failure is None:
                first_failure = "evaluation raised %s: %s at point %d %r" % (
                    type(exc).__name__, exc, k, {v: str(env[v]) for v in dom})
            continue

        want = target(env["x"], env["y"])
        if im > im_max:
            im_max = im
        if isinstance(got, mpc):
            im_root = max(im_root, abs(got.imag))
            got_re = got.real
        else:
            got_re = got

        scale = abs(want) if abs(want) > 1 else mpf(1)
        err = abs(got_re - want) / scale
        imerr = (abs(got.imag) / scale) if isinstance(got, mpc) else mpf(0)
        dev = max(err, imerr)
        if dev > worst:
            worst = dev
            worst_pt = {v: mp.nstr(env[v], 20) for v in dom}
        if dev > tol:
            failures += 1
            if first_failure is None:
                first_failure = "deviation %s at point %d %r" % (
                    mp.nstr(dev, 8), k, {v: mp.nstr(env[v], 20) for v in dom})

    measured_complex = im_max > mpf("1e-40")
    flag_ok = (measured_complex == bool(entry["complex"]))
    if not flag_ok and first_failure is None:
        first_failure = ("complex flag mismatch: basis says complex=%s, measured "
                         "max|Im(intermediate)| = %s" % (entry["complex"], mp.nstr(im_max, 8)))

    return {
        "id": cid,
        "step": entry["step"],
        "restricted": entry.get("domain_restriction"),
        "route": entry.get("complex_route"),
        "target": entry["target_name"],
        "nodes": entry["eml_nodes"],
        "depth": entry["eml_depth"],
        "worst_dev": worst,
        "worst_pt": worst_pt,
        "im_max": im_max,
        "im_root": im_root,
        "declared_complex": bool(entry["complex"]),
        "measured_complex": measured_complex,
        "flag_ok": flag_ok,
        "failures": failures,
        "first_failure": first_failure,
        "ok": failures == 0 and flag_ok,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--points", type=int, default=POINTS)
    ap.add_argument("--dps", type=int, default=DPS)
    ap.add_argument("--tol", default=TOL)
    ap.add_argument("--only", default=None, help="check one construction id")
    args = ap.parse_args()

    if args.points < 200:
        sys.stderr.write("section 1.1 requires >= 200 points; refusing %d\n" % args.points)
        return 2
    if args.dps < 50:
        sys.stderr.write("section 1.1 requires >= 50 significant digits; refusing %d\n" % args.dps)
        return 2

    mp.dps = args.dps
    tol = mpf(args.tol)

    with open(BASIS, "r", encoding="ascii") as fh:
        raw = fh.read()
    doc = json.loads(raw)

    print("EML transcription control  (preregistration draft section 1.1)")
    print("  basis            : %s" % os.path.relpath(BASIS, os.getcwd()))
    print("  basis sha256     : %s" % hashlib.sha256(raw.encode("ascii")).hexdigest())
    print("  source pin       : arXiv:%s%s (%s), %s" % (
        doc["source"]["arxiv_id"], doc["source"]["version"],
        doc["source"]["version_date"], doc["source"]["format"]))
    print("  source sha256    : %s" % doc["source"]["sha256"])
    print("  mpmath           : %s" % mpmath.__version__)
    print("  precision        : mp.dps = %d" % mp.dps)
    print("  tolerance        : |eml - target| <= %s * max(|target|, 1)" % args.tol)
    print("  points per constr: %d" % args.points)
    print("  RNG seed         : %r" % SEED)
    print("  point derivation : u = int(sha256(\"<seed>|<id>|<var>|<k>|<draw>\")[:16]) / 2**128,")
    print("                     mapped through the construction's domain sampler")
    print()

    entries = doc["constructions"]
    missing = set(e["id"] for e in entries) ^ set(TARGETS)
    if missing:
        sys.stderr.write("target table and basis disagree on ids: %s\n" % sorted(missing))
        return 2
    if args.only:
        entries = [e for e in entries if e["id"] == args.only]

    hdr = ("%-4s %-12s %-12s %9s %6s  %-16s %-9s %-11s %-6s %s" %
           ("step", "id", "target", "nodes", "depth", "worst rel dev",
            "max|Im|", "class", "domain", "result"))
    print(hdr)
    print("-" * len(hdr))

    results = []
    for e in entries:
        r = check_one(e, args.points, tol)
        results.append(r)
        cls = ("real_via_C/" + (r["route"] or "?")[:1]) if r["measured_complex"] else "real"
        print("%-4d %-12s %-12s %9d %6d  %-16s %-9s %-11s %-6s %s" % (
            r["step"], r["id"], r["target"], r["nodes"], r["depth"],
            mp.nstr(r["worst_dev"], 6), mp.nstr(r["im_max"], 3), cls,
            "RESTRICT" if r["restricted"] else "full",
            "PASS" if r["ok"] else "FAIL"))
        if not r["ok"]:
            print("       -> %s" % r["first_failure"])
        sys.stdout.flush()

    print()
    bad = [r for r in results if not r["ok"]]
    n_cx = sum(1 for r in results if r["measured_complex"])
    print("constructions checked      : %d" % len(results))
    print("complex-flagged            : %d  (real_via_complex; complex-valued targets: 0)" % n_cx)
    print("purely real                : %d" % (len(results) - n_cx))
    print("  of which route via Euler : %d  (complex at every point of the domain)"
          % sum(1 for r in results if r["route"] == "euler"))
    print("  of which argument-driven : %d  (complex only for some arguments)"
          % sum(1 for r in results if r["route"] == "argument_dependent"))
    print("worst deviation anywhere   : %s" % mp.nstr(max(r["worst_dev"] for r in results), 8))
    print("largest root |Im|          : %s" % mp.nstr(max(r["im_root"] for r in results), 8))
    restricted = [r for r in results if r["restricted"]]
    print()
    print("checked on a RESTRICTED sub-domain: %d" % len(restricted))
    for r in restricted:
        print("  %-12s target domain %-12s checked on %-12s  (paper's construction does not "
              "compute the target elsewhere; see basis.json domain_restriction and "
              "TRANSCRIPTION_LOG.md finding T1)"
              % (r["id"], r["restricted"]["target_real_domain"], r["restricted"]["checked_on"]))
    print()
    if bad:
        print("TRANSCRIPTION CONTROL: FAIL (%d of %d)" % (len(bad), len(results)))
        for r in bad:
            print("  FAIL %s: %s" % (r["id"], r["first_failure"]))
        return 1
    print("TRANSCRIPTION CONTROL: PASS (%d of %d)" % (len(results), len(results)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
