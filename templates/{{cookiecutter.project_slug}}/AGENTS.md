# AGENTS.md - Contrato de Comportamiento de Agentes

**Versión:** 1.0
**Scope:** Todo agente que opere en este repositorio

## 1. Identidad

Este repositorio sigue el **Plan Maestro V5** para desarrollo asistido por IA.
Todo agente (Claude Code, Cursor, Codex, Antigravity, etc.) debe adherirse a
estas reglas sin excepción.

## 2. Reglas universales

### 2.1 Separación de roles
- **No** investigar, diseñar, implementar, probar y aprobar tu propio trabajo.
- **No** modificar contracts sin ACR aprobado.
- **No** auto-aprobar cambios de alto riesgo.

### 2.2 Scope enforcement
- Opera **solo** dentro de los archivos permitidos por el micro-prompt.
- Si necesitas tocar otro archivo: **detente y genera ACR**.
- **No** amplíes scope sin aprobación.

### 2.3 Seguridad
- **Nunca** commitees secrets (API keys, tokens, passwords).
- **Nunca** loguees PII (emails, names, phones).
- **Nunca** envíes datos restricted a LLMs externos.
- **Siempre** pasa payloads por Sanitization Gateway.

### 2.4 Multi-tenancy
- **Toda** query de negocio debe filtrar por `tenant_id`.
- **Nunca** asumas tenant del contexto sin validar.
- **Toda** cache key debe incluir `tenant_id`.

### 2.5 Billing
- **Todo** campo financiero usa `DECIMAL/NUMERIC` o `BIGINT` (cents).
- **Nunca** `FLOAT` o `DOUBLE`.
- **Toda** transición de billing state machine requiere test.

### 2.6 Testing
- **Crea o actualiza** tests antes de declarar éxito.
- **Ejecuta** tests, lint y typecheck.
- **No** declares éxito si solo pasan tests triviales.
- **Mutation testing** cuando aplique (R2/R3).

## 3. Condiciones de parada obligatoria

Detente y reporta si encuentras:

- Cambio en billing, auth o multi-tenancy fuera de scope
- Migración destructiva
- Necesidad de modificar archivos prohibidos
- Test que contradice PRD
- Discrepancia entre contrato API y código
- Necesidad de tocar secrets
- Posible fuga cross-tenant
- Semantic drift < 0.85
- Blast radius excedido
- PII o secret detectado

## 4. Circuit Breaker

Si fallas **3 veces** sobre el mismo test o entras en loop:
1. Detente
2. Captura estado (comando, error, diff)
3. Revierte cambios experimentales
4. Solicita diagnóstico a Critic
5. Genera plan quirúrgico

## 5. Context Summary obligatorio

Al terminar cada micro-prompt, genera:

```markdown
# Context Summary - MP-___
- Invariantes evaluadas: [lista]
- Archivos modificados: [lista]
- Scope creep: [0% o lista]
- Tests ejecutados: [resultados]
- PII/secrets: [None o detalles]
- Egress: [whitelisted domains]
- Budget: [tokens/cost]
- Anomalies: [lista]
```

## 6. Comunicación

- **No** uses jerga ambigua.
- **Marca** toda inferencia como tal.
- **Cita** fuentes si usas knowledge layer.
- **Reporta** supuestos no validados.

## 7. Consecuencias del incumplimiento

- PR bloqueado por Enforcement Verifier
- Circuit Breaker activado
- Escalamiento a humano
- Registro en post-mortem si genera incidente

## 8. References

- Plan Maestro V5: `/docs/plan-maestro-v5.md`
- Invariantes: `/docs/architecture/invariants.md`
- Data classification: `/docs/architecture/data-classification.yaml`
- Threat model: `/docs/architecture/threat-model.md`
