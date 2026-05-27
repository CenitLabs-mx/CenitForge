# Environments

**Versión:** 1.0
**Infraestructura:** AWS / GCP / Azure (según stack)

## 1. Matriz de environments

| Env | Propósito | Datos | Secrets | Uptime SLO |
|-----|-----------|-------|---------|:----------:|
| **Local** | Desarrollo | Fixtures | `.env` efímero | N/A |
| **CI** | Validación PR | Synthetic | CI vault | N/A |
| **Staging** | Pre-prod | Synthetic realista | Staging vault | 99% |
| **Production** | Clientes | Reales | Prod vault auditado | 99.9% |

## 2. Local

### 2.1 Setup
```bash
cp .env.example .env
docker-compose up -d  # DB, Redis, etc.
npm run seed:fixtures
```

### 2.2 Reglas
- **Nunca** conectar a staging/prod desde local
- Secrets en `.env` (no commiteado)
- DB aislada en Docker

## 3. CI

### 3.1 Características
- DB efímera por job
- Synthetic data generada
- Sin egress a producción
- Tests paralelos

### 3.2 Secrets
- Vault de CI (GitHub Secrets, etc.)
- Rotación automática
- Sin secretos de producción

## 4. Staging

### 4.1 Datos
- Synthetic realista (mismo volumen que prod /100)
- Sin PII real
- Seed scripts versionados

### 4.2 Parity con producción
- Mismo stack y versiones
- Mismas config (excepto scale)
- Mismos feature flags

### 4.3 Acceso
- Devs con MFA
- Audit log
- Sin acceso a prod data

## 5. Production

### 5.1 Acceso restringido
- Solo on-call con break-glass
- MFA + hardware key
- Audit log inmutable
- Session recording

### 5.2 Cambios
- Solo vía CI/CD
- Approval gate
- Rollback automático si error rate > umbral

## 6. Data flow entre environments

```
prod (real) ──X──▶ staging
staging (synth) ──X──▶ local
local (fixtures)
```

**Regla INV-015:** Nunca copiar datos reales a env no productivo sin anonimizar.

## 7. Disaster recovery
- **Backups:** Continuous (PITR)
- **Restore tests:** Quarterly
- **RPO:** 5 min
- **RTO:** 1 hora
