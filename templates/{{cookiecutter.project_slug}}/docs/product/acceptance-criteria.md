# Acceptance Criteria - Consolidado

**PRD:** PRD-2026-001

## Matriz de trazabilidad

| User Story | Criterio | Test asociado | Status |
|------------|----------|---------------|:------:|
| US-001 | Tenant isolation | `tests/test_tenant_isolation.py::test_signup_isolation` | ✅ |
| US-001 | Email validación | `tests/test_auth.py::test_invalid_email` | ✅ |
| US-002 | RBAC invitación | `tests/test_rbac.py::test_invite_permission` | ⏳ |

## Criterios globales (aplican a todos los US)

### Funcionales
- [ ] Todos los endpoints documentados en OpenAPI
- [ ] Error responses con código + mensaje consistente
- [ ] Paginación en listas > 100 elementos

### No funcionales
- [ ] p95 latency < 500ms en endpoints principales
- [ ] Zero PII in logs (validado por CI)
- [ ] Tenant isolation suite al 100%
- [ ] Billing webhook gauntlet pasa

### Seguridad
- [ ] SAST sin high/critical findings
- [ ] Secret scan limpio
- [ ] AuthN en todos los endpoints mutantes
- [ ] Rate limiting aplicado

## Regla de validación
Un US no se considera "done" hasta que:
1. Todos sus criterios tienen test automatizado pasando
2. Critic review sin bloqueadores
3. Enforcement Verifier PASS en invariantes aplicables
