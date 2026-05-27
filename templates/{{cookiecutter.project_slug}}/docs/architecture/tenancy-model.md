# Tenancy Model

**ADR:** ADR-0001-tenancy-strategy
**Versión:** 1.0

## 1. Estrategia elegida: Shared schema + RLS

Todas las tablas de negocio incluyen `tenant_id`. El aislamiento se garantiza con PostgreSQL Row Level Security.

## 2. Alternativas consideradas

| Opción | Pros | Contras | Descarte |
|--------|------|---------|----------|
| DB per tenant | Aislamiento máximo | Ops costosa, caro | No para SaaS SMB |
| Schema per tenant | Buen aislamiento | Migraciones complejas | Overhead |
| **Shared + RLS** | Simple, económico | Requiere disciplina | **Elegida** |

## 3. Reglas obligatorias

### 3.1 INV-001: tenant_id en toda query de negocio
- Middleware inyecta `SET app.current_tenant_id = ?` al inicio del request
- RLS policies usan `current_setting('app.current_tenant_id')`
- Linter CI detecta queries sin filtro

### 3.2 INV-005: No cross-tenant access
- Admin de Tenant A **nunca** puede acceder a Tenant B
- Tests negativos obligatorios en CI

### 3.3 Tablas globales (sin tenant_id)
Solo justificadas con ADR:
- `tenants`
- `plans`
- `regions`
- `system_config`

## 4. Identidad del tenant

### 4.1 En JWT
```json
{
  "sub": "user_uuid",
  "tenant_id": "tenant_uuid",
  "roles": ["admin"],
  "exp": 1234567890
}
```

### 4.2 En requests
- El `tenant_id` se extrae **siempre** del token, nunca del body
- Middleware valida que el usuario pertenece al tenant

## 5. Data isolation tests obligatorios
```python
def test_user_cannot_access_other_tenant():
    tenant_a_user = create_user(tenant=A)
    tenant_b_data = create_resource(tenant=B)
    assert tenant_a_user.get(tenant_b_data.id) == 403
```

## 6. Backup y restore por tenant
- **Export:** Job asíncrono que genera ZIP con datos del tenant
- **Delete:** Soft-delete inicial, hard-delete tras 30 días (GDPR)
- **Restore:** Solo disponible para plan Enterprise

## 7. Noisy-neighbor protection
Ver testing requirements en M2+.

## 8. Cross-tenant operations (admin platform)
- Endpoints internos con authZ separado (service accounts)
- Audit log obligatorio
- Rate limiting estricto
