<script>
  import { cart, cartTotal } from '../../stores/cart';
  import { notify } from '../../stores/auth';
  import { fade, fly, slide } from 'svelte/transition';

  export let onCheckout = () => {};

  let paymentMethod = 'cash';
  let amountPaid = '';

  $: total = $cartTotal;
  // Auto-fill amount paid if fully empty, otherwise let user adjust
  $: if (!amountPaid && total > 0) amountPaid = total;
  $: change = Math.max(0, (amountPaid || 0) - total);

  function updateQuantity(id, type, delta) {
    const item = $cart.find(i => i.id === id && i.type === type);
    if (!item || item.type === 'repair') return;
    cart.updateQuantity(id, type, item.quantity + delta);
  }

  function removeItem(id, type) {
    cart.removeItem(id, type);
  }

  async function handleCheckout() {
    if ($cart.length === 0) {
      notify('El carrito está vacío', 'warning');
      return;
    }
    if (amountPaid < total) {
      notify('El monto pagado es insuficiente', 'danger');
      return;
    }

    try {
      await onCheckout({
        items: $cart,
        payment_method: paymentMethod,
        amount_paid: amountPaid,
        total: total,
        change: change
      });
      // Clear cart on success
      cart.clear();
      amountPaid = '';
    } catch (error) {
      notify('Error al procesar el pago: ' + error.message, 'danger');
    }
  }
</script>

<div class="cart-premium-container flex flex-col h-full bg-[#0f172a] text-white font-['Outfit']">
  <!-- Header -->
  <div class="p-8 border-b border-white/5 bg-white/5 backdrop-blur-md">
    <div class="flex justify-between items-center">
      <h3 class="text-2xl font-black text-white tracking-tight flex items-center gap-3">
        <span class="text-3xl">🛒</span> MI CAJA
      </h3>
      <span class="bg-indigo-600/20 text-indigo-400 text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-wider border border-indigo-600/30">
        {$cart.length} items
      </span>
    </div>
  </div>

  <!-- Items List -->
  <div class="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar">
    {#if $cart.length === 0}
      <div class="flex flex-col items-center justify-center h-full opacity-20 text-center py-20" in:fade>
        <svg class="w-24 h-24 mb-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
          <circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle>
          <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
        </svg>
        <p class="text-xl font-black uppercase tracking-widest">Caja vacía</p>
        <p class="text-[10px] mt-2 font-bold opacity-60">Agrega servicios o productos de la tienda</p>
      </div>
    {:else}
      {#each $cart as item (item.type + '-' + item.id)}
        <div 
          class="bg-white/5 backdrop-blur-sm p-4 rounded-2xl border border-white/10 flex justify-between items-center group hover:border-indigo-500/50 transition-all"
          in:fly={{ x: 20, duration: 300 }}
          out:slide
        >
          <div class="flex flex-col flex-1">
            <span class="font-bold text-white line-clamp-1 leading-tight text-sm uppercase tracking-tight">{item.name}</span>
            <span class="text-xs text-indigo-400 font-black mt-1">${item.unit_price.toFixed(2)}</span>
          </div>
          
          <div class="flex items-center gap-3 ml-4">
            {#if item.type === 'product' || item.type === 'extra'}
              <div class="flex items-center bg-black/40 p-1 rounded-xl border border-white/5">
                <button class="w-7 h-7 flex items-center justify-center hover:bg-white/10 rounded-lg transition-all font-black text-indigo-400" on:click={() => updateQuantity(item.id, item.type, -1)}>-</button>
                <span class="w-8 text-center font-black text-xs">{item.quantity}</span>
                <button class="w-7 h-7 flex items-center justify-center hover:bg-white/10 rounded-lg transition-all font-black text-indigo-400" on:click={() => updateQuantity(item.id, item.type, 1)}>+</button>
              </div>
            {:else}
              <span class="text-[9px] font-black px-2 py-1 bg-indigo-600/20 text-indigo-400 rounded-lg uppercase tracking-widest border border-indigo-600/30">Servicio</span>
            {/if}
            
            <button class="text-white/20 hover:text-red-500 transition-colors p-2" on:click={() => removeItem(item.id, item.type)}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" class="w-4 h-4">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>
      {/each}
    {/if}
  </div>

  <!-- Checkout Section -->
  <div class="p-8 bg-black/40 border-t border-white/10 backdrop-blur-xl">
    <div class="flex justify-between items-end mb-8">
      <div>
        <p class="text-[10px] font-black text-white/40 uppercase tracking-[0.2em] mb-1">Total a Pagar</p>
        <p class="text-5xl font-black text-white tracking-tighter">${total.toFixed(2)}</p>
      </div>
    </div>

    <div class="space-y-5 mb-8">
      <div class="form-control">
        <label for="payment-method" class="label pb-1"><span class="label-text font-black text-[10px] text-white/40 uppercase tracking-widest">Método</span></label>
        <select id="payment-method" class="bg-white/5 border border-white/10 rounded-xl h-12 w-full px-4 font-bold text-sm text-white focus:border-indigo-500 outline-none transition-all cursor-pointer" bind:value={paymentMethod}>
          <option value="cash" class="bg-[#0f172a]">💵 Efectivo</option>
          <option value="credit_card" class="bg-[#0f172a]">💳 Tarjeta</option>
          <option value="transfer" class="bg-[#0f172a]">🏦 Transferencia</option>
        </select>
      </div>

      {#if paymentMethod === 'cash'}
        <div class="form-control" in:slide>
          <label for="amount-paid" class="label pb-1"><span class="label-text font-black text-[10px] text-white/40 uppercase tracking-widest">Efectivo Recibido</span></label>
          <div class="relative">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 font-black text-white/30">$</span>
            <input id="amount-paid" name="amount-paid" type="number" class="bg-white/5 border border-white/10 rounded-xl h-12 w-full pl-8 pr-4 font-black text-lg text-white focus:border-indigo-500 outline-none transition-all" bind:value={amountPaid} min={total} step="0.01">
          </div>
        </div>
        {#if change > 0}
          <div class="flex justify-between items-center p-4 bg-green-500/10 rounded-2xl border border-green-500/20 border-dashed" in:fade>
            <span class="text-green-400 font-black uppercase text-[10px] tracking-widest">Su cambio</span>
            <span class="text-green-400 font-black text-xl">${change.toFixed(2)}</span>
          </div>
        {/if}
      {/if}
    </div>

    <button 
      class="w-full h-16 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-white/20 text-white font-black rounded-xl transition-all active:scale-[0.98] shadow-lg shadow-indigo-600/20 uppercase tracking-widest text-sm flex items-center justify-center gap-3" 
      disabled={$cart.length === 0 || (paymentMethod === 'cash' && amountPaid < total)}
      on:click={handleCheckout}
    >
      <span>✅</span> FINALIZAR COBRO
    </button>
  </div>
</div>

<style>
  .custom-scrollbar::-webkit-scrollbar {
    width: 5px;
  }
  .custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.2);
  }

  /* Animación para entrada de items */
  @keyframes flyIn {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
  }
</style>
