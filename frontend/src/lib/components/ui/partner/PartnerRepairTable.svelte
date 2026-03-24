<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  export let repairs = [];

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
</script>

<div class="table-container">
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>Foto</th>
        <th>Dispositivo</th>
        <th>Estado</th>
        <th>Costo</th>
        <th>Ingreso</th>
        <th class="actions">Acciones</th>
      </tr>
    </thead>
    <tbody>
      {#each repairs as repair (repair.id)}
        <tr on:click={() => dispatch('row-click', repair)}>
          <td class="order-id">{repair.repair_number}</td>
          <td class="photo">
            {#if repair.photos?.length > 0}
              <button 
                class="photo-trigger" 
                on:click|stopPropagation={() => dispatch('view-photos', repair)}
                aria-label="Ver fotos"
              >
                <img src={repair.photos[0]} alt="Device">
              </button>
            {:else}
              <div class="no-photo-small">📱</div>
            {/if}
          </td>
          <td class="device">
            <strong>{repair.device?.brand || ''} {repair.device?.model || 'Equipo'}</strong>
            <span>{repair.description?.substring(0, 30) || 'Sin descripción'}...</span>
          </td>
          <td>
            <span class="status {repair.status?.toLowerCase()}">{getStatusLabel(repair.status)}</span>
          </td>
          <td class="cost">${(repair.final_cost || repair.estimated_cost || 0).toFixed(2)}</td>
          <td class="date">{new Date(repair.created_at).toLocaleDateString()}</td>
          <td class="actions">
            <div class="action-row">
              <button class="icon-btn" title="Editar" on:click|stopPropagation={() => dispatch('edit', repair)}>✏️</button>
              <a href="/portal/{repair.portal_token}" class="icon-btn" title="Detalles" on:click|stopPropagation>🔍</a>
              <button class="icon-btn" title="Estado" on:click|stopPropagation={() => dispatch('status', repair)}>⚙️</button>
            </div>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>

<style>
  .table-container {
    background: rgba(30, 41, 59, 0.3);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    overflow: hidden;
    backdrop-filter: blur(8px);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    font-size: 0.9rem;
  }

  thead {
    background: rgba(15, 23, 42, 0.6);
    position: sticky;
    top: 0;
    z-index: 10;
  }

  th {
    padding: 1.25rem 1rem;
    color: #94a3b8;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 0.7rem;
    letter-spacing: 1px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  td {
    padding: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    color: #f1f5f9;
    vertical-align: middle;
  }

  tbody tr {
    transition: background 0.2s;
    cursor: pointer;
  }

  tbody tr:hover {
    background: rgba(255, 255, 255, 0.04);
  }

  .order-id {
    font-family: monospace;
    color: #818cf8;
    font-weight: 700;
    font-size: 0.8rem;
  }

  .photo-trigger {
    background: transparent;
    border: none;
    padding: 0;
    cursor: pointer;
    display: block;
  }

  .photo img {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    object-fit: cover;
    border: 1px solid rgba(255,255,255,0.1);
  }

  .no-photo-small {
    width: 40px;
    height: 40px;
    background: rgba(0,0,0,0.2);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    opacity: 0.3;
  }

  .device {
    display: flex;
    flex-direction: column;
  }

  .device strong {
    font-size: 0.95rem;
  }

  .device span {
    font-size: 0.75rem;
    color: #64748b;
  }

  .cost {
    font-weight: 800;
    color: white;
  }

  .date {
    color: #64748b;
    font-size: 0.8rem;
  }

  .status {
    padding: 0.3rem 0.6rem;
    border-radius: 8px;
    font-size: 0.65rem;
    font-weight: 800;
    text-transform: uppercase;
    display: inline-block;
  }

  .status.in_progress { background: rgba(59, 130, 246, 0.1); color: #60a5fa; border: 1px solid rgba(96, 165, 250, 0.2); }
  .status.completed { background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.2); }
  .status.delivered { background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.2); }
  .status.pending { background: rgba(245, 158, 11, 0.1); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.2); }
  .status.diagnosing { background: rgba(139, 92, 246, 0.1); color: #a78bfa; border: 1px solid rgba(167, 139, 250, 0.2); }

  .actions {
    text-align: right;
  }

  .action-row {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
  }

  .icon-btn {
    width: 32px;
    height: 32px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #94a3b8;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.9rem;
    text-decoration: none;
  }

  .icon-btn:hover {
    background: #6366f1;
    color: white;
    border-color: #6366f1;
  }
</style>
