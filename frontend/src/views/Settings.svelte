<script>
  import { onMount } from 'svelte';
  import { settings, fetchAllSettings, updateSetting } from '../stores/settings';
  import { notify } from '../stores/auth';

  let loading = true;
  let saving = false;

  onMount(async () => {
    await fetchAllSettings();
    loading = false;
  });

  async function handleSave(key, value) {
    saving = true;
    try {
      await updateSetting(key, value);
      notify('Configuración actualizada', 'success');
    } catch (error) {
      notify('Error al actualizar configuración', 'error');
    } finally {
      saving = false;
    }
  }

  let localValues = {
    store_name: '',
    portal_url: '',
    ticket_footer: ''
  };

  $: if ($settings.isLoaded) {
    localValues = {
      store_name: $settings.store_name?.value || '',
      portal_url: $settings.portal_url?.value || '',
      ticket_footer: $settings.ticket_footer?.value || ''
    };
  }
</script>

<div class="settings-container">
  <header class="page-header">
    <div>
      <h1 class="page-title">Configuración del Sistema</h1>
      <p class="page-subtitle">Gestiona las preferencias y personalización de tu plataforma</p>
    </div>
  </header>

  {#if loading}
    <div class="loading-state">
      <div class="spinner"></div>
      <p>Cargando configuraciones...</p>
    </div>
  {:else}
    <div class="settings-grid">
      <!-- SECCIÓN: TICKET Y PORTAL -->
      <section class="settings-card">
        <div class="card-header">
          <div class="card-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2M6 14h12v8H6v-8z"/>
            </svg>
          </div>
          <h2 class="card-title">Tickets y Portal de Clientes</h2>
        </div>
        
        <div class="card-body">
          <div class="form-group">
            <label for="store_name">Nombre de la Tienda</label>
            <div class="input-with-action">
              <input 
                type="text" 
                id="store_name" 
                bind:value={localValues.store_name} 
                placeholder="Ej: CareldPOS"
              />
              <button 
                class="btn btn-sm btn-primary" 
                disabled={saving || localValues.store_name === $settings.store_name?.value}
                on:click={() => handleSave('store_name', localValues.store_name)}
              >
                Guardar
              </button>
            </div>
            <p class="field-help">Aparece en la cabecera de todos los tickets impresos.</p>
          </div>

          <div class="form-group">
            <label for="portal_url">URL del Portal de Clientes</label>
            <div class="input-with-action">
              <input 
                type="text" 
                id="portal_url" 
                bind:value={localValues.portal_url} 
                placeholder="https://tu-dominio.com"
              />
              <button 
                class="btn btn-sm btn-primary" 
                disabled={saving || localValues.portal_url === $settings.portal_url?.value}
                on:click={() => handleSave('portal_url', localValues.portal_url)}
              >
                Guardar
              </button>
            </div>
            <p class="field-help">URL que se usará para generar el código QR de seguimiento. Si se deja vacío, se usará el dominio actual.</p>
          </div>

          <div class="form-group">
            <label for="ticket_footer">Pie de página del Ticket</label>
            <div class="input-with-action">
              <textarea 
                id="ticket_footer" 
                bind:value={localValues.ticket_footer} 
                rows="2"
              ></textarea>
              <button 
                class="btn btn-sm btn-primary" 
                disabled={saving || localValues.ticket_footer === $settings.ticket_footer?.value}
                on:click={() => handleSave('ticket_footer', localValues.ticket_footer)}
              >
                Guardar
              </button>
            </div>
            <p class="field-help">Mensaje personalizado que aparece al final de los tickets.</p>
          </div>
        </div>
      </section>

      <!-- SECCIÓN: PRÓXIMAMENTE -->
      <section class="settings-card coming-soon">
        <div class="card-header">
          <div class="card-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/>
            </svg>
          </div>
          <h2 class="card-title">Otras Configuraciones</h2>
        </div>
        <div class="card-body">
          <p class="empty-text">Próximamente: Configuración de impresoras, impuestos, y notificaciones por correo.</p>
        </div>
      </section>
    </div>
  {/if}
</div>

<style>
  .settings-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: 2rem;
  }

  .page-header {
    margin-bottom: 2.5rem;
  }

  .page-title {
    font-size: 1.875rem;
    font-weight: 700;
    color: var(--dark);
    margin: 0;
  }

  .page-subtitle {
    font-size: 1rem;
    color: var(--text-light);
    margin-top: 0.5rem;
  }

  .settings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2rem;
  }

  .settings-card {
    background: var(--white);
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    overflow: hidden;
    border: 1px solid var(--border-light);
  }

  .card-header {
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    border-bottom: 1px solid var(--border-light);
    background: var(--light);
  }

  .card-icon {
    width: 40px;
    height: 40px;
    background: var(--primary-light);
    color: var(--primary);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .card-icon svg {
    width: 24px;
    height: 24px;
  }

  .card-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 0;
    color: var(--dark);
  }

  .card-body {
    padding: 1.5rem;
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  .form-group:last-child {
    margin-bottom: 0;
  }

  label {
    display: block;
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--dark);
    margin-bottom: 0.5rem;
  }

  .input-with-action {
    display: flex;
    gap: 0.75rem;
  }

  input, textarea {
    flex: 1;
    padding: 0.625rem 0.875rem;
    border: 1px solid var(--border-light);
    border-radius: 6px;
    font-size: 0.875rem;
    transition: all 0.2s;
  }

  input:focus, textarea:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px var(--primary-light);
  }

  .field-help {
    font-size: 0.75rem;
    color: var(--text-light);
    margin-top: 0.375rem;
  }

  .coming-soon {
    opacity: 0.7;
    background: var(--light);
  }

  .empty-text {
    font-style: italic;
    color: var(--text-light);
    text-align: center;
    padding: 2rem;
  }

  .loading-state {
    text-align: center;
    padding: 4rem;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border-light);
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin: 0 auto 1.5rem;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  @media (max-width: 640px) {
    .settings-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
