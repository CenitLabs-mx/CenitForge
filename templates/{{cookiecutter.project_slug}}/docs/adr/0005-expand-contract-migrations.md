# ADR-0005: Migraciones Zero-Downtime con Expand-and-Contract

**Estado:** Aceptada
**Fecha:** 2026-05-27
**Owner:** @db-lead
**Relacionado:** INV-017

## Contexto

Migraciones DDL en tablas grandes (>100k filas) pueden causar:
- Locks de tabla prolongados
- Downtime para usuarios
- Replication lag
- Timeouts en queries concurrentes

Operaciones especialmente peligrosas:
- `ALTER TABLE ... ALTER COLUMN TYPE`
- `ALTER TABLE ... RENAME COLUMN`
- `DROP COLUMN` con índices
- `ADD COLUMN ... NOT NULL` sin default

## Decisión

### Patrón Expand-and-Contract en 3 fases

#### Fase 1: EXPAND (migración N)
Agregar estructura compatible hacia adelante.

```sql
-- Ejemplo: cambiar columna de FLOAT a BIGINT cents
ALTER TABLE invoices ADD COLUMN total_cents BIGINT;

-- Crear trigger para dual-write
CREATE OR REPLACE FUNCTION sync_total_cents()
RETURNS TRIGGER AS $$
BEGIN
  NEW.total_cents := (NEW.total * 100)::BIGINT;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER invoices_total_cents_sync
  BEFORE INSERT OR UPDATE ON invoices
  FOR EACH ROW EXECUTE FUNCTION sync_total_cents();
```

**Deploy código:** aplicación escribe en AMBAS columnas.

#### Fase 2: BACKFILL (job asíncrono)
Rellenar datos históricos en batches.

```python
def backfill_total_cents():
    batch_size = 1000
    last_id = 0
    while True:
        rows = db.fetch_all("""
            UPDATE invoices 
            SET total_cents = (total * 100)::BIGINT
            WHERE id IN (
                SELECT id FROM invoices 
                WHERE id > ? AND total_cents IS NULL
                ORDER BY id LIMIT ?
            )
            RETURNING id
        """, (last_id, batch_size))
        
        if not rows:
            break
        last_id = rows[-1].id
        time.sleep(0.1)  # Evitar saturar DB
```

**Validación:** `SELECT COUNT(*) FROM invoices WHERE total_cents IS NULL` → debe ser 0.

#### Fase 3: MIGRATE READS (deploy código)
Cambiar aplicación para leer de columna nueva.

#### Fase 4: CONTRACT (migración N+1, días/semanas después)
Retirar estructura vieja cuando métricas confirman estabilidad.

```sql
-- Remover trigger
DROP TRIGGER invoices_total_cents_sync ON invoices;
DROP FUNCTION sync_total_cents();

-- Remover columna vieja
ALTER TABLE invoices DROP COLUMN total;

-- Renombrar si aplica
ALTER TABLE invoices RENAME COLUMN total_cents TO total;
```

## Consecuencias positivas

- **Zero downtime:** operaciones DDL seguras en tablas grandes
- **Rollback granular:** cada fase es reversible
- **Observabilidad:** métricas por fase

## Consecuencias negativas

- **Complejidad:** 1 migración se convierte en 3-4
- **Tiempo:** proceso completo toma días/semanas
- **Dual-write:** código temporal más complejo

## Reglas obligatorias (INV-017)

Toda migración en tabla con >100k filas DEBE:

1. Documentarse en ADR específico
2. Seguir patrón Expand-and-Contract
3. Tener backfill job idempotente
4. Validar 0 rows pendientes entre fases
5. Monitorear locks durante ejecución
6. Ejecutarse fuera de horario pico

## Herramientas

- **strong_migrations** (Ruby): detecta operaciones peligrosas
- **pgroll** (Go): automatiza expand-and-contract
- **squawk** (Python): linter de migraciones Postgres

## Alternativas consideradas

### pt-online-schema-change (MySQL)
No aplica: usamos PostgreSQL.

### pg_repack
Solo reorganiza, no cambia schema.

## Testing

- [ ] Dry-run en staging con volumen real
- [ ] Load test durante migración
- [ ] Rollback probado en cada fase
- [ ] Zero data loss verificado
