#!/usr/bin/env python3
"""Negative tests for the release gate.

Codex review 2026-08-26, finding 7: "Add negative mutation tests that delete
each required artifact and corrupt each frozen digest. The gate should fail on
the deletion, not merely on malformed content."

Codex review of `f9d6e5b`, finding on the soundness denominator: a mutation that
only changes bytes is caught by the digest and proves nothing about the semantic
check. The SEMANTIC mutations below edit a recorded value **and re-freeze its
digest in the manifest**, so the digest gate is satisfied and only
`soundness.py --check` can reject them. If that check ever stops regenerating
every verdict, these three mutations survive and this tool fails.

The mutation total is derived from the manifest, never written down twice;
`tools/check-release.py` fails if a literal count in README.md disagrees with it.

Every mutation runs in a throwaway copy of the repository. The real working
tree is never modified.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tools" / "release-manifest.json"


SOUNDNESS = "experiments/kappa-exp-008/soundness.json"


def bump_disagreements(document: dict) -> None:
    document["disagreements"] += 1


def erase_exclusions(document: dict) -> None:
    document["excluded"] = 0


def flip_one_verdict(document: dict) -> None:
    vector = document["verdict_vector"]
    index = next(i for i, code in enumerate(vector) if code == "AGREE")
    vector[index] = "DISAGREE_NORMAL_FORM"


SEMANTIC = [
    ("soundness disagreement count", SOUNDNESS, bump_disagreements),
    ("soundness exclusion count", SOUNDNESS, erase_exclusions),
    ("one soundness per-term verdict", SOUNDNESS, flip_one_verdict),
]


def mutation_total(manifest: dict) -> int:
    return 2 * len(manifest["frozen"]) + len(manifest["required"]) + len(SEMANTIC)


def refreeze(sandbox: Path, path: str) -> None:
    """Re-record the mutated file's digest, so only the semantic check can object."""
    manifest_path = sandbox / "tools" / "release-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["frozen"][path] = hashlib.sha256((sandbox / path).read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def gate_fails(sandbox: Path) -> bool:
    result = subprocess.run(
        [sys.executable, "tools/check-release.py"], cwd=sandbox, capture_output=True, text=True, check=False
    )
    return result.returncode != 0


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    targets = [("delete", path) for path in list(manifest["frozen"]) + manifest["required"]]
    targets += [("corrupt", path) for path in manifest["frozen"]]

    survivors: list[str] = []
    with tempfile.TemporaryDirectory() as workspace:
        pristine = Path(workspace) / "pristine"
        shutil.copytree(ROOT, pristine, symlinks=True)
        if gate_fails(pristine):
            print("FAIL: the gate does not pass on an unmutated copy", file=sys.stderr)
            return 1

        for kind, path in targets:
            sandbox = Path(workspace) / "sandbox"
            if sandbox.exists():
                shutil.rmtree(sandbox)
            shutil.copytree(pristine, sandbox, symlinks=True)
            target = sandbox / path
            if kind == "delete":
                target.unlink()
            else:
                target.write_bytes(target.read_bytes() + b"\n")
            if not gate_fails(sandbox):
                survivors.append(f"{kind} {path}")

        for why, path, mutate in SEMANTIC:
            sandbox = Path(workspace) / "sandbox"
            if sandbox.exists():
                shutil.rmtree(sandbox)
            shutil.copytree(pristine, sandbox, symlinks=True)
            target = sandbox / path
            document = json.loads(target.read_text(encoding="utf-8"))
            mutate(document)
            target.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
            refreeze(sandbox, path)
            if not gate_fails(sandbox):
                survivors.append(f"semantic {why}")

    if survivors:
        for survivor in survivors:
            print(f"FAIL: gate passed after mutation: {survivor}", file=sys.stderr)
        return 1
    total = mutation_total(manifest)
    assert total == len(targets) + len(SEMANTIC)
    print(f"PASS: release gate rejects all {total} mutations ({len(manifest['frozen'])} frozen "
          f"deletions + {len(manifest['required'])} required deletions + "
          f"{len(manifest['frozen'])} digest corruptions + {len(SEMANTIC)} semantic mutations "
          f"that keep their digests valid)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
