# ADR-0003: Estrategia de Idempotencia Global

**Estado:** Aceptada
**Fecha:** 2026-05-27
**Owner:** @tech-lead

## Contexto

En sistemas distribuidos, las operaciones pueden ejecutarse múltiples veces
por retries de red, crashes, o reintentos del cliente. Necesitamos una
estrategia coherente para garantizar idempotencia en:

1. Webhooks entrantes (Stripe, etc.)
2. API endpoints mutantes del cliente
3. Jobs asíncronos reintentados
4. Mensajes de cola reentregados

## Decisión

### Tres niveles de idempotencia

#### Nivel 1: Idempotencia natural
Operaciones intrínsecamente idempotentes (PUT, DELETE por ID, upserts).

```sql
-- Ejemplo: actualizar email
UPDATE users SET email = ? WHERE id = ? AND tenant_id = ?
```

**No requiere mecanismo adicional.**

#### Nivel 2: Idempotencia por clave única (UNIQUE constraint)
Para operaciones que crean recursos o procesan eventos.

```sql
CREATE TABLE processed_events (
  event_id TEXT,
  provider TEXT,
  PRIMARY KEY (event_id, provider)
);
```

**Usado en:** webhooks, job deduplication.

#### Nivel 3: Idempotencia por Idempotency-Key header
Para API endpoints del cliente que crean recursos.

```http
POST /v1/billing/checkout
Idempotency-Key: idk_abc123xyz
```

**Implementación:**
```python
@app.post("/v1/billing/checkout")
@require_idempotency_key
async def create_checkout(request, idempotency_key: str):
    # Check if already processed
    existing = await db.fetch_one(
        "SELECT response_body, status_code FROM idempotency_keys "
        "WHERE key = ? AND tenant_id = ?",
        (idempotency_key, request.tenant_id)
    )
    if existing:
        return Response(existing.response_body, status_code=existing.status_code)
    
    # Process
    result = await checkout_service.create(...)
    
    # Store result
    await db.execute(
        "INSERT INTO idempotency_keys (key, tenant_id, response_body, status_code) "
        "VALUES (?, ?, ?, ?)",
        (idempotency_key, request.tenant_id, json.dumps(result), 201)
    )
    
    return result
```

### Tabla idempotency_keys

```sql
CREATE TABLE idempotency_keys (
  key TEXT NOT NULL,
  tenant_id UUID NOT NULL,
  endpoint TEXT NOT NULL,
  request_hash TEXT,
  response_body JSONB,
  status_code INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '24 hours',
  PRIMARY KEY (key, tenant_id)
);
CREATE INDEX idx_idempotency_keys_expires ON idempotency_keys(expires_at);
```

### Cleanup
Job diario elimina claves expiradas:

```sql
DELETE FROM idempotency_keys WHERE expires_at < NOW();
```

## Consecuencias positivas

- **Consistencia:** cliente puede reintentar con seguridad
- **Simplicidad:** patrón uniforme en toda la API
- **Auditabilidad:** todas las operaciones registradas

## Consecuencias negativas

- **Storage:** tabla idempotency_keys crece con tráfico
- **Latencia:** 1 query adicional por operación (~2ms)
- **Complejidad:** cliente debe generar keys únicos

## Convención de Idempotency-Key
- Formato: `idk_<uuid>` o `<client-generated-uuid>`
- Longitud máxima: 128 caracteres
- Requerido en: POST /checkout, POST /invoices, POST /subscriptions/change

## Alternativas consideradas

### Client-side deduplication
**Rechazada:** No confiable, cliente puede tener bugs.

### Server-side cache only
**Rechazada:** No sobrevive a restarts.

## Impacto
- **INV-004:** Idempotencia en webhooks
- **API contracts:** Header `Idempotency-Key` documentado
- **SDKs:** Generan keys automáticamente
