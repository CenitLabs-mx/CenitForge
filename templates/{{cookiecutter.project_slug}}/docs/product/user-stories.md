# User Stories: [Producto]

**PRD:** PRD-2026-001
**Fecha:** 2026-05-27

## Convención
```
Como [ROL],
Quiero [ACCIÓN],
Para [BENEFICIO].

Acceptance Criteria:
- Given [contexto], When [acción], Then [resultado]
- ...
```

## US-001: Crear cuenta multi-tenant
**Prioridad:** P0
**Risk class:** R3

Como **admin de empresa**,
Quiero **crear una cuenta para mi organización**,
Para **empezar a usar el producto con mi equipo**.

### Acceptance Criteria
- Given usuario sin cuenta, When completa signup con email corporativo, Then se crea tenant + user admin
- Given email ya registrado, When signup, Then muestra error claro
- Given signup exitoso, When confirma email, Then tenant pasa a estado `Trialing`
- Given tenant creado, When consulta `/me`, Then solo ve su propio tenant_id

### Non-goals
- SSO en MVP
- Invitación masiva de usuarios

---

## US-002: Invitar miembro al tenant
**Prioridad:** P0
**Risk class:** R2

...

## US-003: Suscribirse a plan pago
...
