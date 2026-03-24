<script>
  export let product;
  export let onView = () => {};
  export let onAddToCart = () => {};

  function getFirstPhoto() {
    if (product.photo_url) {
      return product.photo_url;
    }
    return null;
  }

  $: price = (product.unit_price || 0).toFixed(2);
  $: stock = product.stock_quantity || 0;
</script>

<div class="card-premium group cursor-pointer relative" on:click={() => onView(product)} on:keydown={(e) => e.key === 'Enter' && onView(product)} role="button" tabindex="0">
  <figure class="relative bg-gray-50 dark-bg-gray-900 border-b border-gray-100 dark-border-gray-700 overflow-hidden" style="height: 12rem;">
    {#if getFirstPhoto()}
      <img src={getFirstPhoto()} alt={product.name} class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
    {:else}
      <div class="flex flex-col items-center justify-center w-full h-full opacity-30 group-hover:opacity-60 transition-opacity">
        <span class="text-6xl mb-2">📦</span>
        <span class="text-[10px] font-black uppercase tracking-widest">Sin imagen</span>
      </div>
    {/if}
    
    <div class="absolute top-3 left-3">
      <span class="badge {stock > 0 ? 'badge-success' : 'badge-error'} border-none font-black text-[10px] px-3 py-2 rounded-lg shadow-sm">
        {stock > 0 ? `${stock} EN STOCK` : 'SIN STOCK'}
      </span>
    </div>

    <div class="absolute top-3 right-3 bg-indigo-600 text-white text-[10px] font-black px-2 py-1 rounded-lg shadow-lg">
      ${price}
    </div>
  </figure>

  <div class="card-body p-5 gap-0">
    <div class="flex items-center gap-2 mb-4">
      <div class="w-10 h-10 rounded-xl bg-indigo-50 dark-bg-indigo-900-20 flex items-center justify-center text-xl">
        📦
      </div>
      <div class="flex flex-col">
        <h3 class="card-title text-base font-black text-gray-900 dark-text-white line-clamp-1 leading-tight group-hover:text-indigo-600 transition-colors">
          {product.name}
        </h3>
        <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">SKU: {product.sku || 'N/A'}</span>
      </div>
    </div>

    <p class="text-xs text-gray-500 line-clamp-2 mb-6 h-8">
      {product.description || 'Sin descripción disponible.'}
    </p>

    <div class="card-actions grid grid-cols-2 border-t border-gray-50 dark-border-gray-700 pt-4 -mx-1">
      <button
        class="btn btn-ghost btn-sm flex flex-col h-auto py-2 gap-1 hover:bg-indigo-50 dark:hover-bg-indigo-900-20 text-gray-400 hover:text-indigo-600 transition-all rounded-xl"
        on:click|stopPropagation={() => onView(product)}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="w-4 h-4">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
        <span class="text-[9px] font-black uppercase">Detalle</span>
      </button>

      <button
        class="btn btn-ghost btn-sm flex flex-col h-auto py-2 gap-1 hover:bg-green-50 dark:hover-bg-green-900-20 text-gray-400 hover:text-green-600 transition-all rounded-xl {stock <= 0 ? 'opacity-50 cursor-not-allowed' : ''}"
        on:click|stopPropagation={() => stock > 0 && onAddToCart(product)}
        disabled={stock <= 0}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" class="w-4 h-4">
          <circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>
          <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
        </svg>
        <span class="text-[9px] font-black uppercase">Cargar</span>
      </button>
    </div>
  </div>
</div>

<style>
  :global(.dark) .dark-bg-indigo-900-20 { background-color: rgba(49, 46, 129, 0.2); }
</style>
