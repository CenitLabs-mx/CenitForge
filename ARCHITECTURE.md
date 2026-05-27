# Arquitectura del Kit CenitForge

## Principios de diseño

1. **Separación kit vs proyecto:** El kit es un generador; los proyectos
   generados son independientes.
2. **Templates sobre código:** Preferimos templates cookiecutter a scripts
   de inicialización complejos.
3. **Herramientas portables:** Todo en Python estándar + herramientas open source.
4. **Documentación viva:** Cada archivo tiene propósito claro.

## Estructura de capas

```
┌─────────────────────────────────────────┐
│   Proyectos generados (usuarios)        │
├─────────────────────────────────────────┤
│   Templates cookiecutter                │
├─────────────────────────────────────────┤
│   Tools (Python)                        │
├─────────────────────────────────────────┤
│   Infrastructure (Terraform + Docker)   │
├─────────────────────────────────────────┤
│   Documentation (Plan Maestro V5)       │
└─────────────────────────────────────────┘
```

## Flujo de uso típico

```
1. git clone cenitforge
            ↓
2. make install
            ↓
3. make new-project  →  cookiecutter genera proyecto
            ↓
4. cd mi_producto
            ↓
5. make setup && make validate
            ↓
6. Inicio de Fase -1: Market Scoring
```

## Decisiones de diseño

### ADR-KIT-001: ¿Por qué cookiecutter?
Cookiecutter es estándar, mantenible, y soporta hooks pre/post generación.

### ADR-KIT-002: ¿Por qué Python para tools?
Python es el denominador común para tooling de IA, con ecosistema maduro.

### ADR-KIT-003: ¿Por qué el Plan Maestro no es dependencia?
Es conocimiento, no código. Los proyectos lo referencian pero no lo importan.
