# RUN-004: Discrepancia de Billing Detectada

**Severidad:** P1 (P0 si afecta >100 tenants)
**Owner:** @billing-oncall + @finance
**Última prueba:** 2026-05-18
**Tiempo estimado:** 30-90 min

## Síntomas

- Shadow billing discrepancy alert
- Cliente reporta cobro incorrecto
- Stripe vs DB mismatch detectado
- Reconciliación financiera no cuadra

## Triaje (10 min)

### 1. Determinar alcance

```sql
-- Contar tenants afectados
SELECT COUNT(DISTINCT tenant_id) 
FROM billing_audit_log 
WHERE created_at > NOW() - INTERVAL '24 hours'
  AND discrepancy_detected = true;

-- Sumar impacto financiero
SELECT 
  SUM(ABS(db_amount_cents - stripe_amount_cents)) as total_discrepancy_cents,
  COUNT(*) as affected_invoices
FROM invoice_reconciliation 
WHERE reconciled_at > NOW() - INTERVAL '7 days'
  AND db_amount_cents != stripe_amount_cents;
```

### 2. Categorizar

| Tipo | Causa probable | Acción |
|------|---------------|--------|
| Shadow discrepancy | Bug en nueva lógica | Pausar rollout, investigar |
| Proration incorrecto | Timezone/float issue | Hotfix + compensación |
| Doble cobro | Idempotencia rota | Refund inmediato |
| Sin cobro | State machine bug | Invoice manual |
| Monto incorrecto | Price override | Ajuste + ADR |

## Resolución por Tipo

### Shadow Billing Discrepancy

**Acción inmediata:** Pausar rollout de nueva lógica

```bash
# Desactivar shadow flag
kubectl set env deployment/billing SHADOW_MODE=false -n production

# Alertar al equipo
echo "Shadow billing discrepancy detected, rollout paused" | \
  slack-cli send --channel #billing
```

**Diagnóstico:**
```bash
# Ver discrepancias específicas
python tools/billing/analyze_shadow_discrepancies.py \
  --since 7d \
  --output /tmp/discrepancies.json

# Por tipo de evento
jq 'group_by(.event_type) | map({type: .[0].event_type, count: length})' \
  /tmp/discrepancies.json
```

### Doble Cobro

**Acción inmediata:** Refund + disculpa

```python
# Script de compensación masiva
from billing.stripe_client import StripeClient

stripe = StripeClient()

for invoice in affected_invoices:
    # Refund del cargo duplicado
    stripe.refund(
        charge_id=invoice.duplicate_charge_id,
        amount=invoice.amount_cents,
        reason="duplicate",
        metadata={"incident": "INC-XXX", "reason": "duplicate_charge"}
    )
    
    # Marcar como compensado
    db.execute("""
        UPDATE invoice_compensations 
        SET compensated_at = NOW(), compensation_type = 'refund'
        WHERE invoice_id = ?
    """, (invoice.id,))
```

**Comunicación al cliente:**
```
Subject: We've issued a refund for a duplicate charge

Dear [name],

We identified a technical issue that resulted in a duplicate 
charge of $X.XX on your account on [date].

We have issued a full refund which should appear in 3-5 business days.

We apologize for the inconvenience...
```

### Proration Incorrecto

**Diagnóstico:**
```sql
-- Ver cálculos de proration
SELECT 
  tenant_id, 
  subscription_id,
  old_plan,
  new_plan,
  proration_factor,
  expected_cents,
  actual_cents
FROM proration_calculations 
WHERE created_at > NOW() - INTERVAL '7 days'
  AND expected_cents != actual_cents;
```

**Causas comunes:**
1. **Timezone:** cálculo usa local en vez de UTC
2. **Float:** pérdida de precisión
3. **Day count:** 30 vs 31 días
4. **Plan price:** override no aplicado

**Compensación:**
- Ajuste manual en próxima invoice
- O credit note inmediato

## Reconciliación

### Daily reconciliation job

```python
# Corre cada día a las 2 AM
def reconcile_billing():
    discrepancies = []
    
    for invoice in db.query("""
        SELECT * FROM invoices 
        WHERE reconciled_at IS NULL
          AND created_at > NOW() - INTERVAL '1 day'
    """):
        stripe_invoice = stripe.get_invoice(invoice.stripe_id)
        
        if invoice.amount_cents != stripe_invoice.amount_paid:
            discrepancies.append({
                "invoice_id": invoice.id,
                "db_amount": invoice.amount_cents,
                "stripe_amount": stripe_invoice.amount_paid,
                "delta": invoice.amount_cents - stripe_invoice.amount_paid
            })
    
    if discrepancies:
        alert_billing_team(discrepancies)
        # Auto-crear tickets
        for d in discrepancies:
            create_ticket(
                title=f"Billing discrepancy: invoice {d['invoice_id']}",
                priority="P1" if abs(d['delta']) > 10000 else "P2",
                data=d
            )
```

## Post-mortem obligatorio

Si impacto > $1000 USD o >10 tenants:

1. Root cause completo
2. Timeline de detección → resolución
3. Compensaciones emitidas
4. Acciones preventivas
5. Actualizar billing tests
6. ADR si hay cambio arquitectónico

## Herramientas

- `tools/billing/reconcile.py`
- `tools/billing/analyze_shadow_discrepancies.py`
- `tools/billing/mass_refund.py`
- `tools/admin/issue_credit.py`
