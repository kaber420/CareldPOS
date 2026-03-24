<script>
  import { cartItemsCount, cartTotal } from '../../stores/cart';
  import { isCartOpen } from '../../stores/cartUI';
  import POSCart from './POSCart.svelte';
  import { slide } from 'svelte/transition';

  export let onCheckout = () => {};

  let showBadgeAnimation = false;
  let lastCount = 0;

  $: if ($cartItemsCount > lastCount) {
    showBadgeAnimation = true;
    setTimeout(() => showBadgeAnimation = false, 1000);
    lastCount = $cartItemsCount;
  } else if ($cartItemsCount < lastCount) {
    lastCount = $cartItemsCount;
  }

  function toggleCart() {
    isCartOpen.update(v => !v);
  }
</script>

<div class="floating-accordion-container">
  <!-- The Accordion Panel -->
  {#if $isCartOpen}
    <div 
      class="accordion-panel shadow-2xl overflow-hidden border-2 border-indigo-500/50"
      transition:slide={{ duration: 400 }}
    >
      <POSCart {onCheckout} />
    </div>
  {/if}

  <!-- The Toggle Bar / FAB -->
  <div class="toggle-bar shadow-2xl border-2 border-indigo-500/30">
    <button 
      class="flex items-center gap-4 px-6 py-4 w-full h-full text-white"
      on:click={toggleCart}
    >
      <div class="icon-container relative">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        {#if $cartItemsCount > 0}
          <span class="badge {showBadgeAnimation ? 'animate-bounce' : ''}">
            {$cartItemsCount}
          </span>
        {/if}
      </div>
      
      <div class="flex-1 text-left">
        <span class="text-xs font-black uppercase opacity-60 tracking-widest block leading-none mb-1">Caja Registradora</span>
        <span class="text-lg font-black tracking-tight leading-none">
          {#if $cartItemsCount > 0}
            ${($cartTotal || 0).toFixed(2)}
          {:else}
            Vacía
          {/if}
        </span>
      </div>

      <div class="toggle-icon { $isCartOpen ? 'rotate-180' : '' } transition-transform">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
        </svg>
      </div>
    </button>
  </div>
</div>

<style>
  .floating-accordion-container {
    position: fixed;
    bottom: 1.5rem;
    right: 1.5rem;
    width: 400px;
    max-width: calc(100vw - 3rem);
    z-index: 1000;
    font-family: 'Outfit', sans-serif;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    pointer-events: auto;
  }

  .accordion-panel {
    background-color: #0f172a;
    border-radius: 2rem;
    height: 600px;
    max-height: calc(100vh - 10rem);
    display: flex;
    flex-direction: column;
  }

  .toggle-bar {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    border-radius: 1.5rem;
    overflow: hidden;
    height: 72px;
    transition: all 0.3s ease;
  }

  .toggle-bar:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(99, 102, 241, 0.4);
  }

  .badge {
    position: absolute;
    top: -10px;
    right: -10px;
    background-color: #ef4444;
    color: white;
    font-size: 10px;
    font-weight: 900;
    padding: 2px 6px;
    border-radius: 999px;
    border: 2px solid #4f46e5;
    box-shadow: 0 4px 6px rgba(0,0,0,0.2);
  }

  .toggle-icon {
    background: rgba(255, 255, 255, 0.1);
    padding: 8px;
    border-radius: 50%;
  }
</style>
