# Bug Patterns - Patrones de Bugs Recurrentes

**Versión:** 1.0
**Última actualización:** 2026-05-27
**Fuente:** Incidentes P1/P2, bugs reportados, QA findings
**Knowledge Quarantine:** source_type=production_incident, decay=90d

## 1. Propósito

Catálogo de patrones de bugs que han aparecido en producción o staging.
Alimenta:
- ✅ Threat model
- ✅ Test plan
- ✅ Runbooks
- ✅ Critic memory
- ❌ Market scoring (prohibido)
- ❌ PRD generation (prohibido)

## 2. Categorías

### 2.1 Concurrency bugs
### 2.2 Data integrity bugs
### 2.3 Security bugs
### 2.4 Performance bugs
### 2.5 Integration bugs
### 2.6 State machine bugs

## 3. Patrones documentados

### BP-001: Race condition en webhook processing

**Dominio:** Billing  
**Severidad:** P1  
**Frecuencia:** 2 incidentes en 12 meses  
**Última aparición:** 2026-04-15

**Descripción:**
Dos webhooks del mismo evento llegan casi simultáneamente. Ambos pasan
el chequeo de idempotencia porque el INSERT aún no se commiteó.

**Root cause:**
```python
# ❌ No usa transacción atómica
if not already_processed(event_id):
    process_event(payload)
    mark_processed(event_id)  # Demasiado tarde
```

**Fix aplicado:**
```python
# ✅ UNIQUE constraint + INSERT atómico
try:
    db.execute("INSERT INTO processed_events VALUES (?, ?)", (event_id, provider))
    process_event(payload)
except IntegrityError:
    return {"status": "already_processed"}
```

**Tests añadidos:**
- `test_concurrent_webhooks` (10 requests paralelos)
- `test_webhook_storm` (100 requests en 1s)

**Invariantes reforzadas:** INV-004

**ADR relacionado:** ADR-0003 (actualizado)

---

### BP-002: Timezone mismatch en cálculos de billing

**Dominio:** Billing  
**Severidad:** P2  
**Frecuencia:** 3 veces  
**Última aparición:** 2026-03-20

**Descripción:**
Prorrateo usaba `datetime.now()` (local) vs `datetime.utcnow()` (UTC),
generando diferencias de 1 día en cambios de plan.

**Fix:**
```python
# ✅ Todo en UTC
from datetime import datetime, timezone
now = datetime.now(timezone.utc)
```

**Tests añadidos:**
- `test_proration_across_timezones`

**Runbook:** RUN-007 "Billing discrepancy investigation"

---

### BP-003: Cache poisoning cross-tenant

**Dominio:** Tenancy  
**Severidad:** P1 (security)  
**Frecuencia:** 1 vez  
**Aparición:** 2026-02-10

**Descripción:**
Cache key omitió tenant_id. Usuario de Tenant A recibió datos de Tenant B.

**Fix:** Wrapper `TenantCache` obligatorio.

**Invariantes reforzadas:** INV-011

---

### BP-004: Memory leak en job worker

**Dominio:** Performance  
**Severidad:** P2  
**Frecuencia:** 2 veces  
**Última aparición:** 2026-05-01

**Descripción:**
Worker cargaba todos los users en memoria al procesar batch.

**Fix:**
```python
# ✅ Streaming / batching
for batch in yield_per(users_query, 100):
    process_batch(batch)
```

---

### BP-005: Floating point en prorrateo

**Dominio:** Billing  
**Severidad:** P1  
**Frecuencia:** 1 vez  
**Aparición:** 2025-12-15

**Descripción:**
`amount * (days/30)` en float generó $0.01 de diferencia.

**Fix:** Todo en cents (BIGINT).

**Invariantes reforzadas:** INV-002

---

## 4. Métricas

| Métrica | Últimos 90d | Últimos 365d |
|---------|:-----------:|:------------:|
| Incidentes P1 | 2 | 7 |
| Incidentes P2 | 5 | 18 |
| Patrones nuevos | 3 | 12 |
| Tiempo medio detección | 2.3h | 4.1h |
| Tiempo medio fix | 8h | 14h |

## 5. Tendencias

**Dominios con más incidentes:**
1. Billing (40%)
2. Tenancy (25%)
3. Auth (15%)
4. Integrations (10%)
5. Otros (10%)

**Root causes más comunes:**
1. Race conditions (30%)
2. Validación insuficiente (25%)
3. Estado inconsistente (20%)
4. Timezone/datatype issues (15%)
5. Otros (10%)

## 6. Acción correctiva continua

Cada patrón nuevo dispara:
1. **Inmediato:** Hotfix + post-mortem
2. **Corto plazo (7d):** Tests de regresión
3. **Medio plazo (30d):** Refuerzo de invariantes/lint
4. **Largo plazo (90d):** ADR si cambia arquitectura

## 7. Relación con otros documentos
- Threat model: Amenazas derivadas de bugs
- Runbooks: Procedimientos de detección/mitigación
- Critic patterns: Versión preventiva de bugs pasados
- Test plan: Tests de regresión agregados
