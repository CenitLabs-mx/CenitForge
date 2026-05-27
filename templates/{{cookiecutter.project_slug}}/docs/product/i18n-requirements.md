# Requisitos de Internacionalización (i18n)

**PRD:** PRD-2026-001

## Idiomas soportados
| Idioma | Código | Fase | Status |
|--------|:------:|:----:|:------:|
| English (US) | en-US | MVP | ✅ |
| Español (LATAM) | es-419 | Q3 2026 | ⏳ |
| Português (BR) | pt-BR | Q4 2026 | ⏳ |

## Arquitectura
- **Formato:** JSON keys (`messages.{lang}.json`)
- **Librería:** react-intl (frontend), i18next (backend)
- **No hardcoded strings:** Lint rule obligatoria

## Convenciones
- Keys: `feature.component.element` (ej. `billing.invoice.total`)
- Plurales: usar ICU message syntax
- Fechas: ISO 8601 internamente, localized en UI
- Números: localized (1,000.00 vs 1.000,00)
- Timezones: UTC storage, browser tz display

## Testing
- [ ] Pseudo-localization en CI (detecta strings hardcoded)
- [ ] Screenshot comparison por idioma
- [ ] RTL testing si se agrega árabe/hebreo

## Non-goals
- ❌ RTL en MVP
- ❌ CJK fonts optimization
- ❌ User-generated content translation
