# Plan de Mejoras: Sistema de Impresión y Seguimiento QR

Este plan describe la reestructuración del sistema de tickets para lograr impresiones aisladas (sin UI), etiquetas para dispositivos y seguimiento mediante códigos QR vinculados al portal del cliente.

## 1. Objetivos Técnicos
- **Aislamiento de Impresión**: Usar `@media print` para ocultar todo excepto el ticket seleccionado.
- **Componente Unificado**: Crear `TicketModal.svelte` para centralizar la lógica de diseño y botones.
- **Botones de Impresión Específica**: Permitir elegir entre "Recibo", "Etiqueta" o "Venta".
- **QR con Seguimiento**: Integrar códigos QR que apunten a `WWW.CARELD.COM/portal/{token}`.

## 2. Componentes a Modificar

### [NUEVO] TicketModal.svelte (`src/components/common/`)
- Contendrá los contenedores `#printable-receipt`, `#printable-label` y `#printable-sale`.
- Lógica de `window.print()` con clases CSS inyectadas (`print-receipt-only`, etc.).
- Generación dinámica de QR usando el `portal_token` de la reparación.

### [MODIFICAR] POS.svelte
- Eliminar la implementación local del ticket.
- Importar y usar `TicketModal`.
- Asegurar que al finalizar una venta o recepción se active el modal con la data correcta.

### [MODIFICAR] Repairs.svelte
- Añadir columna de acciones con el icono 🖨️.
- Función `printRepairTicket(repair)` para abrir el modal unificado.

## 3. Estrategia CSS (Aislamiento)
En `TicketModal.svelte` (o global):
```css
@media print {
  body * { visibility: hidden !important; }
  #ticket-content, #ticket-content * { visibility: visible !important; }
  /* ... clases para ocultar partes específicas según la selección ... */
}
```

## 4. Plan de Verificación
1. **Flujo POS**: Realizar venta y probar botones "Solo Venta" y "Imprimir Todo".
2. **Flujo Reparaciones**: Imprimir etiqueta de equipo y verificar que el tamaño (80mm) sea correcto.
3. **QR**: Escanear con móvil y verificar que el link generado sea válido.
