# RUN-003: Secreto Comprometido

**Severidad:** P0
**Owner:** @security-oncall
**Última prueba:** 2026-05-10
**Tiempo estimado:** 30-60 min

## Síntomas

- Alerta de GitGuardian/Gitleaks
- Uso anómalo de API key (Stripe, AWS, etc.)
- Reporte externo de secreto en pastebin/GitHub público
- Actividad inusual en logs del proveedor

## Respuesta Inmediata (10 min)

### 1. Identificar el secreto

```bash
# Si es alerta de scanner
cat /tmp/secret-alert.json | jq '.secret_type, .location, .commit'

# Determinar:
# - Tipo: API key, DB password, JWT secret, etc.
# - Proveedor: Stripe, AWS, DB, etc.
# - Exposición: commit, log, chat, etc.
# - Tiempo de exposición
```

### 2. Rotar el secreto INMEDIATAMENTE

**Stripe API key:**
```bash
# Stripe Dashboard → Developers → API keys → Roll key
# Actualizar vault:
vault write secret/stripe/api_key value=sk_live_NEW_KEY

# Restart pods
kubectl rollout restart deployment/api -n production
kubectl rollout restart deployment/billing -n production
```

**AWS access key:**
```bash
aws iam create-access-key --user-name $USER
aws iam delete-access-key --user-name $USER --access-key-id $OLD_KEY

# Actualizar en vault/secrets manager
```

**Database password:**
```bash
# RDS: Modify → Change password
# O vía terraform
terraform apply -target=aws_db_instance.main

# Actualizar vault
vault write secret/db/password value=$NEW_PASSWORD

# Restart connections
kubectl rollout restart deployment/api -n production
```

**JWT secret:**
```bash
# Generar nuevo
NEW_SECRET=$(openssl rand -hex 64)

# Actualizar vault
vault write secret/jwt/secret value=$NEW_SECRET

# Invalidate todas las sessions activas
python tools/admin/invalidate_all_sessions.py --reason "secret rotation INC-XXX"

# Restart
kubectl rollout restart deployment/api -n production
```

### 3. Eliminar de historia (si fue commit)

```bash
# BFG Repo-Cleaner (más rápido que filter-branch)
bfg --replace-text passwords.txt repo.git
cd repo.git && git reflog expire --expire=now --all && git gc --prune=now --aggressive

# Force push (coordinar con equipo)
git push --force --all
git push --force --tags

# Alertar a GitHub Support si fue público
# https://support.github.com/contact?tags[]=exposed-credentials
```

### 4. Evaluar impacto

**Preguntas:**
- ¿Cuánto tiempo estuvo expuesto?
- ¿Hubo uso no autorizado? (revisar logs del proveedor)
- ¿Qué datos/sistemas pudieron ser accedidos?

**Stripe:**
```bash
# Dashboard → Developers → Logs → filtrar por key
# Buscar activity inusual
```

**AWS:**
```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=$EXPOSED_KEY \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ)
```

## Contención

### Si hay evidencia de compromiso

1. **Aislar recursos afectados**
2. **Forzar logout de sessions**
3. **Habilitar MFA en cuentas relacionadas**
4. **Notificar a clientes si hubo acceso a sus datos**

### Si solo fue exposición (sin uso)

1. Rotación es suficiente
2. Monitorear por 72h
3. Post-mortem

## Prevención

- [ ] Pre-commit hook con gitleaks
- [ ] CI scan con Trufflehog
- [ ] GitHub secret scanning habilitado
- [ ] Vault para todos los secretos
- [ ] Rotación automática (90 días para API keys)
- [ ] Training anual para developers

## Comunicación

- **Security team:** inmediato
- **CTO:** <30 min si P0
- **Clientes:** solo si hubo acceso a datos
- **Autoridades:** si GDPR aplica y hubo acceso a PII

## Post-mortem obligatorio

Incluir:
- Cómo se expuso el secreto
- Tiempo de exposición
- Uso no autorizado (sí/no)
- Tiempo de detección
- Tiempo de rotación
- Acciones preventivas
