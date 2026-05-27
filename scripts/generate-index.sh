#!/usr/bin/env bash
# Regenera INDEX.md desde la estructura actual
set -euo pipefail

echo "📚 Regenerando INDEX.md..."

cat > INDEX.md <<'EOF'
# Índice Maestro de Archivos del Kit

> Referencia rápida de los archivos del kit organizados por categoría.
> Generado automáticamente. Última actualización: $(date -I)

## 📚 Documentación

- [README.md](README.md) - Punto de entrada
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura del kit
- [QUICKSTART.md](QUICKSTART.md) - Tutorial de 5 min
- [CHANGELOG.md](CHANGELOG.md) - Historial

## 📘 Plan Maestro V5

- [docs/plan-maestro-v5.md](docs/plan-maestro-v5.md)
- [docs/audit-report-v5.md](docs/audit-report-v5.md)
- [docs/adoption-roadmap.md](docs/adoption-roadmap.md)

## 🛠️ Herramientas Python

Ver directorio `tools/` para:
- Enforcement Verifier
- Sanitization Gateway
- Semantic Drift Detector
- Blast Radius Gate
- Knowledge Quarantine
- Emergency Budget Tracker

## 🎨 Templates

Ver directorio `templates/`

## ☁️ Infraestructura

Ver directorio `infrastructure/` (Terraform + Docker)
EOF

echo "✅ INDEX.md regenerado"
