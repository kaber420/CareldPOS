<script>
  import { onMount } from 'svelte';
  import { api } from '../stores/api';
  import { notify } from '../stores/auth';
  import Layout from '../components/Layout.svelte';

  let stats = {
    totalRepairs: 0,
    pendingRepairs: 0,
    inProgressRepairs: 0,
    completedToday: 0,
    totalCustomers: 0,
    totalDevices: 0,
    lowStockItems: 0,
    revenueToday: 0
  };

  let recentRepairs = [];
  let isLoading = true;

  onMount(async () => {
    await loadStats();
    await loadRecentRepairs();
    isLoading = false;
  });

  async function loadStats() {
    try {
      const [repairs, customers, devices, inventory] = await Promise.all([
        api.getRepairs({ limit: 100 }),
        api.getCustomers({ limit: 100 }),
        api.getDevices({ limit: 100 }),
        api.getInventoryItems({ low_stock: true })
      ]);

      const today = new Date().toISOString().split('T')[0];
      
      stats = {
        totalRepairs: repairs.length,
        pendingRepairs: repairs.filter(r => r.status === 'pending').length,
        inProgressRepairs: repairs.filter(r => r.status === 'in_progress').length,
        completedToday: repairs.filter(r => 
          r.status === 'completed' && r.completed_at?.startsWith(today)
        ).length,
        totalCustomers: customers.length,
        totalDevices: devices.length,
        lowStockItems: inventory.length,
        revenueToday: 0 // Se calcularía desde los pagos
      };
    } catch (error) {
      notify('Error al cargar estadísticas', 'danger');
    }
  }

  async function loadRecentRepairs() {
    try {
      const repairs = await api.getRepairs({ limit: 5 });
      recentRepairs = repairs;
    } catch (error) {
      console.error('Error loading recent repairs:', error);
    }
  }

  function getStatusBadge(status) {
    const statusMap = {
      pending: 'badge-warning',
      diagnosing: 'badge-primary',
      waiting_approval: 'badge-warning',
      in_progress: 'badge-primary',
      waiting_parts: 'badge-warning',
      completed: 'badge-success',
      delivered: 'badge-success',
      cancelled: 'badge-danger'
    };
    return statusMap[status] || 'badge-secondary';
  }

  function formatStatus(status) {
    const statusLabels = {
      pending: 'Pendiente',
      diagnosing: 'Diagnóstico',
      waiting_approval: 'Esperando Aprobación',
      in_progress: 'En Progreso',
      waiting_parts: 'Esperando Repuestos',
      completed: 'Completada',
      delivered: 'Entregada',
      cancelled: 'Cancelada'
    };
    return statusLabels[status] || status;
  }

  function formatDate(dateString) {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
</script>

<Layout>
  <div class="dashboard">
    <div class="page-header">
      <h1 class="page-title">Dashboard</h1>
      <p class="page-subtitle">Resumen general del taller</p>
    </div>

    {#if isLoading}
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Cargando estadísticas...</p>
      </div>
    {:else}
      <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon icon-primary">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-label">Reparaciones Pendientes</div>
          <div class="stat-value">{stats.pendingRepairs}</div>
          <div class="stat-change">De {stats.totalRepairs} totales</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon icon-success">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-label">En Progreso</div>
          <div class="stat-value">{stats.inProgressRepairs}</div>
          <div class="stat-change">Técnicos trabajando</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon icon-info">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-label">Clientes</div>
          <div class="stat-value">{stats.totalCustomers}</div>
          <div class="stat-change">Registrados</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon icon-warning">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-label">Stock Bajo</div>
          <div class="stat-value">{stats.lowStockItems}</div>
          <div class="stat-change text-danger">Requieren atención</div>
        </div>
      </div>
    </div>

    <!-- Recent Repairs -->
    <div class="card mt-6">
      <div class="card-header">
        <h2 class="card-title">Reparaciones Recientes</h2>
        <a href="/repairs" class="btn btn-sm btn-outline">Ver todas</a>
      </div>
      <div class="card-body">
        {#if recentRepairs.length === 0}
          <div class="empty-state">
            <div class="empty-state-icon">📋</div>
            <p class="empty-state-title">No hay reparaciones</p>
            <p class="empty-state-description">Las reparaciones aparecerán aquí</p>
          </div>
        {:else}
          <div class="table-container">
            <table class="table">
              <thead>
                <tr>
                  <th>Número</th>
                  <th>Dispositivo</th>
                  <th>Estado</th>
                  <th>Fecha</th>
                  <th>Prioridad</th>
                </tr>
              </thead>
              <tbody>
                {#each recentRepairs as repair}
                  <tr>
                    <td class="font-medium">{repair.repair_number}</td>
                    <td>
                      {repair.device?.brand} {repair.device?.model}
                    </td>
                    <td>
                      <span class="badge {getStatusBadge(repair.status)}">
                        {formatStatus(repair.status)}
                      </span>
                    </td>
                    <td>{formatDate(repair.created_at)}</td>
                    <td>
                      <span class="badge badge-{
                        repair.priority === 'urgent' ? 'danger' :
                        repair.priority === 'high' ? 'warning' :
                        'secondary'
                      }">
                        {repair.priority}
                      </span>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/if}
      </div>
    </div>
  {/if}
  </div>
</Layout>

<style>
  .dashboard {
    max-width: 1200px;
  }

  .page-header {
    margin-bottom: 1.5rem;
  }

  .page-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--dark);
    margin-bottom: 0.25rem;
  }

  .page-subtitle {
    color: var(--text-light);
    font-size: 0.875rem;
  }

  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    color: var(--text-light);
  }

  .loading-state .spinner {
    margin-bottom: 1rem;
  }

  .stat-card {
    background: white;
    padding: 1.25rem;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: var(--radius);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .stat-icon svg {
    width: 24px;
    height: 24px;
  }

  .icon-primary {
    background: #dbeafe;
    color: var(--primary);
  }

  .icon-success {
    background: #d1fae5;
    color: var(--success);
  }

  .icon-info {
    background: #dbeafe;
    color: var(--primary);
  }

  .icon-warning {
    background: #fef3c7;
    color: var(--warning);
  }

  .stat-content {
    flex: 1;
    min-width: 0;
  }

  .stat-label {
    font-size: 0.875rem;
    color: var(--text-light);
    margin-bottom: 0.25rem;
  }

  .stat-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--dark);
    line-height: 1;
  }

  .stat-change {
    font-size: 0.75rem;
    color: var(--text-light);
    margin-top: 0.25rem;
  }

  .card-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--dark);
  }

  :global(.text-danger) {
    color: var(--danger);
  }
</style>
