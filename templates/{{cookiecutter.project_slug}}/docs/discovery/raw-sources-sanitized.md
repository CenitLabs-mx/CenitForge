# Raw Sources - Versión Sanitizada

> Generado automáticamente por `SanitizationGateway` el 2026-05-27

## Resumen de sanitización
- **PII detectada:** N emails, N teléfonos, N nombres
- **Secrets detectados:** N (bloqueados)
- **Acción tomada:** Pseudonymize + Redact

## Fuentes sanitizadas

### RF-001 (sanitizado)
- Email original: `[EMAIL_001]` (hash: abc123)
- Teléfono: `[PHONE_REDACTED]`
- Contenido: [texto con reemplazos estables]

### RF-002 (sanitizado)
...

## Hash de integridad
- Original: `sha256:...`
- Sanitizado: `sha256:...`

## Registro en Sanitization Gateway
```json
{
  "timestamp": "2026-05-27T10:00:00Z",
  "verdict": "ALLOWED",
  "action_taken": "Sanitized: PII redacted/pseudonymized"
}
```
