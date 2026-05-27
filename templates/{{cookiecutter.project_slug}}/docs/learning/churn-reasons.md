# Churn Reasons - Análisis de Cancelaciones

**Versión:** 1.0
**Última actualización:** 2026-05-27
**Fuente:** Exit surveys, interviews, usage data
**Knowledge Quarantine:** source_type=user_feedback, decay=180d

## 1. Propósito

Entender por qué los clientes cancelan para:
- Reducir churn
- Mejorar product-market fit
- Priorizar features anti-churn
- Detectar señales tempranas

Alimenta:
- ✅ Market scoring
- ✅ PRD generation
- ✅ Threat model (business risk)
- ✅ Retention strategies

## 2. Métricas de churn

| Métrica | Últimos 30d | Últimos 90d | YoY |
|---------|:-----------:|:-----------:|:---:|
| Churn rate mensual | 3.2% | 3.5% | -0.8pp ✅ |
| Churn rate anual | 32% | 34% | -6pp ✅ |
| Net revenue retention | 108% | 105% | +5pp ✅ |
| Tiempo medio permanencia | 14 meses | 13 meses | +1m |

## 3. Churn por segmento

| Segmento | Churn mensual | Causa principal |
|----------|:-------------:|-----------------|
| SMB | 4.8% | Precio |
| Mid-market | 2.1% | Feature gaps |
| Enterprise | 0.8% | Cambio estratégico |

## 4. Razones de churn (categorizadas)

### 4.1 Producto (45% del churn)

#### CR-001: Feature faltante crítica
- **% del churn:** 18%
- **Features más pedidas antes de cancelar:**
  1. Integración con Salesforce (32 menciones)
  2. SSO SAML (28 menciones)
  3. Reporting avanzado (24 menciones)
- **Acción:** Feature prioritizada en roadmap Q3

#### CR-002: UX confusa
- **% del churn:** 12%
- **Flujos problemáticos:**
  1. Configuración inicial
  2. Gestión de usuarios
  3. Setup de integraciones
- **Acción:** UX redesign Q2

#### CR-003: Performance inadecuada
- **% del churn:** 8%
- **Síntomas:**
  - Latencia > 2s en dashboards
  - Timeouts en exports
- **Acción:** Performance optimization Q2-Q3

#### CR-004: Bugs recurrentes
- **% del churn:** 7%
- **Dominios más problemáticos:**
  - Billing (inconsistencias)
  - Sincronización de datos
- **Acción:** Bug bash mensual + stability sprint

### 4.2 Precio/valor (30% del churn)

#### CR-005: Precio muy alto para el valor percibido
- **% del churn:** 20%
- **Segmento:** SMB principalmente
- **Acción:** Plan starter más accesible evaluando

#### CR-006: ROI no demostrado
- **% del churn:** 10%
- **Acción:** Onboarding mejorado + success program

### 4.3 Competencia (15% del churn)

#### CR-007: Competidor con mejor pricing
- **% del churn:** 8%
- **Competidores mencionados:** CompX, CompY
- **Acción:** Price match strategy para Enterprise

#### CR-008: Competidor con feature específica
- **% del churn:** 7%
- **Features clave:** Reporting AI, mobile app
- **Acción:** Evaluar build vs partner

### 4.4 Otros (10% del churn)

#### CR-009: Quiebra/adquisición del cliente
- **% del churn:** 5%
- **Acción:** No accionable (business risk)

#### CR-010: Cambio de prioridades internas
- **% del churn:** 3%
- **Acción:** Win-back campaign a 6 meses

#### CR-011: Soporte inadecuado
- **% del churn:** 2%
- **Acción:** Soporte 24/5 para Pro+

## 5. Early warning signals

Indicadores predictivos de churn (detectables 60-90 días antes):

| Señal | Predictive power | Acción automática |
|-------|:----------------:|-------------------|
| Login frequency -50% | Alto | CSM outreach |
| Feature usage -60% | Alto | Email re-engagement |
| Support tickets +200% | Medio | Priority support |
| NPS < 6 | Alto | Executive call |
| Invoice overdue >30d | Alto | Retention offer |
| Admin leaves company | Alto | New admin onboarding |

## 6. Retention strategies por segmento

### SMB
- Plan anual con descuento (20%)
- Success templates
- Community access

### Mid-market
- Quarterly business reviews
- Dedicated CSM
- Feature advisory board

### Enterprise
- Executive sponsor
- Custom roadmap input
- SLA guarantees

## 7. Win-back program

**Elegibilidad:** Cancelaron hace 3-9 meses, sin bad debt

**Oferta:**
- 30% descuento primeros 3 meses
- Migration assistance gratuita
- Feature updates highlight

**Tasa de éxito:** 12% (mejorando, era 8% en 2025)

## 8. Cohort analysis

| Cohort | 6m retention | 12m retention | 24m retention |
|--------|:------------:|:-------------:|:-------------:|
| 2024-Q1 | 82% | 71% | 58% |
| 2024-Q2 | 84% | 73% | TBD |
| 2024-Q3 | 86% | 75% | TBD |
| 2024-Q4 | 88% | TBD | TBD |

**Tendencia:** Retención mejorando +2-3pp por cohorte ✅

## 9. Churn prevention roadmap

| Iniciativa | ETA | Impacto estimado |
|------------|-----|------------------|
| Early warning system | Q2 2026 | -15% churn |
| Success program | Q3 2026 | -10% churn |
| Feature gap closure (top 3) | Q4 2026 | -20% churn |
| UX redesign | Q3 2026 | -8% churn |

## 10. Knowledge destillation

Cada razón de churn genera:
- **Feature gap** → Market scoring + PRD
- **UX issue** → Support insights + design
- **Performance issue** → Bug patterns
- **Pricing issue** → Pricing strategy review

## 11. Review cadence
- **Semanal:** Revenue team revisa churn nuevos
- **Mensual:** Análisis de cohortes + tendencias
- **Quarterly:** Churn prevention strategy review
- **Anual:** Pricing + packaging review
