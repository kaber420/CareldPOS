<script>
  import { navigate } from 'svelte-routing';
</script>

<div class="not-found">
  <div class="not-found-content">
    <div class="not-found-icon">404</div>
    <h1 class="not-found-title">Página no encontrada</h1>
    <p class="not-found-description">
      La página que estás buscando no existe o fue movida.
    </p>
    <button class="btn btn-primary btn-lg" on:click={() => navigate('/dashboard')}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
        <polyline points="9 22 9 12 15 12 15 22"/>
      </svg>
      Volver al Dashboard
    </button>
  </div>
</div>

<style>
  .not-found {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    background: var(--light);
  }

  .not-found-content {
    text-align: center;
    max-width: 500px;
  }

  .not-found-icon {
    font-size: 6rem;
    font-weight: 700;
    color: var(--border);
    margin-bottom: 1rem;
  }

  .not-found-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--dark);
    margin-bottom: 0.5rem;
  }

  .not-found-description {
    color: var(--text-light);
    font-size: 1rem;
    margin-bottom: 2rem;
  }
</style>
