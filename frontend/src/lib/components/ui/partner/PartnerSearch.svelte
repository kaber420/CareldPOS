<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  export let value = '';
  export let placeholder = 'Buscar por cliente o dispositivo...';
</script>

<div class="partner-search">
  <span class="search-icon">🔍</span>
  <input 
    type="text" 
    {placeholder}
    bind:value
    on:input={() => dispatch('input', value)}
  >
</div>

<style>
  .partner-search {
    position: relative;
    width: 100%;
    max-width: 500px;
  }

  .search-icon {
    position: absolute;
    left: 1.25rem;
    top: 50%;
    transform: translateY(-50%);
    opacity: 0.6;
    font-size: 1.1rem;
    pointer-events: none;
  }

  input {
    width: 100%;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 0.85rem 1.5rem;
    padding-left: 3.25rem;
    border-radius: 14px;
    color: white;
    outline: none;
    font-family: 'Outfit', sans-serif;
    font-size: 0.95rem;
    transition: border-color 0.2s, background 0.2s;
  }

  input:focus {
    border-color: #6366f1;
    background: rgba(255, 255, 255, 0.08);
  }

  input::placeholder {
    color: #94a3b8;
    opacity: 0.7;
  }
</style>
