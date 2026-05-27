# API Contract: [METHOD] [PATH]

**Versión:** v1
**Risk class:** R0 / R1 / R2 / R3

## Metadata

| Atributo | Valor |
|----------|-------|
| Método | GET / POST / PUT / PATCH / DELETE |
| Path | `/v1/[resource]` |
| Autenticación | Requerida |
| Authorization | `[permission:action]` |
| Tenant scope | Propio |
| Rate limit | X req/min |

## Request

### Headers
| Header | Requerido | Descripción |
|--------|:---------:|-------------|
| `Authorization` | ✅ | Bearer token |

### Body
```json
{
  "field": "type (required/optional)"
}
```

## Response 200
```json
{
  "data": { ... }
}
```

## Errores

| Status | Code | Descripción |
|--------|------|-------------|
| 400 | `VALIDATION_ERROR` | Request inválido |
| 401 | `UNAUTHORIZED` | Sin auth |
| 403 | `FORBIDDEN` | Sin permiso |
| 404 | `NOT_FOUND` | No existe |

## Testing
- [ ] Contract tests
- [ ] Tenant isolation tests
- [ ] Security tests
