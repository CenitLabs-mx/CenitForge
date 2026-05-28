# CenitForge Kit - Developer Preview Makefile

.PHONY: help install new-project validate smoke docs test clean stats

PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin

help: ## Show available commands
	@echo "CenitForge Kit - available commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: $(VENV)/bin/activate ## Install kit dependencies
	@echo "Installing kit dependencies..."
	@$(BIN)/pip install --upgrade pip
	@$(BIN)/pip install cookiecutter pyyaml
	@echo "Kit installed"

$(VENV)/bin/activate:
	@echo "Creating virtual environment..."
	@$(PYTHON) -m venv $(VENV)
	@touch $(VENV)/bin/activate

new-project: $(VENV)/bin/activate ## Create a new generated project with cookiecutter
	@echo "Generating new project..."
	@$(BIN)/cookiecutter templates/ --output-dir ../
	@echo "Project created"

validate: ## Validate developer-preview kit structure
	@bash scripts/validate-kit.sh

smoke: ## Run developer-preview sentinel smoke checks
	@bash scripts/smoke-demo.sh

docs: ## Regenerate INDEX.md
	@bash scripts/generate-index.sh

test: $(VENV)/bin/activate ## Run tests when tests/ exists
	@if [ -d tests ]; then \
		$(BIN)/python -m pytest tests/ -v; \
	else \
		echo "No root tests/ directory yet. Use 'make smoke' for current developer-preview checks."; \
	fi

clean: ## Remove temporary files
	@rm -rf $(VENV) __pycache__ .pytest_cache
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "Clean complete"

stats: ## Show kit statistics
	@echo "CenitForge Kit statistics"
	@echo "=========================="
	@echo "Files total: $$(find . -type f ! -path '*/.git/*' ! -path '*/__pycache__/*' | wc -l)"
	@echo "Python files: $$(find . -name '*.py' | wc -l)"
	@echo "Markdown files: $$(find . -name '*.md' | wc -l)"
