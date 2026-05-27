# Support Insights - Aprendizajes de Soporte

**Versión:** 1.0
**Última actualización:** 2026-05-27
**Fuente:** Tickets de soporte, chat, emails
**Knowledge Quarantine:** source_type=user_feedback, decay=180d

## 1. Propósito

Patrones extraídos de interacciones con clientes. Alimenta:
- ✅ Market scoring
- ✅ PRD generation
- ✅ Opportunity scorecard
- ✅ Threat model
- ✅ Feature prioritization

## 2. Categorías de tickets

| Categoría | % del total | Tendencia |
|-----------|:-----------:|:---------:|
| Onboarding | 22% | ⬇️ bajando |
| Feature request | 28% | ⬆️ subiendo |
| Bug report | 15% | ➡️ estable |
| Billing question | 12% | ➡️ estable |
| How-to | 18% | ⬇️ bajando |
| Account issues | 5% | ➡️ estable |

## 3. Insights clave

### INS-001: Onboarding friction en setup de integraciones

**Frecuencia:** 45 tickets/mes  
**CSAT impact:** -0.8 puntos  
**Tiempo medio resolución:** 25 min

**Frase recurrente:**
> "No entiendo cómo conectar con X"

**Root causes:**
1. Documentación asume conocimiento técnico
2. No hay wizard guiado
3. Errores poco descriptivos

**Acciones tomadas:**
- ✅ Wizard paso-a-paso (Q2 2026)
- ✅ Video tutorial (Q2 2026)
- ⏳ Error messages mejorados (Q3 2026)

**Feature requests relacionados:** FR-042, FR-058

---

### INS-002: Confusión sobre pricing tiers

**Frecuencia:** 30 tickets/mes  
**CSAT impact:** -0.5 puntos

**Frase recurrente:**
> "No sé qué plan necesito"

**Root causes:**
1. Feature comparison no es clara
2. No hay calculator
3. Trial muy corto para evaluar

**Acciones:**
- ✅ Pricing page redesign (Q1 2026)
- ⏳ ROI calculator (Q3 2026)
- ⏳ Trial extension a 30 días (evaluando)

---

### INS-003: Export de datos complejo

**Frecuencia:** 18 tickets/mes  
**CSAT impact:** -0.3 puntos

**Frase recurrente:**
> "Solo quiero bajar mis datos en CSV"

**Acciones:**
- ✅ One-click CSV export (Q2 2026)
- ✅ Scheduled exports (Q3 2026)

---

### INS-004: API documentation insuficiente

**Frecuencia:** 25 tickets/mes  
**Segmento:** Developers en plan Pro/Enterprise

**Frase recurrente:**
> "Faltan ejemplos de código"

**Acciones:**
- ✅ OpenAPI spec público (Q1 2026)
- ✅ SDKs oficiales Python/JS (Q2 2026)
- ⏳ Postman collection (Q3 2026)

---

### INS-005: Multi-user permissions confusas

**Frecuencia:** 22 tickets/mes  
**Segmento:** Admins de tenant

**Frase recurrente:**
> "No sé qué puede hacer cada rol"

**Acciones:**
- ✅ Permission matrix visible en UI (Q2 2026)
- ⏳ Role templates predefinidos (Q3 2026)

---

## 4. Feature requests más solicitados

| Rank | Feature | Menciones (90d) | Segmento |
|------|---------|:---------------:|----------|
| 1 | Integración con Slack | 87 | Todos |
| 2 | API webhooks | 65 | Pro/Enterprise |
| 3 | Mobile app | 54 | Todos |
| 4 | SSO SAML | 48 | Enterprise |
| 5 | Custom branding | 42 | Enterprise |

## 5. Pain points por segmento

### SMB (1-50 users)
- Precio percibido alto
- Setup requiere dev
- Prefieren plantillas

### Mid-market (50-500 users)
- Reporting insuficiente
- Roles muy básicos
- Integraciones limitadas

### Enterprise (500+ users)
- SSO SAML/SCIM
- SLAs contractuales
- Compliance (SOC2, HIPAA)
- Dedicated support

## 6. CSAT trends

| Trimestre | CSAT | NPS | Top detractor |
|-----------|:----:|:---:|---------------|
| 2025-Q4 | 4.2 | 35 | Onboarding |
| 2026-Q1 | 4.3 | 38 | Pricing clarity |
| 2026-Q2 (parcial) | 4.4 | 41 | API docs |

## 7. Knowledge destillation

Cada insight se destila en:
- **Feature request** → PRD generation feed
- **Bug pattern** → bug-patterns.md
- **Confusion point** → Docs improvement
- **Process gap** → Runbook o automation

## 8. Review cadence
- **Semanal:** Support lead revisa top 5 temas
- **Mensual:** PM + Support consolidan insights
- **Quarterly:** Revisión estratégica con leadership
