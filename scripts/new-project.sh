#!/usr/bin/env bash
# Wrapper para crear nuevo proyecto
set -euo pipefail

if [[ ! -f "cookiecutter.json" ]]; then
    echo "❌ Ejecuta este script desde el directorio raíz del kit"
    exit 1
fi

echo "🏗️  Generando nuevo proyecto con CenitForge"

if ! command -v cookiecutter &> /dev/null; then
    echo "📦 Instalando cookiecutter..."
    pip install cookiecutter
fi

cookiecutter templates/ --output-dir ../
echo ""
echo "✅ Proyecto creado!"
