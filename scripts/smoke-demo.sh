#!/usr/bin/env bash
# CenitForge developer-preview smoke check.
# This is not a production certification. It verifies that seed guardrails exist
# and that Python seed files are syntactically valid.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE="$ROOT/templates/{{cookiecutter.project_slug}}"

printf 'CenitForge smoke check\n'
printf '======================\n\n'

REQUIRED=(
  "tools/enforcement_verifier.py"
  "sanitization/gateway.py"
  "tests/shadow/shadow_safety_contract.py"
  "ci/blast_radius_gate.py"
  "tools/semantic_drift_detector.py"
  "docs/architecture/data-classification.yaml"
)

for rel in "${REQUIRED[@]}"; do
  if [[ ! -f "$TEMPLATE/$rel" ]]; then
    echo "FAIL missing template sentinel file: $rel"
    exit 1
  fi
  echo "OK present: $rel"
done

echo ""
echo "Checking Python syntax..."
python3 -m py_compile \
  "$TEMPLATE/tools/enforcement_verifier.py" \
  "$TEMPLATE/sanitization/gateway.py" \
  "$TEMPLATE/tests/shadow/shadow_safety_contract.py" \
  "$TEMPLATE/ci/blast_radius_gate.py" \
  "$TEMPLATE/tools/semantic_drift_detector.py"

echo "OK Python syntax checks passed"

echo ""
echo "Running minimal sanitizer smoke check..."
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
cat > "$TMP_DIR/payload.txt" <<'PAYLOAD'
Contact john.doe@example.com about this non-secret issue.
PAYLOAD

python3 "$TEMPLATE/sanitization/gateway.py" --file "$TMP_DIR/payload.txt" --destination smoke-test >/tmp/cenitforge_sanitizer_smoke.json

grep -q 'email' /tmp/cenitforge_sanitizer_smoke.json || {
  echo "FAIL sanitizer did not report email detection"
  cat /tmp/cenitforge_sanitizer_smoke.json
  exit 1
}

echo "OK sanitization smoke check passed"
echo ""
echo "Smoke check PASSED for developer-preview seed guardrails."
