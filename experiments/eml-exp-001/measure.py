#!/usr/bin/env python3
"""EML-EXP-001 measurement harness — content addressing over the Odrzywolek basis.

Preregistration: `experiments/EML-EXP-001-preregistration.md` (with Amendment 1
and the 2026-08-27 predictions addendum), committed at `a6da44b`, before this
file existed.  The harness author did not write the preregistration and does
not edit it; every choice the preregistration leaves open is recorded in
`RESULT.md`'s provenance section, and every deviation is named there.

WHAT IS MEASURED
    The basis is encoded into Book I terms exactly as the draft's `Encoding`
    section fixes:

        E   := LITERAL(sha256("EML"))
        ONE := LITERAL(sha256("ONE"))
        X   := LITERAL(sha256("X"))
        Y   := LITERAL(sha256("Y"))
        eml(a, b) := APPLY(APPLY(E, a), b)

    `size_tree` counts one Book I node per occurrence; `size_dag` counts
    distinct Book I NodeHashes.  Both are in **Book I nodes**, the unit the
    store actually holds: an EML tree with `n` operator nodes encodes to
    `4n + 1` Book I nodes.

SCALE
    692375 `eml` nodes across the basis, `artanh` alone 504554, maximum depth
    260.  Every tree walk here is iterative or hash-consed bottom-up; nothing
    recurses per occurrence and nothing hashes a subtree twice.  The union of
    all 32 constructions has 849 distinct EML subterms, so the DAG the harness
    actually manipulates is tiny even though the trees it counts are not.

NULLS
    N4 is the primary null (Amendment A1.2), N1 and N2 are descriptive
    baselines (the draft's text), N3 is `not constructible (CAS identity)`
    (Amendment, the draft's own provision), N5 is `not run` with its reason
    recorded.  100 draws each, mean and minimum reported, the minimum gates.

Run:  python3 measure.py --collect     # freeze measurements.json
      python3 measure.py --check       # cheap re-derivation for tools/test-all.sh
      python3 measure.py --body-digest # internal: determinism control 5
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import random
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
BASIS = REPO / "experiments" / "eml-basis" / "basis.json"
TRANSCRIPTION = REPO / "experiments" / "eml-basis" / "transcription_check.py"
MEASUREMENTS = HERE / "measurements.json"

# The corpus, pinned by the preregistration at `d6b97d2` and unmoved since.
BASIS_SHA256 = "14853489bf3701e276d67e6f6fe6e007ebb507c7dad527b9fe0f4ffd6cdf5475"
SOURCE_SHA256 = "2a3b4219a7784d8fd0b3ffe6e7d3dd570cf73d60f8cf368459122fe78e1421db"

# Oracle, pinned exactly as KAPPA-EXP-002 pins it.
ORACLE_PATH = Path(os.environ.get(
    "SIGMA_GLYPH_IMPL", Path.home() / "Projects" / "sigma-glyph" / "impl" / "sigma_glyph.py"))
ORACLE_SHA256 = "413d1f9805cdbdf42f13d967a17be26eb959c692eeb067e7146203ed9cebe64d"
ORACLE_HEAD = "c78e866420f016adf706f3806593cebc05e47dd0"
BOOK1_SPEC = ORACLE_PATH.parent.parent / "spec" / "book-1-truth.en.md"
BOOK1_SHA256 = "cc8c41bbe7cd27c3bca51c7a0636d2de8239c91334f230af4d6044b454d7bcd3"

DRAWS = 100                     # preregistered, all nulls
ATP_BUDGET = 2 ** 40            # control 1 headroom; never binding (see RESULT)
NF_DRIVE_CAP = 5000             # Book I nodes; see RESULT provenance, choice C2
SPECTRUM_THRESHOLDS = (100, 1000)   # fixed by Amendment A1.4, not by this file
DEGENERATE_NODES = 2            # control 4: nodes(f) <= 2 leaves per-function stats


# ---------------------------------------------------------------------------
# Book I serialization, reimplemented here so the corpus can be encoded without
# the oracle present.  Control `encoding_agrees_with_oracle` checks these bytes
# against the pinned oracle whenever the checkout exists.
# ---------------------------------------------------------------------------

LITERAL, APPLY = 0x00, 0x02
F_ATOM, F_LEFT_RIGHT = 0x01, 0x06


def sha(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def lit_bytes(atom: bytes) -> bytes:
    return bytes([LITERAL, F_ATOM]) + atom


def app_bytes(left: bytes, right: bytes) -> bytes:
    return bytes([APPLY, F_LEFT_RIGHT]) + left + right


E_BYTES = lit_bytes(sha(b"EML"))
LEAF_BYTES = {"1": lit_bytes(sha(b"ONE")), "x": lit_bytes(sha(b"X")), "y": lit_bytes(sha(b"Y"))}
E_HASH = sha(E_BYTES)
LEAF_HASH = {k: sha(v) for k, v in LEAF_BYTES.items()}
SYMBOLS = ("1", "x", "y")


# ---------------------------------------------------------------------------
# The EML DAG.  Parsing is iterative and interns structurally equal subterms
# globally, so the union DAG falls out of the parse.
# ---------------------------------------------------------------------------

class EmlDag:
    def __init__(self) -> None:
        self.kind: list[int] = []       # 0 leaf, 1 eml
        self.left: list[int] = []
        self.right: list[int] = []
        self.sym: list[str | None] = []
        self._intern: dict[object, int] = {}

    def leaf(self, sym: str) -> int:
        key = ("L", sym)
        got = self._intern.get(key)
        if got is None:
            got = len(self.kind)
            self.kind.append(0); self.left.append(-1); self.right.append(-1); self.sym.append(sym)
            self._intern[key] = got
        return got

    def node(self, a: int, b: int) -> int:
        key = (a << 32) | b
        got = self._intern.get(key)
        if got is None:
            got = len(self.kind)
            self.kind.append(1); self.left.append(a); self.right.append(b); self.sym.append(None)
            self._intern[key] = got
        return got

    def parse(self, text: str) -> int:
        """`(eml A B)` over {eml,1,x,y}; iterative, so a 4 MB S-expression is fine."""
        stack: list[list[int]] = []
        root = -1
        i, n = 0, len(text)
        while i < n:
            c = text[i]
            if c == "(":
                if text[i:i + 5] != "(eml ":
                    raise ValueError("malformed S-expression at %d" % i)
                stack.append([]); i += 5
            elif c == ")":
                kids = stack.pop()
                if len(kids) != 2:
                    raise ValueError("eml is binary; got %d" % len(kids))
                nid = self.node(kids[0], kids[1])
                if stack:
                    stack[-1].append(nid)
                else:
                    root = nid
                i += 1
            elif c == " ":
                i += 1
            elif c in LEAF_BYTES:
                nid = self.leaf(c)
                if stack:
                    stack[-1].append(nid)
                else:
                    root = nid
                i += 1
            else:
                raise ValueError("symbol %r outside {eml,1,x,y} at %d" % (c, i))
        if stack or root < 0:
            raise ValueError("unbalanced S-expression")
        return root


# ---------------------------------------------------------------------------
# Book I DAG over the EML DAG: one APPLY per eml node, one auxiliary
# APPLY(E, left) per distinct left child, one LITERAL per leaf symbol, plus E.
# ---------------------------------------------------------------------------

class Book1Dag:
    def __init__(self) -> None:
        self.kids: list[tuple[int, int] | None] = []
        self.hash: list[bytes] = []
        self.index: dict[bytes, int] = {}
        self.size: list[int] = []

    def put(self, digest: bytes, kids: tuple[int, int] | None) -> int:
        got = self.index.get(digest)
        if got is None:
            got = len(self.hash)
            self.index[digest] = got
            self.hash.append(digest)
            self.kids.append(kids)
            self.size.append(1 if kids is None else 1 + self.size[kids[0]] + self.size[kids[1]])
        return got


def encode(dag: EmlDag) -> tuple[Book1Dag, list[int]]:
    """Bottom-up hash-consing.  Each distinct EML subterm is hashed once."""
    book = Book1Dag()
    e_index = book.put(E_HASH, None)
    node_hash: list[bytes] = [b""] * len(dag.kind)
    node_index: list[int] = [-1] * len(dag.kind)
    for i in range(len(dag.kind)):          # ids are topologically ordered by construction
        if dag.kind[i] == 0:
            digest = LEAF_HASH[dag.sym[i]]
            node_hash[i] = digest
            node_index[i] = book.put(digest, None)
        else:
            left_hash = node_hash[dag.left[i]]
            aux = sha(app_bytes(E_HASH, left_hash))
            aux_index = book.put(aux, (e_index, node_index[dag.left[i]]))
            digest = sha(app_bytes(aux, node_hash[dag.right[i]]))
            node_hash[i] = digest
            node_index[i] = book.put(digest, (aux_index, node_index[dag.right[i]]))
    return book, node_index


# ---------------------------------------------------------------------------
# Fast size_dag identity, used for the null ensembles.
#
#   size_dag = 1 (the E literal)
#            + |distinct EML subterms, leaves included|
#            + |distinct left children of eml nodes|
#
# Control `dag_identity_holds` checks it against real SHA-256 hashing on the
# real basis at every level before any null is drawn.
# ---------------------------------------------------------------------------

INTERNAL = 3


def intern_stream(stream: bytes, leaves: list[int], table: dict, lefts: set) -> None:
    """Hash-cons a post-order token stream.  Tokens 0..2 are leaf symbols by
    index, token 3 is an `eml` node.  Iterative: no recursion, no per-occurrence
    hashing."""
    stack: list[int] = []
    push, pop, get = stack.append, stack.pop, table.get
    add_left = lefts.add
    li = 0
    for tok in stream:
        if tok == INTERNAL:
            b = pop(); a = pop()
            key = (a << 32) | b
            got = get(key)
            if got is None:
                got = len(table); table[key] = got; get = table.get
            add_left(a)
            push(got)
        else:
            key = -1 - leaves[li]
            li += 1
            got = get(key)
            if got is None:
                got = len(table); table[key] = got; get = table.get
            push(got)


def real_stream(dag: EmlDag, root: int, nodes: int) -> tuple[bytes, list[int]]:
    """Post-order token stream of the FULL tree of `root` (occurrences, not the
    DAG), plus its leaf-symbol sequence.  Iterative; `artanh` is ~1e6 tokens."""
    out = bytearray()
    leaves: list[int] = []
    kind, left, right, sym = dag.kind, dag.left, dag.right, dag.sym
    stack: list[int] = [root]
    while stack:
        i = stack.pop()
        if i < 0:
            out.append(INTERNAL)
            continue
        if kind[i] == 0:
            out.append(SYMBOLS.index(sym[i]))
            leaves.append(SYMBOLS.index(sym[i]))
        else:
            stack.append(-1)
            stack.append(right[i])
            stack.append(left[i])
    if len(out) != 2 * nodes + 1:
        raise AssertionError("stream length %d != %d" % (len(out), 2 * nodes + 1))
    return bytes(out), leaves


# ---------------------------------------------------------------------------
# Null draw procedures
# ---------------------------------------------------------------------------

def seed_for(null: str, cid: str, draw: int) -> int:
    """The review's convention, extended to N1/N2 by substituting the null name:
    sha256("EML-EXP-001/{null}/{f}/{draw}")[:16] big-endian.  `{f}` is the
    construction's basis.json `id`."""
    msg = "EML-EXP-001/%s/%s/%d" % (null, cid, draw)
    return int.from_bytes(hashlib.sha256(msg.encode("ascii")).digest()[:16], "big")


def shape_uniform_split(n: int, rng: random.Random) -> bytes:
    """N4, verbatim from the review: choose the split of the internal nodes
    between left and right uniformly from the k valid splits, then recurse.
    Iterative with an explicit stack; n reaches 504554."""
    out = bytearray()
    stack: list[int] = [n]
    randrange = rng.randrange
    while stack:
        k = stack.pop()
        if k < 0:
            out.append(INTERNAL)
        elif k == 0:
            out.append(0)               # placeholder; labelled by the leaf sequence
        else:
            i = randrange(k)
            stack.append(-1)
            stack.append(k - 1 - i)
            stack.append(i)
    return bytes(out)


def shape_uniform_tree(n: int, rng: random.Random) -> bytes:
    """N1, the draft's `uniformly random binary tree`: Remy's algorithm, which
    is exactly uniform over the C(n) binary trees with n internal nodes."""
    total = 2 * n + 1
    left = [-1] * total
    right = [-1] * total
    parent = [-1] * total
    side = [0] * total
    root = 0
    randrange = rng.randrange
    for k in range(1, n + 1):
        x = randrange(2 * k - 1)
        internal, leaf = 2 * k - 1, 2 * k
        flip = randrange(2)
        p, s = parent[x], side[x]
        if flip == 0:
            left[internal], right[internal] = x, leaf
            parent[x], side[x] = internal, 0
            parent[leaf], side[leaf] = internal, 1
        else:
            left[internal], right[internal] = leaf, x
            parent[x], side[x] = internal, 1
            parent[leaf], side[leaf] = internal, 0
        parent[internal], side[internal] = p, s
        if p == -1:
            root = internal
        elif s == 0:
            left[p] = internal
        else:
            right[p] = internal
    out = bytearray()
    stack: list[int] = [root]
    while stack:
        node = stack.pop()
        if node < 0:
            out.append(INTERNAL)
        elif left[node] == -1:
            out.append(0)
        else:
            stack.append(-1)
            stack.append(right[node])
            stack.append(left[node])
    return bytes(out)


def leaf_permutation(multiset: list[int], rng: random.Random) -> list[int]:
    """Leaves drawn from L(f) without replacement into the leaf positions in
    left-to-right order — the review's base case, which is exactly a uniform
    permutation of the multiset."""
    pool = list(multiset)
    rng.shuffle(pool)
    return pool


# ---------------------------------------------------------------------------
# Oracle
# ---------------------------------------------------------------------------

class Skipped(Exception):
    pass


def load_oracle():
    if not ORACLE_PATH.exists():
        raise Skipped("oracle not found at %s" % ORACLE_PATH)
    digest = hashlib.sha256(ORACLE_PATH.read_bytes()).hexdigest()
    if digest != ORACLE_SHA256:
        raise Skipped("oracle digest %s... != pinned %s..." % (digest[:16], ORACLE_SHA256[:16]))
    spec = importlib.util.spec_from_file_location("sigma_glyph_oracle", ORACLE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def oracle_terms(dag: EmlDag, sg) -> list:
    """Materialize every distinct EML subterm as an oracle tuple, bottom-up.

    `EmlDag` ids are topologically ordered by construction (a node is interned
    only after both children are), so one forward pass suffices and no subterm
    is built twice.  The union DAG has 849 nodes, so the whole table is small
    even though the trees it denotes reach 2e6 Book I nodes.  Equal subterms
    are the SAME tuple, which is what keeps `store_term` linear in the DAG.
    """
    E = ("lit", sg.sha(b"EML"))
    leaf_term = {"1": ("lit", sg.sha(b"ONE")), "x": ("lit", sg.sha(b"X")), "y": ("lit", sg.sha(b"Y"))}
    built: list = [None] * len(dag.kind)
    for i in range(len(dag.kind)):
        if dag.kind[i] == 0:
            built[i] = leaf_term[dag.sym[i]]
        else:
            built[i] = ("app", ("app", E, built[dag.left[i]]), built[dag.right[i]])
    return built


def store_term(sg, store, term) -> bytes:
    """Write every DISTINCT node of `term` to the store.  Shared subterms are
    the same object, so identity memoization keeps this linear in the DAG."""
    stack = [term]
    seen = set()
    while stack:
        node = stack.pop()
        if id(node) in seen:
            continue
        seen.add(id(node))
        store.put(sg.term_bytes(node))
        if node[0] == "app":
            stack.append(node[1]); stack.append(node[2])
    return sg.term_hash(term)


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------

def measure() -> dict:
    started = time.time()
    raw = BASIS.read_bytes()
    basis_digest = hashlib.sha256(raw).hexdigest()
    doc = json.loads(raw.decode("ascii"))
    entries = doc["constructions"]

    dag = EmlDag()
    roots = [(c["id"], dag.parse(c["eml_sexpr"])) for c in entries]
    n_dag = len(dag.kind)

    # Per-node EML statistics, bottom-up over the DAG (ids topologically ordered).
    eml_nodes = [0] * n_dag
    leaf_counts = [None] * n_dag
    for i in range(n_dag):
        if dag.kind[i] == 0:
            eml_nodes[i] = 0
            counts = [0, 0, 0]
            counts[SYMBOLS.index(dag.sym[i])] = 1
            leaf_counts[i] = counts
        else:
            a, b = dag.left[i], dag.right[i]
            eml_nodes[i] = 1 + eml_nodes[a] + eml_nodes[b]
            leaf_counts[i] = [leaf_counts[a][k] + leaf_counts[b][k] for k in range(3)]

    book, node_index = encode(dag)
    n_book = len(book.hash)

    # Occurrence counts and per-construction membership masks over the Book I DAG.
    occurrences = [0] * n_book
    mask = [0] * n_book
    book_roots = [(cid, node_index[r]) for cid, r in roots]
    for position, (_cid, r) in enumerate(book_roots):
        occurrences[r] += 1
        mask[r] |= 1 << position
    for i in range(n_book - 1, -1, -1):
        kids = book.kids[i]
        if kids is None:
            continue
        if occurrences[i]:
            occurrences[kids[0]] += occurrences[i]
            occurrences[kids[1]] += occurrences[i]
        if mask[i]:
            mask[kids[0]] |= mask[i]
            mask[kids[1]] |= mask[i]

    size_dag_union = sum(1 for i in range(n_book) if mask[i])
    cross_only = sum(1 for i in range(n_book) if bin(mask[i]).count("1") >= 2)

    # Per-construction quantities.
    per_construction = []
    real_streams = {}
    for position, (cid, r) in enumerate(roots):
        entry = entries[position]
        broot = node_index[r]
        reach: set[int] = set()
        stack = [broot]
        while stack:
            i = stack.pop()
            if i in reach:
                continue
            reach.add(i)
            kids = book.kids[i]
            if kids is not None:
                stack.append(kids[0]); stack.append(kids[1])
        size_tree = book.size[broot]
        size_dag = len(reach)
        stream, leaves = real_stream(dag, r, eml_nodes[r])
        real_streams[cid] = (stream, leaves)
        per_construction.append({
            "id": cid,
            "step": entry["step"],
            "target": entry["target_name"],
            "nodes": eml_nodes[r],
            "depth": entry["eml_depth"],
            "leaf_multiset": {"1": leaf_counts[r][0], "x": leaf_counts[r][1], "y": leaf_counts[r][2]},
            "size_tree": size_tree,
            "size_dag": size_dag,
            "ratio": size_dag / size_tree,
            "degenerate": eml_nodes[r] <= DEGENERATE_NODES,
            "root_hash": book.hash[broot].hex(),
        })
    size_tree_union = sum(row["size_tree"] for row in per_construction)
    savings = size_tree_union - size_dag_union

    # ---- Amendment A1.4: the size spectrum -------------------------------
    # Attribution: walk the union tree expansion with memoization on NodeHash,
    # constructions in basis order, left child before right.  A first visit
    # costs one stored node; a hit on an already-seen hash prunes an entire
    # subtree occurrence of size s(h), and those s(h) node occurrences are the
    # ones content addressing removes.  The total is exactly `savings`, for any
    # visit order; the split across size classes is order-dependent, and the
    # order is fixed here.
    seen: set[int] = set()
    pruned: list[int] = []
    for _cid, broot in book_roots:
        stack = [broot]
        while stack:
            i = stack.pop()
            if i in seen:
                pruned.append(i)
                continue
            seen.add(i)
            kids = book.kids[i]
            if kids is not None:
                stack.append(kids[1]); stack.append(kids[0])
    attributed = sum(book.size[i] for i in pruned)
    spectrum_fraction = {}
    for threshold in SPECTRUM_THRESHOLDS:
        spectrum_fraction[str(threshold)] = (
            sum(book.size[i] for i in pruned if book.size[i] >= threshold) / savings)

    shared = [i for i in range(n_book) if occurrences[i] >= 2]
    histogram: dict[int, int] = {}
    for i in shared:
        histogram[book.size[i]] = histogram.get(book.size[i], 0) + 1
    cdf = []
    cumulative = 0
    for size in sorted(histogram):
        cumulative += histogram[size]
        cdf.append([size, histogram[size], cumulative / len(shared)])

    def describe(i: int) -> dict:
        return {
            "hash": book.hash[i].hex(),
            "size_book1": book.size[i],
            "eml_nodes": (book.size[i] - 1) // 4 if (book.size[i] - 1) % 4 == 0 else (book.size[i] - 3) // 4,
            "is_encoded_subterm": (book.size[i] - 1) % 4 == 0,
            "occurrences": occurrences[i],
            "constructions": [book_roots[j][0] for j in range(len(book_roots)) if mask[i] >> j & 1],
        }

    largest_shared = max(shared, key=lambda i: (book.size[i], i))
    cross_shared = [i for i in range(n_book) if bin(mask[i]).count("1") >= 2]
    largest_cross = max(cross_shared, key=lambda i: (book.size[i], i))
    largest_shared_subterm = max((i for i in shared if (book.size[i] - 1) % 4 == 0),
                                 key=lambda i: (book.size[i], i))

    # ---- Controls --------------------------------------------------------
    controls: dict[str, object] = {}
    controls["corpus_digest_matches_pin"] = (basis_digest == BASIS_SHA256)
    controls["source_digest_matches_pin"] = (doc["source"]["sha256"] == SOURCE_SHA256)

    transcription = run_transcription_control()
    controls["transcription_control"] = transcription["status"]

    # Control: the fast size_dag identity used for the nulls reproduces real
    # SHA-256 hashing on the real basis, per construction and for the union.
    identity_ok = True
    union_table: dict = {}
    union_lefts: set = set()
    for row in per_construction:
        stream, leaves = real_streams[row["id"]]
        table: dict = {}
        lefts: set = set()
        intern_stream(stream, leaves, table, lefts)
        if 1 + len(table) + len(lefts) != row["size_dag"]:
            identity_ok = False
        intern_stream(stream, leaves, union_table, union_lefts)
    if 1 + len(union_table) + len(union_lefts) != size_dag_union:
        identity_ok = False
    controls["dag_identity_holds"] = identity_ok

    controls["alphabet_sanity_excluded"] = sorted(
        row["id"] for row in per_construction if row["degenerate"])

    oracle_block, normal_form = run_oracle_controls(dag, roots, book, node_index, per_construction)
    controls["normal_form"] = normal_form

    # ---- Nulls -----------------------------------------------------------
    nulls = {
        "N1": draw_null("N1", "shape", per_construction, real_streams),
        "N2": draw_null("N2", "leafshuffle", per_construction, real_streams),
        "N4": draw_null("N4", "split", per_construction, real_streams),
        "N3": {"status": "not constructible (CAS identity)",
               "reason": "independent derivation of the same content yields the same NodeHash, "
                         "so 'no reuse of the same derived term' is not expressible on a "
                         "content-addressed store (preregistration, Delta)"},
        "N5": {"status": "not run",
               "reason": "the review's pool P(f) is size-matched only and admits substitutions "
                         "of different arity (e.g. for f=sigma the only pool members within 10% "
                         "of inv's 12 nodes are two (arity 0) and add (arity 2)), so step 4 of "
                         "the draw procedure is undefined; an arity filter would be a design "
                         "choice made after the preregistration closed"},
    }

    real_block = {
        "union": {
            "size_tree": size_tree_union,
            "size_dag": size_dag_union,
            "ratio": size_dag_union / size_tree_union,
            "cross_only": cross_only,
            "cross_only_fraction_of_size_dag": cross_only / size_dag_union,
            "savings": savings,
        },
        "per_construction": per_construction,
    }
    spectrum = {
        "unit": "Book I nodes (an EML tree of n operator nodes encodes to 4n+1)",
        "attribution": "memoized DFS over the union tree expansion, constructions in basis "
                       "order, left child before right; a pruned hit at h attributes s(h)",
        "attributed_total": attributed,
        "attributed_total_equals_savings": attributed == savings,
        "fraction_of_savings_from_shared_subtrees_at_least": spectrum_fraction,
        "shared_subtree_count": len(shared),
        "cdf": cdf,
        "largest_shared_subtree": describe(largest_shared),
        "largest_shared_encoded_subterm": describe(largest_shared_subterm),
        "largest_cross_construction_shared_subtree": describe(largest_cross),
    }

    return {
        "experiment": "EML-EXP-001",
        "preregistration": "experiments/EML-EXP-001-preregistration.md at a6da44b "
                           "(Amendment 1 and the predictions addendum included)",
        "corpus": {
            "path": "experiments/eml-basis/basis.json",
            "sha256": basis_digest,
            "arxiv": "%s%s" % (doc["source"]["arxiv_id"], doc["source"]["version"]),
            "source_sha256": doc["source"]["sha256"],
            "constructions": len(entries),
            "eml_nodes_total": sum(row["nodes"] for row in per_construction),
        },
        "encoding": {
            "E": E_HASH.hex(), "ONE": LEAF_HASH["1"].hex(),
            "X": LEAF_HASH["x"].hex(), "Y": LEAF_HASH["y"].hex(),
            "rule": "eml(a,b) := APPLY(APPLY(E,a),b)",
            "unit": "Book I nodes",
        },
        "oracle": oracle_block,
        "transcription_control": transcription,
        "controls": controls,
        "real": real_block,
        "spectrum": spectrum,
        "nulls": nulls,
        "draws": DRAWS,
        "elapsed_seconds_excluded_from_digest": round(time.time() - started, 1),
    }


def run_transcription_control() -> dict:
    """Preregistered control 3.  Re-runs the committed control; `SKIPPED
    (mpmath absent)` mirrors the oracle-absent rule and never counts as a pass."""
    try:
        import mpmath  # noqa: F401
    except ImportError:
        return {"status": "SKIPPED (mpmath absent)", "returncode": None}
    proc = subprocess.run([sys.executable, str(TRANSCRIPTION)],
                          capture_output=True, text=True, cwd=str(REPO))
    tail = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    return {
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "returncode": proc.returncode,
        "last_line": tail,
        "stdout_sha256": hashlib.sha256(proc.stdout.encode()).hexdigest(),
    }


def run_oracle_controls(dag, roots, book, node_index, per_construction):
    """Preregistered controls 1 and 2, against the pinned oracle.

    Control 1 as preregistered demands `spent = 0`.  Under the pinned oracle
    (v0.5 hash-thunk semantics) every materialization is priced, so a root
    handed to `eval_hash` as a hash can never cost zero; the preregistration's
    number is unreachable by construction, not by defect of the encoding.  What
    the control is FOR — that `E` at the head is a normal form and nothing
    reduces — is checked in three ways, all recorded: the returned term's hash
    equals the root hash; `spent` equals the closed form `8n+1`, which is pure
    materialization and admits no contraction; and no literal in the store is
    glyph-equal to I, K or S, which makes a redex structurally impossible.
    See RESULT.md, deviation D1.
    """
    try:
        sg = load_oracle()
    except Skipped as exc:
        return ({"status": "SKIPPED", "reason": str(exc),
                 "path_env": "SIGMA_GLYPH_IMPL"},
                {"status": "SKIPPED (oracle absent)", "reason": str(exc)})

    spec_digest = (hashlib.sha256(BOOK1_SPEC.read_bytes()).hexdigest()
                   if BOOK1_SPEC.exists() else None)
    head = None
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ORACLE_PATH.parent.parent),
                              capture_output=True, text=True).stdout.strip() or None
    except OSError:
        pass

    oracle_block = {
        "status": "present",
        "path_env": "SIGMA_GLYPH_IMPL",
        "path": str(ORACLE_PATH),
        "sha256": ORACLE_SHA256,
        "head": head,
        "head_matches_pin": head == ORACLE_HEAD,
        "book_1_spec": "spec/book-1-truth.en.md",
        "book_1_spec_sha256": spec_digest,
        "book_1_spec_matches_pin": spec_digest == BOOK1_SHA256,
    }

    # Encoding agreement: our own serializer against the oracle's.
    encoding_agrees = (
        sg.term_bytes(("lit", sg.sha(b"EML"))) == E_BYTES
        and sg.term_hash(("app", ("app", ("lit", sg.sha(b"EML")), ("lit", sg.sha(b"ONE"))),
                          ("lit", sg.sha(b"ONE")))) == sha(app_bytes(sha(app_bytes(E_HASH, LEAF_HASH["1"])), LEAF_HASH["1"])))

    genesis = {sg.I_H, sg.K_H, sg.S_H}
    literals_disjoint_from_genesis = not (
        {E_HASH, LEAF_HASH["1"], LEAF_HASH["x"], LEAF_HASH["y"]} & genesis)

    terms = oracle_terms(dag, sg)
    limits = dict(sg.DEFAULT_LIMITS)
    limits["max_store_fetches"] = 10 ** 9
    limits["max_materialized_nodes"] = 10 ** 9

    driven = []
    hash_agreement = True
    for position, (cid, r) in enumerate(roots):
        row = per_construction[position]
        if row["size_tree"] > NF_DRIVE_CAP:
            driven.append({"id": cid, "status": "not driven (size_tree %d > cap %d)"
                           % (row["size_tree"], NF_DRIVE_CAP),
                           "spent_closed_form": 8 * row["nodes"] + 1})
            continue
        term = terms[r]
        store = sg.Store()
        root_hash = store_term(sg, store, term)
        # Control 2: our size_dag against the store's own key count.
        if len(store.m) != row["size_dag"]:
            hash_agreement = False
        result, spent = sg.eval_hash(root_hash, ATP_BUDGET, store, limits)
        driven.append({
            "id": cid,
            "status": "driven",
            "result_hash_equals_root": sg.term_hash(result) == root_hash,
            "spent": spent,
            "spent_closed_form": 8 * row["nodes"] + 1,
            "spent_is_zero": spent == 0,
        })

    # Control 2 for the four undriven constructions: the store is still built
    # (cheap, the DAG is small) and its key count compared, without evaluating.
    for position, (cid, r) in enumerate(roots):
        row = per_construction[position]
        if row["size_tree"] <= NF_DRIVE_CAP:
            continue
        broot = node_index[r]
        reach: set[int] = set()
        stack = [broot]
        while stack:
            i = stack.pop()
            if i in reach:
                continue
            reach.add(i)
            kids = book.kids[i]
            if kids is not None:
                stack.append(kids[0]); stack.append(kids[1])
        store = sg.Store()
        for i in reach:
            kids = book.kids[i]
            if kids is None:
                store.put(lit_bytes(sha(b"EML")) if book.hash[i] == E_HASH
                          else next(v for k, v in LEAF_BYTES.items() if sha(v) == book.hash[i]))
            else:
                store.put(app_bytes(book.hash[kids[0]], book.hash[kids[1]]))
        if len(store.m) != row["size_dag"]:
            hash_agreement = False

    all_driven = [d for d in driven if d["status"] == "driven"]
    normal_form = {
        "status": "PASS (as reinterpreted; see deviation D1)",
        "preregistered_criterion": "eval_hash returns f's hash with spent = 0",
        "preregistered_criterion_met": all(d["spent_is_zero"] for d in all_driven),
        "result_hash_equals_root_for_all_driven": all(d["result_hash_equals_root"] for d in all_driven),
        "spent_equals_materialization_closed_form": all(
            d["spent"] == d["spent_closed_form"] for d in all_driven),
        "no_literal_is_genesis": literals_disjoint_from_genesis,
        "encoding_agrees_with_oracle": encoding_agrees,
        "driven": len(all_driven),
        "not_driven": len(driven) - len(all_driven),
        "drive_cap_book1_nodes": NF_DRIVE_CAP,
        "atp_budget": ATP_BUDGET,
        "per_construction": driven,
    }
    normal_form["status"] = ("PASS (as reinterpreted; see deviation D1)"
                             if (normal_form["result_hash_equals_root_for_all_driven"]
                                 and normal_form["spent_equals_materialization_closed_form"]
                                 and literals_disjoint_from_genesis and encoding_agrees)
                             else "FAIL")
    oracle_block["hash_agreement"] = hash_agreement
    return oracle_block, normal_form


def draw_null(name: str, mode: str, per_construction: list[dict], real_streams: dict) -> dict:
    """100 draws; mean and minimum of `ratio` per construction and for the union."""
    per_min = {row["id"]: None for row in per_construction}
    per_ratios = {row["id"]: [] for row in per_construction}
    union_ratios: list[float] = []
    size_tree_union = sum(row["size_tree"] for row in per_construction)
    for draw in range(DRAWS):
        union_table: dict = {}
        union_lefts: set = set()
        for row in per_construction:
            cid = row["id"]
            rng = random.Random(seed_for(name, cid, draw))
            multiset = ([0] * row["leaf_multiset"]["1"] + [1] * row["leaf_multiset"]["x"]
                        + [2] * row["leaf_multiset"]["y"])
            if mode == "leafshuffle":
                stream = real_streams[cid][0]
                leaves = leaf_permutation(multiset, rng)
            elif mode == "shape":
                stream = shape_uniform_tree(row["nodes"], rng)
                leaves = leaf_permutation(multiset, rng)
            else:
                stream = shape_uniform_split(row["nodes"], rng)
                leaves = leaf_permutation(multiset, rng)
            table: dict = {}
            lefts: set = set()
            intern_stream(stream, leaves, table, lefts)
            size_dag = 1 + len(table) + len(lefts)
            ratio = size_dag / row["size_tree"]
            per_ratios[cid].append(ratio)
            if per_min[cid] is None or ratio < per_min[cid]:
                per_min[cid] = ratio
            intern_stream(stream, leaves, union_table, union_lefts)
        union_ratios.append((1 + len(union_table) + len(union_lefts)) / size_tree_union)
    # `math.fsum`, not `sum`: CPython 3.12 gave `builtins.sum` a compensated
    # (Neumaier) summation for floats, so a plain `sum` over 100 ratios differs
    # by one ULP between 3.9 and 3.14 and the determinism control fails on a
    # digit no measurement depends on. `math.fsum` is exactly rounded and has
    # been stable since 2.6. See RESULT.md, correction C11.
    return {
        "status": "run",
        "draws": DRAWS,
        "seed_scheme": 'sha256("EML-EXP-001/%s/{id}/{draw}")[:16] big-endian, random.Random' % name,
        "union": {
            "ratio_mean": math.fsum(union_ratios) / len(union_ratios),
            "ratio_min": min(union_ratios),
            "ratio_max": max(union_ratios),
        },
        "per_construction": {
            cid: {"ratio_mean": math.fsum(per_ratios[cid]) / DRAWS, "ratio_min": per_min[cid]}
            for cid in sorted(per_min)
        },
    }


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def body(document: dict) -> str:
    volatile = dict(document)
    volatile.pop("elapsed_seconds_excluded_from_digest", None)
    return json.dumps(volatile, indent=2, sort_keys=False) + "\n"


def determinism_control(document: dict) -> dict:
    """Preregistered control 5.  A second run in a fresh interpreter with a
    different PYTHONHASHSEED must produce a byte-identical document body; that
    is what catches a set- or dict-ordering leak, which a second run inside the
    same process cannot see."""
    expected = hashlib.sha256(body(document).encode()).hexdigest()
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "1"
    env["EML_EXP_001_CHILD"] = "1"
    runs = []
    for label, interpreter in [("same interpreter, PYTHONHASHSEED=1", sys.executable),
                               ("alternate interpreter", os.environ.get("EML_ALT_PYTHON"))]:
        if not interpreter:
            runs.append({"run": label, "status": "not performed (EML_ALT_PYTHON unset)"})
            continue
        proc = subprocess.run([interpreter, str(Path(__file__).resolve()), "--body-digest"],
                              capture_output=True, text=True, env=env)
        got = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
        runs.append({
            "run": label,
            "interpreter": subprocess.run([interpreter, "-c", "import sys;print(sys.version.split()[0])"],
                                          capture_output=True, text=True).stdout.strip(),
            "body_sha256": got,
            "byte_identical": got == expected,
        })
    return {"body_sha256": expected, "runs": runs,
            "byte_identical": all(r.get("byte_identical") for r in runs if "byte_identical" in r)
                              and any("byte_identical" in r for r in runs)}


def collect() -> int:
    if MEASUREMENTS.exists():
        print("refusing to overwrite frozen measurements", file=sys.stderr)
        return 1
    document = measure()
    document["controls"]["determinism"] = determinism_control(document)
    text = json.dumps(document, indent=2) + "\n"
    MEASUREMENTS.write_text(text, encoding="utf-8")
    union = document["real"]["union"]
    print("froze %d constructions; ratio(U) = %.6g; cross_only = %d/%d"
          % (len(document["real"]["per_construction"]), union["ratio"],
             union["cross_only"], union["size_dag"]))
    return 0


def check() -> int:
    """Cheap re-derivation for tools/test-all.sh.

    Re-derives from the corpus everything that does not need 100 null draws —
    the digest, the encoding, every real per-construction row, the union, the
    size spectrum — and compares each against the frozen document. Then it
    redraws draw 0 of each null and requires the result to sit inside the
    frozen [min, max] envelope, which catches a changed draw procedure or a
    changed RNG without paying for 300 more draws. The full ensembles are
    reproduced by rerunning `--collect` on a clean tree, not on every test run.
    """
    if not MEASUREMENTS.exists():
        print("PASS: EML-EXP-001 not measured yet")
        return 0
    frozen = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    raw = BASIS.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != frozen["corpus"]["sha256"]:
        print("FAIL: corpus digest moved: %s != %s" % (digest, frozen["corpus"]["sha256"]),
              file=sys.stderr)
        return 1
    doc = json.loads(raw.decode("ascii"))
    dag = EmlDag()
    roots = [(c["id"], dag.parse(c["eml_sexpr"])) for c in doc["constructions"]]
    book, node_index = encode(dag)

    if book.hash[book.index[E_HASH]].hex() != frozen["encoding"]["E"]:
        print("FAIL: the encoding's E literal moved", file=sys.stderr)
        return 1

    occurrences = [0] * len(book.hash)
    mask = [0] * len(book.hash)
    for position, (_cid, r) in enumerate(roots):
        occurrences[node_index[r]] += 1
        mask[node_index[r]] |= 1 << position
    for i in range(len(book.hash) - 1, -1, -1):
        kids = book.kids[i]
        if kids is None:
            continue
        if occurrences[i]:
            occurrences[kids[0]] += occurrences[i]
            occurrences[kids[1]] += occurrences[i]
        if mask[i]:
            mask[kids[0]] |= mask[i]
            mask[kids[1]] |= mask[i]

    per = frozen["real"]["per_construction"]
    for position, (cid, r) in enumerate(roots):
        row = per[position]
        broot = node_index[r]
        reach: set[int] = set()
        stack = [broot]
        while stack:
            i = stack.pop()
            if i in reach:
                continue
            reach.add(i)
            kids = book.kids[i]
            if kids is not None:
                stack.append(kids[0]); stack.append(kids[1])
        if (row["id"] != cid or row["size_tree"] != book.size[broot]
                or row["size_dag"] != len(reach)
                or row["root_hash"] != book.hash[broot].hex()):
            print("FAIL: %s does not re-derive from the corpus" % cid, file=sys.stderr)
            return 1

    size_dag_union = sum(1 for i in range(len(book.hash)) if mask[i])
    size_tree_union = sum(row["size_tree"] for row in per)
    cross_only = sum(1 for i in range(len(book.hash)) if bin(mask[i]).count("1") >= 2)
    union = frozen["real"]["union"]
    if (size_dag_union != union["size_dag"] or size_tree_union != union["size_tree"]
            or cross_only != union["cross_only"]):
        print("FAIL: the union re-derivation differs from the frozen document", file=sys.stderr)
        return 1

    seen: set[int] = set()
    pruned: list[int] = []
    for _cid, r in roots:
        stack = [node_index[r]]
        while stack:
            i = stack.pop()
            if i in seen:
                pruned.append(i)
                continue
            seen.add(i)
            kids = book.kids[i]
            if kids is not None:
                stack.append(kids[1]); stack.append(kids[0])
    if sum(book.size[i] for i in pruned) != frozen["spectrum"]["attributed_total"]:
        print("FAIL: the size-spectrum attribution does not re-derive", file=sys.stderr)
        return 1

    streams = {}
    for position, (cid, r) in enumerate(roots):
        streams[cid] = real_stream(dag, r, per[position]["nodes"])
    for name, mode in (("N1", "shape"), ("N2", "leafshuffle"), ("N4", "split")):
        union_table: dict = {}
        union_lefts: set = set()
        for row in per:
            cid = row["id"]
            rng = random.Random(seed_for(name, cid, 0))
            multiset = ([0] * row["leaf_multiset"]["1"] + [1] * row["leaf_multiset"]["x"]
                        + [2] * row["leaf_multiset"]["y"])
            if mode == "leafshuffle":
                stream, leaves = streams[cid][0], leaf_permutation(multiset, rng)
            elif mode == "shape":
                stream, leaves = shape_uniform_tree(row["nodes"], rng), leaf_permutation(multiset, rng)
            else:
                stream, leaves = shape_uniform_split(row["nodes"], rng), leaf_permutation(multiset, rng)
            table: dict = {}
            lefts: set = set()
            intern_stream(stream, leaves, table, lefts)
            ratio = (1 + len(table) + len(lefts)) / row["size_tree"]
            if ratio < frozen["nulls"][name]["per_construction"][cid]["ratio_min"] - 1e-12:
                print("FAIL: %s draw 0 for %s is below the frozen minimum" % (name, cid),
                      file=sys.stderr)
                return 1
            intern_stream(stream, leaves, union_table, union_lefts)
        ratio = (1 + len(union_table) + len(union_lefts)) / size_tree_union
        frozen_union = frozen["nulls"][name]["union"]
        if not (frozen_union["ratio_min"] - 1e-12 <= ratio <= frozen_union["ratio_max"] + 1e-12):
            print("FAIL: %s draw 0 union ratio %.9g is outside the frozen envelope [%.9g, %.9g]"
                  % (name, ratio, frozen_union["ratio_min"], frozen_union["ratio_max"]),
                  file=sys.stderr)
            return 1

    print("PASS: EML-EXP-001 re-derived from the corpus (ratio(U) = %.6g, size_dag(U) = %d, "
          "cross_only = %d, spectrum attribution %d); N1/N2/N4 draw 0 inside the frozen envelope"
          % (union["ratio"], size_dag_union, cross_only, frozen["spectrum"]["attributed_total"]))
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
