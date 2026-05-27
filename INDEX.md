# Índice Maestro de Archivos del Kit

> Referencia rápida de los archivos del kit organizados por categoría.

## 📚 Documentación Principal

- [README.md](README.md) - Punto de entrada
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitectura del kit
- [QUICKSTART.md](QUICKSTART.md) - Tutorial 5 min
- [CHANGELOG.md](CHANGELOG.md) - Historial
- [CONTRIBUTING.md](CONTRIBUTING.md) - Cómo contribuir
- [LICENSE](LICENSE) - MIT

## 📘 Plan Maestro V5

- [docs/plan-maestro-v5.md](docs/plan-maestro-v5.md) - Framework completo
- [docs/audit-report-v5.md](docs/audit-report-v5.md) - Auditoría 97/100
- [docs/adoption-roadmap.md](docs/adoption-roadmap.md) - Roadmap 12 semanas

## 🎓 Capacitación

- [docs/training/engineer-onboarding.md](docs/training/engineer-onboarding.md) - 16h
- [docs/training/pm-onboarding.md](docs/training/pm-onboarding.md) - 8h
- [docs/training/devops-onboarding.md](docs/training/devops-onboarding.md) - 24h
- [docs/training/security-onboarding.md](docs/training/security-onboarding.md) - 12h

## 🎨 Templates

- [templates/micro-prompt-template.md](templates/micro-prompt-template.md)
- [templates/api-contract-template.md](templates/api-contract-template.md)
- [templates/billing-state-machine-template.md](templates/billing-state-machine-template.md)

## 🤖 CI/CD

- [.github/workflows/kit-validation.yml](.github/workflows/kit-validation.yml)

## 📂 Cookiecutter Templates

El directorio `templates/` contiene:
- `{{cookiecutter.project_slug}}/` - Proyecto generado
- `hooks/` - Hooks pre/post generación

## 🛠️ Scripts

- `scripts/bootstrap.sh` - Setup inicial
- `scripts/validate-kit.sh` - Validación de integridad
- `scripts/new-project.sh` - Wrapper de cookiecutter
- `scripts/generate-index.sh` - Regenera este archivo

## 📊 Estadísticas

Ver `make stats` para conteo actualizado.
