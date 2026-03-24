<script>
  import { createEventDispatcher } from 'svelte';
  import { cart } from '../../../../stores/cart';
  const dispatch = createEventDispatcher();

  export let product = {};

  $: mainPhoto = product.photo_url || null;
  $: price = (product.unit_price || 0).toFixed(2);
  $: inCart = $cart.find(i => i.id === product.id);
  $: isLimitReached = inCart && inCart.quantity >= product.stock_quantity;
</script>

<div class="part-card">
  <!-- 1. Media Section -->
  <div 
    class="card-media" 
    on:click={() => dispatch('view-photo', product)}
    on:keydown={(e) => e.key === 'Enter' && dispatch('view-photo', product)}
    role="button"
    tabindex="0"
    aria-label="Ver foto de la refacción"
  >
    {#if mainPhoto}
      <img src={mainPhoto} alt={product.name}>
    {:else}
      <div class="placeholder-icon">
        <span>📦</span>
      </div>
    {/if}
    <div class="sku-overlay">
      {product.sku}
    </div>
  </div>

  <!-- 2. Data Section -->
  <div class="card-data">
    <div class="header">
      <h3>{product.name}</h3>
      <span class="stock {product.stock_quantity > 0 ? 'in-stock' : 'out-of-stock'}">
        {product.stock_quantity > 0 ? `${product.stock_quantity} EN STOCK` : 'SIN STOCK'}
      </span>
    </div>
    <p class="description">{product.description || 'Especificación técnica original de fábrica.'}</p>
    <div class="meta">
      {#if product.unit_price && product.unit_price > 0}
        <span class="price">${price}</span>
      {:else}
        <span class="price text-sm opacity-80" style="color: #fb923c;">Consultar</span>
      {/if}
      <span class="category">{product.category_name || 'General'}</span>
    </div>
  </div>

  <!-- 3. Action Section -->
  <div class="card-actions">
    <button 
      class="action-btn primary" 
      on:click={() => dispatch('add-to-cart', product)}
      disabled={product.stock_quantity === 0 || isLimitReached}
    >
      <i>🛒</i> {isLimitReached ? 'Límite en Carrito' : 'Añadir al Carrito'}
    </button>
  </div>
</div>

<style>
  .part-card {
    background: rgba(30, 41, 59, 0.5);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    transition: border-color 0.2s, background 0.2s;
  }

  .part-card:hover {
    border-color: #6366f1;
    background: rgba(45, 55, 72, 0.7);
  }

  /* Media Section */
  .card-media {
    height: 160px;
    background: #0f172a;
    position: relative;
    cursor: pointer;
    overflow: hidden;
  }

  .card-media img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.8;
    transition: opacity 0.3s;
  }

  .card-media:hover img {
    opacity: 1;
  }

  .placeholder-icon {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
    opacity: 0.3;
  }

  .sku-overlay {
    position: absolute;
    top: 1rem;
    left: 1rem;
    background: rgba(15, 23, 42, 0.8);
    padding: 0.4rem 0.8rem;
    border-radius: 8px;
    font-size: 0.7rem;
    font-weight: 800;
    color: #818cf8;
    letter-spacing: 1px;
    backdrop-filter: blur(4px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    text-transform: uppercase;
  }

  /* Data Section */
  .card-data {
    padding: 1.5rem;
    flex: 1;
  }

  .card-data .header {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
  }

  h3 {
    font-size: 1.1rem;
    font-weight: 800;
    margin: 0;
    color: white;
    line-height: 1.2;
    text-transform: uppercase;
  }

  .description {
    color: #94a3b8;
    font-size: 0.85rem;
    margin-bottom: 1.5rem;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    line-clamp: 2;
    overflow: hidden;
    line-height: 1.4;
  }

  .meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 700;
  }

  .price {
    font-size: 1.25rem;
    color: #818cf8;
  }

  .category {
    font-size: 0.75rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .stock {
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    font-size: 0.6rem;
    font-weight: 800;
    display: inline-block;
    width: fit-content;
  }

  .stock.in-stock { background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.2); }
  .stock.out-of-stock { background: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid rgba(248, 113, 113, 0.2); }

  /* Action Section */
  .card-actions {
    padding: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
  }

  .action-btn {
    width: 100%;
    padding: 0.75rem;
    border: none;
    border-radius: 12px;
    background: rgba(99, 102, 241, 0.1);
    color: #818cf8;
    font-size: 0.8rem;
    font-weight: 800;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    transition: all 0.2s;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .action-btn:hover:not(:disabled) {
    background: #6366f1;
    color: white;
  }

  .action-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
