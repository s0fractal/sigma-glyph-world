#!/usr/bin/env bash
set -euo pipefail

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo_root"

python3 experiments/scope-pilot-001/render_blind.py --check
python3 experiments/scope-pilot-001/validate.py
git diff --check
