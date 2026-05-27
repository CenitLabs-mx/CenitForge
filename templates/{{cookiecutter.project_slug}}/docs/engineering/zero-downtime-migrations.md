# Zero-Downtime Migrations

**ADR:** ADR-0008-expand-contract
**Versión:** 1.0

## 1. Patrón: Expand-and-Contract

Obligatorio para tablas con >100k filas o alto tráfico (INV-017).

## 2. Fases

### Fase 1: EXPAND
```sql
ALTER TABLE invoices ADD COLUMN total_cents BIGINT;
-- Código escribe en total (NUMERIC) Y total_cents (BIGINT)
-- Backfill asíncrono de datos existentes
UPDATE invoices SET total_cents = (total * 100)::BIGINT WHERE total_cents IS NULL;
```

### Fase 2: MIGRATE
```sql
-- Validar que todos los registros tienen total_cents
SELECT COUNT(*) FROM invoices WHERE total_cents IS NULL;
-- Debe ser 0 antes de continuar
-- Código lee de total_cents
```

### Fase 3: CONTRACT
```sql
-- Eliminar código que escribe en columna vieja
-- Drop columna vieja (con backup previo)
ALTER TABLE invoices DROP COLUMN total;
```

## 3. Checklist por migración

- [ ] ADR documentado
- [ ] Fases 1, 2, 3 implementadas como migraciones separadas
- [ ] Backfill job idempotente
- [ ] Validación entre fases (0 rows pendientes)
- [ ] Rollback plan por fase
- [ ] Monitoreo de locks durante ejecución
- [ ] Comunicación a stakeholders (si aplica)

## 4. Anti-patrones

### ❌ NO hacer
```sql
-- Bloquea la tabla por minutos en tablas grandes
ALTER TABLE big_table ALTER COLUMN status TYPE VARCHAR(50);
```

### ✅ SÍ hacer
```sql
-- 1. Crear columna nueva
ALTER TABLE big_table ADD COLUMN status_new VARCHAR(50);
-- 2. Dual-write desde código
-- 3. Backfill en batches
-- 4. Cambiar reads a columna nueva
-- 5. Drop columna vieja
```

## 5. Tools
- **pg_repack:** Para reorganizar tablas sin locks largos
- **pg_online_schema_change:** Inspirado en pt-osc de MySQL
- **Strong migrations (gem):** Detecta operaciones peligrosas

## 6. Monitoring
- Lock wait time
- Replication lag durante migración
- Query latency pre/post
