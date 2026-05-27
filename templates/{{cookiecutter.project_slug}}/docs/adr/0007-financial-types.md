# ADR-0007: Tipos de Datos Financieros

**Estado:** Aceptada
**Fecha:** 2026-05-27
**Owner:** @billing-lead
**Relacionado:** INV-002

## Contexto

Campos financieros mal tipados causan:
- Errores de redondeo
- Discrepancias contables
- Pérdida de centavos en agregaciones
- Issues legales/fiscales

El caso clásico: `0.1 + 0.2 ≠ 0.3` en floating point.

## Decisión

### Reglas

#### 1. Montos: BIGINT en cents

```sql
-- Para montos de dinero (precios, totales, impuestos)
amount_cents BIGINT NOT NULL
```

**Justificación:**
- Operaciones enteras, sin pérdida de precisión
- Performance superior a NUMERIC
- Fácil serialización JSON (número, no string)

**Convención:**
- Sufijo `_cents` en toda columna que use este patrón
- Documentar moneda en columna adyacente o en metadata

#### 2. Cálculos intermedios: NUMERIC(20, 4)

```sql
-- Para tasas, prorrateos, cálculos con fracciones
tax_rate NUMERIC(10, 6)
proration_factor NUMERIC(20, 10)
```

#### 3. Moneda: ISO 4217 TEXT(3)

```sql
currency CHAR(3) NOT NULL DEFAULT 'USD'
-- 'USD', 'EUR', 'MXN', etc.
```

#### 4. Nunca FLOAT

```sql
-- ❌ PROHIBIDO EN TODA CIRCUNSTANCIA
amount FLOAT
price DOUBLE PRECISION
tax REAL
```

### Ejemplo completo

```sql
CREATE TABLE invoices (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  subtotal_cents BIGINT NOT NULL,        -- Monto sin impuestos
  tax_cents BIGINT NOT NULL DEFAULT 0,   -- Impuestos
  discount_cents BIGINT NOT NULL DEFAULT 0,
  total_cents BIGINT NOT NULL,           -- Total a pagar
  currency CHAR(3) NOT NULL DEFAULT 'USD',
  
  -- Para cálculos (no se persiste normalmente)
  tax_rate NUMERIC(10, 6),               -- 0.160000 = 16%
  
  -- Audit
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  CONSTRAINT positive_subtotal CHECK (subtotal_cents >= 0),
  CONSTRAINT positive_total CHECK (total_cents >= 0)
);
```

### En código (Python)

```python
from decimal import Decimal
from pydantic import BaseModel, Field

class Money(BaseModel):
    """Representación de dinero en cents."""
    amount_cents: int = Field(..., ge=0)
    currency: str = Field(..., min_length=3, max_length=3)
    
    @property
    def amount(self) -> Decimal:
        return Decimal(self.amount_cents) / Decimal(100)
    
    @classmethod
    def from_decimal(cls, amount: Decimal, currency: str) -> "Money":
        cents = int((amount * 100).quantize(Decimal('1')))
        return cls(amount_cents=cents, currency=currency)
    
    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(
            amount_cents=self.amount_cents + other.amount_cents,
            currency=self.currency
        )
```

## Consecuencias positivas

- **Precisión:** cero errores de redondeo
- **Performance:** BIGINT más rápido que NUMERIC
- **Simplicidad:** aritmética entera estándar

## Consecuencias negativas

- **Conversión:** hay que dividir entre 100 para mostrar
- **Monedas fraccionales:** algunas monedas (JPY) no tienen cents
  - **Mitigación:** usar factor de escala por moneda

## Linter CI

```python
# Detecta FLOAT en columnas financieras
import re
FINANCIAL_KEYWORDS = {"amount", "price", "total", "tax", "fee", "balance", "cost"}
FLOAT_PATTERN = re.compile(r"\b(FLOAT|DOUBLE|REAL)\b", re.I)

for migration in migrations:
    for line in migration.content.splitlines():
        if any(k in line.lower() for k in FINANCIAL_KEYWORDS):
            if FLOAT_PATTERN.search(line):
                raise LintError(f"INV-002 violation: {line}")
```
