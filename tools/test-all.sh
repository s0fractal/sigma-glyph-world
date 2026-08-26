#!/usr/bin/env bash
set -euo pipefail

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo_root"

python3 experiments/scope-pilot-001/render_blind.py --check
python3 experiments/scope-pilot-001/validate.py
python3 experiments/scope-instrument-001/validate.py
python3 experiments/scope-pilot-002/validate_protocol.py
python3 experiments/scope-pilot-002/sample.py --check
python3 experiments/scope-pilot-003/validate_protocol.py
python3 experiments/scope-pilot-003/sample.py --check
python3 experiments/scope-pilot-003/screen.py --check
python3 experiments/kappa-exp-001/measure.py --check
python3 experiments/kappa-exp-001/validate.py
python3 experiments/kappa-exp-002/oracle.py --check
python3 experiments/kappa-exp-002/validate.py
python3 experiments/kappa-exp-003/measure.py --check
python3 experiments/kappa-exp-003/validate.py
git diff --check
