# Threat Model: [Producto]

**Framework:** STRIDE + PASTA
**Versión:** 1.0
**Última revisión:** 2026-05-27
**Owner:** @security-lead

## 1. Alcance
- Aplicación web multi-tenant
- API REST
- Integración con Stripe (billing)
- LLMs externos (sanitizados)

## 2. Activos críticos

| Activo | Clasificación | Impacto de compromiso |
|--------|---------------|----------------------|
| Datos de tenants | Confidencial | Alto (legal + reputación) |
| API keys / secrets | Restringido | Crítico |
| Billing state | Confidencial | Crítico (financiero) |
| PII (email, name) | Confidencial | Alto (GDPR) |
| Webhook secrets | Restringido | Alto |
| Logs | Interno | Medio |

## 3. Matriz de amenazas

### 3.1 Spoofing
| Amenaza | Prob. | Impacto | Control |
|---------|:-----:|:-------:|---------|
| Credential stuffing | Media | Alto | Auth throttling + MFA opcional |
| JWT forgery | Baja | Crítico | Librería validada + rotación |

### 3.2 Tampering
| Amenaza | Prob. | Impacto | Control |
|---------|:-----:|:-------:|---------|
| Cross-tenant write | Media | Crítico | RLS + middleware (INV-005) |
| Webhook replay | Media | Alto | Unique event_id (INV-004) |

### 3.3 Repudiation
| Amenaza | Control |
|---------|---------|
| Usuario niega acción | Audit log inmutable |
| Admin niega cambio | ADR + approval workflow |

### 3.4 Information disclosure
| Amenaza | Prob. | Impacto | Control |
|---------|:-----:|:-------:|---------|
| Cross-tenant read | Media | Alto | RLS + tests |
| PII en logs | Media | Alto | Log sanitizer (INV-012) |
| Secret leakage | Baja | Crítico | Vault + pre-commit scan |

### 3.5 Denial of Service
| Amenaza | Control |
|---------|---------|
| API abuse | Rate limiting por tenant/IP |
| DDoS | CDN/WAF + autoscaling |
| Noisy neighbor | Resource isolation (M2+) |

### 3.6 Elevation of privilege
| Amenaza | Control |
|---------|---------|
| Self-promotion | Solo owner puede promover |
| API key escalation | Scopes granulares |

## 4. Amenazas específicas de IA

| Amenaza | Control |
|---------|---------|
| Prompt injection | Separación data/instructions + sanitization |
| Data exfiltration a LLM | Sanitization Gateway |
| Model hallucination | Critic review + verification |
| Agent scope creep | Blast radius gate |

## 5. Data flow diagram
```
[Browser] ──HTTPS──▶ [CDN/WAF] ──▶ [LB] ──▶ [API]
                                           │
                                    ┌──────┴──────┐
                                    ▼             ▼
                                [PostgreSQL]   [Redis]
                                    │
                                    ▼
                              [Vault (secrets)]
```

## 6. Mitigaciones priorizadas

| Prioridad | Mitigación | Owner | Deadline |
|-----------|-----------|-------|----------|
| P0 | RLS en todas las tablas | @dev | 2026-06-15 |
| P0 | Sanitization Gateway | @devops | 2026-06-20 |
| P1 | Webhook signature verification | @dev | 2026-06-25 |
| P1 | Secret scanning en CI | @devops | 2026-06-15 |

## 7. Threat model review cadence
- **Quarterly:** Revisión completa
- **Triggers:** Incidente P1/P2, nuevo feature crítico, cambio de proveedor

## 8. Relación con incidentes
Todo incidente de seguridad actualiza este documento (ver Learning Loop).
