<script>
  export let device;
  export let customerName = '';
  export let onView = () => {};
  export let onEdit = () => {};
  export let onStatusChange = () => {};
  export let onOpenGallery = () => {};

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

  function getFirstPhoto() {
    if (device.photos && device.photos.trim()) {
      const photos = device.photos.split(',');
      const firstPhoto = photos[0].trim();
      // Si ya es URL completa, devolverla
      if (firstPhoto.startsWith('http') || firstPhoto.startsWith('/api/')) {
        return firstPhoto;
      }
      // Si es solo nombre de archivo, construir URL
      return `/api/v1/uploads/photo/${firstPhoto}`;
    }
    return null;
  }
</script>

<div class="device-card">
  <div class="card-image" on:click|stopPropagation={() => onOpenGallery(device)}>
    {#if getFirstPhoto()}
      <img src={getFirstPhoto()} alt={device.brand} />
      <div class="photo-indicator">📷</div>
    {:else}
      <div class="card-image-placeholder">
        <span class="device-icon">{getDeviceIcon()}</span>
      </div>
    {/if}
    <span class="status-badge badge {statusColors[device.status]}">
      {statusLabels[device.status]}
    </span>
  </div>

  <div class="card-content">
    <div class="device-header">
      <span class="device-icon-small">{getDeviceIcon()}</span>
      <h3 class="device-title">{device.brand} {device.model}</h3>
    </div>

    <div class="device-info">
      <div class="info-row">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        <span>{customerName}</span>
      </div>

      {#if device.color}
        <div class="info-row">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 2a10 10 0 0 1 10 10"/>
          </svg>
          <span>{device.color}</span>
        </div>
      {/if}

      {#if device.storage}
        <div class="info-row">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="2" width="20" height="8" rx="2" ry="2"/>
            <rect x="2" y="14" width="20" height="8" rx="2" ry="2"/>
            <line x1="6" y1="6" x2="6.01" y2="6"/>
            <line x1="6" y1="18" x2="6.01" y2="18"/>
          </svg>
          <span>{device.storage}</span>
        </div>
      {/if}
    </div>
  </div>

  <div class="card-actions">
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
  </div>
</div>

<style>
  .device-card {
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
    cursor: pointer;
  }

  .device-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }

  .card-image {
    position: relative;
    height: 160px;
    background: linear-gradient(135deg, var(--light) 0%, #e0e7ff 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }

  .card-image:hover {
    background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
  }

  .photo-indicator {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    background: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: var(--radius-sm);
    font-size: 0.875rem;
  }

  .card-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .card-image-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
  }

  .device-icon {
    font-size: 4rem;
    opacity: 0.8;
  }

  .device-icon-small {
    font-size: 1.5rem;
  }

  .status-badge {
    position: absolute;
    top: 0.75rem;
    right: 0.75rem;
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
  }

  .card-content {
    padding: 1rem;
  }

  .device-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
  }

  .device-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--dark);
    margin: 0;
    line-height: 1.2;
  }

  .device-info {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .info-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.8125rem;
    color: var(--text-light);
  }

  .info-row svg {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
  }

  .card-actions {
    display: flex;
    border-top: 1px solid var(--border);
  }

  .action-btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.75rem;
    border: none;
    background: transparent;
    cursor: pointer;
    transition: all 0.2s;
    color: var(--text-light);
  }

  .action-btn svg {
    width: 20px;
    height: 20px;
  }

  .action-btn:hover {
    background: var(--light);
    color: var(--primary);
  }

  .action-btn:not(:last-child) {
    border-right: 1px solid var(--border);
  }
</style>
