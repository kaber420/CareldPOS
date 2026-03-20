# Estrategia de Impresión POS y Seguimiento QR (v2.0)

Este documento define el estándar técnico para el sistema de tickets de CareldPOS, enfocándose en la modularidad, aislamiento de CSS y la experiencia de seguimiento del cliente.

## 1. Arquitectura de Impresión (Aislamiento Zero-Friction)

Para evitar que la UI del ERP interfiera con los tickets, se implementará un sistema de **visibilidad exclusiva**.

### Estrategia CSS `@media print`
No usaremos `visibility: hidden` (que mantiene el espacio del elemento), sino una combinación de `display: none` y `position: absolute`.

```css
@media print {
  /* Ocultar TODO el layout del ERP */
  :global(#root), :global(.modal-overlay > *:not(.modal)) { 
    display: none !important; 
  }

  /* Forzar que el ticket sea el único elemento en el viewport */
  .ticket-preview {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    margin: 0;
    padding: 0;
  }

  /* Control de saltos de página para etiquetas */
  .ticket-label {
    page-break-before: always;
  }
}
```

## 2. Componente Unificado: `TicketModal.svelte`

El componente debe actuar como un "Pure Component" que solo renderiza datos.

### Propiedades (Props)
- `show`: Booleano para control de visibilidad.
- `ticketData`: Objeto con `type` ('recepcion' | 'venta' | 'etiqueta'), `customer`, `device` y `items`.
- `autoPrint`: Si es `true`, dispara `window.print()` inmediatamente después de montar el QR.

### Mejoras Técnicas
1.  **Soporte Multi-Rollo**: Implementar clases `.w-58mm` y `.w-80mm` basadas en la configuración del usuario.
2.  **Generación de QR Robusta**:
    - URL base configurable: `CARELD_PORTAL_URL`.
    - Estructura: `${base}/portal/${token}`.
    - Fallback: Si no hay token, mostrar el logo de la empresa.

## 3. Flujos de Integración

### A. Recepción de Equipos (`POS.svelte`)
Al confirmar una recepción, el sistema debe:
1.  Generar el `portal_token` en el backend.
2.  Abrir el `TicketModal` con la opción "Imprimir Todo" preseleccionada.
3.  **Objetivo**: El técnico entrega el ticket al cliente y pega la etiqueta al equipo en un solo clic.

### B. Ventas y Pagos (`POS.svelte`)
1.  Al finalizar el checkout, abrir el ticket de venta simplificado.
2.  Incluir resumen de garantía automática (30 días por defecto).

### C. Consulta de Reparaciones (`Repairs.svelte`)
1.  Acceso rápido desde la tabla de órdenes (icono 🖨️).
2.  Permitir re-imprimir etiquetas de equipo si la original se daña.

## 4. Plan de Verificación (QA)

| Prueba | Resultado Esperado |
| :--- | :--- |
| **Aislamiento** | Al imprimir, no debe aparecer el header ni el sidebar del ERP (ni siquiera espacios en blanco). |
| **Escalabilidad** | El QR debe ser legible incluso en papel térmico de baja calidad (usar `margin: 2` y `errorCorrectionLevel: 'M'`). |
| **Deep-Link** | Al escanear el QR, el cliente debe llegar directamente a su orden sin login previo (usar el token UUID). |
| **Multi-Página** | Imprimir Recibo + Etiqueta debe generar exactamente 2 "páginas" en el driver de la impresora térmica. |

---
> [!TIP]
> Para impresoras térmicas en Linux, se recomienda configurar el tamaño de papel en el driver CUPS como "Custom 80mm x 210mm" para evitar cortes prematuros.
