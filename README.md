# 🏭 CenitForge

> **Plan Maestro Auditable para Desarrollo Asistido por IA**
>
> Framework de producción para construir SaaS B2B multi-tenant con agentes de IA,
> enforcement técnico verificable y gobernanza por niveles de madurez.

[![Audit Score](https://img.shields.io/badge/audit-97%2F100-success.svg)](docs/audit-report-v5.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-5.0-success.svg)](CHANGELOG.md)

---

## 🎯 ¿Qué es esto?

CenitForge es un **framework operativo completo** que transforma el desarrollo
asistido por IA de un "chat de programación" a una **cadena de producción controlada**:

- ✅ **20 invariantes críticas** con enforcement verificado criptográficamente
- ✅ **3 niveles de madurez** (M1/M2/M3) que escalan con el riesgo
- ✅ **10 controles automáticos** (Sanitization, Drift, Blast Radius, Quarantine...)
- ✅ **82+ archivos ejecutables** listos para producción
- ✅ **Templates cookiecutter** para generar proyectos en minutos
- ✅ **Runbooks operativos** para incidentes P0/P1
- ✅ **IaC (Terraform)** para DB, Vault y Sanitization Gateway

**No es un prompt. Es un sistema de producción.**

## 🚀 Quickstart (3 comandos)

```bash
git clone https://github.com/your-org/CenitForge.git
cd CenitForge
make new-project
```

👉 Continúa en [QUICKSTART.md](QUICKSTART.md) para el tutorial completo.

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [📘 Plan Maestro V5](docs/plan-maestro-v5.md) | Framework completo (97/100 audit) |
| [🏗️ Arquitectura](ARCHITECTURE.md) | Organización del kit |
| [📑 Índice](INDEX.md) | Mapeo de los 82+ archivos |
| [🗓️ Roadmap 12 Semanas](docs/adoption-roadmap.md) | Plan de adopción |
| [🎓 Capacitación](docs/training/) | Guías por rol |

## 🔒 Las 20 Invariantes Críticas

Todas verificadas por el **Enforcement Verifier** con firma HMAC-SHA256:

| ID | Invariante | Enforcement |
|----|-----------|-------------|
| INV-001 | Ninguna query sin `tenant_id` | PostgreSQL RLS + middleware |
| INV-002 | Ningún campo financiero en FLOAT | Migration linter |
| INV-003 | Webhooks verifican firma | Middleware criptográfico |
| INV-004 | Idempotencia en eventos | UNIQUE constraint |
| INV-005 | No cross-tenant access | RLS + tests |
| INV-006 | AuthZ en endpoints mutantes | Middleware obligatorio |
| INV-007 | Migraciones con rollback | Dry-run en CI |
| INV-008 | No secrets en repo/logs | Vault + gitleaks |
| INV-009 | Billing tests antes de deploy | CI billing gate |
| INV-010 | ACR para cambios de contratos | Workflow de approval |
| INV-011 | Cache keys con tenant prefix | Wrapper obligatorio |
| INV-012 | No PII en logs | Log sanitizer |
| INV-013 | API versionada | Route lint |
| INV-014 | Restricted data en vault | Audit automático |
| INV-015 | Envs no-prod sin datos reales | Synthetic seed |
| INV-016 | Sanitization para LLMs externos | Gateway obligatorio |
| INV-017 | Expand-and-contract >100k rows | Table-size check |
| INV-018 | Sandbox con egress filtrado | Docker network policy |
| INV-019 | Budget ceiling por micro-prompt | Orchestrator monitor |
| INV-020 | Shadow testing para billing | Feature flag + safety contract |

## 🎭 Niveles de Madurez

- **M1 Exploración:** Ideas, prototipos. Enforcement Seed activo.
- **M2 Crecimiento Controlado:** Beta cerrada. CI completo, sanitizer.
- **M3 Producción Auditada:** SaaS monetizado. Enforcement completo verificado.

## 📜 Licencia

MIT License. Ver [LICENSE](LICENSE).

---

<div align="center">

**¿Listo para construir con IA de forma controlada?**

[🚀 Quickstart](QUICKSTART.md) · [📖 Plan Maestro](docs/plan-maestro-v5.md)

</div>
