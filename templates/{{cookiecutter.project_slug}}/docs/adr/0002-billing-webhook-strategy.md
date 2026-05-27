# ADR-0002: Estrategia de Webhooks de Billing

**Estado:** Aceptada
**Fecha:** 2026-05-27
**Owner:** @billing-lead
**Relacionado:** INV-003, INV-004, INV-009

## Contexto

El sistema depende de webhooks de Stripe para mutar el estado de billing.
Los webhooks son inherentemente no confiables: pueden llegar duplicados,
fuera de orden, con latencia, o ser falsificados.

**Requisitos:**
- Idempotencia absoluta (INV-004)
- Verificación criptográfica de firma (INV-003)
- Tolerancia a reordenamiento
- Auditabilidad completa

## Decisión

### Arquitectura de procesamiento

```
Stripe → /v1/webhooks/stripe
       → VerifySignature (middleware)
       → RateLimit (100/min global)
       → IdempotencyCheck (INSERT UNIQUE en processed_events)
       → EventRouter (dispatch por event_type)
       → StateMachine (muta subscription)
       → Emit Domain Event (invoice.paid, etc.)
       → 200 OK
```

### Tabla processed_events

```sql
CREATE TABLE processed_events (
  event_id TEXT NOT NULL,
  provider TEXT NOT NULL,
  event_type TEXT NOT NULL,
  received_at TIMESTAMPTZ DEFAULT NOW(),
  processed_at TIMESTAMPTZ,
  tenant_id UUID REFERENCES tenants(id),
  PRIMARY KEY (event_id, provider)
);
CREATE INDEX idx_processed_events_tenant ON processed_events(tenant_id);
```

### Flujo idempotente

```python
@app.post("/v1/webhooks/stripe")
async def stripe_webhook(request: Request):
    # 1. Verificar firma (antes de leer body)
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    if not verify_signature(payload, sig, STRIPE_WEBHOOK_SECRET):
        return JSONResponse({"error": "invalid_signature"}, status_code=401)
    
    # 2. Parsear
    event = json.loads(payload)
    event_id = event["id"]
    event_type = event["type"]
    
    # 3. Idempotency check atómico
    try:
        await db.execute(
            "INSERT INTO processed_events (event_id, provider, event_type, tenant_id) "
            "VALUES (?, 'stripe', ?, ?)",
            (event_id, event_type, extract_tenant_id(event))
        )
    except IntegrityError:
        # Ya procesado: responder 200 OK (Stripe no reintenta)
        return {"status": "already_processed"}
    
    # 4. Procesar
    await state_machine.handle(event)
    
    # 5. Marcar como completado
    await db.execute(
        "UPDATE processed_events SET processed_at = NOW() WHERE event_id = ? AND provider = 'stripe'",
        (event_id,)
    )
    
    return {"status": "ok"}
```

## Consecuencias positivas

- **Idempotencia garantizada** a nivel DB (UNIQUE constraint)
- **Seguridad** por firma criptográfica
- **Tolerancia a retries** de Stripe sin efectos secundarios
- **Auditabilidad** completa vía tabla processed_events

## Consecuencias negativas

- **Complejidad** adicional vs procesamiento ingenuo
- **Latencia** de ~10ms por operación DB de idempotencia
- **Cleanup** requerido: job mensual borra eventos >90 días

## Alternativas consideradas

### In-memory deduplication (Redis SET NX)
**Rechazada:** No sobrevive a restarts, riesgo de doble procesamiento.

### Application-level check + INSERT
**Rechazada:** Race condition entre check e insert.

## Impacto en seguridad
Mitiga: webhook forgery, replay attacks, double-spending.

## Impacto en billing
Garantiza que cada evento financiero se procesa exactamente una vez.

## Tests requeridos

- [ ] Webhook con firma válida → 200 OK
- [ ] Webhook con firma falsa → 401
- [ ] Webhook duplicado → 200 OK sin mutar estado
- [ ] Webhook concurrente (10 simultáneos) → solo 1 mutación
- [ ] Webhook con event_id malicioso → sanitized
- [ ] Webhook para customer sin tenant mapping → 200 + log

## Observabilidad

Métricas expuestas:
- `webhooks_received_total{provider, event_type}`
- `webhooks_processed_total{provider, event_type}`
- `webhooks_duplicate_total`
- `webhooks_invalid_signature_total`
- `webhook_processing_latency_seconds`

Alertas:
- `invalid_signature_rate > 1%` → P2
- `duplicate_rate > 5%` → P3 (puede indicar problema en Stripe)
- `processing_latency_p95 > 5s` → P2
