#!/usr/bin/env bash
# Bootstrap script para setup inicial del kit
set -euo pipefail

echo "🏭 CenitForge Kit - Bootstrap"
echo "===================================="

check_cmd() {
    if ! command -v "$1" &> /dev/null; then
        echo "❌ Falta: $1"
        return 1
    fi
    echo "✅ $1: $(command -v $1)"
}

echo ""
echo "🔍 Verificando prerrequisitos..."
check_cmd python3 || exit 1
check_cmd git || exit 1
check_cmd make || exit 1

echo ""
echo "🔧 Instalando kit..."
make install

echo ""
echo "🔍 Validando kit..."
make validate

echo ""
echo "✅ Bootstrap completado!"
echo ""
echo "📖 Próximos pasos:"
echo "   make new-project   # Crear tu primer proyecto"
echo "   cat QUICKSTART.md  # Ver tutorial detallado"
