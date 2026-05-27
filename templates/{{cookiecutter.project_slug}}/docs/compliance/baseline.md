# Compliance Baseline

**Versión:** 1.0
**Jurisdicción primaria:** [GDPR/CCPA/LFPDPPP/etc.]
**Owner:** @legal + @security

## 1. Jurisdicciones aplicables

| Jurisdicción | Aplica | Justificación |
|--------------|:------:|---------------|
| GDPR (EU) | ✅ | Usuarios en EU |
| CCPA/CPRA (California) | ✅ | >50k usuarios CA |
| LFPDPPP (México) | ✅ | Operaciones MX |
| LGPD (Brasil) | ❌ | Sin usuarios BR |
| SOC2 Type II | ✅ | Requisito enterprise |
| PCI-DSS | ⚠️ Parcial | Stripe procesa pagos |

## 2. Data retention

| Tipo de dato | Retención | Justificación |
|--------------|-----------|---------------|
| Account data | Mientras cuenta activa + 30d | Servicio |
| Billing data | 7 años | Fiscal |
| Audit logs | 2 años | SOC2 |
| Support tickets | 1 año post-close | Calidad |
| Marketing data | Hasta opt-out | Consentimiento |
| Backups | 30 días rotativo | DR |

## 3. Derechos del usuario/tenant

### 3.1 GDPR Art. 15-22
- **Access:** Export JSON de todos los datos
- **Rectification:** Editar desde UI
- **Erasure:** Hard delete tras 30d soft-delete
- **Portability:** Export vía API/CSV
- **Object:** Opt-out de marketing

### 3.2 Implementación
```python
# Job asíncrono
def process_data_deletion(tenant_id, user_id):
    # 1. Soft delete inmediato
    soft_delete_user(user_id)
    # 2. Quitar de backups (30 días)
    # 3. Hard delete tras período legal
    schedule_hard_delete(user_id, days=30)
    # 4. Notificar completado
```

## 4. Logs de auditoría

### 4.1 Campos obligatorios
```json
{
  "actor": "user_uuid",
  "tenant_id": "tenant_uuid",
  "timestamp": "ISO-8601",
  "action": "invoice.paid",
  "resource": "invoice:inv_123",
  "result": "success",
  "ip": "1.2.3.4",
  "user_agent": "..."
}
```

### 4.2 Retención: 2 años
### 4.3 Inmutabilidad: Append-only + hash chain

## 5. Consentimiento

### 5.1 Modelo
- **Opt-in** para marketing
- **Legitimate interest** para transactional
- **Contract** para servicio

### 5.2 Versionado
```json
{
  "user_id": "uuid",
  "consent_version": "2.1",
  "accepted_at": "ISO-8601",
  "scope": ["marketing", "analytics"]
}
```

### 5.3 Revocación
- UI de preferences
- API `DELETE /v1/consent`
- Propagación < 24h

## 6. Data Processing Agreements (DPA)
- Con Stripe: ✅
- Con AWS: ✅
- Con proveedores de email: ✅
- Con LLMs: ✅ (ver sanitization)

## 7. Incident response
Ver `incident-response-plan.md`.
- **Notificación GDPR:** 72h
- **Notificación CCPA:** Razonable

## 8. Review cadence
- **Anual:** Revisión completa
- **Triggers:** Nuevas leyes, expansiones geográficas, incidentes

## 9. Monitoring
- Regulatory Change Monitor (ver V5)
- Quarterly compliance audit
