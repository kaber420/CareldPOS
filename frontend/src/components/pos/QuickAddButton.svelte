<script>
  export let onClick = () => {};
  export let label = 'Nueva Recepción';
</script>

<button class="fab-button" on:click={onClick} title={label}>
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <line x1="12" y1="5" x2="12" y2="19"/>
    <line x1="5" y1="12" x2="19" y2="12"/>
  </svg>
  <span class="fab-label">{label}</span>
</button>

<style>
  .fab-button {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: var(--primary);
    color: white;
    border: none;
    box-shadow: var(--shadow-lg);
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 100;
  }

  .fab-button:hover {
    transform: scale(1.1) translateY(-2px);
    box-shadow: 0 8px 25px rgba(37, 99, 235, 0.4);
    background: var(--primary-dark);
  }

  .fab-button:active {
    transform: scale(0.95);
  }

  .fab-button svg {
    width: 28px;
    height: 28px;
    transition: transform 0.3s;
  }

  .fab-button:hover svg {
    transform: rotate(90deg);
  }

  .fab-label {
    position: absolute;
    right: 64px;
    background: var(--dark);
    color: white;
    padding: 0.375rem 0.75rem;
    border-radius: var(--radius-sm);
    font-size: 0.8125rem;
    font-weight: 500;
    white-space: nowrap;
    opacity: 0;
    pointer-events: none;
    transition: all 0.2s;
    transform: translateX(10px);
  }

  .fab-label::after {
    content: '';
    position: absolute;
    right: -6px;
    top: 50%;
    transform: translateY(-50%);
    border-width: 6px 0 6px 6px;
    border-style: solid;
    border-color: transparent transparent transparent var(--dark);
  }

  .fab-button:hover .fab-label {
    opacity: 1;
    transform: translateX(0);
  }

  @media (max-width: 640px) {
    .fab-button {
      bottom: 1.5rem;
      right: 1.5rem;
      width: 52px;
      height: 52px;
    }

    .fab-button svg {
      width: 24px;
      height: 24px;
    }

    .fab-label {
      display: none;
    }
  }
</style>
