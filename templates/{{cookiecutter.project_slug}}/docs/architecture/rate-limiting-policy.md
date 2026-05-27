# Rate Limiting Policy

**ADR:** ADR-0012-rate-limiting
**Versión:** 1.0

## 1. Estrategia: Token bucket por tenant + IP

## 2. Límites por tier

| Plan | Requests/min | Burst | Concurrent connections |
|------|:------------:|:-----:|:----------------------:|
| Free | 60 | 10 | 5 |
| Pro | 600 | 100 | 50 |
| Enterprise | 6000 | 1000 | Custom |

## 3. Límites por endpoint

| Endpoint | Límite específico | Razón |
|----------|:-----------------:|-------|
| POST /auth/login | 5/min por IP | Anti-brute-force |
| POST /billing/checkout | 10/min por tenant | Anti-fraud |
| GET /data/export | 2/hora por tenant | Costoso |
| Webhooks incoming | 1000/min global | Proteger de storms |

## 4. Headers de respuesta

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 600
X-RateLimit-Remaining: 594
X-RateLimit-Reset: 1716800000
```

## 5. Respuesta al exceder

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30
```

## 6. Implementación
- **Redis-based** token bucket
- **Middleware** en API gateway
- **Sliding window** para endpoints sensibles

## 7. Observabilidad
- `rate_limit_hits_by_tenant`
- `rate_limit_hits_by_endpoint`
- Alerta si un tenant excede > 10 veces/hora
