<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  export let repair = {};

  function getStatusLabel(status) {
    const labels = {
      'pending': 'Pendiente',
      'diagnosing': 'En Diagnóstico',
      'in_progress': 'En Proceso',
      'completed': 'Listo',
      'delivered': 'Entregado',
      'cancelled': 'Cancelado'
    };
    return labels[status?.toLowerCase()] || status;
  }

  $: deviceName = `${repair.device?.brand || ''} ${repair.device?.model || 'Equipo'}`.trim();
  $: mainPhoto = repair.photos?.[0] || null;
  $: price = (repair.final_cost || repair.estimated_cost || 0).toFixed(2);
</script>

<div class="repair-card">
  <!-- 1. Media Section -->
  <div 
    class="card-media" 
    on:click={() => dispatch('view-photos', repair)}
    on:keydown={(e) => e.key === 'Enter' && dispatch('view-photos', repair)}
    role="button"
    tabindex="0"
    aria-label="Ver fotos del dispositivo"
  >
    {#if mainPhoto}
      <img src={mainPhoto} alt={deviceName}>
    {:else}
      <div class="placeholder-icon">
        <span>📱</span>
      </div>
    {/if}
    <div class="order-overlay">
      {repair.repair_number}
    </div>
  </div>

  <!-- 2. Data Section -->
  <div class="card-data">
    <div class="header">
      <h3>{deviceName}</h3>
      <span class="status {repair.status?.toLowerCase()}">{getStatusLabel(repair.status)}</span>
    </div>
    <p class="description">{repair.description || 'Sin descripción del problema.'}</p>
    <div class="meta">
      <span class="price">${price}</span>
      <span class="date">{new Date(repair.created_at).toLocaleDateString()}</span>
    </div>
  </div>

  <!-- 3. Action Section -->
  <div class="card-actions">
    <button class="action-btn secondary" on:click={() => dispatch('edit', repair)}>
      <i>✏️</i> Editar
    </button>
    <a href="/portal/{repair.portal_token}" class="action-btn primary">
      <i>🔍</i> Detalles
    </a>
    <button class="action-btn secondary" on:click={() => dispatch('status', repair)}>
      <i>⚙️</i> Estado
    </button>
  </div>
</div>

<style>
  .repair-card {
    background: rgba(30, 41, 59, 0.5);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    transition: border-color 0.2s, background 0.2s;
  }

  .repair-card:hover {
    border-color: #6366f1;
    background: rgba(45, 55, 72, 0.7);
  }

  /* Media Section */
  .card-media {
    height: 180px;
    background: #0f172a;
    position: relative;
    cursor: pointer;
    overflow: hidden;
  }

  .card-media img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.8;
    transition: opacity 0.3s;
  }

  .card-media:hover img {
    opacity: 1;
  }

  .placeholder-icon {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
    opacity: 0.3;
  }

  .order-overlay {
    position: absolute;
    top: 1rem;
    left: 1rem;
    background: rgba(15, 23, 42, 0.8);
    padding: 0.4rem 0.8rem;
    border-radius: 8px;
    font-size: 0.75rem;
    font-weight: 800;
    color: #818cf8;
    letter-spacing: 1px;
    backdrop-filter: blur(4px);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  /* Data Section */
  .card-data {
    padding: 1.5rem;
    flex: 1;
  }

  .card-data .header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.75rem;
    gap: 1rem;
  }

  h3 {
    font-size: 1.15rem;
    font-weight: 800;
    margin: 0;
    color: white;
    line-height: 1.2;
  }

  .description {
    color: #94a3b8;
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    line-clamp: 2;
    overflow: hidden;
    line-height: 1.5;
  }

  .meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 700;
  }

  .price {
    font-size: 1.2rem;
    color: white;
  }

  .date {
    font-size: 0.8rem;
    color: #64748b;
  }

  .status {
    padding: 0.3rem 0.6rem;
    border-radius: 8px;
    font-size: 0.65rem;
    font-weight: 800;
    text-transform: uppercase;
    white-space: nowrap;
  }

  .status.in_progress { background: rgba(59, 130, 246, 0.1); color: #60a5fa; border: 1px solid rgba(96, 165, 250, 0.2); }
  .status.completed { background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.2); }
  .status.delivered { background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.2); }
  .status.pending { background: rgba(245, 158, 11, 0.1); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.2); }
  .status.diagnosing { background: rgba(139, 92, 246, 0.1); color: #a78bfa; border: 1px solid rgba(167, 139, 250, 0.2); }

  /* Action Section */
  .card-actions {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    background: rgba(15, 23, 42, 0.3);
  }

  .action-btn {
    padding: 1rem 0.5rem;
    border: none;
    background: transparent;
    color: #94a3b8;
    font-size: 0.75rem;
    font-weight: 700;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.4rem;
    transition: all 0.2s;
    text-decoration: none;
    text-align: center;
  }

  .action-btn i {
    font-size: 1.1rem;
    font-style: normal;
  }

  .action-btn:not(:last-child) {
    border-right: 1px solid rgba(255, 255, 255, 0.1);
  }

  .action-btn:hover {
    color: white;
    background: rgba(255, 255, 255, 0.05);
  }

  .action-btn.primary:hover {
    background: rgba(99, 102, 241, 0.1);
    color: #818cf8;
  }
</style>
