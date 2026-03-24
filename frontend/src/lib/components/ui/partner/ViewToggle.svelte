<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  export let currentView = 'grid'; // 'grid' or 'table'
</script>

<div class="view-toggle">
  <button 
    class="toggle-btn {currentView === 'table' ? 'active' : ''}" 
    on:click={() => dispatch('change', 'table')}
    title="Vista de Lista"
  >
    <span>☰</span>
  </button>
  <button 
    class="toggle-btn {currentView === 'grid' ? 'active' : ''}" 
    on:click={() => dispatch('change', 'grid')}
    title="Vista de Cuadrícula"
  >
    <span>▤</span>
  </button>
</div>

<style>
  .view-toggle {
    display: flex;
    background: rgba(255, 255, 255, 0.05);
    padding: 4px;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    width: fit-content;
  }

  .toggle-btn {
    background: transparent;
    border: none;
    color: #94a3b8;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.2s, color 0.2s;
    font-size: 1.1rem;
  }

  .toggle-btn:hover:not(.active) {
    background: rgba(255, 255, 255, 0.05);
    color: white;
  }

  .toggle-btn.active {
    background: #6366f1;
    color: white;
  }
</style>
