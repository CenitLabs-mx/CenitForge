# Micro-Prompt ID: MP-___

**Título:** [título descriptivo]
**Maturity:** M1 / M2 / M3
**Risk class:** R0 / R1 / R2 / R3
**Budget ceiling:** $X.XX USD
**Timeout:** X min

## Blast Radius Declaration

### Archivos permitidos
- `src/path/file1.py`
- `tests/path/test1.py`

### Scope creep máximo
X% (default: 10% R0/R1, 5% R2/R3)

## Invariantes globales aplicables

- **INV-001:** Ninguna query sin `tenant_id`
- **INV-008:** Ningún secreto en repo/logs
- **INV-012:** Ningún PII en logs
- **INV-016:** Sanitization Gateway para LLMs

## Objetivo
[Describir exactamente qué debe implementarse]

## Tests obligatorios
- [ ] Unit tests
- [ ] Integration tests
- [ ] Mutation tests (si R2/R3)

## Definition of Done
- [ ] Tests pasan
- [ ] Lint/typecheck pasan
- [ ] Blast radius gate PASS
- [ ] Semantic drift > 0.85
- [ ] Enforcement Verifier PASS
- [ ] Context summary generado
- [ ] Critic review sin bloqueadores
