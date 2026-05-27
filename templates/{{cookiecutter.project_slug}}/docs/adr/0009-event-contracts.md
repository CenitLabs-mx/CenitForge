# ADR-0009: Event Contracts y Schema Registry

**Estado:** Aceptada
**Fecha:** 2026-05-27
**Owner:** @platform-lead

## Contexto

El sistema emite eventos de dominio (invoice.paid, user.created, etc.) que
son consumidos por múltiples servicios. Sin contratos explícitos:
- Consumers rompen cuando producer cambia payload
- No hay validación de schema
- Debugging difícil

## Decisión

### 1. Schema-first con JSON Schema

Todo evento tiene schema versionado:

```json
// events/schemas/invoice.paid.v1.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "InvoicePaid",
  "type": "object",
  "required": ["event_id", "event_type", "timestamp", "tenant_id", "payload"],
  "properties": {
    "event_id": {"type": "string", "format": "uuid"},
    "event_type": {"type": "string", "const": "invoice.paid"},
    "event_version": {"type": "string", "const": "1.0"},
    "timestamp": {"type": "string", "format": "date-time"},
    "tenant_id": {"type": "string", "format": "uuid"},
    "payload": {
      "type": "object",
      "required": ["invoice_id", "amount_cents", "currency"],
      "properties": {
        "invoice_id": {"type": "string", "format": "uuid"},
        "amount_cents": {"type": "integer", "minimum": 0},
        "currency": {"type": "string", "minLength": 3, "maxLength": 3}
      }
    }
  }
}
```

### 2. Envelope estándar

```python
@dataclass
class DomainEvent:
    event_id: str
    event_type: str
    event_version: str
    timestamp: datetime
    tenant_id: str
    aggregate_id: str
    aggregate_type: str
    correlation_id: str
    causation_id: Optional[str]
    payload: dict
```

### 3. Versionado de eventos

- Versión MAJOR: breaking change (nuevo event type)
- Versión MINOR: additive change (nuevos campos opcionales)

### 4. Publicación

```python
class EventPublisher:
    def publish(self, event: DomainEvent):
        # 1. Validar contra schema
        schema = load_schema(event.event_type, event.event_version)
        validate(event.to_dict(), schema)
        
        # 2. Publicar
        broker.publish(
            topic=f"events.{event.event_type}",
            message=event.to_dict(),
            key=event.aggregate_id  # Ordered por aggregate
        )
```

### 5. Schema Registry

Schemas viven en Git:
```
events/
  schemas/
    invoice.paid.v1.json
    invoice.paid.v2.json
    user.created.v1.json
  registry.yaml
```

CI valida:
- Schemas válidos (JSON Schema)
- Backward compatibility (nuevo schema acepta eventos viejos)
- Registro actualizado

## Consumers

```python
@consumer(topic="events.invoice.paid")
async def on_invoice_paid(event: dict):
    # Validar schema
    validate(event, load_schema("invoice.paid", event["event_version"]))
    # Procesar
    ...
```

## Consecuencias positivas

- **Contratos explícitos** entre producer y consumer
- **Validación automática** en CI y runtime
- **Evolución controlada** de eventos

## Consecuencias negativas

- **Overhead:** validación añade ~1ms
- **Tooling:** requiere schema registry
