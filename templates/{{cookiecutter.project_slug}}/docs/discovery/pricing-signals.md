# Pricing Signals: [Oportunidad]

**Fecha:** 2026-05-27

## Precios de competidores

| Competidor | Plan entry | Plan pro | Enterprise | Modelo |
|------------|:----------:|:--------:|:----------:|--------|
| CompA | $49/mo | $149/mo | Custom | Por usuario |
| CompB | $29/mo | $79/mo | N/A | Flat |
| CompC | Free | $19/mo | N/A | Freemium |

## Señales de disposición de pago
- [ ] Usuarios pagan alternativas caras (evidencia: RF-005)
- [ ] Hay servicios manuales que cobran $X/hora
- [ ] Presupuestos aprobados mencionados en interviews
- [ ] Búsquedas de "pricing" + "alternativa" altas

## Elasticidad estimada
- Precio ancla: **$X/mes**
- Precio óptimo estimado: **$Y/mes**
- Precio de descarte: **>$Z/mes**

## Estrategia propuesta
- **Modelo:** [por usuario | por uso | flat | tiered]
- **Plan entry:** $X/mes (feature-limited)
- **Plan pro:** $Y/mes (core value)
- **Enterprise:** custom (SLA + dedicated)
- **Trial:** 14 días sin tarjeta

## Riesgos de pricing
| Riesgo | Mitigación |
|--------|------------|
| Competidor baja precio | Diferenciar por X |
| Churn alto en plan entry | Feature gate estratégico |
