<script>
  import { onMount } from 'svelte';
  import { notify } from '../stores/auth';

  let repair = null;
  let loading = true;
  let error = null;
  let approvalStatus = null; // null = pending, true = approved, false = rejected

  // Extract token from URL (assuming route is /portal/:token)
  const token = window.location.pathname.split('/').pop();

  onMount(async () => {
    if (!token) {
      error = 'Invalid portal link';
      loading = false;
      return;
    }

    try {
      const response = await fetch(`/api/v1/repairs/portal/${token}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      repair = await response.json();
      // Determine approval status from the repair object
      if (repair.client_approved === true) {
        approvalStatus = true;
      } else if (repair.client_approved === false) {
        approvalStatus = false;
      } else {
        approvalStatus = null; // pending
      }
    } catch (err) {
      error = 'Failed to load repair details. The link may be expired or invalid.';
      console.error(err);
    } finally {
      loading = false;
    }
  });

  async function approve() {
    try {
      const response = await fetch(`/api/v1/repairs/portal/${token}/approve`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      // Update local state
      repair.client_approved = true;
      approvalStatus = true;
      notify('¡Gracias por aprobar el presupuesto!', 'success');
    } catch (err) {
      notify('Error al aprobar el presupuesto. Por favor, inténtalo de nuevo.', 'error');
      console.error(err);
    }
  }

  async function reject() {
    try {
      const response = await fetch(`/api/v1/repairs/portal/${token}/reject`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      // Update local state
      repair.client_approved = false;
      approvalStatus = false;
      notify('Hemos registrado tu rechazo. Nos pondremos en contacto contigo.', 'info');
    } catch (err) {
      notify('Error al rechazar el presupuesto. Por favor, inténtalo de nuevo.', 'error');
      console.error(err);
    }
  }
</script>

<div class="client-portal">
  {#if loading}
    <div class="loading">
      <div class="spinner"></div>
      <p>Cargando información de tu reparación...</p>
    </div>
  {:else if error}
    <div class="error">
      <p>{error}</p>
      <p>Si crees que esto es un error, por favor contacta al taller directamente.</p>
    </div>
  {:else if repair}
    <div class="repair-info">
      <h1>Estado de tu Reparación</h1>
      <div class="repair-details">
        <p><strong>Orden:</strong> {repair.repair_number}</p>
        <p><strong>Dispositivo:</strong> {repair.device.brand} {repair.device.model}</p>
        <p><strong>Problema reportado:</strong> {repair.description}</p>
        <p><strong>Estado actual:</strong>
          <span class="status-{repair.status.toLowerCase()}">
            {#if repair.status === 'pending'}Pendiente de revisión
            {:else if repair.status === 'diagnosing'}En diagnóstico
            {:else if repair.status === 'waiting_approval'}Esperando tu aprobación
            {:else if repair.status === 'in_progress'}En reparación
            {:else if repair.status === 'waiting_parts'}Esperando repuestos
            {:else if repair.status === 'completed'}Reparación completada
            {:else if repair.status === 'delivered'}Entregado
            {:else if repair.status === 'cancelled'}Cancelada
            {/if}
          </span>
        </p>
        {#if repair.diagnosis}
          <p><strong>Diagnóstico:</strong> {repair.diagnosis}</p>
        {/if}
        {#if repair.notes}
          <p><strong>Notas del taller:</strong> {repair.notes}</p>
        {/if}
      </div>

      {#if (repair.estimated_cost !== null || repair.final_cost !== null) && approvalStatus === null}
        <div class="cost-section">
          <h2>Presupuesto</h2>
          <p>
            {#if repair.final_cost !== null}
              Costo final: ${repair.final_cost.toFixed(2)}
            {:else if repair.estimated_cost !== null}
              Costo estimado: ${repair.estimated_cost.toFixed(2)}
            {/if}
          </p>
          <p class="cost-note">Este costo incluye mano de obra y repuestos.</p>
          <div class="button-group">
            <button on:click={approve} class="btn approve">Aprobar Presupuesto</button>
            <button on:click={reject} class="btn reject">Rechazar Presupuesto</button>
          </div>
        </div>
      {:else if approvalStatus === true}
        <div class="approval-status approved">
          <p>✅ Has aprobado el presupuesto. ¡Gracias!</p>
          <p>Nos pondremos en contacto contigo cuando la reparación esté completa.</p>
        </div>
      {:else if approvalStatus === false}
        <div class="approval-status rejected">
          <p>❌ Has rechazado el presupuesto.</p>
          <p>Nos pondremos en contacto contigo para discutir las opciones.</p>
        </div>
      {/if}

      {#if repair.delivered_at}
        <div class="delivery-info">
          <p><strong>Fecha de entrega:</strong> {new Date(repair.delivered_at).toLocaleDateString()}</p>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .client-portal {
    max-width: 600px;
    margin: 2rem auto;
    padding: 0 1rem;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }

  .loading, .error {
    text-align: center;
    padding: 3rem;
    color: var(--dark);
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 4px solid var(--border-light);
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin: 0 auto 1rem;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .error {
    background-color: var(--error-light);
    border: 1px solid var(--error);
    border-radius: 4px;
    padding: 1.5rem;
  }

  .repair-info {
    background-color: var(--white);
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    padding: 1.5rem;
  }

  .repair-details {
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-light);
  }

  .repair-details p {
    margin: 0.5rem 0;
    line-height: 1.5;
  }

  .status-pending { color: var(--warning); }
  .status-diagnosing { color: var(--info); }
  .status-waiting-approval { color: var(--warning); }
  .status-in-progress { color: var(--info); }
  .status-waiting-parts { color: var(--warning); }
  .status-completed { color: var(--success); }
  .status-delivered { color: var(--success); }
  .status-cancelled { color: var(--error); }

  .cost-section {
    background-color: var(--primary-light);
    border-left: 4px solid var(--primary);
    padding: 1rem;
    margin: 1.5rem 0;
    border-radius: 0 4px 4px 0;
  }

  .cost-section h2 {
    margin-top: 0;
    color: var(--primary);
  }

  .cost-note {
    font-size: 0.9rem;
    color: var(--dark);
    margin-top: 0.5rem;
  }

  .button-group {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
  }

  .btn {
    flex: 1;
    padding: 0.75rem;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .btn.approve {
    background-color: var(--success);
    color: white;
  }

  .btn.approve:hover {
    background-color: var(--success-dark);
  }

  .btn.reject {
    background-color: var(--error);
    color: white;
  }

  .btn.reject:hover {
    background-color: var(--error-dark);
  }

  .approval-status {
    padding: 1rem;
    border-radius: 4px;
    text-align: center;
    margin: 1.5rem 0;
  }

  .approval-status.approved {
    background-color: var(--success-light);
    border: 1px solid var(--success);
    color: var(--success-dark);
  }

  .approval-status.rejected {
    background-color: var(--error-light);
    border: 1px solid var(--error);
    color: var(--error-dark);
  }

  .delivery-info {
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border-light);
    font-size: 0.9rem;
    color: var(--dark);
  }

  /* Responsive */
  @media (max-width: 480px) {
    .client-portal {
      padding: 0;
    }
    
    .button-group {
      flex-direction: column;
    }
  }
</style>