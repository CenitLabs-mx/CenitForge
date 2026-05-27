#!/usr/bin/env bash
# Valida integridad del kit
set -euo pipefail

echo "🔍 Validando integridad del kit..."
echo ""

ERRORS=0

CRITICAL_FILES=(
    "README.md"
    "ARCHITECTURE.md"
    "INDEX.md"
    "QUICKSTART.md"
    "Makefile"
    "cookiecutter.json"
    "LICENSE"
    "docs/plan-maestro-v5.md"
    "scripts/bootstrap.sh"
)

echo "📋 Archivos críticos:"
for f in "${CRITICAL_FILES[@]}"; do
    if [[ -f "$f" ]]; then
        echo "  ✅ $f"
    else
        echo "  ❌ $f (FALTA)"
        ERRORS=$((ERRORS + 1))
    fi
done

TOTAL_FILES=$(find . -type f ! -path '*/.*' ! -path '*/__pycache__/*' ! -path '*/node_modules/*' | wc -l)
echo ""
echo "📊 Archivos totales: $TOTAL_FILES"

echo ""
echo "===================================="
if [[ $ERRORS -eq 0 ]]; then
    echo "✅ Validación PASSED - Kit listo para usar"
    exit 0
else
    echo "❌ Validación FAILED - $ERRORS errores"
    exit 1
fi
