# RUN-001: Webhook de Billing No Llega

**Severidad:** P1 (si afecta múltiples tenants)
**Owner:** @billing-oncall
**Última prueba:** 2026-05-15
**Tiempo estimado:** 15-30 min

## Síntomas

- Tenant reporta que pago procesado en Stripe no se refleja
- Estado de subscription no cambia tras `invoice.payment_succeeded`
- Dashboard de webhooks muestra caída en recepción

## Triaje Inicial (5 min)

### 1. Verificar en Stripe Dashboard

1. Ir a Stripe Dashboard → Developers → Events
2. Buscar eventos del tenant afectado (últimas 24h)
3. Confirmar que Stripe **envió** el evento
4. Verificar response status de nuestro endpoint

**Escenarios:**
- Stripe no envió → Problema en Stripe, escalar con soporte
- Stripe envió, respondió 5xx → Problema nuestro, continuar
- Stripe envió, respondió 200 pero no procesó → Bug de idempotencia, saltar a sección "Doble procesamiento"

### 2. Verificar logs de aplicación

```bash
# Buscar por event_id
kubectl logs -l app=billing -n production --tail=10000 | \
  grep "event_id=$EVENT_ID"

# O por tenant
kubectl logs -l app=billing -n production --tail=10000 | \
  grep "tenant_id=$TENANT_ID"
```

### 3. Verificar tabla processed_events

```sql
SELECT * FROM processed_events 
WHERE event_id = '$EVENT_ID' AND provider = 'stripe';
```

- Si existe → Evento procesado, problema en state machine
- Si no existe → Evento nunca llegó o falló antes de INSERT

## Resolución por Escenario

### Escenario A: Webhook rechazado por firma inválida

**Causa probable:** Secret de webhook rotado o desincronizado

**Solución:**
```bash
# Verificar secret en vault
vault read secret/stripe/webhook_secret

# Comparar con Stripe Dashboard → Webhooks → Signing secret
# Si difieren, actualizar vault:
vault write secret/stripe/webhook_secret value=$NEW_SECRET

# Restart billing pods
kubectl rollout restart deployment/billing -n production
```

### Escenario B: Webhook llegó pero state machine falló

**Causa probable:** Transición inválida o bug en lógica

**Diagnóstico:**
```sql
SELECT * FROM subscriptions 
WHERE tenant_id = '$TENANT_ID' 
ORDER BY updated_at DESC LIMIT 5;

-- Ver audit log
SELECT * FROM billing_audit_log 
WHERE tenant_id = '$TENANT_ID' 
  AND created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;
```

**Solución:**
- Si estado actual permite transición → Re-disparar evento desde Stripe
- Si no → Intervención manual con ADR documentado

### Escenario C: Worker queue backlogged

**Verificar:**
```bash
# Queue depth
redis-cli LLEN billing_events_queue

# Workers activos
kubectl get pods -l app=billing-worker -n production
```

**Si queue > 10k mensajes:**
```bash
# Escalar workers
kubectl scale deployment/billing-worker --replicas=20 -n production

# Monitorear drain rate
watch -n 5 'redis-cli LLEN billing_events_queue'
```

## Recuperación Manual (último recurso)

Si el webhook nunca llegó y Stripe no puede re-disparar:

```python
# Script de compensación
from billing.state_machine import StateMachine

sm = StateMachine()
sm.force_transition(
    tenant_id="$TENANT_ID",
    from_state="PastDue",
    to_state="Active",
    reason="Manual compensation - webhook lost - INC-XXX",
    actor="oncall@example.com"
)
```

**Obligatorio:**
1. ADR documentando la compensación
2. Post-mortem en 72h
3. Test de regresión agregado

## Comunicación

- **Cliente:** Notificar vía support ticket que se está investigando
- **Interno:** Slack #incidents con updates cada 15 min
- **Post-resolución:** Email de confirmación al cliente

## Métricas de éxito

- Tiempo de detección: < 5 min
- Tiempo de resolución: < 30 min
- Tenant afectado: < 1 (idealmente 0)

## Referencias

- Stripe webhook docs: https://stripe.com/docs/webhooks
- Dashboard interno: https://metrics.internal/billing
- ADR-0002: Webhook strategy
