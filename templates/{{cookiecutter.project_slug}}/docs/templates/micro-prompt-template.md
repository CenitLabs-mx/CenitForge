# Micro-Prompt ID: MP-___

**Título:** [título descriptivo]
**Maturity:** M1 / M2 / M3
**Risk class:** R0 / R1 / R2 / R3
**Complexity:** S / M / L
**Priority:** P0 / P1 / P2 / P3
**Budget ceiling:** $X.XX USD
**Timeout:** X min
**Owner:** @[user]
**Created:** YYYY-MM-DD

## Dependencias
- [ ] MP-XXX completado
- [ ] ADR-YYY aprobado

## Objetivo
[Describir exactamente qué debe implementarse en 2-3 oraciones]

## Blast Radius Declaration

### Archivos permitidos
- `src/path/to/file1.py`
- `src/path/to/file2.py`
- `tests/path/to/test_file1.py`

### Líneas estimadas
~N líneas de cambio

### Scope creep máximo tolerado
X% (default: 10% para R0/R1, 5% para R2/R3)

## Impact Surface

| Dimensión | ¿Afecta? | Detalle |
|-----------|:--------:|---------|
| Code | ✅/❌ | [archivos] |
| API Contracts | ✅/❌ | [endpoints] |
| Event Contracts | ✅/❌ | [events] |
| Tests | ✅/❌ | [test files] |
| Migrations | ✅/❌ | [migration files] |
| Security | ✅/❌ | [impacto] |
| Billing | ✅/❌ | [impacto] |
| Tenancy | ✅/❌ | [impacto] |
| Performance | ✅/❌ | [impacto] |

## Archivos prohibidos
- ❌ Configuration de producción
- ❌ Secrets (aunque estén en .env.example)
- ❌ Contratos no relacionados con este ticket
- ❌ Código de billing/auth/tenancy fuera de scope
- ❌ Migraciones de otras tablas
- ❌ CI/CD workflows

## Contexto obligatorio

### Documentos de referencia
- **PRD:** `/docs/product/prd.md#section-X`
- **ADR relacionado:** `/docs/adr/XXXX-titulo.md`
- **API contract:** `/docs/architecture/api-contracts.md#endpoint`
- **Data model:** `/docs/architecture/data-model.md#tabla`
- **Test plan:** `/docs/product/acceptance-criteria.md#US-XXX`
- **Data classification:** `/docs/architecture/data-classification.yaml`
- **Threat model:** `/docs/architecture/threat-model.md#threat-X`

### Código de referencia
- Archivos existentes que el agente DEBE leer antes de empezar
- Ejemplos de patrones a seguir

## Invariantes globales aplicables

Las siguientes invariantes aplican SIEMPRE, incluso si no se mencionan en las tareas:

- **INV-001:** Ninguna query de negocio sin `tenant_id`
- **INV-002:** Ningún campo financiero en `FLOAT`
- **INV-008:** Ningún secreto en repo/logs/prompts
- **INV-012:** Ningún PII en logs
- **INV-016:** Sanitization Gateway para LLMs externos

### Invariantes específicas del risk class

**Si R2 o R3:**
- **INV-006:** AuthZ en endpoints mutantes
- **INV-011:** Cache keys con tenant prefix

**Si R3:**
- **INV-003/004:** Webhook signature + idempotencia
- **INV-009:** Billing tests antes de deploy
- **INV-020:** Shadow testing para billing

## Tareas

### 1. [Primera tarea atómica]
**Input:** [estado inicial]
**Output:** [estado final]
**Validación:** [cómo saber que está completa]

### 2. [Segunda tarea atómica]
...

### 3. [Tercera tarea atómica]
...

## Tests obligatorios

### Unit tests
- [ ] `test_[nombre_descriptivo]`: [qué valida]
- [ ] `test_[edge_case]`: [qué valida]

### Integration tests
- [ ] `test_[integration_scenario]`: [qué valida]

### Contract tests (si aplica)
- [ ] Valida schema de request/response
- [ ] Valida códigos HTTP de error

### Tenant isolation tests (si aplica)
- [ ] Tenant A no ve datos de Tenant B

### Security tests (si R2/R3)
- [ ] AuthN requerida
- [ ] AuthZ verificada
- [ ] Input validation

### Mutation tests (si R2/R3)
- Umbral: 80%
- Módulos: [lista]

### Accessibility tests (si UI)
- [ ] WCAG 2.1 AA compliance
- [ ] Keyboard navigation
- [ ] Screen reader compatible

## Comandos

```bash
# Lint
ruff check src/ tests/

# Type check
mypy src/

# Unit tests
pytest tests/unit/ -v

# Integration tests (requiere DB)
pytest tests/integration/ -v

# Mutation tests (si R2/R3)
mutmut run --paths-to-mutate src/path/ --use-coverage

# Coverage
pytest --cov=src --cov-report=html
```

## Semantic Drift Budget

- **Umbral de similitud coseno:** 0.85
- **PRD reference hash:** `[sha256:...]`
- **Detector:** `/tools/semantic_drift_detector.py`

## Enforcement Verifier Requirements

Al finalizar, las siguientes invariantes deben verificar PASS:

- [ ] INV-001 (RLS policies)
- [ ] INV-008 (no secrets)
- [ ] [otras según risk class]

## Rollback plan

Si el cambio falla en staging/producción:

1. **Revert git:** `git revert <commit>`
2. **Database:** [migración inversa si aplica]
3. **Feature flag:** [si está tras flag, desactivar]
4. **Comunicación:** [a quién notificar]

## Definition of Done

Un micro-prompt se considera "done" SOLO si:

- [ ] Todos los tests obligatorios pasan
- [ ] Lint sin errores
- [ ] Type check sin errores
- [ ] Mutation score ≥ 80% (si aplica)
- [ ] Blast radius gate PASS (scope creep < X%)
- [ ] Semantic drift ≥ 0.85
- [ ] Enforcement Verifier PASS
- [ ] No secrets/PII en diff
- [ ] Context summary generado
- [ ] Documentación actualizada (si aplica)
- [ ] Critic review sin bloqueadores
- [ ] ACR generado (si hubo scope change)

## Notas para el agente

- Lee los archivos de contexto ANTES de empezar a codificar
- Genera tests ANTES o en paralelo al código (TDD preferido)
- Si encuentras ambigüedad, detente y genera ACR
- Si necesitas tocar archivo prohibido, detente y reporta
- Al terminar, genera Context Summary

## Context Summary (al finalizar)

```markdown
# Context Summary - MP-___

## Invariantes evaluadas
- INV-001: PASS/FAIL/N/A
- INV-002: PASS/FAIL/N/A
- ...

## Archivos modificados
- src/path/file1.py (±X lines)
- tests/path/test1.py (±Y lines)

## Scope creep
- Declarados: N archivos
- Modificados: M archivos
- Creep: X% (PASS/FAIL)

## Tests ejecutados
- Unit: X passed, Y failed
- Integration: X passed, Y failed
- Mutation: Z% score

## PII/secrets detectados
- None / [detalles]

## Egress
- Solo dominios whitelisted / [detalles]

## Budget
- Tokens usados: X / Y (Z%)
- Costo: $A / $B (C%)

## Anomalías
- None / [detalles]

## Semantic drift
- PRD-Code similarity: X.XXX
- PRD-Tests similarity: Y.YYY
- Overall: Z.ZZZ (threshold: 0.85)
- Verdict: PASS/FAIL
```
