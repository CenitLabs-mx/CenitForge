# ADR-0010: Estrategia de Caching con Tenant Isolation

**Estado:** Aceptada
**Fecha:** 2026-05-27
**Owner:** @platform-lead
**Relacionado:** INV-011

## Contexto

Cache mal implementado en SaaS multi-tenant puede causar:
- Fuga de datos entre tenants (cache poisoning)
- Stale data en operaciones críticas
- Inconsistencias post-write

## Decisión

### 1. Tenant prefix obligatorio (INV-011)

```python
# ❌ INCORRECTO
cache.get(f"user:{user_id}")

# ✅ CORRECTO
cache.get(f"tenant:{tenant_id}:user:{user_id}")
```

### 2. Wrapper obligatorio

```python
class TenantCache:
    def __init__(self, redis_client, tenant_id: str):
        self.redis = redis_client
        self.tenant_id = tenant_id
        self.prefix = f"tenant:{tenant_id}"
    
    def get(self, key: str):
        return self.redis.get(f"{self.prefix}:{key}")
    
    def set(self, key: str, value, ttl: int = None):
        full_key = f"{self.prefix}:{key}"
        if ttl:
            return self.redis.setex(full_key, ttl, value)
        return self.redis.set(full_key, value)
    
    def delete(self, key: str):
        return self.redis.delete(f"{self.prefix}:{key}")
    
    def invalidate_pattern(self, pattern: str):
        """Invalida todas las keys que match el patrón dentro del tenant."""
        full_pattern = f"{self.prefix}:{pattern}"
        keys = self.redis.keys(full_pattern)
        if keys:
            self.redis.delete(*keys)
```

### 3. Inyección en requests

```python
@app.middleware("http")
async def inject_tenant_cache(request, call_next):
    request.cache = TenantCache(redis, request.tenant_id)
    return await call_next(request)
```

### 4. Niveles de cache

| Tipo | TTL | Invalidation | Uso |
|------|-----|--------------|-----|
| HTTP (CDN) | 1h | Purge manual | Assets |
| API response | 5 min | Event-driven | Lectura frecuente |
| DB query | 1 min | Write-through | Queries pesadas |
| Feature flags | 30s | Polling | Config |
| Session | 24h | Logout | Auth state |

### 5. Invalidation strategies

#### Write-through
Para datos críticos (billing, auth):
```python
def update_user(user_id, data):
    db.update("users", user_id, data)
    cache.delete(f"user:{user_id}")
```

#### Event-driven
Para datos compartidos:
```python
@consumer(topic="events.user.updated")
async def invalidate_user_cache(event):
    cache = TenantCache(redis, event["tenant_id"])
    cache.invalidate_pattern(f"user:{event['user_id']}*")
```

### 6. Stampede prevention

```python
import asyncio

class SingleFlightCache:
    """Evita que múltiples requests regeneren la misma key."""
    
    _inflight = {}
    
    async def get_or_set(self, key: str, factory, ttl: int):
        cached = await self.cache.get(key)
        if cached is not None:
            return cached
        
        # Single flight: solo 1 regenera
        if key not in self._inflight:
            self._inflight[key] = asyncio.Event()
            try:
                value = await factory()
                await self.cache.set(key, value, ttl)
                return value
            finally:
                self._inflight.pop(key).set()
        else:
            # Esperar a que el otro termine
            await self._inflight[key].wait()
            return await self.cache.get(key)
```

## Consecuencias positivas

- **Aislamiento garantizado** por wrapper
- **Performance:** hit rate >80% esperado
- **Consistencia:** invalidation automática

## Testing obligatorio

- [ ] Tenant A no lee cache de Tenant B
- [ ] Invalidation propaga correctamente
- [ ] Stampede prevention funciona
- [ ] TTL respeta límites

## Linter CI

Detecta uso directo de `redis.get` sin wrapper:
```python
FORBIDDEN = re.compile(r"\bredis\.(get|set|hget|hset)\(")
# Debe usar request.cache.* en su lugar
```
