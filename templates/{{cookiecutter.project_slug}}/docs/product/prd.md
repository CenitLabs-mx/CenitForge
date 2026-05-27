# Product Requirements Document: [Producto]

**ID:** PRD-2026-001
**Versión:** 1.0
**Owner:** @pm-lead
**Fecha:** 2026-05-27
**Status:** draft | reviewed | locked
**Origen:** OPP-2026-001

## 1. Resumen del problema
[1-2 párrafos: qué dolor resolvemos, para quién, por qué ahora]

## 2. Evidencia a favor
- E1: [hecho concreto + fuente]
- E2: ...

## 3. Evidencia en contra / limitaciones
- C1: [contraargumento]
- C2: ...

## 4. Segmentos afectados

| Segmento | Tamaño est. | Dolor | Disposición pago |
|----------|:-----------:|:-----:|:----------------:|
| SMB tech | 5k | Alto | Media |
| Mid-market | 800 | Alto | Alta |

## 5. Alternativas existentes
(ver `competitor-analysis.md`)

## 6. Señales de disposición de pago
(ver `pricing-signals.md`)

## 7. Evidencia cuantitativa y sus límites
(ver `quantitative-validation.md`)
- **Límites:** [qué no sabemos todavía]

## 8. Riesgos de falso positivo
(ver `false-positive-risks.md`)

## 9. Requisitos funcionales del MVP

### 9.1 Core features (must-have)
| ID | Feature | User story | Criterio aceptación |
|----|---------|------------|---------------------|
| F-001 | [x] | US-001 | [testable] |
| F-002 | [x] | US-002 | [testable] |

### 9.2 Nice-to-have (post-MVP)
- F-101: ...

## 10. Requisitos no funcionales

| Categoría | Requisito | Métrica |
|-----------|-----------|---------|
| Performance | API latency p95 | < 500ms |
| Seguridad | Tenant isolation | RLS + tests |
| Disponibilidad | Uptime SLO | 99.9% |
| Compliance | GDPR, SOC2 | Baseline v1 |

## 11. Accesibilidad e i18n

### 11.1 Accesibilidad
- **Nivel objetivo:** WCAG 2.1 AA
- **Non-goal MVP:** WCAG AAA, auditoría externa
- **Checklist:**
  - [ ] Navegación por teclado
  - [ ] Contraste ≥ 4.5:1
  - [ ] Labels en todos los inputs
  - [ ] Screen reader tested

### 11.2 Internacionalización
- **Idiomas MVP:** EN (US)
- **Idiomas Q3:** ES, PT-BR
- **Non-goal MVP:** RTL, CJK
- **Arquitectura:** i18n keys en JSON, no strings hardcoded

## 12. Supuestos no validados
1. [ ] Usuarios integrarán X en <15 min
2. [ ] Y no es bloqueante
3. [ ] ...

## 13. Preguntas abiertas
1. [ ] ¿Cuál es el pricing tier óptimo?
2. [ ] ...

## 14. Criterios de aceptación globales
- [ ] Todos los US tienen ≥1 test automatizado
- [ ] Tenant isolation pasa suite completa
- [ ] Billing state machine validada
- [ ] No PII en logs (validado por sanitizer)

## 15. Recomendación
**Decisión:** CONSTRUIR / INVESTIGAR MÁS / DESCARTAR
**Justificación:** [1-2 líneas]

## 16. Aprobaciones
- [ ] PM Lead
- [ ] Tech Lead
- [ ] Design Lead
- [ ] Security (si aplica)
