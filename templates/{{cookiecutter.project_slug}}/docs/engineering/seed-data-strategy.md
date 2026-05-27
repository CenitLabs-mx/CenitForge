# Seed Data Strategy

**Versión:** 1.0

## 1. Objetivos
- Datos consistentes para testing
- Datos realistas para staging
- **Nunca** PII real en env no productivo (INV-015)

## 2. Tipos de seed

### 2.1 Fixtures (local)
- Conjunto mínimo para desarrollo
- Datos deterministas (seeded random)
- ~10 tenants, ~50 users

### 2.2 Synthetic (CI/staging)
- Generado por scripts
- Mismo schema que prod
- Volumen escalable

### 2.3 Production-like (solo staging, anonimizado)
- Dump de producción **anonimizado**
- PII reemplazada con faker
- Estructura preservada

## 3. Generación

### 3.1 Tools
- **Python:** Faker + factory_boy
- **JS:** Faker.js
- **SQL:** pg_generate_series + random()

### 3.2 Ejemplo Python
```python
from faker import Faker
fake = Faker()
Faker.seed(42)  # Determinista

def create_test_tenant():
    return Tenant(
        id=uuid4(),
        name=fake.company(),
        slug=fake.slug(),
    )
```

## 4. Consistencia
- **Seed fijo** para datos deterministas
- **Scripts versionados** en repo
- **Idempotentes** (pueden correrse N veces)

## 5. Seguridad
- **Nunca** dump crudo de prod a staging
- **Anonimización** obligatoria:
  - Emails → faker email
  - Names → faker name
  - IDs financieros → random
  - API keys → regeneradas

## 6. Maintenance
- Scripts revisados quarterly
- Nuevos campos → actualizar seed
- Nuevos tenants test → agregar fixtures
