#!/usr/bin/env python3
"""Gate the published repository state against tools/release-manifest.json.

`tools/test-all.sh` is a progress reporter: it passes when a phase has not
started, when a measurement is absent, and when the external Σ-GLYPH oracle is
missing. That is correct for progress and wrong for release, because a commit
deleting a result stays green. Codex review 2026-08-26, finding 7.

This is the gate. A missing artifact, a changed frozen digest, a required
terminal state that is absent, or any skip marker anywhere in the suite output
is a failure.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tools" / "release-manifest.json"


def tracked_files() -> set[str]:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=False
    )
    return set(out.stdout.split("\n"))


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    tracked = tracked_files()
    executed: list[str] = []
    absent: list[str] = []
    failed: list[str] = []

    for path, digest in manifest["frozen"].items():
        target = ROOT / path
        if not target.exists():
            absent.append(f"frozen artifact missing: {path}")
            continue
        if path not in tracked:
            failed.append(f"frozen artifact not tracked by git: {path}")
            continue
        observed = hashlib.sha256(target.read_bytes()).hexdigest()
        if observed != digest:
            failed.append(f"frozen digest changed: {path}\n    expected {digest}\n    observed {observed}")
        else:
            executed.append(f"digest ok: {path}")

    for path in manifest["required"]:
        if not (ROOT / path).exists():
            absent.append(f"required artifact missing: {path}")
        elif path not in tracked:
            failed.append(f"required artifact not tracked by git: {path}")
        else:
            executed.append(f"present: {path}")

    for state in manifest["required_states"]:
        result = subprocess.run(state["command"], cwd=ROOT, capture_output=True, text=True, check=False)
        output = result.stdout + result.stderr
        if result.returncode != 0:
            failed.append(f"{state['why']}: command exited {result.returncode}")
        elif state["must_contain"] not in output:
            failed.append(f"{state['why']}: output lacks {state['must_contain']!r}")
        else:
            executed.append(f"state ok: {state['why']}")
        for marker in manifest["forbidden_markers"]:
            if marker in output:
                failed.append(f"{state['why']}: skip marker {marker!r} in output")

    # Codex review of f9d6e5b: the release section quoted 37 mutations while the
    # manifest generated 54. A user-facing literal must agree with what the tool
    # derives, or it must not be user-facing. This makes disagreement a failure.
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    quoted = re.findall(r"rejects? all (\d+) mutations", readme)
    sys.path.insert(0, str(ROOT / "tools"))
    import importlib.util as _iu
    _spec = _iu.spec_from_file_location("mutation_test", ROOT / "tools" / "mutation-test.py")
    _mutation = _iu.module_from_spec(_spec)
    _spec.loader.exec_module(_mutation)
    derived = _mutation.mutation_total(manifest)
    for literal in quoted:
        if int(literal) != derived:
            failed.append(f"README.md claims {literal} mutations; the manifest derives {derived}")
    if quoted:
        executed.append(f"mutation count literal agrees with the manifest: {derived}")

    suite = subprocess.run([str(ROOT / "tools" / "test-all.sh")], capture_output=True, text=True, check=False)
    suite_output = suite.stdout + suite.stderr
    if suite.returncode != 0:
        failed.append(f"tools/test-all.sh exited {suite.returncode}")
    else:
        executed.append("state ok: tools/test-all.sh")
    for marker in manifest["forbidden_markers"]:
        if marker in suite_output:
            failed.append(f"tools/test-all.sh: skip marker {marker!r} in output")

    print(f"executed: {len(executed)}   absent: {len(absent)}   failed: {len(failed)}")
    for entry in absent:
        print(f"ABSENT: {entry}", file=sys.stderr)
    for entry in failed:
        print(f"FAIL: {entry}", file=sys.stderr)
    if absent or failed:
        return 1
    print("PASS: release state complete; every manifest artifact present, tracked and unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
