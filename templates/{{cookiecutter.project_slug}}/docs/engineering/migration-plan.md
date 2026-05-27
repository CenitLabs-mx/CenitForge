# Migration Plan

**Versión:** 1.0
**Herramienta:** Alembic (Python) / golang-migrate (Go)

## 1. Convenciones

### 1.1 Nomenclatura
```
YYYYMMDD_HHMMSS_descripcion_corta.sql
```

### 1.2 Estructura
```
migrations/
  20260527_100000_create_tenants_table.sql
  20260527_100100_create_users_table.sql
  20260527_100200_add_rls_policies.sql
```

## 2. Políticas

### 2.1 Toda migración debe tener
- **Up function** (aplicar)
- **Down function** (rollback)
- **Idempotencia** (puede ejecutarse 2 veces sin error)

### 2.2 Orden de ejecución
1. Migrations se aplican en staging primero
2. Dry-run automático en CI
3. Aprobación humana para producción
4. Rollback plan documentado

### 2.3 Locks y tiempos
- **Timeout lock:** 5s por tabla
- **Max downtime:** 0 (ver zero-downtime-migrations)
- **Horario:** Fuera de business hours del cliente más grande

## 3. Tipos de migraciones

### 3.1 Non-destructive (auto-aprobadas)
- Crear tabla nueva
- Añadir columna nullable
- Crear índice concurrente

### 3.2 Destructive (requieren ADR)
- Drop column
- Rename column
- Cambiar tipo de dato
- Drop table

### 3.3 Alto volumen (Expand-and-Contract)
Ver `zero-downtime-migrations.md`.

## 4. Testing
- **Dry-run en CI:** Aplica y revierte en DB temporal
- **Data integrity tests:** Post-migración validación
- **Rollback test:** Quarterly en staging

## 5. Monitoring
- Duración de migraciones
- Lock contention
- Errores post-migración
