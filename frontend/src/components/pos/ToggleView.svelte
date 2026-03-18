<script>
  export let viewMode = 'grid'; // 'grid' o 'list'
  
  function setView(mode) {
    viewMode = mode;
  }
</script>

<div class="toggle-view">
  <button
    class="toggle-btn {viewMode === 'list' ? 'active' : ''}"
    on:click={() => setView('list')}
    title="Vista de lista"
  >
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <line x1="8" y1="6" x2="21" y2="6"/>
      <line x1="8" y1="12" x2="21" y2="12"/>
      <line x1="8" y1="18" x2="21" y2="18"/>
      <line x1="3" y1="6" x2="3.01" y2="6"/>
      <line x1="3" y1="12" x2="3.01" y2="12"/>
      <line x1="3" y1="18" x2="3.01" y2="18"/>
    </svg>
    <span class="btn-label">Lista</span>
  </button>
  
  <button
    class="toggle-btn {viewMode === 'grid' ? 'active' : ''}"
    on:click={() => setView('grid')}
    title="Vista de cuadrícula"
  >
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <rect x="3" y="3" width="7" height="7"/>
      <rect x="14" y="3" width="7" height="7"/>
      <rect x="14" y="14" width="7" height="7"/>
      <rect x="3" y="14" width="7" height="7"/>
    </svg>
    <span class="btn-label">Cuadrícula</span>
  </button>
</div>

<style>
  .toggle-view {
    display: flex;
    gap: 0.5rem;
    background: var(--light);
    padding: 0.25rem;
    border-radius: var(--radius);
  }

  .toggle-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    border: none;
    background: transparent;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all 0.2s;
    color: var(--text-light);
    font-size: 0.875rem;
  }

  .toggle-btn svg {
    width: 18px;
    height: 18px;
  }

  .toggle-btn:hover:not(.active) {
    background: white;
    color: var(--text);
    box-shadow: var(--shadow);
  }

  .toggle-btn.active {
    background: white;
    color: var(--primary);
    box-shadow: var(--shadow);
  }

  .btn-label {
    display: none;
  }

  @media (min-width: 640px) {
    .btn-label {
      display: inline;
    }
  }
</style>
