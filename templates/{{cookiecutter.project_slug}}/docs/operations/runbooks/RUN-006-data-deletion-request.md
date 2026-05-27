# RUN-006: Solicitud de Eliminación de Datos (GDPR/CCPA)

**Severidad:** P2 (pero con deadline legal: 30 días)
**Owner:** @privacy-oncall + @data-engineering
**Última prueba:** 2026-05-22
**Tiempo estimado:** 2-4 horas por solicitud

## Contexto Legal

**GDPR Art. 17 (Right to Erasure):**
- Plazo: 30 días (extensible a 90 en casos complejos)
- Excepciones: obligaciones legales (facturación 7 años)

**CCPA:**
- Plazo: 45 días
- Excepciones similares

## Proceso

### 1. Recepción y validación (día 1)

**Verificar identidad:**
- [ ] Email confirmado (link de verificación)
- [ ] O ID gubernamental (si es cuenta enterprise)
- [ ] O autenticación en app

**Documentar solicitud:**
```python
# tools/privacy/create_deletion_request.py
python tools/privacy/create_deletion_request.py \
  --tenant-id $TENANT_ID \
  --requester-email $EMAIL \
  --scope full \  # o partial
  --legal-basis gdpr-art-17 \
  --received-date 2026-05-27
```

### 2. Inventario de datos (día 1-2)

```python
# Generar reporte de datos del usuario/tenant
python tools/privacy/inventory_data.py \
  --tenant-id $TENANT_ID \
  --output /tmp/data-inventory-$TENANT_ID.json
```

**Categorización automática:**
- ✅ **Eliminable:** account data, usage data, logs
- ⚠️ **Requiere revisión:** support tickets, comunicaciones
- ❌ **Retención legal:** facturas (7 años), audit logs (2 años)

### 3. Revisión de excepciones (día 2-3)

**Legal team revisa:**
- Obligaciones contractuales
- Litigios pendientes
- Requerimientos regulatorios

**Output:** Lista final de datos a eliminar vs retener

### 4. Ejecución de eliminación (día 3-10)

#### Soft delete (inmediato, reversible)

```sql
UPDATE users SET 
  deleted_at = NOW(),
  email = 'deleted+' || id || '@example.com',
  name = 'Deleted User',
  phone = NULL
WHERE id = $USER_ID;
```

#### Hard delete (irreversible, programado)

```python
# tools/privacy/hard_delete.py
python tools/privacy/hard_delete.py \
  --tenant-id $TENANT_ID \
  --tables users,events,sessions,api_keys \
  --dry-run  # primero sin ejecutar

# Verificar output, luego:
python tools/privacy/hard_delete.py \
  --tenant-id $TENANT_ID \
  --tables users,events,sessions,api_keys \
  --confirm
```

#### Anonimización (para datos que deben retenerse agregados)

```sql
-- Ejemplo: analytics data
UPDATE page_views SET
  user_id = NULL,
  tenant_id = NULL,
  ip_address = NULL,
  user_agent = 'redacted'
WHERE user_id = $USER_ID;
```

### 5. Limpieza de sistemas secundarios

```bash
# Cache
redis-cli --scan --pattern "*$USER_ID*" | xargs redis-cli del

# Search indexes
python tools/privacy/remove_from_search.py --user-id $USER_ID

# Backups (no modificar, pero documentar)
# Los backups se purgan según retención (30 días)
# Anotar en el caso para verificación futura

# Third-party services
python tools/privacy/notify_third_parties.py \
  --user-id $USER_ID \
  --services sendgrid,intercom,segment
```

### 6. Verificación (día 10-15)

```python
# tools/privacy/verify_deletion.py
python tools/privacy/verify_deletion.py \
  --tenant-id $TENANT_ID \
  --output /tmp/verification-report.json
```

**Verificaciones:**
- [ ] DB primary: 0 rows con email/PII
- [ ] Read replicas: propagado
- [ ] Search indexes: sin resultados
- [ ] Cache: sin keys
- [ ] Logs: solo referencias anonimizadas

### 7. Confirmación al solicitante (día 15-20)

**Template email:**
```
Subject: Your data deletion request has been completed

Dear [name],

We have processed your data deletion request received on [date].

The following data has been permanently deleted:
- Account information
- Usage history
- [list]

The following data has been retained as required by law:
- Invoices (7 years for tax compliance)
- Audit logs (2 years for security)

This retained data will be automatically deleted after the 
required period and will not be used for any other purpose.

If you have questions, contact privacy@example.com.
```

### 8. Documentación y cierre (día 20-30)

**Registrar en compliance log:**
```yaml
- request_id: REQ-2026-XXX
  tenant_id: ...
  received_at: 2026-05-27
  completed_at: 2026-06-15
  data_deleted: [list]
  data_retained: [list with legal basis]
  verified_by: ...
```

## Casos especiales

### Enterprise con datos en backups

Si el cliente exige eliminación de backups:
1. Legal evalúa viabilidad
2. Si se acepta: restore backup → eliminar → re-backup
3. Costo: ~$5k-$50k USD (pasar al cliente si contrato lo permite)

### Datos en third-party processors

Notificar vía API/webhook:
- SendGrid (unsubscribe + delete)
- Intercom (delete user)
- Segment (delete user)
- Stripe (si aplica, redact PII)

### Usuario arrepentido

Si solicita reversa dentro de 7 días de soft-delete:
- Soft-delete es reversible
- Documentar como "withdrawn request"

## Herramientas

- `tools/privacy/create_deletion_request.py`
- `tools/privacy/inventory_data.py`
- `tools/privacy/hard_delete.py`
- `tools/privacy/verify_deletion.py`
- `tools/privacy/notify_third_parties.py`
- `tools/privacy/anonymize.py`

## Auditoría

Cada solicitud genera audit trail inmutable:
- Quién solicitó
- Cuándo se recibió
- Quién procesó
- Qué se eliminó
- Qué se retuvo (con justificación)
- Cuándo se verificó
- Cuándo se confirmó al usuario

## Métricas

- Tiempo promedio de procesamiento: < 20 días
- % completadas dentro de deadline: >95%
- Solicitudes por mes: tracking
- Quejas post-eliminación: 0
