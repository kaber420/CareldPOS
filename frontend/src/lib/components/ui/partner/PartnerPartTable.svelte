<script>
  import { createEventDispatcher } from 'svelte';
  import { cart } from '../../../../stores/cart';
  const dispatch = createEventDispatcher();

  export let products = [];
</script>

<div class="table-container">
  <table>
    <thead>
      <tr>
        <th>SKU</th>
        <th>Foto</th>
        <th>Nombre</th>
        <th>Stock</th>
        <th>Precio</th>
        <th class="actions">Acciones</th>
      </tr>
    </thead>
    <tbody>
      {#each products as product (product.id)}
        <tr on:click={() => dispatch('row-click', product)}>
          <td class="sku">{product.sku}</td>
          <td class="photo">
            {#if product.photo_url}
              <button 
                class="photo-trigger" 
                on:click|stopPropagation={() => dispatch('view-photo', product)}
                aria-label="Ver foto"
              >
                <img src={product.photo_url} alt={product.name}>
              </button>
            {:else}
              <div class="no-photo-small">📦</div>
            {/if}
          </td>
          <td class="name">
            <strong>{product.name}</strong>
            <span>{product.category_name || 'General'}</span>
          </td>
          <td>
            <span class="stock {product.stock_quantity > 0 ? 'in-stock' : 'out-of-stock'}">
              {product.stock_quantity > 0 ? `${product.stock_quantity} EN STOCK` : 'SIN STOCK'}
            </span>
          </td>
          <td class="price">
            {#if product.unit_price && product.unit_price > 0}
              ${(product.unit_price || 0).toFixed(2)}
            {:else}
              <span class="text-orange-400 text-[10px] uppercase font-bold">Consultar</span>
            {/if}
          </td>
          <td class="actions">
            {#each [$cart.find(i => i.id === product.id)] as inCart}
              {@const isLimitReached = inCart && inCart.quantity >= product.stock_quantity}
              <button 
                class="icon-btn" 
                title={isLimitReached ? "Stock agotado en carrito" : "Añadir al carrito"}
                on:click|stopPropagation={() => dispatch('add-to-cart', product)}
                disabled={product.stock_quantity === 0 || isLimitReached}
                style={isLimitReached ? "opacity: 0.3; cursor: not-allowed;" : ""}
              >
                {isLimitReached ? '✅' : '🛒'}
              </button>
            {/each}
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>

<style>
  .table-container {
    background: rgba(30, 41, 59, 0.3);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    overflow: hidden;
    backdrop-filter: blur(8px);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    font-size: 0.9rem;
  }

  thead {
    background: rgba(15, 23, 42, 0.6);
    position: sticky;
    top: 0;
    z-index: 10;
  }

  th {
    padding: 1.25rem 1rem;
    color: #94a3b8;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 0.7rem;
    letter-spacing: 1px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  td {
    padding: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    color: #f1f5f9;
    vertical-align: middle;
  }

  tbody tr {
    transition: background 0.2s;
    cursor: pointer;
  }

  tbody tr:hover {
    background: rgba(255, 255, 255, 0.04);
  }

  .sku {
    font-family: monospace;
    color: #818cf8;
    font-weight: 700;
    font-size: 0.8rem;
    text-transform: uppercase;
  }

  .photo-trigger {
    background: transparent;
    border: none;
    padding: 0;
    cursor: pointer;
    display: block;
  }

  .photo img {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    object-fit: cover;
    border: 1px solid rgba(255,255,255,0.1);
  }

  .no-photo-small {
    width: 40px;
    height: 40px;
    background: rgba(0,0,0,0.2);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    opacity: 0.3;
  }

  .name {
    display: flex;
    flex-direction: column;
  }

  .name strong {
    font-size: 0.95rem;
    text-transform: uppercase;
  }

  .name span {
    font-size: 0.75rem;
    color: #64748b;
  }

  .price {
    font-weight: 800;
    color: white;
  }

  .stock {
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    font-size: 0.6rem;
    font-weight: 800;
    display: inline-block;
  }

  .stock.in-stock { background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.2); }
  .stock.out-of-stock { background: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid rgba(248, 113, 113, 0.2); }

  .actions {
    text-align: right;
  }

  .icon-btn {
    width: 40px;
    height: 40px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #94a3b8;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 1.1rem;
  }

  .icon-btn:hover:not(:disabled) {
    background: #6366f1;
    color: white;
    border-color: #6366f1;
  }

  .icon-btn:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }
</style>
