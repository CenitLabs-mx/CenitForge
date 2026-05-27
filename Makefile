# CenitForge Kit - Makefile

.PHONY: help install new-project validate docs test clean

PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin

help: ## Muestra esta ayuda
\t@echo "CenitForge Kit - Comandos disponibles"
\t@echo ""
\t@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \\
\t\tawk 'BEGIN {FS = ":.*?## "}; {printf "  \\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

install: $(VENV)/bin/activate ## Instala dependencias del kit
\t@echo "📦 Instalando dependencias del kit..."
\t@$(BIN)/pip install --upgrade pip
\t@$(BIN)/pip install cookiecutter pyyaml
\t@echo "✅ Kit instalado"

$(VENV)/bin/activate:
\t@echo "🔧 Creando virtual environment..."
\t@$(PYTHON) -m venv $(VENV)
\t@touch $(VENV)/bin/activate

new-project: $(VENV)/bin/activate ## Crea nuevo proyecto con cookiecutter
\t@echo "🏗️  Generando nuevo proyecto..."
\t@$(BIN)/cookiecutter templates/ --output-dir ../
\t@echo ""
\t@echo "✅ Proyecto creado"

validate: ## Valida integridad del kit
\t@echo "🔍 Validando integridad del kit..."
\t@bash scripts/validate-kit.sh

docs: ## Regenera INDEX.md
\t@bash scripts/generate-index.sh

test: $(VENV)/bin/activate ## Corre tests del kit
\t@$(BIN)/python -m pytest tests/ -v

clean: ## Limpia archivos temporales
\t@rm -rf $(VENV) __pycache__ .pytest_cache
\t@find . -name "*.pyc" -delete 2>/dev/null || true
\t@echo "✅ Limpieza completada"

stats: ## Muestra estadísticas del kit
\t@echo "📊 Estadísticas del Kit CenitForge"
\t@echo "====================================="
\t@echo "Archivos totales: $$(find . -type f ! -path '*/.*' ! -path '*/__pycache__/*' | wc -l)"
\t@echo "Archivos Python:  $$(find . -name '*.py' | wc -l)"
\t@echo "Archivos Markdown:$$(find . -name '*.md' | wc -l)"
