<script>
  import { cart, cartTotal, cartItemsCount } from '../../../stores/cart';
  import { api } from '../../../stores/api';
  import { notify } from '../../../stores/auth';
  import { createEventDispatcher } from 'svelte';
  import { fade, fly, slide } from 'svelte/transition';

  const dispatch = createEventDispatcher();
  let isSubmitting = false;

  async function placeOrder() {
    if ($cart.length === 0) return;
    
    isSubmitting = true;
    try {
      const orderData = {
        items: $cart.map(item => ({
          inventory_item_id: item.id,
          quantity: item.quantity
        }))
      };

      const result = await api.createPartnerOrder(orderData);
      notify('Pedido enviado correctamente. Nos pondremos en contacto contigo.', 'success');
      cart.clear();
      dispatch('orderCreated', result);
    } catch (error) {
      notify(error.message || 'Error al enviar pedido', 'error');
    } finally {
      isSubmitting = false;
    }
  }

  function updateQuantity(id, delta) {
    cart.updateQuantity(id, delta);
  }

  function removeItem(id) {
    cart.removeItem(id);
  }
</script>

<div class="cart-container-solid flex flex-col h-full bg-slate-900 text-white">
  <!-- Header -->
  <div class="p-6 border-b border-slate-700 bg-slate-800/50 relative">
    <div class="flex justify-between items-center">
      <h2 class="text-xl font-black text-white flex items-center gap-3">
        <span class="text-2xl">🛒</span> MI PEDIDO
      </h2>
      <div class="flex items-center gap-3">
        <span class="bg-indigo-600 text-white text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-wider">
          {$cartItemsCount} artículos
        </span>
        <button 
          on:click={() => dispatch('close')} 
          class="p-2 hover:bg-slate-700 rounded-lg transition-colors text-slate-400 hover:text-white"
          aria-label="Cerrar"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </div>

  <!-- Items List -->
  <div class="flex-1 overflow-y-auto p-4 space-y-3">
    {#if $cart.length === 0}
      <div class="h-full flex flex-col items-center justify-center text-center py-20" in:fade>
        <div class="text-6xl mb-4 opacity-20">📦</div>
        <h3 class="text-lg font-bold text-slate-400">Tu carrito está vacío</h3>
        <p class="text-sm text-slate-500 mt-2 uppercase tracking-widest font-black">Explora el catálogo para agregar piezas</p>
      </div>
    {:else}
      {#each $cart as item, i (item.id || i)}
        <div 
          class="item-card group flex gap-4 p-3 rounded-xl border border-slate-700 bg-slate-800 hover:border-indigo-500/50 transition-all"
          in:fly={{ x: 20, duration: 400 }}
          out:slide
        >
          <div class="flex-1">
            <h4 class="font-bold text-white text-sm uppercase tracking-tight leading-tight mb-1">{item.name || 'Producto'}</h4>
            <div class="flex items-center gap-2">
              {#if item.unit_price && item.unit_price > 0}
                <span class="text-xs font-black text-indigo-400">${(item.unit_price || 0).toFixed(2)}</span>
              {:else}
                <span class="text-[9px] font-black text-orange-400 uppercase bg-orange-400/10 px-2 py-0.5 rounded border border-orange-400/20">Precio a convenir</span>
              {/if}
            </div>
          </div>

          <div class="flex flex-col items-center gap-1">
            <div class="flex items-center gap-3 bg-slate-900/50 rounded-lg p-1 px-2 border border-slate-700">
              <button 
                on:click={() => updateQuantity(item.id, item.quantity - 1, item.stock_quantity)}
                class="w-6 h-6 flex items-center justify-center bg-slate-700 hover:bg-indigo-600 rounded text-white transition-colors"
                disabled={item.quantity <= 1}
              >
                <span class="font-bold">-</span>
              </button>
              <span class="text-sm font-black w-4 text-center">{item.quantity}</span>
              <button 
                on:click={() => updateQuantity(item.id, item.quantity + 1, item.stock_quantity)}
                class="w-6 h-6 flex items-center justify-center bg-slate-700 hover:bg-indigo-600 rounded text-white transition-colors"
                disabled={item.quantity >= item.stock_quantity}
              >
                <span class="font-bold">+</span>
              </button>
            </div>
            {#if item.quantity >= item.stock_quantity}
              <span class="text-[9px] text-orange-400 font-bold uppercase">Límite alcanzado</span>
            {/if}
          </div>

          <button 
            on:click={() => removeItem(item.id)}
            class="p-2 text-slate-500 hover:text-red-400 transition-colors"
            aria-label="Eliminar"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      {/each}
    {/if}
  </div>

  <!-- Footer -->
  {#if $cart.length > 0}
    <div class="p-6 border-t border-slate-700 bg-slate-800/80">
      <div class="flex justify-between items-end mb-6">
        <div class="flex flex-col">
          <span class="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Total Estimado</span>
          <span class="text-3xl font-black text-indigo-400 tracking-tighter">${($cartTotal || 0).toFixed(2)}</span>
        </div>
        <div class="text-right">
          <span class="text-[10px] text-green-400 font-black uppercase bg-green-400/10 px-2 py-1 rounded border border-green-400/20">Pago vs Entrega</span>
        </div>
      </div>

      <button 
        on:click={placeOrder}
        disabled={isSubmitting}
        class="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 text-white font-black py-4 rounded-xl shadow-xl transition-all transform hover:scale-[1.02] active:scale-95 flex items-center justify-center gap-3 uppercase tracking-widest text-sm"
      >
        {#if isSubmitting}
          <div class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
          ENVIANDO...
        {:else}
          <span>🚀</span> ENVIAR PEDIDO
        {/if}
      </button>

      <p class="text-center text-[10px] text-slate-500 mt-4 uppercase font-bold tracking-tight">
        Al enviar el pedido, un asesor confirmará stock y precios finales.
      </p>
    </div>
  {/if}
</div>

<style>
  .cart-container-solid {
    font-family: 'Outfit', sans-serif;
  }
  
  /* Custom scrollbar */
  .overflow-y-auto::-webkit-scrollbar {
    width: 6px;
  }
  .overflow-y-auto::-webkit-scrollbar-track {
    background: transparent;
  }
  .overflow-y-auto::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 10px;
  }
  .overflow-y-auto::-webkit-scrollbar-thumb:hover {
    background: #475569;
  }
</style>
