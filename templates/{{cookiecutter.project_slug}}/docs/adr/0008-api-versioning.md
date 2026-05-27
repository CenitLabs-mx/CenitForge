# ADR-0008: API Versioning Strategy

**Estado:** Aceptada
**Fecha:** 2026-05-27
**Owner:** @api-lead
**Relacionado:** INV-013

## Contexto

APIs públicas evolucionan. Sin versionado, cambios breaking rompen clientes.
Opciones:
1. URL path: `/v1/users`, `/v2/users`
2. Header: `Accept: application/vnd.api.v2+json`
3. Query param: `/users?version=2`
4. Host: `v1.api.example.com`

## Decisión

**URL path-based versioning**

```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

## Justificación

| Alternativa | Problema |
|-------------|----------|
| Header | Difícil de probar en browser, caching complejo |
| Query param | Rompe REST semántico, URLs feas |
| Host | Overhead DNS, certificados SSL por host |

## Reglas

### 1. Versionado obligatorio (INV-013)

Todo endpoint público DEBE tener versión:
```python
# ✅ CORRECTO
@app.get("/v1/users")
@app.get("/v2/users")

# ❌ INCORRECTO
@app.get("/users")  # Sin versión
```

### 2. Breaking vs non-breaking changes

#### Non-breaking (no requiere nueva versión)
- Añadir campo nuevo en response
- Añadir endpoint nuevo
- Añadir query param opcional
- Relajar validaciones

#### Breaking (requiere nueva versión)
- Eliminar/renombrar campo
- Cambiar tipo de campo
- Endurecer validaciones
- Cambiar códigos HTTP
- Cambiar semántica

### 3. Soporte de versiones

- **Versión actual:** soporte completo
- **N-1:** soporte 18 meses tras lanzamiento de N
- **N-2 o menor:** sin soporte

### 4. Deprecation headers

```http
HTTP/1.1 200 OK
Deprecation: true
Sunset: Sat, 01 Nov 2027 00:00:00 GMT
Link: <https://api.example.com/v2/docs>; rel="successor-version"
```

## Implementación

```python
# Router versionado
v1_router = APIRouter(prefix="/v1")
v2_router = APIRouter(prefix="/v2")

@v1_router.get("/users")
async def list_users_v1():
    return await users_service.list_v1()

@v2_router.get("/users")
async def list_users_v2():
    return await users_service.list_v2()

app.include_router(v1_router)
app.include_router(v2_router)
```

## Migration guide para clientes

Cada versión nueva incluye:
1. Changelog detallado
2. Ejemplos before/after
3. Script de migración (si aplica)
4. Timeline de deprecación

## Testing

- CI valida que no haya breaking changes sin nueva versión
- Contract tests comparan v1 vs v2 behavior
- OpenAPI diff en PR
