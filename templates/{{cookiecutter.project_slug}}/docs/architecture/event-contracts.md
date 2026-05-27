# Event Contracts: [Producto]

**ADR:** ADR-0010-event-contracts
**Versión:** 1.0

## 1. Principios

1. **Schema-first:** Todo evento tiene JSON Schema versionado
2. **Inmutabilidad:** Una vez publicado, el schema no cambia (se añade nueva versión)
3. **Idempotencia:** Los consumers deben ser idempotentes (reintentos son normales)
4. **Ordered por aggregate:** Eventos del mismo aggregate se entregan en orden

## 2. Formato estándar

```json
{
  "event_id": "evt_uuid",
  "event_type": "invoice.paid",
  "event_version": "1.0",
  "timestamp": "2026-05-27T10:00:00Z",
  "tenant_id": "tenant_uuid",
  "aggregate_id": "inv_uuid",
  "aggregate_type": "invoice",
  "correlation_id": "corr_uuid",
  "causation_id": "evt_anterior_uuid",
  "payload": { ... }
}
```

## 3. Catálogo de eventos

### 3.1 Billing domain

#### `invoice.paid` (v1.0)
**Trigger:** Webhook `invoice.payment_succeeded` de Stripe validado  
**Payload:**
```json
{
  "invoice_id": "uuid",
  "amount_cents": 9900,
  "currency": "USD",
  "paid_at": "2026-05-27T..."
}
```
**Consumers:** SubscriptionState, Entitlements, Analytics, AuditLog

#### `invoice.failed` (v1.0)
...

### 3.2 Identity domain

#### `user.created`, `user.invited`, `user.deleted`
...

### 3.3 Tenant domain

#### `tenant.created`, `tenant.suspended`, `tenant.deleted`
...

## 4. Infraestructura
- **Broker:** RabbitMQ / AWS EventBridge / Kafka (según escala)
- **Retención:** 7 días mínimo
- **DLQ:** Dead Letter Queue por consumer
- **Schema registry:** Confluent o custom con Git

## 5. Testing
- **Event contract tests** en CI validan schema
- **Consumer tests** usan test doubles
- **Producer tests** validan que el evento disparado cumple contrato
