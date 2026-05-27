# ADR-0004: Boundaries de Authorization

**Estado:** Aceptada
**Fecha:** 2026-05-27
**Owner:** @security-lead

## Contexto

Authorization (AuthZ) es distinto de Authentication (AuthN). AuthN responde
"¿quién eres?", AuthZ responde "¿qué puedes hacer?". Errores en AuthZ son
la causa #1 de brechas de seguridad en SaaS multi-tenant.

Necesitamos definir:
- Dónde se verifica AuthZ
- Cómo se expresa el permiso
- Qué pasa si falla

## Decisión

### 1. AuthZ en middleware, nunca en handlers (INV-006)

```python
# ❌ INCORRECTO: AuthZ en handler
@app.post("/v1/users")
async def create_user(request, user_data):
    if not current_user.has_permission("users:create"):
        raise HTTPException(403)
    # ... lógica

# ✅ CORRECTO: AuthZ en middleware/decorator
@app.post("/v1/users")
@require_permission("users:create")
async def create_user(request, user_data):
    # Handler asume permiso verificado
    # ... lógica
```

### 2. Modelo de permisos

Formato: `resource:action`

**Recursos:**
- `users`, `teams`, `billing`, `settings`, `data`, `api_keys`

**Acciones:**
- `create`, `read`, `update`, `delete`, `list`, `export`, `invite`

**Ejemplos:**
- `users:invite`
- `billing:checkout`
- `data:export`
- `settings:update`

### 3. Roles predefinidos con permisos

```yaml
roles:
  owner:
    inherits: [admin]
    permissions: ["billing:*", "settings:delete_tenant"]
  
  admin:
    inherits: [member]
    permissions: ["users:*", "teams:*", "settings:update"]
  
  member:
    inherits: [viewer]
    permissions: ["data:create", "data:update", "data:delete"]
  
  viewer:
    permissions: ["*:read", "*:list"]
  
  billing_admin:
    inherits: [member]
    permissions: ["billing:*", "users:read"]
```

### 4. Orden de verificación

```
Request → AuthN (JWT válido) 
       → Tenant status check (Active/Trialing/PastDue)
       → AuthZ (permission check)
       → Business rules
       → Handler
```

### 5. Entitlements por billing status

```python
ENTITLEMENT_MATRIX = {
    "Trialing":   {"premium": True,  "billing_ui": True,  "data": "full"},
    "Active":     {"premium": True,  "billing_ui": True,  "data": "full"},
    "PastDue":    {"premium": False, "billing_ui": True,  "data": "full"},
    "Suspended":  {"premium": False, "billing_ui": True,  "data": "readonly"},
    "Canceled":   {"premium": False, "billing_ui": True,  "data": "export_only"},
}

@middleware
async def entitlement_check(request):
    tenant = await get_tenant(request.tenant_id)
    entitlement = ENTITLEMENT_MATRIX[tenant.billing_status]
    
    if request.path.startswith("/v1/premium/") and not entitlement["premium"]:
        raise HTTPException(403, "Feature requires active subscription")
    
    if entitlement["data"] == "readonly" and request.method in ("POST", "PUT", "DELETE"):
        if not request.path.startswith("/v1/billing/"):
            raise HTTPException(403, "Account suspended")
```

## Consecuencias positivas

- **Consistencia:** AuthZ siempre en middleware
- **Claridad:** permisos explícitos y auditables
- **Seguridad:** defense-in-depth (middleware + handler puede re-check)

## Consecuencias negativas

- **Overhead:** 1-2ms por request para verificar permisos
- **Complejidad:** matriz de roles requiere mantenimiento

## Testing

### Tests negativos obligatorios
- Usuario sin permiso → 403
- Usuario de otro tenant → 403/404
- Usuario PastDue en feature premium → 403
- Service account sin scope → 403

## Impacto

- **INV-006:** Middleware obligatorio
- **INV-005:** Cross-tenant bloqueado
- **Threat model:** Mitiga privilege escalation
