# API Versioning Strategy

**ADR:** ADR-0009-api-versioning
**Versión:** 1.0

## 1. Estrategia elegida: URL path-based

```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

## 2. Justificación
| Alternativa | Razón de descarte |
|-------------|-------------------|
| Header-based (`Accept: v1`) | Menos descubrible, dificulta testing |
| Query param (`?version=2`) | Rompe REST semántico |
| Host-based (`v1.api.example.com`) | Overhead de DNS y certificados |

## 3. Reglas de breaking vs non-breaking

### 3.1 Non-breaking (no requiere nueva versión)
- Añadir nuevo campo en response
- Añadir nuevo endpoint
- Añadir nuevo valor a ENUM (si cliente usa `default`)
- Relajar validaciones
- Añadir query params opcionales

### 3.2 Breaking (requiere nueva versión)
- Eliminar o renombrar campo
- Cambiar tipo de campo
- Endurecer validaciones
- Cambiar semántica de endpoint
- Cambiar códigos HTTP de error
- Eliminar valor de ENUM

## 4. Ciclo de vida
Ver `api-deprecation-policy.md` para detalles de sunset.

## 5. Testing de backward compatibility
- **CI check:** OpenAPI diff entre PR y main
- **Contract tests:** Validan que cambios son backward-compatible
- **Tool:** `oasdiff` o `openapi-diff`

## 6. Comunicación
- Changelog público en `https://docs.example.com/changelog`
- Email a usuarios con uso de versiones a deprecar
- Dashboard de uso por versión
