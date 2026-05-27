# 🚀 Quickstart - CenitForge

De cero a primer micro-prompt en **5 minutos**.

## Prerrequisitos

```bash
python --version        # 3.11+
git --version           # 2.30+
make --version          # GNU Make
```

## Paso 1: Clonar el kit

```bash
git clone https://github.com/your-org/CenitForge.git
cd CenitForge
```

## Paso 2: Instalar dependencias

```bash
make install
```

## Paso 3: Validar integridad

```bash
make validate
```

Output esperado:
```
✅ 82/82 archivos presentes
✅ Hashes verificados
Kit listo para usar.
```

## Paso 4: Crear tu primer proyecto

```bash
make new-project
```

Responde las preguntas:
```
project_name [Mi SaaS B2B]: Mi Producto
initial_maturity (M1/M2/M3) [M1]: M1
has_billing (yes/no) [yes]: yes
has_multi_tenancy (yes/no) [yes]: yes
```

## Paso 5: Entrar al proyecto

```bash
cd mi_producto
make setup
make validate
```

Output:
```
✅ Enforcement Seed (M1):
   - RLS skeleton: log_only
   - vault stub: ready
   - sanitizer local: ready
✅ Proyecto listo para Fase -1: Market Scoring
```

## Paso 6: Comenzar

```bash
code docs/discovery/opportunity-scorecard.md
```

---

## 🎯 Próximos pasos

| Objetivo | Recurso |
|----------|---------|
| Framework completo | [Plan Maestro V5](docs/plan-maestro-v5.md) |
| Roadmap 12 semanas | [adoption-roadmap.md](docs/adoption-roadmap.md) |
| Capacitación | [docs/training/](docs/training/) |
