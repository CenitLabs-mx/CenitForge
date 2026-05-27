# Riesgos de Falso Positivo: [Oportunidad]

**Fecha:** 2026-05-27

## Definición
Un falso positivo ocurre cuando las señales de mercado sugieren demanda
que no se materializa en producto exitoso.

## Riesgos identificados

### FP-001: Vocal minority
- **Descripción:** Reddit/foros sobre-representan early adopters técnicos
- **Probabilidad:** Media
- **Impacto:** Alto (construir para nicho pequeño)
- **Detección:** Validar con interviews a buyers (no solo users)
- **Mitigación:** Requerir ≥5 interviews con decision-makers

### FP-002: Astroturfing
- **Descripción:** Reviews/posts plantados por competidores o fans
- **Probabilidad:** Baja
- **Impacto:** Medio
- **Detección:** Verificar edad de cuentas, historial, patrones
- **Mitigación:** Cross-referenciar ≥3 fuentes independientes

### FP-003: Hype temporal
- **Descripción:** Tendencia pasajera (ej. AI-washing, modas)
- **Probabilidad:** Media
- **Impacto:** Alto
- **Detección:** Comparar YoY, no MoM
- **Mitigación:** Exigir tendencia estable ≥12 meses

### FP-004: Dolor real pero sin presupuesto
- **Descripción:** Usuarios quieren solución pero no pagan
- **Probabilidad:** Media
- **Impacto:** Alto
- **Detección:** Preguntar por presupuesto actual, no intención
- **Mitigación:** Requerir carta de intención o piloto pagado

### FP-005: Solución técnica en busca de problema
- **Descripción:** Equipo enamorado de la tech, no del dolor
- **Probabilidad:** Baja
- **Impacto:** Crítico
- **Detección:** ¿Podemos describir el dolor sin mencionar tecnología?
- **Mitigación:** PRD grounded, sin soluciones en Fase -1

## Gate anti-falso-positivo
Antes de avanzar a PRD, al menos **uno** de estos debe ser cierto:
- [ ] ≥5 interviews con buyers confirmando presupuesto
- [ ] Carta de intención firmada
- [ ] Piloto pagado comprometido
- [ ] Evidencia cuantitativa sólida (score 5/5)

## Decisión
**Riesgo residual después de mitigaciones:** Bajo / Medio / Alto
