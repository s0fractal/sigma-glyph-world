#!/usr/bin/env bash
# Release gate. Unlike tools/test-all.sh, a missing artifact, a changed frozen
# digest, or a skipped dependency is a failure rather than a progress report.
set -euo pipefail
repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo_root"
python3 tools/check-release.py
python3 tools/mutation-test.py
