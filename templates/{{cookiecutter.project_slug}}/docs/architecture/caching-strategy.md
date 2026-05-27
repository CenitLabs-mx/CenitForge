# Caching Strategy

**ADR:** ADR-0011-caching
**Versión:** 1.0

## 1. Principios

### 1.1 INV-011: Tenant isolation en cache
Toda cache key de negocio **debe** incluir `tenant_id`.

```python
# ❌ INCORRECTO
cache.get(f"user:{user_id}")

# ✅ CORRECTO
cache.get(f"tenant:{tenant_id}:user:{user_id}")
```

### 1.2 Cache invalidation
- **Write-through** para datos críticos (billing, authz)
- **TTL** para datos de lectura frecuente (config, catálogos)
- **Manual invalidation** vía pub/sub para cambios cross-pod

## 2. Tipos de cache

| Tipo | Tecnología | TTL | Uso |
|------|-----------|-----|-----|
| HTTP | CDN (CloudFront) | 1h | Assets estáticos |
| API response | Redis | 5 min | Endpoints de lectura |
| DB query | Redis | 1 min | Queries pesadas |
| Feature flags | In-memory | 30s | LaunchDarkly SDK |
| Session | Redis | 24h | JWTs, rate limits |

## 3. Cache keys convención

```
{tenant_id}:{resource}:{resource_id}:{version}

Ejemplos:
- t_abc:users:list:v2
- t_abc:plan:pro:v1
- t_abc:invoice:inv_123:v1
```

## 4. Stampede prevention
- **Probabilistic early expiration**
- **Mutex locks** con Redis SETNX
- **Fallback a stale data** con revalidación en background

## 5. Testing
- **Cache isolation tests:** Tenant A no puede leer cache de Tenant B
- **Invalidation tests:** Cambio en DB se refleja en cache
- **Performance tests:** Cache hit rate > 80% en hot paths

## 6. Observabilidad
Métricas expuestas:
- `cache_hit_rate`
- `cache_miss_rate`
- `cache_latency_p95`
- `cache_size_bytes`
