<script>
  import { onMount } from 'svelte';
  import { api } from '../stores/api';
  import { notify } from '../stores/auth';
  import { openModal } from '../stores/modals';
  import Layout from '../components/Layout.svelte';

  // POS Components
  import ToggleView from '../components/pos/ToggleView.svelte';
  import DeviceCard from '../components/pos/DeviceCard.svelte';
  import DeviceListItem from '../components/pos/DeviceListItem.svelte';
  import DeviceSearchBar from '../components/pos/DeviceSearchBar.svelte';
  import POSModalHost from '../components/pos/POSModalHost.svelte';
  import ProductCard from '../components/pos/ProductCard.svelte';
  import FloatingPOSCart from '../components/pos/FloatingPOSCart.svelte';
  import { cart } from '../stores/cart';

  let viewMode = 'grid';
  let devices = [];
  let products = [];
  let customers = [];
  let deviceSearch = '';
  // Filtro de tipos: 'all', 'repairs', 'products'
  let activeCategory = 'all'; 
  let deviceFilters = { status: '', device_type: '', brand: '' };
  
  // Minimal local state for host props
  let selectedDeviceRepairs = [];
  let deviceForStatusChange = null;
  let isProcessing = false;

  onMount(async () => {
    try {
      const [c, d, p] = await Promise.all([
        api.getCustomers({ limit: 100 }),
        api.getDevices(),
        api.getInventoryItems({ limit: 100 })
      ]);
      customers = c || [];
      devices = d || [];
      products = p || [];
    } catch (e) {
      notify('Error al cargar datos', 'danger');
    }
  });

  async function loadData() {
    try {
      const [d, p] = await Promise.all([
        api.getDevices(),
        api.getInventoryItems({ limit: 100 })
      ]);
      devices = d || [];
      products = p || [];
    } catch (e) {
      notify('Error al recargar', 'danger');
    }
  }

  $: filteredItems = [
    ...(activeCategory === 'all' || activeCategory === 'repairs' ? (devices || []).map(d => ({ ...d, card_type: 'repair' })) : []),
    ...(activeCategory === 'all' || activeCategory === 'products' ? (products || []).map(p => ({ ...p, card_type: 'product' })) : [])
  ].filter(item => {
    const s = (deviceSearch || '').toLowerCase();
    
    if (item.card_type === 'repair') {
      const brand = (item.brand || '').toLowerCase();
      const model = (item.model || '').toLowerCase();
      const customer = (item.customer?.name || '').toLowerCase();
      const serial = (item.serial_number || '').toLowerCase();
      const matchSearch = !s || brand.includes(s) || model.includes(s) || customer.includes(s) || serial.includes(s);
      
      const statusMatch = !deviceFilters.status || item.status === deviceFilters.status;
      return matchSearch && statusMatch;
    } else {
      const name = (item.name || '').toLowerCase();
      const sku = (item.sku || '').toLowerCase();
      const matchSearch = !s || name.includes(s) || sku.includes(s);
      return matchSearch;
    }
  });

  function openReceptionModal() { 
    openModal('reception');
  }
  
  async function onViewDevice(device) {
    if (!device) return;
    try { 
      selectedDeviceRepairs = await api.getRepairs({ device_id: device.id }) || []; 
      openModal('detail', { device });
    } catch (e) { 
      notify('Error al cargar detalle', 'danger');
    }
  }

  const deviceStatusLabels = {
    registered: 'Registrado',
    in_repair: 'En Reparación',
    waiting_parts: 'Repuestos',
    ready: 'Listo para Entrega',
    delivered: 'Entregado'
  };

  async function handleCheckout(cartData) {
    try {
      isProcessing = true;
      const checkoutItems = cartData.items || [];

      // 1. Process repairs logic (only for UI ticket handling later)
      const repairItems = checkoutItems.filter(i => i.type === 'repair');
      
      // 2. Process all items (create sale to deduct stock, update repair status, etc)
      if (checkoutItems.length > 0) {
        const saleItems = checkoutItems.map(i => {
          const up = i.price || i.unit_price || 0;
          const qty = i.quantity || 1;
          const itemRes = { quantity: qty, unit_price: up, subtotal: up * qty };

          if (i.type === 'product') {
            itemRes.inventory_item_id = i.id;
          } else if (i.type === 'repair') {
            itemRes.repair_id = i.id;
          } else if (i.type === 'service') {
            itemRes.service_name = i.name;
          } else {
            return null;
          }
          return itemRes;
        }).filter(Boolean);

        const saleData = {
          total: cartData.total,
          items: saleItems,
          payment_method: cartData.payment_method,
          amount_paid: cartData.amount_paid,
          customer_id: null, // Optional for POS sales
          notes: `Venta POS - ${new Date().toLocaleString()}`
        };
        const response = await api.createSale(saleData);
        
        // Use backend-generated sale number for the ticket if available
        if (response && response.sale_number) {
          cartData.sale_number = response.sale_number;
        }
      }

      // 3. Prepare ticket data
      const itemsForTicket = checkoutItems.map(i => {
        const up = i.price || i.unit_price || 0;
        const qty = i.quantity || 1;
        return {
          ...i,
          sale_price: up,
          subtotal: up * qty
        };
      });

      notify('Cobro realizado correctamente', 'success');
      
      const ticketData = { 
        type: 'venta', 
        items: itemsForTicket, 
        total: cartData.total, 
        sale_number: cartData.sale_number || 'S-TEMP',
        date: new Date().toISOString(),
        payment_method: cartData.payment_method 
      };
      
      openModal('ticket', { ticketData });
      await loadData();
    } catch (e) { 
      console.error(e);
      notify('Error al procesar cobro: ' + e.message, 'danger'); 
    } finally { 
      isProcessing = false; 
    }
  }

  function handleAddProductToCart(product) {
    cart.addItem({
      id: product.id,
      type: 'product',
      name: product.name,
      price: product.unit_price,
      stock_quantity: product.stock_quantity
    });
    notify('Agregado al carrito', 'success');
  }

  async function handleCancelRepair(device) {
    if (!confirm(`¿Estás seguro de cancelar la reparación de ${device.brand} ${device.model}?`)) return;
    try {
      await api.updateDevice(device.id, { status: 'cancelled' });
      notify('Reparación cancelada', 'success');
      await loadData();
    } catch (e) {
      notify('Error al cancelar', 'danger');
    }
  }

  function handleAddToCart(device) {
    if (!device) return;
    api.getRepairs({ device_id: device.id }).then(repairs => {
      const active = (repairs || []).find(r => ['ready', 'completed', 'delivered'].includes(r.status));
      if (active) {
        cart.addItem({ 
          id: active.id, 
          device_id: device.id, 
          type: 'repair', 
          name: `Servicio: ${device.brand} ${device.model}`, 
          price: active.final_cost || active.estimated_cost || 0
        });
        notify('Reparación cargada', 'success');
      } else notify('No hay orden lista para entrega', 'warning');
    });
  }

  async function handleStatusSelect(s) {
    if (s && deviceForStatusChange) {
      try { 
        await api.updateDevice(deviceForStatusChange.id, { status: s }); 
        notify('Estado actualizado', 'success'); 
        await loadData(); 
      } catch (e) { notify('Error al actualizar estado', 'danger'); }
    }
  }

  function handleAddGenericService() {
    const name = prompt('Nombre del servicio:');
    if (!name?.trim()) return;
    
    const priceStr = prompt('Precio cobrado por el servicio:');
    const price = parseFloat(priceStr);
    
    if (isNaN(price) || price < 0) {
      notify('Precio inválido', 'danger');
      return;
    }
    
    cart.addItem({
      id: `service_${Date.now()}`,
      type: 'service',
      name: name.trim(),
      price: price
    });
    notify('Servicio agregado al carrito', 'success');
  }
</script>

<POSModalHost 
  {customers} 
  onSuccessReception={loadData} 
  {selectedDeviceRepairs} 
  {deviceStatusLabels} 
  {handleStatusSelect} 
/>

<Layout title="Terminal POS">
  <div class="pos-container bg-slate-50 min-h-screen">
    <div class="max-w-[1920px] mx-auto px-6 py-8">
      
      <!-- Toolbar -->
      <header class="flex flex-col md:flex-row justify-between items-center bg-white p-6 rounded-2xl shadow-sm mb-8 border border-slate-200">
        <h1 class="text-2xl font-bold text-slate-800">Terminal POS</h1>
        <div class="flex gap-4">
          <button class="bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-2.5 rounded-xl font-bold transition-all shadow-lg shadow-emerald-200 cursor-pointer relative z-10" on:click={handleAddGenericService}>
            + SERVICIO MANUAL
          </button>
          <button class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-xl font-bold transition-all shadow-lg shadow-indigo-200 cursor-pointer relative z-10" on:click={openReceptionModal}>
            + REGISTRAR INGRESO
          </button>
        </div>
      </header>

      <div class="flex flex-col lg:flex-row gap-8 items-start">
        <!-- Main Area -->
        <main class="flex-1 w-full relative z-0">
          <div class="space-y-6">
            <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex flex-wrap items-center gap-4 sticky top-4 z-10 transition-all">
              <div class="flex-1 min-w-[300px]">
                <DeviceSearchBar bind:value={deviceSearch} bind:filters={deviceFilters} placeholder="Buscar reparaciones, accesorios, refacciones..." />
              </div>
              
              <div class="flex bg-slate-100 p-1 rounded-xl gap-1">
                <button 
                  class="px-4 py-1.5 rounded-lg text-xs font-black uppercase tracking-widest transition-all {activeCategory === 'all' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-400 hover:text-slate-600'}"
                  on:click={() => activeCategory = 'all'}
                >
                  Todos
                </button>
                <button 
                  class="px-4 py-1.5 rounded-lg text-xs font-black uppercase tracking-widest transition-all {activeCategory === 'repairs' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-400 hover:text-slate-600'}"
                  on:click={() => activeCategory = 'repairs'}
                >
                  Reparaciones
                </button>
                <button 
                  class="px-4 py-1.5 rounded-lg text-xs font-black uppercase tracking-widest transition-all {activeCategory === 'products' ? 'bg-white shadow-sm text-indigo-600' : 'text-slate-400 hover:text-slate-600'}"
                  on:click={() => activeCategory = 'products'}
                >
                  Tienda
                </button>
              </div>

              <ToggleView bind:viewMode />
            </div>

            {#if filteredItems.length === 0}
              <div class="bg-white rounded-3xl p-20 text-center border-2 border-dashed border-slate-200">
                <p class="text-slate-400 font-medium">No se encontraron artículos</p>
              </div>
            {:else if viewMode === 'grid'}
              <div class="device-grid-auto">
                {#each filteredItems as item (item.card_type + '-' + item.id)}
                  {#if item.card_type === 'repair'}
                    <DeviceCard 
                      device={item} 
                      customerName={item.customer?.name || 'Cliente'} 
                      showEdit={false}
                      showStatus={false}
                      showCancel={true}
                      showAddToCart={item.status === 'ready'}
                      onView={() => onViewDevice(item)} 
                      onCancel={() => handleCancelRepair(item)}
                      onAddToCart={() => handleAddToCart(item)}
                      onOpenGallery={() => { if(item.photos) { openModal('gallery', { photos: item.photos.split(','), currentIndex: 0 }); } }}
                    />
                  {:else}
                    <ProductCard 
                      product={item}
                      onView={() => notify('Detalle de producto próximamente', 'info')}
                      onAddToCart={() => handleAddProductToCart(item)}
                    />
                  {/if}
                {/each}
              </div>
            {:else}
              <div class="space-y-3">
                {#each filteredItems as item (item.card_type + '-' + item.id)}
                  {#if item.card_type === 'repair'}
                    <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-all flex items-center justify-between gap-4 cursor-pointer relative z-0" on:click={() => onViewDevice(item)} on:keydown={(e) => e.key === 'Enter' && onViewDevice(item)} role="button" tabindex="0">
                      <div class="flex-1">
                        <DeviceListItem device={item} customerName={item.customer?.name || 'Cliente'} onView={() => onViewDevice(item)} onStatusChange={() => { deviceForStatusChange = item; openModal('status', {device: item}); }} />
                      </div>
                      {#if item.status === 'ready'}
                        <button class="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-xl font-bold relative z-10" on:click|stopPropagation={() => handleAddToCart(item)}>CARGAR</button>
                      {/if}
                    </div>
                  {:else}
                    <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-all flex items-center justify-between gap-4 cursor-pointer relative z-0">
                      <div class="flex items-center gap-4">
                        <div class="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center text-xl">📦</div>
                        <div>
                          <h4 class="font-bold">{item.name}</h4>
                          <p class="text-xs text-slate-400">SKU: {item.sku || 'N/A'}</p>
                        </div>
                      </div>
                      <div class="flex items-center gap-6">
                        <span class="font-black text-indigo-600">${item.unit_price}</span>
                        <button class="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-xl font-bold" on:click={() => handleAddProductToCart(item)}>AGREGAR</button>
                      </div>
                    </div>
                  {/if}
                {/each}
              </div>
            {/if}
          </div>
        </main>
      </div>
    </div>
  </div>

  <FloatingPOSCart onCheckout={handleCheckout} />
</Layout>

<style>
  .device-grid-auto {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.5rem;
  }
  
  /* Ajuste para pantallas muy pequeñas */
  @media (max-width: 480px) {
    .device-grid-auto {
      grid-template-columns: 1fr;
    }
  }
</style>
