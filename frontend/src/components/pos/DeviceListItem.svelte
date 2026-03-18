<script>
  export let device;
  export let customerName = '';
  export let onView = () => {};
  export let onEdit = () => {};
  export let onStatusChange = () => {};

  const statusLabels = {
    registered: 'Registrado',
    in_repair: 'En Reparación',
    waiting_parts: 'Esperando Repuestos',
    ready: 'Listo para Entrega',
    delivered: 'Entregado'
  };

  const statusColors = {
    registered: 'badge-secondary',
    in_repair: 'badge-primary',
    waiting_parts: 'badge-warning',
    ready: 'badge-success',
    delivered: 'badge-success'
  };

  const deviceIcons = {
    smartphone: '📱',
    tablet: '📟',
    laptop: '💻',
    desktop: '🖥️',
    smartwatch: '⌚',
    console: '🎮',
    other: '📦'
  };

  function getDeviceIcon() {
    return deviceIcons[device.device_type] || deviceIcons.other;
  }
</script>

<div class="device-list-item">
  <div class="device-info-main" on:click={() => onView(device)}>
    <div class="device-icon-wrapper">
      <span class="device-icon">{getDeviceIcon()}</span>
    </div>
    
    <div class="device-details">
      <div class="device-name-row">
        <h3 class="device-name">{device.brand} {device.model}</h3>
        <span class="status-badge badge {statusColors[device.status]}">
          {statusLabels[device.status]}
        </span>
      </div>
      
      <div class="device-meta">
        <span class="meta-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
          {customerName}
        </span>
        
        {#if device.color}
          <span class="meta-item">• {device.color}</span>
        {/if}
        
        {#if device.storage}
          <span class="meta-item">• {device.storage}</span>
        {/if}
      </div>
    </div>
  </div>

  <div class="device-actions">
    <button
      class="action-btn"
      on:click={() => onView(device)}
      title="Ver detalles"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
        <circle cx="12" cy="12" r="3"/>
      </svg>
    </button>
    
    <button
      class="action-btn"
      on:click={() => onEdit(device)}
      title="Editar"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
      </svg>
    </button>
    
    <button
      class="action-btn"
      on:click={() => onStatusChange(device)}
      title="Cambiar estado"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="23 4 23 10 17 10"/>
        <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
      </svg>
    </button>
    
    <button class="chevron-btn" title="Expandir">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="9 18 15 12 9 6"/>
      </svg>
    </button>
  </div>
</div>

<style>
  .device-list-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: white;
    padding: 0.75rem 1rem;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    transition: all 0.2s;
    margin-bottom: 0.5rem;
  }

  .device-list-item:hover {
    box-shadow: var(--shadow-md);
    transform: translateX(2px);
  }

  .device-info-main {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex: 1;
    cursor: pointer;
    min-width: 0;
  }

  .device-icon-wrapper {
    width: 48px;
    height: 48px;
    border-radius: var(--radius);
    background: linear-gradient(135deg, var(--light) 0%, #e0e7ff 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .device-icon {
    font-size: 1.75rem;
  }

  .device-details {
    flex: 1;
    min-width: 0;
  }

  .device-name-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.25rem;
  }

  .device-name {
    font-size: 1rem;
    font-weight: 600;
    color: var(--dark);
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .status-badge {
    font-size: 0.65rem;
    padding: 0.2rem 0.5rem;
    flex-shrink: 0;
  }

  .device-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.8125rem;
    color: var(--text-light);
    flex-wrap: wrap;
  }

  .meta-item {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .meta-item svg {
    width: 14px;
    height: 14px;
  }

  .device-actions {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    margin-left: 0.5rem;
  }

  .action-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border: none;
    background: transparent;
    cursor: pointer;
    transition: all 0.2s;
    color: var(--text-light);
    border-radius: var(--radius-sm);
  }

  .action-btn svg {
    width: 18px;
    height: 18px;
  }

  .action-btn:hover {
    background: var(--light);
    color: var(--primary);
  }

  .chevron-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border: none;
    background: transparent;
    cursor: pointer;
    color: var(--text-light);
    margin-left: 0.5rem;
  }

  .chevron-btn svg {
    width: 20px;
    height: 20px;
  }

  .chevron-btn:hover {
    color: var(--text);
  }

  @media (max-width: 640px) {
    .device-list-item {
      padding: 0.75rem;
    }

    .device-info-main {
      gap: 0.75rem;
    }

    .device-icon-wrapper {
      width: 40px;
      height: 40px;
    }

    .device-icon {
      font-size: 1.5rem;
    }

    .device-name {
      font-size: 0.9375rem;
    }

    .device-meta {
      font-size: 0.75rem;
    }

    .action-btn {
      width: 32px;
      height: 32px;
    }

    .action-btn svg {
      width: 16px;
      height: 16px;
    }
  }
</style>
