# System Overview: [Producto]

**ADR:** ADR-0000-system-overview
**Versión:** 1.0
**Owner:** @tech-lead
**Última revisión:** 2026-05-27
**Maturity:** M1 / M2 / M3

## 1. Propósito del sistema
[1 párrafo: qué hace el sistema, para quién, en qué contexto]

## 2. Contexto de negocio
- **Tipo de producto:** SaaS B2B multi-tenant
- **Modelo de monetización:** Suscripción recurrente (monthly/annual)
- **Usuarios esperados año 1:** N tenants, M usuarios totales
- **Regiones iniciales:** us-east-1
- **Compliance objetivo:** SOC2 Type II, GDPR

## 3. Diagrama de alto nivel

```
                    ┌──────────────┐
                    │   Browser    │
                    └──────┬───────┘
                           │ HTTPS
                    ┌──────▼───────┐
                    │   CDN/WAF    │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │ Load Balancer│
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼─────┐     ┌────▼─────┐     ┌────▼─────┐
    │ API Pods │     │ API Pods │     │ Workers  │
    │ (N pods) │     │ (N pods) │     │ (M pods) │
    └────┬─────┘     └────┬─────┘     └────┬─────┘
         │                │                │
         └────────┬───────┴────────┬───────┘
                  │                │
          ┌───────▼───────┐  ┌────▼──────┐
          │  PostgreSQL   │  │   Redis   │
          │  (Primary +   │  │ (Cluster) │
          │   Read Rep.)  │  └───────────┘
          └───────────────┘
```

## 4. Componentes principales

| Componente | Responsabilidad | Stack | Escalabilidad |
|------------|----------------|-------|---------------|
| API Gateway | Routing, rate limiting, auth | FastAPI + Traefik | Horizontal |
| Billing Service | State machine, webhooks | Python worker | Horizontal |
| Tenant Service | CRUD tenants, users | FastAPI | Horizontal |
| Worker Queue | Async jobs, webhooks out | Celery + Redis | Horizontal |
| PostgreSQL | Datos transaccionales | Aurora/RDS | Vertical + Read replicas |
| Redis | Cache, locks, queue | ElastiCache | Cluster mode |
| Vault | Secrets, API keys | HashiCorp Vault | HA |

## 5. Flujos críticos

### 5.1 Request autenticada típica
```
Client → LB → API → AuthMiddleware → TenantMiddleware → Handler → DB
```

### 5.2 Webhook de billing entrante
```
Stripe → LB → /v1/webhooks/stripe → VerifySignature → IdempotencyCheck → StateMachine → DB → Emit Event
```

### 5.3 Job asíncrono
```
API → Enqueue (Redis) → Worker → Process → Emit Event → Notify (si aplica)
```

## 6. Decisiones arquitectónicas clave
- **ADR-0001:** Multi-tenancy con shared schema + RLS
- **ADR-0002:** Webhooks con tabla `processed_events` + UNIQUE constraint
- **ADR-0003:** Billing como state machine pura, nunca cálculos ad-hoc
- **ADR-0004:** AuthZ en middleware, nunca en handlers
- **ADR-0005:** API versionada vía URL path (`/v1/`, `/v2/`)

## 7. Boundaries y contextos
```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  Identity BC     │  │  Billing BC      │  │  Core Domain BC  │
│  - Auth          │  │  - Subscriptions │  │  - [Features]    │
│  - Users         │  │  - Invoices      │  │  - [Entities]    │
│  - Tenants       │  │  - Webhooks      │  │                  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

## 8. Restricciones y non-goals técnicos
- **No:** microservicios distribuidos en fase inicial (monolito modular)
- **No:** event sourcing completo (solo eventos de dominio críticos)
- **No:** multi-region hasta M3 con >$100k MRR
- **Sí:** module boundaries claros para futura extracción

## 9. Capacidades cross-cutting
- Logging estructurado (JSON, con sanitizer PII)
- Tracing distribuido (OpenTelemetry)
- Feature flags (LaunchDarkly / Unleash)
- Health checks (`/healthz`, `/readyz`)
- Métricas Prometheus

## 10. Riesgos arquitectónicos identificados

| Riesgo | Prob. | Impacto | Mitigación |
|--------|:-----:|:-------:|------------|
| Monolito crece demasiado | Media | Alto | Module boundaries + ADRs |
| DB bottleneck | Media | Alto | Read replicas + caching |
| Webhook storms | Baja | Alto | Rate limiting + backoff |

## 11. Evolución prevista
- **M1 → M2:** Añadir read replica, Redis cluster
- **M2 → M3:** Evaluar extracción de Billing Service como microservicio
- **Post-M3:** Multi-region, disaster recovery activo-activo
