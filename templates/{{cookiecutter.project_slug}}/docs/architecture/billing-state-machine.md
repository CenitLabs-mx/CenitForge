# Billing State Machine

**ADR:** ADR-0002-billing-webhook-strategy
**ADR:** ADR-0003-idempotency-strategy
**Versión:** 1.0

## 1. Estados

```
                  ┌─────────────┐
                  │ Incomplete  │
                  └──────┬──────┘
                         │ checkout.completed
                         ▼
                  ┌─────────────┐
     ┌───────────►│   Active    │◄──────────────┐
     │            └──────┬──────┘               │
     │                   │ payment_failed       │ payment_succeeded
     │                   ▼                      │
     │            ┌─────────────┐               │
     │            │  PastDue    ├───────────────┘
     │            └──────┬──────┘
     │                   │ grace_period.expired
     │                   ▼
     │            ┌─────────────┐
     │            │  Suspended  │
     │            └──────┬──────┘
     │                   │ suspension.timeout
     │                   ▼
     │            ┌─────────────┐
     └────────────┤  Canceled   │
                  └─────────────┘
```

## 2. Transiciones

Ver tabla detallada en documento maestro V5 sección 18.2.

## 3. Idempotencia (INV-004)

```sql
CREATE TABLE processed_events (
  event_id TEXT NOT NULL,
  provider TEXT NOT NULL,
  processed_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(event_id, provider)
);
```

**Flujo:**
1. Webhook llega
2. Verificar firma (INV-003)
3. `INSERT INTO processed_events` (si UNIQUE violation → 200 OK sin mutar)
4. Procesar y mutar estado

## 4. Webhook signature verification

```python
def verify_stripe_signature(payload, sig_header, secret):
    try:
        stripe.Webhook.construct_event(payload, sig_header, secret)
        return True
    except ValueError:
        return False
    except stripe.error.SignatureVerificationError:
        return False
```

## 5. Entitlements por estado

| Estado | Premium features | Billing UI | Data access |
|--------|:----------------:|:----------:|:-----------:|
| Incomplete | ❌ | ✅ | ❌ |
| Trialing | ✅ | ✅ | ✅ |
| Active | ✅ | ✅ | ✅ |
| PastDue | ⚠️ Degraded | ✅ | ✅ |
| Suspended | ❌ | ✅ | Read-only |
| Canceled | ❌ | ✅ (grace) | Export |

## 6. Shadow testing (INV-020)

Todo cambio de state machine requiere:
- Shadow Safety Contract activo
- 7 días de shadow testing con lógica vieja vs nueva
- Discrepancia tolerada: 0% en mutaciones financieras
- Reporte diario de métricas

## 7. Audit log

Toda transición registra:
- `from_state`, `to_state`
- `event_id` (idempotency)
- `actor` (system / user)
- `timestamp`
- `metadata` (reason, etc.)
