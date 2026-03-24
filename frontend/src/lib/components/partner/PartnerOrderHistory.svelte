<script>
  import { onMount } from 'svelte';
  import { api } from '../../../stores/api';
  import { notify } from '../../../stores/auth';
  import { fade, fly, scale } from 'svelte/transition';

  export let orders = [];
  let loading = true;

  export async function refreshOrders() {
    loading = true;
    try {
      orders = await api.getMyPartnerOrders();
    } catch (error) {
      notify('Error al cargar historial', 'error');
    } finally {
      loading = false;
    }
  }

  onMount(refreshOrders);

  function getStatusLabel(status) {
    const labels = {
      'pending': 'Pendiente',
      'confirmed': 'Confirmado',
      'cancelled': 'Cancelado',
      'completed': 'Completado'
    };
    return labels[status] || status;
  }

  function getStatusClass(status) {
    const classes = {
      'pending': 'bg-yellow-100 text-yellow-700 dark-bg-yellow-900-20 dark-text-yellow-400',
      'confirmed': 'bg-blue-100 text-blue-700 dark-bg-blue-900-20 dark-text-blue-400',
      'cancelled': 'bg-red-100 text-red-700 dark-bg-red-900-20 dark-text-red-400',
      'completed': 'bg-green-100 text-green-700 dark-bg-green-900-20 dark-text-green-400'
    };
    return classes[status] || 'bg-gray-100 text-gray-700';
  }
</script>

<div class="order-history space-y-6">
  {#if loading && orders.length === 0}
    <div class="flex flex-col items-center justify-center p-20 gap-4" in:fade>
      <div class="spinner-premium mx-auto"></div>
      <p class="text-gray-400 font-bold animate-pulse">Consultando historial...</p>
    </div>
  {:else if orders.length === 0}
    <div class="text-center p-20 glass-premium rounded-[2.5rem] border-dashed" in:scale>
      <div class="text-5xl mb-4 opacity-10">📑</div>
      <p class="text-gray-500 font-medium">Aún no has realizado pedidos de refacciones.</p>
    </div>
  {:else}
    {#each orders as order, i}
      <div 
        class="order-item glass-premium p-8 rounded-[2rem] hover-shadow transition-all duration-500 hover-move-up group"
        in:fly={{ y: 20, duration: 600, delay: i * 100 }}
      >
        <div class="flex flex-wrap justify-between items-start gap-6 mb-8 pb-6 border-b border-gray-100 dark-border-gray-800">
          <div class="space-y-2">
            <div class="flex items-center gap-4">
              <span class="text-xl font-black text-gray-900 dark-text-white tracking-tighter">{order.order_number}</span>
              <span class="px-4 py-1-5 rounded-full text-[10px] font-black uppercase tracking-widest {getStatusClass(order.status)} shadow-sm">
                {getStatusLabel(order.status)}
              </span>
            </div>
            <p class="text-[10px] text-gray-400 font-black uppercase tracking-[0.2em] flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {new Date(order.created_at).toLocaleDateString()} • {new Date(order.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
            </p>
          </div>
          <div class="text-right">
            <span class="text-[10px] text-indigo-500 font-black uppercase block mb-1">Total del Pedido</span>
            <span class="text-3xl font-black text-gray-900 dark-text-white tracking-tighter">${order.total.toFixed(2)}</span>
          </div>
        </div>

        <div class="items-list space-y-3 mb-8">
          {#each order.items as item}
            <div class="flex justify-between items-center text-sm py-3 px-4 rounded-xl bg-gray-50-50 dark-bg-gray-900-30 border border-gray-50-50 dark-border-gray-800 transition-colors group:hover .group-hover-border-indigo-500-10">
              <div class="flex items-center gap-3">
                <span class="flex h-6 w-6 items-center justify-center rounded-lg bg-indigo-600 text-white text-[10px] font-black">
                  {item.quantity}
                </span>
                <span class="text-gray-700 dark-text-gray-300 font-bold uppercase tracking-tight">
                  {item.inventory_item?.name || 'Producto'}
                </span>
              </div>
              <span class="font-black text-gray-900 dark-text-white">
                ${item.subtotal.toFixed(2)}
              </span>
            </div>
          {/each}
        </div>

        {#if order.notes}
          <div class="bg-indigo-50-50 dark-bg-indigo-900-10 p-4 rounded-2xl border-l-4 border-indigo-500 mb-8">
            <span class="text-[10px] font-black text-indigo-600 dark-text-indigo-400 uppercase tracking-widest block mb-2">Comentarios del Socio</span>
            <p class="text-sm text-gray-600 dark-text-gray-400 italic font-medium leading-relaxed">"{order.notes}"</p>
          </div>
        {/if}

        {#if order.status === 'confirmed'}
          <div class="bg-gradient p-6 rounded-2xl shadow-xl shadow-indigo-200/50 dark:shadow-none" in:scale>
            <div class="flex items-center gap-4 text-white">
              <div class="bg-white-10 p-3 rounded-xl backdrop-blur-md">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <div>
                <p class="font-black text-lg leading-tight uppercase tracking-tight">¡Listo para Recoger!</p>
                <p class="text-xs text-white-80 font-medium">Puedes pasar por tus piezas en el mostrador principal.</p>
              </div>
            </div>
          </div>
        {/if}
      </div>
    {/each}
  {/if}
</div>
