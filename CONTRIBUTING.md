# Contribuir al Kit CenitForge

¡Gracias por tu interés!

## Tipos de contribuciones

| Tipo | Proceso |
|------|---------|
| 🐛 Bug fix | PR directo |
| 📚 Docs | PR directo |
| 🔧 Nueva tool | Issue primero |
| 🏛️ Nueva invariante | RFC + auditoría |

## Proceso para nuevas invariantes

1. **RFC:** Issue con formato RFC
2. **Evidencia:** Casos reales donde previene incidentes
3. **Enforcement:** Implementación preventiva + detectiva
4. **Auditoría:** Revisión por auditor independiente
5. **Release:** Incluida en próximo MAJOR version

## Desarrollo local

```bash
git clone <repo>
cd CenitForge
make install
make test
# Hacer cambios
make validate
git commit -m "feat: add X"
```

## Código de conducta

Respeto mutuo, foco técnico, inclusión.
