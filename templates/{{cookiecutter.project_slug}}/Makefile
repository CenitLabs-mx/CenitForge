# Makefile del proyecto {{ cookiecutter.project_name }}

.PHONY: setup validate test lint

setup:
\t@echo "🔧 Setup del proyecto..."
\tpython3 -m venv .venv
\t.venv/bin/pip install -r requirements.txt

validate:
\t@echo "🔍 Validando Enforcement Seed..."
\tpython tools/enforcement_verifier.py --phase architecture_lock --maturity {{ cookiecutter.initial_maturity }}

test:
\t.venv/bin/pytest tests/ -v

lint:
\t.venv/bin/ruff check .
\t.venv/bin/mypy src/
