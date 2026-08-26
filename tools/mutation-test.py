#!/usr/bin/env python3
"""Negative tests for the release gate.

Codex review 2026-08-26, finding 7: "Add negative mutation tests that delete
each required artifact and corrupt each frozen digest. The gate should fail on
the deletion, not merely on malformed content."

Every mutation runs in a throwaway copy of the repository. The real working
tree is never modified.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tools" / "release-manifest.json"


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

    if survivors:
        for survivor in survivors:
            print(f"FAIL: gate passed after mutation: {survivor}", file=sys.stderr)
        return 1
    print(f"PASS: release gate rejects all {len(targets)} mutations ({len(manifest['frozen'])} deletions + "
          f"{len(manifest['required'])} deletions + {len(manifest['frozen'])} digest corruptions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
