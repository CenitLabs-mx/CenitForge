# ADR-0001: Multi-Tenancy con Shared Schema + RLS

**Estado:** Aceptada  
**Fecha:** 2026-05-27  
**Owner:** @tech-lead

## Contexto

Estamos construyendo un SaaS B2B multi-tenant. Necesitamos decidir la
estrategia de aislamiento de datos entre tres opciones principales:
1. Database-per-tenant
2. Schema-per-tenant
3. Shared schema + Row Level Security (RLS)

**Factores:**
- Objetivo: 100-1000 tenants en primeros 12 meses
- Equipo: 3-5 engineers
- Budget: Inicial limitado
- Compliance: GDPR, SOC2 Type II

## Decisión

**Shared schema + PostgreSQL RLS** con las siguientes reglas:

1. Toda tabla de negocio incluye `tenant_id UUID NOT NULL`
2. RLS habilitado con policy basada en `current_setting('app.current_tenant_id')`
3. Middleware de aplicación setea variable de sesión al inicio del request
4. Queries raw (no ORM) deben incluir `WHERE tenant_id = ?` explícitamente
5. Linter CI detecta queries sin filtro

## Consecuencias positivas

- **Costo:** Económico (1 DB compartida)
- **Operación:** Simple (1 schema a migrar)
- **Backup:** 1 backup cubre todos los tenants
- **Performance:** Queries comparten plan cache

## Consecuencias negativas

- **Riesgo:** Bug en middleware = fuga cross-tenant
- **Mitigación:** Tenant isolation tests obligatorios + RLS como segunda capa
- **Complejidad:** Requiere disciplina en queries raw
- **Reporting cross-tenant:** Requiere service account especial

## Alternativas consideradas

### Database-per-tenant
**Rechazada porque:**
- Costo prohibitivo (100 tenants = 100 DBs)
- Operación compleja (100 migraciones paralelas)
- Overhead de conexiones

### Schema-per-tenant
**Rechazada porque:**
- Migraciones en paralelo complicadas
- Backup/restore más complejo
- No justificado para nuestro volumen

## Impacto en seguridad

- **Mitiga:** Fugas cross-tenant (doble capa: middleware + RLS)
- **Requiere:** Testing riguroso de aislamiento
- **Invariantes:** INV-001, INV-005

## Impacto en multi-tenancy

- **Modelo:** Shared schema + RLS
- **Isolation level:** Strong (PostgreSQL RLS)
- **Performance:** Bueno con índices por tenant_id

## Impacto en billing

- Cada tenant tiene su subscription aislada
- Webhooks mapean a tenant vía customer_id
- Stripe metadata incluye `tenant_id`

## Tests requeridos

- [ ] Tenant A no lee datos de Tenant B
- [ ] Tenant A no escribe datos de Tenant B
- [ ] Admin de A no administra B
- [ ] Background jobs respetan tenant scope
- [ ] Webhooks no activan tenant incorrecto
- [ ] Queries sin tenant_id fallan o se rechazan
- [ ] Exportaciones no mezclan tenants
- [ ] Logs no exponen datos de otro tenant

## Revisión

- **Próxima review:** 2027-05-27 o al alcanzar 500 tenants
- **Trigger de cambio:** Si >1000 tenants, evaluar sharding
