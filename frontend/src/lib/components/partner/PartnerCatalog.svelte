<script>
  import { onMount } from 'svelte';
  import { api } from '../../../stores/api';
  import { cart } from '../../../stores/cart';
  import { notify } from '../../../stores/auth';
  import { fade, fly, scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';

  let products = [];
  let loading = true;
  let searchTerm = '';

  onMount(async () => {
    try {
      products = await api.getPartnerInventory();
    } catch (error) {
      notify('Error al cargar inventario', 'error');
    } finally {
      loading = false;
    }
  });

  $: filteredProducts = products.filter(p => 
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    p.sku.toLowerCase().includes(searchTerm.toLowerCase())
  );

  function addToCart(product) {
    cart.addItem(product);
    notify(`Agregado al carrito: ${product.name}`, 'info');
  }
</script>

<div class="partner-catalog">
  <div class="search-bar mb-10" in:fly={{ y: -10, duration: 400 }}>
    <div class="relative group">
      <div class="absolute inset-0 bg-indigo-500/5 rounded-2xl blur-lg group-focus-within:bg-indigo-500/10 transition-all"></div>
      <div class="relative flex items-center bg-gray-50 dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-2xl px-5 py-1">
        <span class="text-xl mr-3 opacity-40">🔎</span>
        <input 
          type="text" 
          bind:value={searchTerm} 
          placeholder="Buscar refacciones por nombre o SKU..." 
          class="w-full bg-transparent py-4 outline-none text-gray-700 dark:text-gray-200 font-medium"
        />
      </div>
    </div>
  </div>

  {#if loading}
    <div class="flex flex-col items-center justify-center p-20 gap-4" in:fade>
      <div class="spinner-premium"></div>
      <p class="text-gray-400 font-bold animate-pulse">Obteniendo catálogo...</p>
    </div>
  {:else if filteredProducts.length === 0}
    <div class="text-center p-20 glass-premium rounded-[2rem] border-dashed" in:scale>
      <div class="text-5xl mb-4 opacity-20">📦</div>
      <p class="text-gray-500 dark:text-gray-400 font-medium text-lg">No se encontraron refacciones para tu búsqueda.</p>
    </div>
  {:else}
    <div class="grid grid-cols-1 md-grid-cols-2 xl-grid-cols-3 gap-6">
      {#each filteredProducts as product, i}
        <div 
          class="product-card group relative flex flex-col bg-white dark-bg-gray-800-50 border border-gray-100 dark-border-gray-800 rounded-3xl p-6 transition-all duration-300 hover-shadow hover-move-up"
          in:fly={{ y: 20, duration: 400, delay: i * 50 }}
        >
          <div class="flex justify-between items-start mb-4">
            <div class="space-y-1">
              <h3 class="font-black text-xl text-gray-900 dark-text-white group-hover-text-indigo-600 transition-colors uppercase tracking-tight">{product.name}</h3>
              <p class="text-[10px] text-gray-400 font-black mono tracking-[0.2em]">{product.sku}</p>
            </div>
            <div class="glass-premium px-3 py-1 rounded-xl">
              <span class="text-lg font-black text-indigo-600 dark-text-indigo-400">${product.unit_price.toFixed(2)}</span>
            </div>
          </div>
          
          <div class="mb-6 flex-1">
            <p class="text-sm text-gray-500 dark-text-gray-400 leading-relaxed line-clamp-2">
              {product.description || 'Especificación técnica original de fábrica.'}
            </p>
          </div>

          <div class="flex items-center justify-between mt-auto pt-6 border-t border-gray-50 dark-border-gray-800">
            <div class="stock-info">
              <span class="inline-flex items-center gap-1-5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider {product.stock_quantity > 0 ? 'bg-green-100 text-green-700 dark-bg-green-900-20 dark-text-green-400' : 'bg-red-100 text-red-700 dark-bg-red-900-20 dark-text-red-400'}">
                <span class="h-1-5 w-1-5 rounded-full {product.stock_quantity > 0 ? 'bg-green-500' : 'bg-red-500'}"></span>
                {product.stock_quantity > 0 ? `${product.stock_quantity} EN STOCK` : 'SIN STOCK'}
              </span>
            </div>
            
            <button 
              on:click={() => addToCart(product)}
              disabled={product.stock_quantity === 0}
              class="btn-premium py-2-5 px-5 !text-xs !rounded-xl flex items-center gap-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Añadir
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .product-card {
    background: var(--surface-gradient);
  }
</style>
