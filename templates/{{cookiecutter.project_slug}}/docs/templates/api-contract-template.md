# API Contract: [METHOD] [PATH]

**Versión:** v1
**ADR relacionado:** ADR-XXXX
**Risk class:** R0 / R1 / R2 / R3
**Owner:** @[user]
**Última revisión:** YYYY-MM-DD

## Metadata

| Atributo | Valor |
|----------|-------|
| Método | GET / POST / PUT / PATCH / DELETE |
| Path | `/v1/[resource]/[params]` |
| Autenticación | Requerida / Opcional / Pública |
| Authorization | `[permission:action]` |
| Tenant scope | Propio / Cross-tenant (requiere admin) |
| Idempotencia | Sí (header `Idempotency-Key`) / No aplica |
| Rate limit | X requests/minuto/tenant |
| Timeout | X segundos |
| Paginación | Cursor / Offset / N/A |

## Descripción

[Descripción clara de lo que hace el endpoint, cuándo usarlo,
y consideraciones importantes]

## Request

### Headers

| Header | Requerido | Descripción |
|--------|:---------:|-------------|
| `Authorization` | ✅ | `Bearer <jwt_token>` |
| `Content-Type` | ✅ | `application/json` |
| `Idempotency-Key` | ⚠️ | Requerido para POST mutantes |
| `Accept-Language` | ❌ | `en-US`, `es-419`, etc. |
| `X-Request-ID` | ❌ | Client-provided trace ID |

### Path parameters

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `id` | UUID | ID del recurso | `550e8400-e29b-41d4-a716-446655440000` |

### Query parameters

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|:---------:|---------|-------------|
| `limit` | integer | ❌ | 20 | Máximo 100 |
| `cursor` | string | ❌ | - | Para paginación |
| `status` | enum | ❌ | all | `active`, `inactive`, `all` |

### Body (si POST/PUT/PATCH)

```json
{
  "name": "string (required, max 100 chars)",
  "email": "string (required, valid email)",
  "role": "enum: admin | member | viewer (required)",
  "metadata": {
    "optional_key": "string"
  }
}
```

**JSON Schema:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["name", "email", "role"],
  "properties": {
    "name": {"type": "string", "maxLength": 100},
    "email": {"type": "string", "format": "email"},
    "role": {"type": "string", "enum": ["admin", "member", "viewer"]},
    "metadata": {"type": "object", "additionalProperties": {"type": "string"}}
  },
  "additionalProperties": false
}
```

## Response

### Success (200 / 201 / 204)

#### 200 OK (GET/PUT/PATCH)

```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "admin",
    "created_at": "2026-05-27T10:00:00Z",
    "updated_at": "2026-05-27T10:00:00Z"
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-05-27T10:00:00Z"
  }
}
```

#### 201 Created (POST)

```json
{
  "data": { ... },
  "meta": {
    "request_id": "req_abc123",
    "location": "/v1/users/550e8400-e29b-41d4-a716-446655440000"
  }
}
```

#### 204 No Content (DELETE)
Sin body.

### Paginación (para listas)

```json
{
  "data": [ ... ],
  "pagination": {
    "next_cursor": "abc123",
    "has_more": true,
    "total_count": 150
  }
}
```

## Errores

| Status | Code | Descripción | Cuándo |
|--------|------|-------------|--------|
| 400 | `VALIDATION_ERROR` | Request inválido | Schema violation |
| 400 | `INVALID_EMAIL` | Email con formato inválido | Email inválido |
| 401 | `UNAUTHORIZED` | Sin token o token inválido | Falta auth |
| 403 | `FORBIDDEN` | Sin permiso | AuthZ fallida |
| 403 | `TENANT_SUSPENDED` | Tenant en estado suspendido | Billing PastDue+ |
| 404 | `NOT_FOUND` | Recurso no existe | ID inválido |
| 409 | `DUPLICATE` | Recurso ya existe | Email duplicado |
| 429 | `RATE_LIMITED` | Rate limit excedido | Demasiadas requests |
| 500 | `INTERNAL_ERROR` | Error del servidor | Bug, DB down, etc. |

### Formato de error

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email format is invalid",
    "details": {
      "field": "email",
      "value": "not-an-email",
      "constraint": "Must be valid email format"
    },
    "request_id": "req_abc123"
  }
}
```

## Estados inválidos

| Estado | Respuesta | Razón |
|--------|-----------|-------|
| POST con tenant suspended | 403 `TENANT_SUSPENDED` | Billing issue |
| DELETE del último admin | 400 `LAST_ADMIN` | Debe quedar al menos 1 admin |
| PUT con datos cross-tenant | 403 `FORBIDDEN` | Intento de escalación |

## Idempotencia

**Requerida:** Sí, para POST

**Mecanismo:** Header `Idempotency-Key`

**Comportamiento:**
- Primera request: procesa normalmente
- Requests subsecuentes con mismo key (24h): retorna respuesta cacheada
- Keys expiran tras 24h

**Ejemplo:**
```http
POST /v1/users HTTP/1.1
Idempotency-Key: idk_abc123
Content-Type: application/json

{"name": "John", "email": "john@example.com"}
```

## Seguridad

### Data classification del request
- `name`: Internal
- `email`: Confidential (PII)
- `metadata`: Internal

### Data classification del response
- Igual que request
- Nunca retornar: password_hash, tokens, internal IDs no expuestos

### Sanitization
- Logs: email redactado (`[EMAIL_REDACTED]`)
- Telemetry: solo user_id y action, no payload

### Audit log
- **Cuándo:** Siempre para POST/PUT/DELETE
- **Campos:** actor, tenant_id, timestamp, action, resource, result
- **Retención:** 2 años

## Testing

### Contract tests

```python
def test_create_user_contract():
    """Valida que el endpoint cumple el contrato."""
    response = client.post(
        "/v1/users",
        json={"name": "John", "email": "john@example.com", "role": "member"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    schema = load_schema("user.create.response.json")
    validate(response.json(), schema)

def test_create_user_validation():
    """Valida rechazo de input inválido."""
    response = client.post(
        "/v1/users",
        json={"name": "John", "email": "not-an-email"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"

def test_create_user_unauthorized():
    """Valida que sin auth retorna 401."""
    response = client.post("/v1/users", json={...})
    assert response.status_code == 401

def test_create_user_forbidden():
    """Valida que sin permission retorna 403."""
    response = client.post(
        "/v1/users",
        json={...},
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert response.status_code == 403
```

### Tenant isolation tests

```python
def test_create_user_scoped_to_tenant():
    """Valida que user creado pertenece al tenant del actor."""
    response = client.post("/v1/users", json={...}, headers=tenant_a_headers)
    user_id = response.json()["data"]["id"]
    
    # User debe ser accesible por Tenant A
    assert client.get(f"/v1/users/{user_id}", headers=tenant_a_headers).status_code == 200
    
    # User NO debe ser accesible por Tenant B
    assert client.get(f"/v1/users/{user_id}", headers=tenant_b_headers).status_code in (403, 404)
```

## Ejemplos de uso

### cURL

```bash
curl -X POST https://api.example.com/v1/users \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: idk_$(uuidgen)" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "role": "member"
  }'
```

### Python SDK

```python
from my_sdk import Client

client = Client(api_key="...")
user = client.users.create(
    name="John Doe",
    email="john@example.com",
    role="member"
)
print(user.id)
```

## Changelog

| Fecha | Versión | Cambio | ADR |
|-------|:-------:|--------|-----|
| 2026-05-27 | v1.0 | Initial release | ADR-XXXX |

## Deprecation

- **Status:** Active
- **Successor:** N/A
- **Sunset date:** N/A
