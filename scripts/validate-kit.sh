#!/usr/bin/env bash
# Validates CenitForge kit structure for developer-preview use.
# This is a structural check, not a production-readiness certification.
set -euo pipefail

echo "Validating CenitForge kit structure..."
echo ""

ERRORS=0

CRITICAL_FILES=(
    "README.md"
    "QUICKSTART.md"
    "CONTRIBUTING.md"
    "ARCHITECTURE.md"
    "INDEX.md"
    "Makefile"
    "cookiecutter.json"
    "LICENSE"
    "docs/plan-maestro-v5.md"
    "docs/project-status.md"
    "docs/mvp-roadmap.md"
    "scripts/bootstrap.sh"
    "scripts/smoke-demo.sh"
)

TEMPLATE_FILES=(
    "templates/{{cookiecutter.project_slug}}/tools/enforcement_verifier.py"
    "templates/{{cookiecutter.project_slug}}/sanitization/gateway.py"
    "templates/{{cookiecutter.project_slug}}/tests/shadow/shadow_safety_contract.py"
    "templates/{{cookiecutter.project_slug}}/ci/blast_radius_gate.py"
    "templates/{{cookiecutter.project_slug}}/tools/semantic_drift_detector.py"
)

echo "Critical kit files:"
for f in "${CRITICAL_FILES[@]}"; do
    if [[ -f "$f" ]]; then
        echo "  OK $f"
    else
        echo "  FAIL missing $f"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""
echo "Developer-preview sentinel seed files:"
for f in "${TEMPLATE_FILES[@]}"; do
    if [[ -f "$f" ]]; then
        echo "  OK $f"
    else
        echo "  FAIL missing $f"
        ERRORS=$((ERRORS + 1))
    fi
done

TOTAL_FILES=$(find . -type f ! -path '*/.git/*' ! -path '*/__pycache__/*' ! -path '*/node_modules/*' | wc -l | tr -d ' ')
echo ""
echo "Total tracked-like files in working tree: $TOTAL_FILES"
echo ""
echo "===================================="
if [[ $ERRORS -eq 0 ]]; then
    echo "Validation PASSED - Kit structure is complete for developer preview."
    echo "Note: this does not certify production readiness. Run 'make smoke' next."
    exit 0
else
    echo "Validation FAILED - $ERRORS missing files."
    exit 1
fi
