# CenitForge File Index

Quick reference for the current developer-preview repository.

## Primary documents

- [README.md](README.md) - Project overview and current scope
- [QUICKSTART.md](QUICKSTART.md) - Runnable developer-preview quickstart
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution process and quality rules
- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture overview
- [TECHNICAL_EXECUTIVE_SUMMARY.md](TECHNICAL_EXECUTIVE_SUMMARY.md) - Executive technical summary
- [LICENSE](LICENSE) - MIT License

## Status and roadmap

- [docs/project-status.md](docs/project-status.md) - Implemented vs seed vs planned features
- [docs/mvp-roadmap.md](docs/mvp-roadmap.md) - Roadmap to `v0.1.0-developer-preview`
- [docs/plan-maestro-v5.md](docs/plan-maestro-v5.md) - Full target-state methodology
- [docs/audit-report-v5.md](docs/audit-report-v5.md) - Audit report, if present
- [docs/adoption-roadmap.md](docs/adoption-roadmap.md) - Adoption roadmap, if present

## Training

- [docs/training/engineer-onboarding.md](docs/training/engineer-onboarding.md)
- [docs/training/pm-onboarding.md](docs/training/pm-onboarding.md)
- [docs/training/devops-onboarding.md](docs/training/devops-onboarding.md)
- [docs/training/security-onboarding.md](docs/training/security-onboarding.md)

## Templates

- [templates/micro-prompt-template.md](templates/micro-prompt-template.md)
- [templates/api-contract-template.md](templates/api-contract-template.md)
- [templates/billing-state-machine-template.md](templates/billing-state-machine-template.md)

## Generated project seed guardrails

These files live inside the generated-project template:

- `templates/{{cookiecutter.project_slug}}/tools/enforcement_verifier.py`
- `templates/{{cookiecutter.project_slug}}/sanitization/gateway.py`
- `templates/{{cookiecutter.project_slug}}/tests/shadow/shadow_safety_contract.py`
- `templates/{{cookiecutter.project_slug}}/ci/blast_radius_gate.py`
- `templates/{{cookiecutter.project_slug}}/tools/semantic_drift_detector.py`

## Scripts

- [scripts/bootstrap.sh](scripts/bootstrap.sh) - Initial setup helper
- [scripts/validate-kit.sh](scripts/validate-kit.sh) - Structural kit validation
- [scripts/validate_kit.py](scripts/validate_kit.py) - Python structural validator
- [scripts/smoke-demo.sh](scripts/smoke-demo.sh) - Developer-preview sentinel smoke check
- [scripts/new-project.sh](scripts/new-project.sh) - Cookiecutter wrapper
- [scripts/generate-index.sh](scripts/generate-index.sh) - Regenerates this file if updated

## Make targets

```bash
make install
make validate
make smoke
make new-project
make stats
```
