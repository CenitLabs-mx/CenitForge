# RUN-002: Reporte de Fuga Cross-Tenant

**Severidad:** P0 (incidente de seguridad)
**Owner:** @security-oncall + @data-privacy-officer
**Última prueba:** 2026-05-20
**Tiempo estimado:** 15-60 min
**Compliance:** Notificación GDPR en 72h si aplica

## Síntomas

- Usuario reporta ver datos de otro tenant
- Anomalía detectada por audit log
- Alerta automática de tenant boundary violation

## Respuesta Inmediata (PRIMEROS 5 MIN)

### 1. Confirmar y contener

```bash
# Si hay evidencia concreta, inhabilitar usuarios involucrados
python tools/admin/disable_user.py --user-id $USER_ID --reason "INC-XXX investigation"

# O aislar tenant si es sistémico
python tools/admin/quarantine_tenant.py --tenant-id $TENANT_ID --mode readonly
```

### 2. Preservar evidencia

```bash
# Capturar logs relevantes
kubectl logs -l app=api -n production --since=1h > /tmp/incident-logs-$(date +%s).txt

# Capturar queries de DB (si se sospecha de query sin filtro)
psql $DATABASE_URL -c "
SELECT query, state, wait_event_type, query_start 
FROM pg_stat_activity 
WHERE usename = 'app' 
  AND query_start > NOW() - INTERVAL '1 hour'
ORDER BY query_start DESC;
" > /tmp/db-activity.txt

# Capturar request del usuario (si aplica)
# Desde access logs del load balancer
```

### 3. Notificar (paralelo)

- **Security team:** @security-oncall (Slack + call)
- **Legal:** @data-privacy-officer (si hay PII involucrada)
- **Leadership:** CTO + CEO si escala
- **Slack:** #incidents con etiqueta `security`

## Investigación

### 1. Determinar el vector

**Preguntas clave:**
- ¿Fue API, UI, export, webhooks?
- ¿Afectó a 1 usuario o es sistémico?
- ¿Qué datos se expusieron? (PII, financieros, etc.)
- ¿Desde cuándo ocurría?

### 2. Verificar RLS policies

```sql
-- Verificar que RLS está activo
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename IN ('users', 'invoices', 'subscriptions');

-- Ver policies
SELECT * FROM pg_policies 
WHERE schemaname = 'public' 
  AND tablename = '$AFFECTED_TABLE';

-- Probar policy manualmente
SET app.current_tenant_id = '$TENANT_A_ID';
SELECT * FROM $AFFECTED_TABLE WHERE tenant_id = '$TENANT_B_ID';
-- Debe retornar 0 rows
```

### 3. Verificar middleware

```bash
# Buscar versión del tenant middleware
kubectl get deployment api -n production -o yaml | grep image:

# Revisar si hubo deploy reciente
kubectl rollout history deployment/api -n production
```

### 4. Revisar queries sin filtro

```bash
# Buscar en logs de queries (si está habilitado)
grep -i "SELECT.*FROM $TABLE" /tmp/db-activity.txt | grep -v tenant_id
```

## Contención

### Si el vector es RLS desactivado

```sql
ALTER TABLE $AFFECTED_TABLE ENABLE ROW LEVEL SECURITY;
-- Forzar re-aplicación de policy
SELECT pg_reload_conf();
```

### Si el vector es query raw sin filtro

1. Identificar endpoint vulnerable
2. Hotfix inmediato (vía modo emergencia si es P0)
3. Desplegar con approval fast-track

### Si el vector es cache poisoning

```bash
# Invalidar cache del tenant afectado
redis-cli --scan --pattern "tenant:$TENANT_ID:*" | xargs redis-cli del

# O invalidar toda la cache si es sistémico
redis-cli FLUSHDB
```

## Remediación

### 1. Notificar a afectados

**GDPR (si PII):**
- Data Protection Officer notifica a autoridad en ≤72h
- Comunicación a usuarios afectados en ≤7 días

**Template de email:**
```
Subject: Important security notice regarding your account

Dear [name],

On [date], we identified a security issue that may have exposed 
some of your data to another customer. The affected data includes:
[list]

We have contained the issue and taken the following actions:
[list]

We sincerely apologize for this incident. If you have questions...
```

### 2. Post-mortem

Obligatorio en 72h con:
- Timeline completo
- Root cause
- Impacto (tenants, usuarios, datos afectados)
- Acciones correctivas inmediatas
- Acciones preventivas a 30/60/90 días
- Owner de cada acción

### 3. Actualizar documentos

- [ ] Threat model: agregar amenaza si es nueva
- [ ] Tenant isolation tests: agregar test de regresión
- [ ] Lint rule: detectar patrón si aplica
- [ ] ADR: documentar cambio arquitectónico

## Comunicación

| Audiencia | Timing | Canal | Responsable |
|-----------|--------|-------|-------------|
| Oncall team | Inmediato | Slack #incidents | Oncall |
| Security team | <5 min | Call | Security lead |
| CTO/CEO | <30 min si P0 | Call | Security lead |
| Clientes afectados | <24h | Email | CEO + Legal |
| Autoridad GDPR | <72h si aplica | Portal | DPO |
| Público | Solo si >1000 afectados | Blog post | Comms |

## Checklist de cierre

- [ ] Fuga contenida
- [ ] Causa raíz identificada
- [ ] Fix desplegado
- [ ] Tests de regresión agregados
- [ ] Usuarios afectados notificados
- [ ] Post-mortem completado
- [ ] Threat model actualizado
- [ ] ADR creado si aplica
- [ ] Métricas del incidente registradas

## Herramientas

- `tools/admin/disable_user.py`
- `tools/admin/quarantine_tenant.py`
- `tools/admin/invalidate_cache.py`
- `tools/forensics/export_tenant_activity.py`
