<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import { notify } from '../stores/auth';
  import { api } from '../stores/api';

  let isLoading = true;
  let hasUsers = false;

  let setupData = {
    username: '',
    email: '',
    full_name: '',
    phone: '',
    password: '',
    confirmPassword: ''
  };
  let setupError = '';
  let isSettingUp = false;

  onMount(async () => {
    try {
      const status = await api.checkStatus();
      if (!status.needs_setup) {
        navigate('/login');
        return;
      }
    } catch (err) {
      console.error('Error:', err);
    }
    isLoading = false;
  });

  async function handleSetup() {
    setupError = '';

    if (!setupData.username || !setupData.email || !setupData.full_name || !setupData.password) {
      setupError = 'Todos los campos son requeridos';
      return;
    }

    if (setupData.password !== setupData.confirmPassword) {
      setupError = 'Las contraseñas no coinciden';
      return;
    }

    if (setupData.password.length < 6) {
      setupError = 'La contraseña debe tener al menos 6 caracteres';
      return;
    }

    isSettingUp = true;

    try {
      await api.setup({
        username: setupData.username,
        email: setupData.email,
        full_name: setupData.full_name,
        phone: setupData.phone || null,
        password: setupData.password,
        role: 'admin'
      });

      notify('Usuario administrador creado. Inicia sesión.', 'success');
      navigate('/login');
    } catch (err) {
      setupError = err.message;
      notify(err.message, 'danger');
    } finally {
      isSettingUp = false;
    }
  }
</script>

<div class="login-container">
  <div class="login-card card">
    {#if isLoading}
      <div class="loading-state">
        <div class="spinner"></div>
        <p>Cargando...</p>
      </div>
    {:else}
      <div class="login-header">
        <div class="logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
          </svg>
        </div>
        <h1>Configuración Inicial</h1>
        <p>Crear usuario administrador</p>
      </div>

      <form class="login-form" on:submit|preventDefault={handleSetup}>
        {#if setupError}
          <div class="alert alert-danger">
            {setupError}
          </div>
        {/if}

        <div class="form-group">
          <label class="label" for="setup-username">Usuario *</label>
          <input id="setup-username" type="text" class="input" bind:value={setupData.username} placeholder="Nombre de usuario" />
        </div>

        <div class="form-group">
          <label class="label" for="setup-email">Email *</label>
          <input id="setup-email" type="email" class="input" bind:value={setupData.email} placeholder="correo@ejemplo.com" />
        </div>

        <div class="form-group">
          <label class="label" for="setup-fullname">Nombre completo *</label>
          <input id="setup-fullname" type="text" class="input" bind:value={setupData.full_name} placeholder="Nombre completo" />
        </div>

        <div class="form-group">
          <label class="label" for="setup-phone">Teléfono</label>
          <input id="setup-phone" type="tel" class="input" bind:value={setupData.phone} placeholder="Número de teléfono" />
        </div>

        <div class="form-group">
          <label class="label" for="setup-password">Contraseña *</label>
          <input id="setup-password" type="password" class="input" bind:value={setupData.password} placeholder="Mínimo 6 caracteres" />
        </div>

        <div class="form-group">
          <label class="label" for="setup-confirm">Confirmar contraseña *</label>
          <input id="setup-confirm" type="password" class="input" bind:value={setupData.confirmPassword} placeholder="Repite la contraseña" />
        </div>

        <button type="submit" class="btn btn-primary w-full" disabled={isSettingUp}>
          {#if isSettingUp}
            <span class="spinner" style="width: 18px; height: 18px; border-width: 2px;"></span>
            Creando...
          {:else}
            Crear Administrador
          {/if}
        </button>
      </form>
    {/if}
  </div>
</div>

<style>
  .login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  .login-card {
    width: 100%;
    max-width: 400px;
  }

  .login-header {
    text-align: center;
    padding: 2rem 1.5rem 1.5rem;
  }

  .logo {
    width: 64px;
    height: 64px;
    margin: 0 auto 1rem;
    background: var(--primary);
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .logo svg {
    width: 36px;
    height: 36px;
  }

  .login-header h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--dark);
    margin-bottom: 0.25rem;
  }

  .login-header p {
    color: var(--text-light);
    font-size: 0.875rem;
  }

  .login-form {
    padding: 0 1.5rem 1.5rem;
  }

  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    color: var(--text-light);
  }
</style>
