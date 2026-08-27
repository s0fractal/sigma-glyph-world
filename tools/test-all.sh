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
python3 experiments/kappa-exp-005/measure.py --check
python3 experiments/kappa-exp-005/validate.py
python3 experiments/kappa-exp-005/theorem.py --check
python3 experiments/kappa-exp-006/measure.py --check
python3 experiments/kappa-exp-006/validate.py
python3 experiments/kappa-exp-007/measure.py --check
python3 experiments/kappa-exp-007/validate.py
python3 experiments/kappa-exp-008/measure.py --check
python3 experiments/kappa-exp-008/soundness.py --check
python3 experiments/kappa-exp-008/traces.py --check
python3 experiments/kappa-exp-008/validate.py
python3 experiments/world-cas-001/measure.py --check
python3 experiments/world-cas-001/validate.py
python3 experiments/kappa-exp-009/measure.py --check
python3 experiments/kappa-exp-009/validate.py

# EML-EXP-001/002. Both depend on mpmath (the transcription control) and
# EML-EXP-001 additionally on a local sigma-glyph checkout; each reports
# SKIPPED rather than importing unconditionally, per both preregistrations'
# dependency rule, and SKIPPED is never a pass.
if python3 -c 'import mpmath' >/dev/null 2>&1; then
  python3 experiments/eml-exp-001/measure.py --check
  python3 experiments/eml-exp-001/validate.py
  python3 experiments/eml-exp-002/measure.py --check
  python3 experiments/eml-exp-002/validate.py
else
  echo "SKIPPED (mpmath absent): EML-EXP-001"
  echo "SKIPPED (mpmath absent): EML-EXP-002"
fi

git diff --check
