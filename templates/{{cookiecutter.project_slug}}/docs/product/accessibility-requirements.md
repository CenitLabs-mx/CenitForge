# Requisitos de Accesibilidad

**PRD:** PRD-2026-001

## Nivel objetivo
- **MVP:** WCAG 2.1 AA
- **v2:** WCAG 2.2 AA
- **No-goal:** WCAG AAA

## Checklist por componente

### Formularios
- [ ] Labels asociados a todos los inputs
- [ ] Error messages con `aria-describedby`
- [ ] Focus visible y orden lógico
- [ ] Autocompletado habilitado donde aplica

### Navegación
- [ ] Skip-to-content link
- [ ] Focus trap en modales
- [ ] Orden de tab consistente
- [ ] Breadcrumbs accesibles

### Contenido
- [ ] Contraste ≥ 4.5:1 (texto normal) / 3:1 (texto grande)
- [ ] Alt text en imágenes informativas
- [ ] `role="presentation"` en imágenes decorativas
- [ ] Jerarquía de headings (h1-h6) sin saltos

### Interactivos
- [ ] Botones con `aria-label` si solo tienen icono
- [ ] Estados de loading anunciados (aria-live)
- [ ] Tooltips accesibles

## Herramientas de validación
- **Automatizado:** axe-core en CI
- **Manual:** NVDA + VoiceOver quarterly
- **Contraste:** Stark plugin + WebAIM checker

## Testing
| Test | Frecuencia | Responsable |
|------|:----------:|-------------|
| axe-core CI | Cada PR | CI/CD |
| Keyboard navigation manual | Cada release | QA |
| Screen reader testing | Quarterly | QA + accessibility champion |

## Known issues
| Issue | Severidad | Workaround | ETA fix |
|-------|:---------:|------------|---------|
| - | - | - | - |
