# Billing State Machine: [Nombre]

## Estados

| Estado | Premium | Billing UI | Data |
|--------|:-------:|:----------:|:----:|
| Incomplete | ❌ | ✅ | ❌ |
| Trialing | ✅ | ✅ | ✅ |
| Active | ✅ | ✅ | ✅ |
| PastDue | ⚠️ | ✅ | ✅ |
| Suspended | ❌ | ✅ | Read |
| Canceled | ❌ | ✅ | Export |

## Transiciones

| Desde | Evento | Hacia |
|-------|--------|-------|
| Incomplete | checkout.completed | Trialing/Active |
| Trialing | invoice.payment_succeeded | Active |
| Active | invoice.payment_failed | PastDue |

## Invariantes

- **INV-003:** Webhook firma válida
- **INV-004:** Idempotencia event_id
- **INV-020:** Shadow testing obligatorio

## Shadow Testing
- Duración: 7 días
- Discrepancia tolerada: 0%
- Shadow Safety Contract activo
