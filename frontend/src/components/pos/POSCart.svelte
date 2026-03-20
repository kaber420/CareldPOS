<script>
  import { api } from '../../stores/api';
  import { notify } from '../../stores/auth';

  export let cartItems = [];
  export let onCheckout = () => {};

  let searchQuery = '';
  let searchResults = [];
  let isSearching = false;
  let paymentMethod = 'cash';
  let amountPaid = '';

  $: total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  // Auto-fill amount paid if fully empty, otherwise let user adjust
  $: if (!amountPaid && total > 0) amountPaid = total;
  $: change = Math.max(0, (amountPaid || 0) - total);

  let searchTimeout;

  function handleSearch(e) {
    searchQuery = e.target.value;
    clearTimeout(searchTimeout);
    if (searchQuery.length < 2) {
      searchResults = [];
      return;
    }

    isSearching = true;
    searchTimeout = setTimeout(async () => {
      try {
        searchResults = await api.searchParts(searchQuery);
      } catch (error) {
        console.error(error);
      } finally {
        isSearching = false;
      }
    }, 500);
  }

  function addToCart(product) {
    if (product.stock_quantity <= 0) {
      notify('Producto sin stock', 'warning');
      return;
    }
    
    // Check if item already in cart
    const existing = cartItems.find(i => i.id === product.id && i.type === 'product');
    if (existing) {
      if (existing.quantity >= product.stock_quantity) {
        notify('Stock máximo alcanzado', 'warning');
        return;
      }
      existing.quantity += 1;
      cartItems = [...cartItems];
    } else {
      cartItems = [...cartItems, {
        id: product.id,
        type: 'product',
        name: product.name,
        price: product.unit_price,
        quantity: 1,
        max_quantity: product.stock_quantity
      }];
    }
    searchQuery = '';
    searchResults = [];
  }

  function addRepairToCart(repair) {
    const existing = cartItems.find(i => i.id === repair.id && i.type === 'repair');
    if (existing) return;

    cartItems = [...cartItems, {
      id: repair.id,
      type: 'repair',
      name: `Reparación #${repair.repair_number}`,
      price: repair.final_cost || repair.estimated_cost || 0,
      quantity: 1,
      max_quantity: 1
    }];
  }

  function updateQuantity(index, delta) {
    const item = cartItems[index];
    if (item.type === 'repair') return; // Cannot change quantity for repairs
    
    const newQuantity = item.quantity + delta;
    if (newQuantity > 0 && newQuantity <= item.max_quantity) {
      item.quantity = newQuantity;
      cartItems = [...cartItems];
    } else if (newQuantity <= 0) {
      removeItem(index);
    }
  }

  function removeItem(index) {
    cartItems = cartItems.filter((_, i) => i !== index);
  }

  async function handleCheckout() {
    if (cartItems.length === 0) {
      notify('El carrito está vacío', 'warning');
      return;
    }
    if (amountPaid < total) {
      notify('El monto pagado es insuficiente', 'danger');
      return;
    }

    try {
      await onCheckout({
        items: cartItems,
        payment_method: paymentMethod,
        amount_paid: amountPaid,
        total: total,
        change: change
      });
      // Clear cart on success
      cartItems = [];
      amountPaid = '';
    } catch (error) {
      notify('Error al procesar el pago: ' + error.message, 'danger');
    }
  }
</script>

<div class="pos-cart">
  <div class="cart-header">
    <h3>Carrito de Cobro</h3>
  </div>

  <div class="cart-search">
    <div class="search-input-wrapper">
      <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input 
        type="text" 
        class="input" 
        placeholder="Buscar accesorios o refacciones..." 
        value={searchQuery}
        on:input={handleSearch}
      />
    </div>

    <!-- Search Results Dropdown -->
    {#if searchResults.length > 0 && searchQuery.length >= 2}
      <div class="search-results">
        {#each searchResults as product}
          <div class="search-result-item" on:click={() => addToCart(product)}>
            <div class="product-info">
              <span class="product-name">{product.name}</span>
              <span class="product-stock text-sm text-muted">Stock: {product.stock_quantity}</span>
            </div>
            <span class="product-price">${product.unit_price}</span>
          </div>
        {/each}
      </div>
    {/if}
  </div>

  <div class="cart-items">
    {#if cartItems.length === 0}
      <div class="empty-cart">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle>
          <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
        </svg>
        <p>El carrito está vacío</p>
      </div>
    {:else}
      {#each cartItems as item, idx}
        <div class="cart-item">
          <div class="item-details">
            <span class="item-name">{item.name}</span>
            <span class="item-price">${item.price.toFixed(2)}</span>
          </div>
          <div class="item-actions">
            {#if item.type === 'product'}
              <div class="quantity-controls">
                <button class="btn btn-sm btn-outline" on:click={() => updateQuantity(idx, -1)}>-</button>
                <span class="quantity">{item.quantity}</span>
                <button class="btn btn-sm btn-outline" on:click={() => updateQuantity(idx, 1)}>+</button>
              </div>
            {:else}
              <span class="item-badge">Servicio</span>
            {/if}
            <button class="btn btn-sm btn-icon-secondary remove-btn" on:click={() => removeItem(idx)}>×</button>
          </div>
        </div>
      {/each}
    {/if}
  </div>

  <div class="cart-footer">
    <div class="summary-row total-row">
      <span>Total a Pagar</span>
      <span>${total.toFixed(2)}</span>
    </div>

    <div class="payment-section">
      <div class="form-group">
        <label>Método de Pago</label>
        <select class="input" bind:value={paymentMethod}>
          <option value="cash">Efectivo</option>
          <option value="credit_card">Tarjeta Crédito/Débito</option>
          <option value="transfer">Transferencia</option>
        </select>
      </div>

      {#if paymentMethod === 'cash'}
        <div class="form-group">
          <label>Monto Recibido</label>
          <div class="input-with-prefix">
            <span class="prefix">$</span>
            <input type="number" class="input" bind:value={amountPaid} min={total} step="0.01">
          </div>
        </div>
        {#if change > 0}
          <div class="summary-row text-success">
            <span>Cambio a devolver</span>
            <span>${change.toFixed(2)}</span>
          </div>
        {/if}
      {/if}
    </div>

    <button 
      class="btn btn-primary btn-block checkout-btn" 
      disabled={cartItems.length === 0 || (paymentMethod === 'cash' && amountPaid < total)}
      on:click={handleCheckout}
    >
      Cobrar ${total.toFixed(2)}
    </button>
  </div>
</div>

<style>
  .pos-cart {
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    display: flex;
    flex-direction: column;
    height: 100%;
    max-height: calc(100vh - 100px);
    overflow: hidden;
  }

  .cart-header {
    padding: 1rem;
    border-bottom: 1px solid var(--border);
  }

  .cart-header h3 {
    margin: 0;
    font-size: 1.25rem;
  }

  .cart-search {
    padding: 1rem;
    border-bottom: 1px solid var(--border);
    position: relative;
    z-index: 10;
  }

  .search-input-wrapper {
    position: relative;
  }

  .search-icon {
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    width: 18px;
    height: 18px;
    color: var(--text-light);
  }

  .search-input-wrapper .input {
    padding-left: 36px;
    width: 100%;
  }

  .search-results {
    position: absolute;
    top: 100%;
    left: 1rem;
    right: 1rem;
    background: white;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
    max-height: 250px;
    overflow-y: auto;
    margin-top: 4px;
  }

  .search-result-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    cursor: pointer;
    border-bottom: 1px solid var(--border-light);
  }

  .search-result-item:hover {
    background: var(--bg-hover);
  }

  .product-info {
    display: flex;
    flex-direction: column;
  }

  .product-name {
    font-weight: 500;
  }

  .product-price {
    font-weight: 600;
    color: var(--primary);
  }

  .cart-items {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    background: var(--bg-body);
  }

  .empty-cart {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-light);
    opacity: 0.7;
  }

  .empty-cart svg {
    width: 48px;
    height: 48px;
    margin-bottom: 1rem;
  }

  .cart-item {
    background: white;
    border-radius: var(--radius-md);
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    border: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .item-details {
    display: flex;
    flex-direction: column;
    flex: 1;
  }

  .item-name {
    font-weight: 500;
    margin-bottom: 0.25rem;
  }

  .item-price {
    font-size: 0.875rem;
    color: var(--text-light);
  }

  .item-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .quantity-controls {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--bg-body);
    border-radius: var(--radius-sm);
    padding: 2px;
  }

  .quantity-controls .btn {
    padding: 2px 8px;
    min-width: 28px;
  }

  .quantity {
    font-weight: 600;
    min-width: 20px;
    text-align: center;
  }

  .item-badge {
    background: var(--info-light);
    color: var(--info);
    padding: 0.25rem 0.5rem;
    border-radius: 1rem;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .remove-btn {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .cart-footer {
    padding: 1rem;
    border-top: 1px solid var(--border);
    background: white;
    border-bottom-left-radius: var(--radius-lg);
    border-bottom-right-radius: var(--radius-lg);
  }

  .summary-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
  }

  .total-row {
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 1.25rem;
    padding-bottom: 1rem;
    border-bottom: 1px dashed var(--border);
  }

  .payment-section {
    margin-bottom: 1.5rem;
  }

  .input-with-prefix {
    position: relative;
    display: flex;
    align-items: center;
  }

  .input-with-prefix .prefix {
    position: absolute;
    left: 12px;
    color: var(--text-light);
    font-weight: 600;
  }

  .input-with-prefix .input {
    padding-left: 28px;
  }

  .checkout-btn {
    height: 3rem;
    font-size: 1.125rem;
    font-weight: 600;
  }
</style>
