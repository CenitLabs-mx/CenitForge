# API Contracts: [Producto]

**Versión:** v1
**Base URL:** `https://api.{domain}/v1`
**Formato:** JSON
**Auth:** Bearer token (JWT)

## 1. Convenciones globales

### 1.1 Versionado
- Path-based: `/v1/`, `/v2/`
- Policy: ver `api-versioning-strategy.md` y `api-deprecation-policy.md`

### 1.2 Autenticación y autorización
- Todos los endpoints mutantes requieren `Authorization: Bearer <token>`
- El tenant_id se extrae del token, **nunca** del request body
- Endpoints públicos marcados explícitamente

### 1.3 Formato de respuesta

**Éxito (2xx):**
```json
{
  "data": { ... },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-05-27T10:00:00Z"
  }
}
```

**Error (4xx/5xx):**
```json
{
  "error": {
    "code": "TENANT_NOT_FOUND",
    "message": "Tenant with id xyz not found",
    "details": { ... },
    "request_id": "req_abc123"
  }
}
```

### 1.4 Códigos HTTP
| Código | Uso |
|--------|-----|
| 200 | GET exitoso, PATCH/PUT exitoso |
| 201 | POST crea recurso |
| 204 | DELETE exitoso |
| 400 | Validación fallida |
| 401 | Sin autenticación |
| 403 | Sin autorización |
| 404 | Recurso no existe |
| 409 | Conflicto (ej. duplicate) |
| 429 | Rate limit excedido |
| 500 | Error interno |

### 1.5 Paginación
Cursor-based para listas grandes:
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "abc123",
    "has_more": true,
    "total_count": 150
  }
}
```

## 2. Catálogo de endpoints

### 2.1 Auth

#### POST /v1/auth/login
**Actor:** Público  
**Permiso:** Ninguno  
**Tenant scope:** N/A

**Request:**
```json
{
  "email": "user@example.com",
  "password": "••••••••"
}
```

**Response 200:**
```json
{
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "rt_...",
    "expires_in": 3600,
    "tenant_id": "uuid"
  }
}
```

**Errores:**
| Code | Status | Descripción |
|------|--------|-------------|
| INVALID_CREDENTIALS | 401 | Email/password incorrectos |
| ACCOUNT_LOCKED | 403 | Muchos intentos fallidos |
| TENANT_SUSPENDED | 403 | Tenant en PastDue/Suspended |

---

### 2.2 Tenants

#### GET /v1/tenants/:id
**Actor:** Authenticated user  
**Permiso:** `tenant:read`  
**Tenant scope:** Solo propio tenant

**Response 200:**
```json
{
  "data": {
    "id": "uuid",
    "name": "Acme Corp",
    "plan": "pro",
    "status": "active",
    "created_at": "2026-01-15T..."
  }
}
```

**Errores:** 404 TENANT_NOT_FOUND, 403 FORBIDDEN

---

### 2.3 Billing

#### POST /v1/billing/checkout
**Actor:** Tenant admin  
**Permiso:** `billing:checkout`  
**Tenant scope:** Propio  
**Idempotencia:** `Idempotency-Key` header requerido

**Request:**
```json
{
  "plan_id": "plan_pro",
  "billing_cycle": "monthly",
  "success_url": "https://...",
  "cancel_url": "https://..."
}
```

**Response 201:**
```json
{
  "data": {
    "checkout_session_id": "cs_...",
    "url": "https://checkout.stripe.com/...",
    "expires_at": "..."
  }
}
```

## 3. Webhooks salientes (si aplica)

### 3.1 Eventos disponibles
| Evento | Payload | Retry policy |
|--------|---------|--------------|
| `invoice.paid` | Invoice object | 5 intentos, backoff exponencial |
| `subscription.updated` | Subscription object | 5 intentos |
| `tenant.suspended` | Tenant object | 5 intentos |

### 3.2 Formato
```json
{
  "id": "evt_...",
  "type": "invoice.paid",
  "created_at": "...",
  "tenant_id": "...",
  "data": { ... }
}
```

### 3.3 Firma
Header `X-Webhook-Signature: sha256=...` con HMAC-SHA256.

## 4. Rate limiting
Ver `rate-limiting-policy.md`.

## 5. OpenAPI spec
Generado automáticamente desde código. Disponible en `/v1/openapi.json`.
