# RUN-005: Database Failover

**Severidad:** P0
**Owner:** @db-oncall + @platform-oncall
**Última prueba:** 2026-05-05 (quarterly drill)
**Tiempo estimado:** 5-15 min (automático) + 30 min (verificación)

## Síntomas

- Alerta de primary DB down
- Errores 500 en API (database connection)
- Métricas de DB latency en spike
- CloudWatch/RDS event notification

## Failover Automático (AWS RDS Multi-AZ)

**RDS maneja failover automáticamente en 60-120s.**

### Durante el failover

```bash
# Monitorear progreso
aws rds describe-db-instances \
  --db-instance-identifier $DB_ID \
  --query 'DBInstances[0].{Status:DBInstanceStatus,Endpoint:Endpoint.Address}'

# Ver logs
aws rds describe-db-instances \
  --db-instance-identifier $DB_ID \
  --query 'DBInstances[0].DBInstanceStatus'
```

### Aplicación

**Comportamiento esperado:**
- Conexiones activas se caen
- Pool reconnects automáticamente
- Requests en vuelo fallan (500)
- Circuit breaker puede activarse

**No hacer:**
- NO reiniciar pods (agrava el problema)
- NO cambiar configuración
- NO escalar (esperar a que DB estabilice)

## Verificación Post-Failover

### 1. Conectividad

```bash
# Desde un pod de aplicación
kubectl exec -it $(kubectl get pod -l app=api -n production -o name | head -1) \
  -n production -- \
  python -c "
import psycopg2
conn = psycopg2.connect('$DATABASE_URL')
cur = conn.cursor()
cur.execute('SELECT NOW(), pg_is_in_recovery()')
print(cur.fetchone())
"
```

### 2. Replication lag

```sql
-- En el nuevo primary
SELECT 
  pg_current_wal_lsn() - replay_lsn AS lag_bytes,
  write_lag,
  flush_lag,
  replay_lag
FROM pg_stat_replication;
```

### 3. Queries en ejecución

```sql
SELECT 
  pid, 
  usename, 
  state, 
  query_start,
  EXTRACT(EPOCH FROM NOW() - query_start) as duration_secs,
  query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration_secs DESC
LIMIT 20;
```

### 4. Métricas de aplicación

```bash
# Error rate debe volver a baseline en <2 min
kubectl logs -l app=api -n production --since=5m | \
  grep -c "500"

# Latency p95
curl -s https://metrics.internal/api_latency_p95 | jq .
```

## Failover Manual (si automático falla)

**Solo si AWS no hace failover en >5 min:**

```bash
aws rds reboot-db-instance \
  --db-instance-identifier $DB_ID \
  --force-failover

# Monitorear
watch -n 10 'aws rds describe-db-instances --db-instance-identifier $DB_ID'
```

## Degradación Graceful

**Si DB está down >2 min:**

```bash
# Activar feature flag de degraded mode
kubectl set env deployment/api DEGRADED_MODE=true -n production

# Esto habilita:
# - Cache-only reads (donde aplica)
# - Cola de writes para replay post-recovery
# - Mensaje de mantenimiento en UI
```

## Recuperación

### Post-failover checklist

- [ ] Aplicación responde 200 OK en health checks
- [ ] Error rate < 0.1%
- [ ] Latency p95 < 500ms
- [ ] Replication lag < 1s
- [ ] No queries largas atascadas
- [ ] Backups funcionando
- [ ] Monitoring restaurado

### Restaurar operaciones normales

```bash
# Desactivar degraded mode
kubectl set env deployment/api DEGRADED_MODE=false -n production

# Si se activó circuit breaker, verificar reset
kubectl logs deployment/api -n production | grep "circuit.breaker" | tail
```

## Post-mortem

Obligatorio si:
- Downtime > 2 min
- Datos perdidos
- Failover manual requerido

Incluir:
- Causa raíz (hardware, network, config, etc.)
- Tiempo de detección
- Tiempo de failover
- Tiempo de recovery total
- Datos perdidos (si alguno)
- Mejoras a DR plan

## DR Drill Quarterly

Cada trimestre:
1. Programar ventana de mantenimiento
2. Notificar clientes (si M3)
3. Forzar failover manual
4. Medir tiempos
5. Documentar lecciones
6. Actualizar runbook
