# Roadmap de Adopción - 12 Semanas

## Cronograma

| Semana | Fase | Entregables |
|:------:|------|-------------|
| 1 | Foundation | `/docs`, AGENTS.md, Enforcement Seed |
| 2 | Discovery | Market Scoring, Knowledge Pack, PRD |
| 3 | Architecture | Data model, API contracts, threat model |
| 4 | Tooling | CI pipeline, sanitizer, orchestrator |
| 5-6 | First Features | 3-5 micro-prompts R0/R1 |
| 7 | Hardening | Tenant isolation, mutation testing |
| 8 | Billing | State machine, webhook gauntlet |
| 9 | Shadow Testing | Shadow Safety Contract, 7 días |
| 10 | Staging | Canary, SLOs, runbooks |
| 11 | Production M2 | Primer cliente beta |
| 12 | Learning Loop | Primer destillation |

## Métricas de éxito

```yaml
process_metrics:
  time_to_first_pr: < 5 días
  circuit_breaker_rate: < 15%
  semantic_drift_avg: > 0.90
  enforcement_pass_rate: > 95%
  blast_radius_violations: < 5%
```
