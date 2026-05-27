# ADR-0006: Convenciones del Data Model

**Estado:** Aceptada
**Fecha:** 2026-05-27
**Owner:** @db-lead

## Contexto

Sin convenciones explícitas, el modelo de datos diverge entre tablas
creadas por distintos developers o agentes. Esto genera:
- Inconsistencia en queries
- Bugs de multi-tenancy
- Problemas de performance
- Dificultad para auditar

## Decisión

### 1. Nomenclatura

| Elemento | Convención | Ejemplo |
|----------|-----------|---------|
| Tablas | `snake_case` plural | `users`, `invoices` |
| Columnas | `snake_case` | `created_at`, `tenant_id` |
| PKs | `id UUID` | `id UUID PRIMARY KEY` |
| FKs | `{entity_singular}_id` | `tenant_id`, `user_id` |
| Índices | `idx_{table}_{columns}` | `idx_users_tenant_email` |
| Constraints | `{table}_{type}_{cols}` | `users_unique_email` |

### 2. Primary Keys

```sql
-- Siempre UUID v4
id UUID PRIMARY KEY DEFAULT uuid_generate_v4()

-- Nunca:
-- - SERIAL (predecible, sequential)
-- - BIGINT auto (predecible)
-- - Natural keys (emails, usernames)
```

**Justificación:** UUIDs evitan enumeration attacks y facilitan sharding futuro.

### 3. Campos de auditoría obligatorios

```sql
-- En toda tabla de negocio:
created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
created_by UUID REFERENCES users(id),
updated_by UUID REFERENCES users(id),
tenant_id UUID NOT NULL REFERENCES tenants(id)  -- salvo tablas globales
```

### 4. Soft delete vs hard delete

| Caso | Estrategia |
|------|-----------|
| Usuarios | Soft delete (`deleted_at`) |
| Datos financieros | **Prohibido hard delete** |
| Logs de auditoría | Nunca se borra |
| Sesiones | Hard delete |
| Cache | Hard delete |

### 5. Tipos de datos financieros

```sql
-- ✅ CORRECTO
amount_cents BIGINT              -- para valores enteros en cents
amount NUMERIC(20, 4)            -- para cálculos con decimales
rate NUMERIC(10, 6)              -- para tasas de cambio/interés

-- ❌ PROHIBIDO
FLOAT, DOUBLE PRECISION, REAL    -- pérdida de precisión
```

### 6. Índices

#### Automáticos
- Toda PK
- Toda FK
- Toda columna usada en WHERE frecuente
- Toda combinación `(tenant_id, ...)` usada en queries

#### Naming
```sql
CREATE INDEX idx_invoices_tenant_status ON invoices(tenant_id, status);
CREATE UNIQUE INDEX users_unique_email_tenant ON users(tenant_id, email);
```

#### Tipos especiales
```sql
-- JSONB con búsqueda frecuente
CREATE INDEX idx_metadata_search ON events USING GIN (metadata jsonb_path_ops);

-- Full-text search
CREATE INDEX idx_notes_search ON notes USING GIN (to_tsvector('english', content));
```

### 7. Tablas globales (sin tenant_id)

Solo con justificación en ADR:
- `tenants`
- `plans`
- `regions`
- `currencies`
- `system_config`

### 8. Comentarios

```sql
COMMENT ON TABLE invoices IS 'Facturas emitidas a tenants';
COMMENT ON COLUMN invoices.amount_cents IS 'Monto en cents (USD)';
```

## Consecuencias positivas

- **Consistencia:** queries predecibles
- **Seguridad:** tenant_id obligatorio
- **Performance:** índices adecuados
- **Auditabilidad:** trazabilidad completa

## Consecuencias negativas

- **Overhead:** UUIDs son más grandes que integers
- **Rigidez:** algunos casos edge requieren excepciones (vía ADR)

## Linting

CI valida:
- [ ] Toda tabla de negocio tiene `tenant_id`
- [ ] Toda FK tiene índice
- [ ] Campos financieros no usan FLOAT
- [ ] PKs son UUID
- [ ] Nombres siguen convención
