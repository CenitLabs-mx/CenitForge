# Authorization Model

**ADR:** ADR-0004-authz-boundaries
**Versión:** 1.0

## 1. Modelo: RBAC + scoped permissions

### 1.1 Roles predefinidos

| Rol | Descripción | Permisos típicos |
|-----|-------------|------------------|
| `owner` | Creador del tenant | Todo, incluyendo billing |
| `admin` | Administrador | CRUD users, settings |
| `member` | Usuario estándar | Uso de features |
| `viewer` | Solo lectura | Read-only |
| `billing_admin` | Gestiona billing | Invoices, plans |

### 1.2 Permissions granularity
Formato: `resource:action`
- `users:invite`, `users:delete`
- `billing:checkout`, `billing:view_invoices`
- `settings:update`
- `data:export`, `data:delete`

## 2. Enforcement

### 2.1 Middleware obligatorio (INV-006)
```python
@require_permission("users:invite")
async def invite_user(request):
    ...
```

### 2.2 Order de validación
1. Autenticación (JWT válido)
2. Tenant activo (no suspended/past_due para features premium)
3. Authorization (rol/permission)
4. Business rules

## 3. Entitlements por estado de billing

| Estado | Features premium | Billing/settings | Datos |
|--------|:----------------:|:----------------:|:-----:|
| Active | ✅ | ✅ | ✅ |
| PastDue | ⚠️ Degradado | ✅ | ✅ |
| Suspended | ❌ | ✅ | Read-only |
| Canceled | ❌ | ✅ (grace) | Export |

## 4. Service accounts (internal)
- Para cross-tenant operations
- JWT con `tenant_id: null` + `scope: admin`
- Audit log reforzado

## 5. Testing
- **Negative tests:** Usuario sin permiso → 403
- **Boundary tests:** Admin A no administra B
- **Entitlement tests:** PastDue → 403 en premium

## 6. Privilege escalation prevention
- **INV-006:** Middleware obligatorio
- Self-promotion prohibida (solo owner puede promover)
- Audit log de cambios de rol
