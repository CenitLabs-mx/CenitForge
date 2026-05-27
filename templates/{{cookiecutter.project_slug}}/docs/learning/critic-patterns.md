# Critic Patterns - Memoria de Patrones Recurrentes

**Versión:** 1.0
**Última actualización:** 2026-05-27
**Owner:** @tech-lead + @security-lead
**Política de rotación:** Top 20 activos, consolidar >3 repeticiones a ADR, archivar inactivos >6 meses

## 1. Propósito

Este documento es la **memoria a largo plazo del Critic Model**. Contiene patrones de errores recurrentes que los Builder agents cometen. Cuando un patrón aparece ≥3 veces, se eleva a bloqueador automático.

## 2. Política de rotación

### 2.1 Promoción a ADR
Si un patrón se detecta ≥3 veces en 90 días:
1. Se crea ADR específico con mitigation
2. Se añade invariante o lint rule
3. El patrón se marca como `promoted_to_adr`

### 2.2 Archivo
Patrones no vistos en >6 meses se mueven a `/docs/learning/archive/critic-patterns-YYYY.md`

### 2.3 Tamaño máximo
Top 20 patrones activos. Al llegar a 21, se archiva el menos frecuente.

## 3. Patrones activos

### PAT-001: Queries sin tenant_id en ORM
**Severidad:** 🔴 Bloqueador  
**Frecuencia:** 12 veces en últimos 90 días  
**Última detección:** 2026-05-20 (PR #142)

**Síntoma:**
```python
# ❌ Builder olvida filtrar
users = session.query(User).filter(User.role == "admin").all()
```

**Fix:**
```python
# ✅ Middleware inyecta tenant_id, pero queries raw deben incluirlo
users = session.query(User).filter(
    User.tenant_id == current_tenant_id,
    User.role == "admin"
).all()
```

**Prevención:**
- Linter rule: `tenant-filter-required`
- Mutation test: Remover filtro debe romper test

**Status:** Activo | **Promoción a ADR:** Pendiente (2/3)

---

### PAT-002: Tests tautológicos
**Severidad:** 🔴 Bloqueador  
**Frecuencia:** 8 veces en últimos 90 días  
**Última detección:** 2026-05-18

**Síntoma:**
```python
def test_calculate_discount():
    result = calculate_discount(1500)
    assert result is not None  # ❌ Siempre pasa
```

**Fix:**
```python
def test_calculate_discount_large_amount():
    assert calculate_discount(1500) == 0.1
    assert calculate_discount(999) == 0  # ✅ Detecta edge
```

**Prevención:**
- Mutation testing obligatorio
- Critic busca asserts débiles (`is not None`, `assertTrue`, `toBeDefined`)

---

### PAT-003: Float en campos financieros
**Severidad:** 🔴 Bloqueador  
**Frecuencia:** 5 veces en últimos 90 días  
**Última detección:** 2026-05-22

**Síntoma:**
```python
class Invoice(Base):
    amount = Column(Float)  # ❌
```

**Fix:**
```python
class Invoice(Base):
    amount_cents = Column(BigInteger)  # ✅
    # o
    amount = Column(Numeric(20, 4))  # ✅
```

**Prevención:**
- Migration linter (INV-002)
- ORM mapping audit quarterly

---

### PAT-004: Cache keys sin tenant prefix
**Severidad:** 🟠 Alto  
**Frecuencia:** 4 veces  
**Última detección:** 2026-05-10

**Síntoma:**
```python
cache.set(f"user:{user_id}", data)  # ❌ Cross-tenant leak
```

**Fix:**
```python
cache.set(f"tenant:{tenant_id}:user:{user_id}", data)  # ✅
```

**Prevención:**
- Wrapper `TenantCache` obligatorio
- Linter detecta uso directo de Redis client

---

### PAT-005: Webhook sin idempotencia
**Severidad:** 🔴 Bloqueador  
**Frecuencia:** 3 veces  
**Última detección:** 2026-05-05

**Síntoma:**
```python
@app.post("/webhooks/stripe")
async def handle(payload):
    process_event(payload)  # ❌ Sin chequeo
```

**Fix:**
```python
@app.post("/webhooks/stripe")
async def handle(payload, request: Request):
    verify_signature(request)
    event_id = payload["id"]
    if already_processed(event_id):
        return {"status": "ok"}  # Idempotente
    mark_processed(event_id)
    process_event(payload)
```

**Status:** Promovido a ADR-0003 ✅

---

### PAT-006: PII en logs de error
**Severidad:** 🟠 Alto  
**Frecuencia:** 6 veces  
**Última detección:** 2026-05-25

**Síntoma:**
```python
logger.error(f"Error processing user {user.email}: {err}")  # ❌
```

**Fix:**
```python
logger.error(f"Error processing user {user.id}: {err}")  # ✅
# o usar sanitizer
logger.error(f"Error: {sanitize(user.email)}")
```

**Prevención:**
- PII log scanner en CI
- LogSanitizer middleware

---

### PAT-007: Mocks excesivos en tests
**Severidad:** 🟡 Medio  
**Frecuencia:** 7 veces  
**Última detección:** 2026-05-24

**Síntoma:**
```python
def test_payment():
    mock_stripe.return_value = {"status": "succeeded"}  # ❌ Mock total
    result = process_payment()
    assert result["status"] == "succeeded"  # Valida el mock
```

**Fix:** Usar integración real con Stripe test mode o test doubles realistas.

---

### PAT-008: Scope creep silencioso
**Severidad:** 🟠 Alto  
**Frecuencia:** 9 veces  
**Última detección:** 2026-05-26

**Síntoma:**
Micro-prompt declara 3 archivos, modifica 12.

**Prevención:**
- Blast Radius Gate en CI (V5)
- Critic compara diff vs MP metadata

---

### PAT-009: Hardcoded secrets en tests
**Severidad:** 🔴 Bloqueador  
**Frecuencia:** 4 veces  
**Última detección:** 2026-05-15

**Síntoma:**
```python
STRIPE_KEY = "sk_test_abc123"  # ❌ Aunque sea test key
```

**Fix:** Usar env vars + fixtures.

**Prevención:**
- Pre-commit secret scan (gitleaks)
- CI secret scan

---

### PAT-010: Rate limiting faltante en endpoints sensibles
**Severidad:** 🟠 Alto  
**Frecuencia:** 3 veces  
**Última detección:** 2026-05-12

**Síntoma:**
Login endpoint sin throttle → vulnerable a brute-force.

**Fix:** Decorator `@rate_limit("5/minute")`

**Status:** Promovido a ADR-0012 ✅

---

## 4. Patrones recientemente archivados

| ID | Patrón | Razón de archivo | Fecha |
|----|--------|------------------|-------|
| PAT-OLD-001 | [Descripción] | No visto en 7 meses | 2026-04-01 |

## 5. Métricas

| Métrica | Valor actual |
|---------|:------------:|
| Patrones activos | 10 |
| Promovidos a ADR (90d) | 2 |
| Archivados (90d) | 1 |
| Detecciones totales (90d) | 58 |
| Top patrón | PAT-001 (queries sin tenant) |

## 6. Proceso de adición

Cuando el Critic detecta un nuevo patrón:

1. Verificar que no esté ya en la lista
2. Registrar en formato estándar (ver arriba)
3. Incrementar contador de frecuencia
4. Si frecuencia ≥ 3, evaluar promoción a ADR
5. Commit a `/docs/learning/critic-patterns.md`
6. Knowledge Quarantine asigna tags: `[critic_memory, bug_pattern]`

## 7. Integración con Critic Model

El prompt del Critic incluye:

```
Revisa el diff buscando estos patrones recurrentes:
[lista de los top 20 activos]

Si detectas alguno, marca como bloqueador y cita el PAT-XXX.
```

## 8. Review cadence
- **Mensual:** Tech lead revisa frecuencia y promueve/archiva
- **Quarterly:** Auditoría completa de memoria
