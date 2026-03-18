<script>
  import { onMount } from 'svelte';
  import { api } from '../stores/api';
  import { notify, user } from '../stores/auth';
  import Layout from '../components/Layout.svelte';
  import Scanner from '../lib/Scanner.svelte';

  let repairs = [];
  let devices = [];
  let users = [];
  let isLoading = true;
  let showForm = false;
  let editingRepair = null;
  let selectedRepair = null;
  let showScanner = false;
  
  // Modal de refacciones
  let showPartsModal = false;
  let repairItems = [];
  let searchPartsQuery = '';
  let searchResults = [];
  let searchingParts = false;
  let loadingParts = false;
  
  // Modal de cobro
  let showCompleteModal = false;
  let completeForm = {
    labor_cost: 0,
    payment_method: 'cash',
    reference: '',
    notes: ''
  };
  
  const paymentMethods = [
    { value: 'cash', label: 'Efectivo' },
    { value: 'credit_card', label: 'Tarjeta de Crédito' },
    { value: 'debit_card', label: 'Tarjeta de Débito' },
    { value: 'transfer', label: 'Transferencia' },
    { value: 'paypal', label: 'PayPal' },
    { value: 'other', label: 'Otro' }
  ];

  let filters = {
    status: '',
    priority: '',
    technician_id: ''
  };

  let formData = {
    device_id: '',
    description: '',
    diagnosis: '',
    estimated_cost: '',
    priority: 'normal',
    warranty_days: 30,
    technician_id: ''
  };

  const statusLabels = {
    pending: 'Pendiente',
    diagnosing: 'Diagnóstico',
    waiting_approval: 'Esperando Aprobación',
    in_progress: 'En Progreso',
    waiting_parts: 'Esperando Repuestos',
    completed: 'Completada',
    delivered: 'Entregada',
    cancelled: 'Cancelada'
  };

  const priorityLabels = {
    low: 'Baja',
    normal: 'Normal',
    high: 'Alta',
    urgent: 'Urgente'
  };

  onMount(async () => {
    await Promise.all([loadRepairs(), loadDevices(), loadUsers()]);
  });

  async function loadRepairs() {
    isLoading = true;
    try {
      const params = {};
      if (filters.status) params.status = filters.status;
      if (filters.priority) params.priority = filters.priority;
      if (filters.technician_id) params.technician_id = filters.technician_id;
      repairs = await api.getRepairs(params);
    } catch (error) {
      notify(error.message, 'danger');
    } finally {
      isLoading = false;
    }
  }

  async function loadDevices() {
    try {
      devices = await api.getDevices({ limit: 1000 });
    } catch (error) {
      console.error('Error loading devices:', error);
    }
  }

  async function loadUsers() {
    try {
      users = await api.getUsers();
    } catch (error) {
      console.error('Error loading users:', error);
    }
  }

  function openForm(repair = null) {
    if (repair) {
      editingRepair = repair;
      formData = {
        device_id: repair.device_id,
        description: repair.description,
        diagnosis: repair.diagnosis || '',
        estimated_cost: repair.estimated_cost || '',
        priority: repair.priority,
        warranty_days: repair.warranty_days,
        technician_id: repair.technician_id || ''
      };
      // Cargar refacciones de la reparación
      loadRepairItems(repair.id);
    } else {
      editingRepair = null;
      formData = {
        device_id: devices[0]?.id || '',
        description: '',
        diagnosis: '',
        estimated_cost: '',
        priority: 'normal',
        warranty_days: 30,
        technician_id: ''
      };
      repairItems = [];
    }
    searchPartsQuery = '';
    searchResults = [];
    showForm = true;
  }

  function closeForm() {
    showForm = false;
    editingRepair = null;
  }

   async function handleSubmit() {
     try {
       const data = {
         description: formData.description,
         diagnosis: formData.diagnosis || null,
         estimated_cost: formData.estimated_cost ? parseFloat(formData.estimated_cost) : null,
         priority: formData.priority,
         warranty_days: formData.warranty_days,
         device_id: formData.device_id ? parseInt(formData.device_id) : null,
         technician_id: formData.technician_id ? parseInt(formData.technician_id) : null
       };

       if (editingRepair) {
         await api.updateRepair(editingRepair.id, data);
         notify('Reparación actualizada correctamente', 'success');
       } else {
         await api.createRepair(data);
         notify('Reparación creada correctamente', 'success');
       }
       closeForm();
       loadRepairs();
     } catch (error) {
       notify(error.message, 'danger');
     }
   }

   async function handleScanResult(code) {
     // Try to parse as repair number first (e.g., REP-20260318-0001)
     if (code.startsWith('REP-')) {
       try {
         const repair = await api.getRepairByNumber(code);
         // Navigate to the repair form in edit mode
         openForm(repair);
         notify(`Orden ${repair.repair_number} cargada`, 'success');
       } catch (error) {
         notify('No se encontró una orden con ese número', 'warning');
       }
       return;
     }

     // If not a repair number, try as device ID (numeric)
     if (/^\d+$/.test(code)) {
       const deviceId = parseInt(code);
       const device = devices.find(d => d.id === deviceId);
       if (device) {
         // Set the device in the form
         formData.device_id = deviceId;
         notify(`Dispositivo ${device.brand} ${device.model} seleccionado`, 'success');
         return;
       }
     }

     // If not a device ID, try as inventory item ID (numeric)
     if (/^\d+$/.test(code)) {
       const itemId = parseInt(code);
       // We need to search inventory to get the item details
       try {
         // This would require a new API endpoint or using search
         // For now, we'll show a message that we found an item ID
         notify(`Código de artículo ${itemId} escaneado. Funcionalidad en desarrollo.`, 'info');
         return;
       } catch (error) {
         // Not found
       }
     }

     // If we got here, we couldn't interpret the code
     notify(`Código escaneado: ${code}. No se pudo interpretar como orden, dispositivo o artículo.`, 'warning');
   }

  async function updateStatus(repair, newStatus) {
    try {
      await api.updateRepair(repair.id, { status: newStatus });
      notify(`Estado actualizado a ${statusLabels[newStatus]}`, 'success');
      loadRepairs();
    } catch (error) {
      notify(error.message, 'danger');
    }
  }

  async function handleDelete(repair) {
    if (!confirm(`¿Estás seguro de eliminar la reparación ${repair.repair_number}?`)) return;

    try {
      await api.deleteRepair(repair.id);
      notify('Reparación eliminada correctamente', 'success');
      loadRepairs();
    } catch (error) {
      notify(error.message, 'danger');
    }
  }

  function handleFilter() {
    loadRepairs();
  }

  function getDeviceName(deviceId) {
    const device = devices.find(d => d.id === deviceId);
    return device ? `${device.brand} ${device.model}` : 'Desconocido';
  }

  function getTechnicianName(technicianId) {
    if (!technicianId) return 'Sin asignar';
    const user = users.find(u => u.id === technicianId);
    return user?.full_name || 'Desconocido';
  }

  function formatDate(dateString) {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  }

  function formatCurrency(amount) {
    if (!amount) return '-';
    return `$${amount.toFixed(2)}`;
  }

  // --- Funciones de refacciones ---
  
  async function openPartsModal(repair) {
    selectedRepair = repair;
    showPartsModal = true;
    repairItems = [];
    searchPartsQuery = '';
    searchResults = [];
    await loadRepairItems(repair.id);
  }

  async function loadRepairItems(repairId) {
    try {
      repairItems = await api.getRepairItems(repairId);
    } catch (error) {
      console.error('Error loading repair items:', error);
    }
  }

  async function searchParts() {
    if (!searchPartsQuery.trim()) {
      searchResults = [];
      return;
    }
    searchingParts = true;
    try {
      searchResults = await api.searchParts(searchPartsQuery, 20);
    } catch (error) {
      notify('Error al buscar refacciones', 'danger');
    } finally {
      searchingParts = false;
    }
  }

  async function addPartToRepair(part) {
    let currentUser;
    user.subscribe(u => currentUser = u)();
    
    try {
      const data = {
        inventory_item_id: part.id,
        quantity: 1,
        unit_price: part.unit_price,
        technician_id: currentUser?.id || null
      };
      await api.addRepairItem(selectedRepair.id, data);
      await loadRepairItems(selectedRepair.id);
      searchResults = [];
      searchPartsQuery = '';
      notify('Refacción agregada correctamente', 'success');
    } catch (error) {
      notify(error.message, 'danger');
    }
  }

  async function removePartFromRepair(item) {
    if (!confirm('¿Eliminar esta refacción de la reparación?')) return;
    
    try {
      await api.removeRepairItem(selectedRepair.id, item.id);
      await loadRepairItems(selectedRepair.id);
      notify('Refacción eliminada', 'success');
    } catch (error) {
      notify(error.message, 'danger');
    }
  }

  function getItemsTotal() {
    return repairItems.reduce((sum, item) => sum + (item.unit_price * item.quantity), 0);
  }

  // --- Funciones de cobro ---
  
  async function openCompleteModal(repair) {
    selectedRepair = repair;
    completeForm = {
      labor_cost: repair.estimated_cost || 0,
      payment_method: 'cash',
      reference: '',
      notes: ''
    };
    await loadRepairItems(repair.id);
    showCompleteModal = true;
    loadRepairItems(repair.id);
  }

  async function completeRepair() {
    try {
      const result = await api.completeRepair(selectedRepair.id, completeForm);
      notify(`Reparación completada. Total: $${result.final_total.toFixed(2)}`, 'success');
      showCompleteModal = false;
      loadRepairs();
    } catch (error) {
      notify(error.message, 'danger');
    }
  }

  function getCompleteTotal() {
    const itemsTotal = getItemsTotal();
    return itemsTotal + parseFloat(completeForm.labor_cost || 0);
  }
</script>

<Layout>
  <div class="repairs-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Reparaciones</h1>
        <p class="page-subtitle">Gestión de órdenes de reparación</p>
      </div>
    <button class="btn btn-primary" on:click={() => openForm()}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="12" y1="5" x2="12" y2="19"/>
        <line x1="5" y1="12" x2="19" y2="12"/>
      </svg>
      Nueva Reparación
    </button>
  </div>

  <!-- Stats -->
  <div class="stats-grid">
    <div class="stat-card stat-pending">
      <div class="stat-value">{repairs.filter(r => r.status === 'pending').length}</div>
      <div class="stat-label">Pendientes</div>
    </div>
    <div class="stat-card stat-progress">
      <div class="stat-value">{repairs.filter(r => r.status === 'in_progress').length}</div>
      <div class="stat-label">En Progreso</div>
    </div>
    <div class="stat-card stat-completed">
      <div class="stat-value">{repairs.filter(r => r.status === 'completed').length}</div>
      <div class="stat-label">Completadas</div>
    </div>
    <div class="stat-card stat-total">
      <div class="stat-value">{repairs.length}</div>
      <div class="stat-label">Total</div>
    </div>
  </div>

  <div class="card mt-6">
    <div class="card-body">
      <!-- Filters -->
      <div class="filters-bar">
        <div class="flex gap-3" style="flex-wrap: wrap;">
          <select class="select" bind:value={filters.status}>
            <option value="">Todos los estados</option>
            {#each Object.entries(statusLabels) as [value, label]}
              <option value={value}>{label}</option>
            {/each}
          </select>
          <select class="select" bind:value={filters.priority}>
            <option value="">Todas las prioridades</option>
            {#each Object.entries(priorityLabels) as [value, label]}
              <option value={value}>{label}</option>
            {/each}
          </select>
          <select class="select" bind:value={filters.technician_id}>
            <option value="">Todos los técnicos</option>
            {#each users as user}
              {#if user.role === 'technician' || user.role === 'admin'}
                <option value={user.id}>{user.full_name}</option>
              {/if}
            {/each}
          </select>
          <button class="btn btn-outline" on:click={handleFilter}>Filtrar</button>
          <button class="btn btn-outline" on:click={() => { filters = { status: '', priority: '', technician_id: '' }; loadRepairs(); }}>Limpiar</button>
        </div>
      </div>

      <!-- Table -->
      {#if isLoading}
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Cargando reparaciones...</p>
        </div>
      {:else if repairs.length === 0}
        <div class="empty-state">
          <div class="empty-state-icon">📋</div>
          <p class="empty-state-title">No hay reparaciones</p>
          <p class="empty-state-description">Comienza creando una nueva orden de reparación</p>
          <button class="btn btn-primary mt-4" on:click={() => openForm()}>
            Crear Reparación
          </button>
        </div>
      {:else}
        <div class="table-container">
          <table class="table">
            <thead>
              <tr>
                <th>Número</th>
                <th>Dispositivo</th>
                <th>Cliente</th>
                <th>Estado</th>
                <th>Prioridad</th>
                <th>Técnico</th>
                <th>Costo</th>
                <th>Fecha</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {#each repairs as repair}
                <tr>
                  <td class="font-medium">{repair.repair_number}</td>
                  <td>{getDeviceName(repair.device_id)}</td>
                  <td>
                    {#if repair.device?.customer?.name}
                      {repair.device.customer.name}
                    {:else}
                      Ver dispositivo
                    {/if}
                  </td>
                  <td>
                    <span class="badge badge-{
                      repair.status === 'pending' ? 'warning' :
                      repair.status === 'in_progress' ? 'primary' :
                      repair.status === 'completed' || repair.status === 'delivered' ? 'success' :
                      repair.status === 'cancelled' ? 'danger' :
                      'secondary'
                    }">
                      {statusLabels[repair.status]}
                    </span>
                  </td>
                  <td>
                    <span class="badge badge-{
                      repair.priority === 'urgent' ? 'danger' :
                      repair.priority === 'high' ? 'warning' :
                      repair.priority === 'low' ? 'secondary' :
                      'primary'
                    }">
                      {priorityLabels[repair.priority]}
                    </span>
                  </td>
                  <td>{getTechnicianName(repair.technician_id)}</td>
                  <td>{formatCurrency(repair.final_cost || repair.estimated_cost)}</td>
                  <td>{formatDate(repair.created_at)}</td>
                    <td>
                      <div class="flex gap-2" style="flex-wrap: wrap;">
                        <button
                          class="btn btn-sm btn-outline"
                          on:click={() => openForm(repair)}
                        >
                          Ver
                        </button>
                        {#if repair.status !== 'delivered' && repair.status !== 'cancelled' && repair.status !== 'completed'}
                          <button
                            class="btn btn-sm btn-success"
                            on:click={() => openCompleteModal(repair)}
                          >
                            💰 Cobrar
                          </button>
                        {/if}
                        {#if repair.status !== 'delivered' && repair.status !== 'cancelled'}
                          <select
                            class="select select-sm"
                            value={repair.status}
                            on:change={(e) => updateStatus(repair, e.target.value)}
                          >
                            {#each Object.entries(statusLabels) as [value, label]}
                              {#if value !== 'delivered' && value !== 'cancelled'}
                                <option value={value}>{label}</option>
                              {/if}
                            {/each}
                          </select>
                        {/if}
                        {#if repair.portal_token}
                          <button
                            class="btn btn-sm btn-outline"
                            on:click={() => navigator.clipboard.writeText(`${window.location.origin}/portal/${repair.portal_token}`).then(() => notify('Link copiado al portapapeles', 'info'))}
                          >
                            🔗 Compartir
                          </button>
                        {/if}
                      </div>
                    </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </div>
  </div>

  <!-- Modal Form -->
  {#if showForm}
    <div class="modal-overlay" on:click|self={closeForm}>
      <div class="modal modal-lg">
        <div class="modal-header">
          <h3 class="modal-title">
            {editingRepair ? `Reparación ${editingRepair.repair_number}` : 'Nueva Reparación'}
          </h3>
          <button class="modal-close" on:click={closeForm}>×</button>
        </div>

        <form on:submit|preventDefault={handleSubmit}>
          <div class="modal-body">
            {#if editingRepair}
              <div class="alert alert-info mb-4">
                <strong>Número de orden:</strong> {editingRepair.repair_number}
              </div>
            {/if}

            <div class="form-group">
              <label class="label" for="device_id">Dispositivo *</label>
              <select id="device_id" class="select" bind:value={formData.device_id} required>
                <option value="">Seleccionar dispositivo</option>
                {#each devices as device}
                  <option value={device.id}>
                    {device.customer?.name || 'Cliente'} - {device.brand} {device.model}
                  </option>
                {/each}
              </select>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="label" for="priority">Prioridad *</label>
                <select id="priority" class="select" bind:value={formData.priority} required>
                  {#each Object.entries(priorityLabels) as [value, label]}
                    <option value={value}>{label}</option>
                  {/each}
                </select>
              </div>

              <div class="form-group">
                <label class="label" for="technician_id">Técnico</label>
                <select id="technician_id" class="select" bind:value={formData.technician_id}>
                  <option value="">Sin asignar</option>
                  {#each users as user}
                    {#if user.role === 'technician' || user.role === 'admin'}
                      <option value={user.id}>{user.full_name}</option>
                    {/if}
                  {/each}
                </select>
              </div>
            </div>

            <div class="form-group">
              <label class="label" for="description">Descripción del problema *</label>
              <textarea id="description" class="textarea" bind:value={formData.description} rows="3" required></textarea>
            </div>

            <div class="form-group">
              <label class="label" for="diagnosis">Diagnóstico</label>
              <textarea id="diagnosis" class="textarea" bind:value={formData.diagnosis} rows="3"></textarea>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="label" for="estimated_cost">Costo Estimado</label>
                <input id="estimated_cost" type="number" step="0.01" class="input" bind:value={formData.estimated_cost} />
              </div>

              <div class="form-group">
                <label class="label" for="warranty_days">Días de Garantía</label>
                <input id="warranty_days" type="number" class="input" bind:value={formData.warranty_days} />
              </div>
            </div>

            <!-- Sección de Refacciones dentro del modal de reparación -->
            {#if editingRepair}
              <div class="parts-section">
                <h4 class="parts-title">🔧 Refacciones</h4>
                
				<!-- Buscador de refacciones -->
				<div class="form-group">
					<div class="flex gap-2">
						<input 
							type="text" 
							class="input" 
							placeholder="Buscar refacción..." 
							bind:value={searchPartsQuery}
						/>
						<button class="btn btn-secondary btn-sm" on:click={searchParts}>
							{searchingParts ? '...' : 'Buscar'}
						</button>
						<button class="btn btn-outline btn-sm" on:click={() => showScanner = true}>
							📷 Escanear
						</button>
					</div>
				</div>

                <!-- Resultados de búsqueda -->
                {#if searchResults.length > 0}
                  <div class="search-results mb-3">
                    {#each searchResults as part}
                      <button 
                        class="result-item"
                        on:click={() => addPartToRepair(part)}
                      >
                        <span class="result-name">{part.name}</span>
                        <span class="result-details">
                          <span class="sku">{part.sku}</span>
                          <span class="stock">Stock: {part.stock_quantity}</span>
                          <span class="price">${part.unit_price.toFixed(2)}</span>
                        </span>
                      </button>
                    {/each}
                  </div>
                {/if}

                <!-- Lista de refacciones agregadas -->
                <div class="parts-list">
                  <table class="table table-sm">
                      <thead>
                      <tr>
                        <th>Refacción</th>
                        <th>Cant.</th>
                        <th>Precio</th>
                        <th>Total</th>
                        <th>Técnico</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      {#each repairItems as item}
                        <tr>
                          <td>{item.inventory_item?.name || 'Refacción'}</td>
                          <td>{item.quantity}</td>
                          <td>${item.unit_price.toFixed(2)}</td>
                          <td>${(item.unit_price * item.quantity).toFixed(2)}</td>
                          <td>{getTechnicianName(item.technician_id)}</td>
                          <td>
                            <button 
                              class="btn btn-xs btn-danger"
                              on:click={() => removePartFromRepair(item)}
                            >
                              ✕
                            </button>
                          </td>
                        </tr>
                      {/each}
                    </tbody>
                    {#if repairItems.length > 0}
                      <tfoot>
                        <tr>
                          <td colspan="3" class="text-right"><strong>Total:</strong></td>
                          <td><strong>${getItemsTotal().toFixed(2)}</strong></td>
                          <td colspan="2"></td>
                        </tr>
                      </tfoot>
                    {/if}
                  </table>
                  {#if repairItems.length === 0}
                    <p class="text-muted text-center p-3">No hay refacciones agregadas</p>
                  {/if}
                </div>
              </div>
            {/if}
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-outline" on:click={closeForm}>Cancelar</button>
            <button type="submit" class="btn btn-primary">
              {editingRepair ? 'Actualizar' : 'Crear'} Reparación
            </button>
          </div>
        </form>
      </div>
    </div>
  {/if}

   <!-- Modal de Refacciones -->
   {#if showPartsModal}
     <div class="modal-overlay" on:click|self={() => showPartsModal = false}>
       <div class="modal modal-lg">
         <div class="modal-header">
           <h3 class="modal-title">🔧 Refacciones - {selectedRepair?.repair_number}</h3>
           <button class="modal-close" on:click={() => showPartsModal = false}>×</button>
         </div>
         
         <div class="modal-body">
           <!-- Buscador -->
           <div class="form-group">
             <label class="label">Buscar refacción</label>
             <div class="flex gap-2">
               <input 
                 type="text" 
                 class="input" 
                 placeholder="Buscar por nombre o SKU..." 
                 bind:value={searchPartsQuery}
                 on:input={searchParts}
               />
               <button class="btn btn-secondary" on:click={searchParts}>
                 {searchingParts ? 'Buscando...' : 'Buscar'}
               </button>
               <button class="btn btn-outline" on:click={() => showScanner = true}>
                 📷 Escanear
               </button>
             </div>
           </div>
           
           <!-- Resultados de búsqueda -->
           {#if searchResults.length > 0}
             <div class="search-results mb-4">
               <p class="text-sm text-muted mb-2">Resultados:</p>
               <div class="results-grid">
                 {#each searchResults as part}
                   <button 
                     class="result-item"
                     on:click={() => addPartToRepair(part)}
                   >
                     <div class="result-name">{part.name}</div>
                     <div class="result-details">
                       <span class="sku">{part.sku}</span>
                       <span class="stock">Stock: {part.stock_quantity}</span>
                       <span class="price">${part.unit_price.toFixed(2)}</span>
                     </div>
                   </button>
                 {/each}
               </div>
             </div>
           {/if}
           
           <!-- Items ya agregados -->
           <div class="items-section">
             <h4 class="mb-3">Refacciones agregadas</h4>
             {#if repairItems.length === 0}
               <p class="text-muted">No hay refacciones agregadas</p>
             {:else}
               <table class="table table-sm">
                 <thead>
                   <tr>
                     <th>Refacción</th>
                     <th>Cantidad</th>
                     <th>Precio</th>
                     <th>Total</th>
                     <th></th>
                   </tr>
                 </thead>
                 <tbody>
                   {#each repairItems as item}
                     <tr>
                       <td>{item.inventory_item?.name || 'Refacción'}</td>
                       <td>{item.quantity}</td>
                       <td>${item.unit_price.toFixed(2)}</td>
                       <td>${(item.unit_price * item.quantity).toFixed(2)}</td>
                       <td>
                         <button 
                           class="btn btn-sm btn-danger"
                           on:click={() => removePartFromRepair(item)}
                         >
                           ✕
                         </button>
                       </td>
                     </tr>
                   {/each}
                 </tbody>
                 <tfoot>
                   <tr>
                     <td colspan="3" class="text-right"><strong>Total:</strong></td>
                     <td><strong>${getItemsTotal().toFixed(2)}</strong></td>
                     <td></td>
                   </tr>
                 </tfoot>
               </table>
             {/if}
           </div>
         </div>
         
         <div class="modal-footer">
           <button class="btn btn-outline" on:click={() => showPartsModal = false}>Cerrar</button>
         </div>
       </div>
     </div>
   {/if}
   
   <!-- Scanner Modal -->
   {#if showScanner}
     <div class="modal-overlay" on:click|self={() => showScanner = false}>
       <div class="modal modal-lg">
         <div class="modal-header">
           <h3 class="modal-title">📷 Escanear Código</h3>
           <button class="modal-close" on:click={() => showScanner = false}>×</button>
         </div>
         
         <div class="modal-body">
           <p class="text-center mb-4">
             Apunta la cámara hacia un código QR o de barras para escanearlo
           </p>
           <Scanner 
             onScan={(code) => {
               handleScanResult(code);
               showScanner = false;
             }}
             placeholder="Escaneando..."
           />
         </div>
         
         <div class="modal-footer">
           <button class="btn btn-outline" on:click={() => showScanner = false}>Cancelar</button>
         </div>
       </div>
     </div>
   {/if}

  <!-- Modal de Completar/Cobrar -->
  {#if showCompleteModal}
    <div class="modal-overlay" on:click|self={() => showCompleteModal = false}>
      <div class="modal modal-lg">
        <div class="modal-header">
          <h3 class="modal-title">💰 Completar Reparación - {selectedRepair?.repair_number}</h3>
          <button class="modal-close" on:click={() => showCompleteModal = false}>×</button>
        </div>
        
        <div class="modal-body">
          <!-- Resumen -->
          <div class="summary-box mb-4">
            <h4>Resumen</h4>
            <div class="summary-row">
              <span>Refacciones:</span>
              <span>${getItemsTotal().toFixed(2)}</span>
            </div>
            <div class="summary-row">
              <span>Mano de obra:</span>
              <span>
                <input 
                  type="number" 
                  step="0.01" 
                  class="input input-sm" 
                  style="width: 100px;"
                  bind:value={completeForm.labor_cost} 
                />
              </span>
            </div>
            <div class="summary-row summary-total">
              <span>Total:</span>
              <span>${getCompleteTotal().toFixed(2)}</span>
            </div>
          </div>
          
          <!-- Forma de pago -->
          <div class="form-group">
            <label class="label" for="payment_method">Forma de Pago</label>
            <select id="payment_method" class="select" bind:value={completeForm.payment_method}>
              {#each paymentMethods as method}
                <option value={method.value}>{method.label}</option>
              {/each}
            </select>
          </div>
          
          <div class="form-group">
            <label class="label" for="reference">Referencia</label>
            <input 
              id="reference" 
              type="text" 
              class="input" 
              placeholder="Número de transacción,folio..." 
              bind:value={completeForm.reference} 
            />
          </div>
          
          <div class="form-group">
            <label class="label" for="notes">Notas</label>
            <textarea 
              id="notes" 
              class="textarea" 
              rows="2" 
              bind:value={completeForm.notes}
            ></textarea>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-outline" on:click={() => showCompleteModal = false}>Cancelar</button>
          <button class="btn btn-success" on:click={completeRepair}>
            ✅ Completar y Cobrar
          </button>
        </div>
      </div>
    </div>
  {/if}
  </div>
</Layout>

<style>
  .repairs-page {
    max-width: 1400px;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .page-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--dark);
    margin-bottom: 0.25rem;
  }

  .page-subtitle {
    color: var(--text-light);
    font-size: 0.875rem;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
  }

  .stat-card {
    background: white;
    padding: 1.25rem;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    text-align: center;
    border-left: 4px solid var(--primary);
  }

  .stat-pending { border-left-color: var(--warning); }
  .stat-progress { border-left-color: var(--primary); }
  .stat-completed { border-left-color: var(--success); }
  .stat-total { border-left-color: var(--secondary); }

  .stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--dark);
  }

  .stat-label {
    font-size: 0.875rem;
    color: var(--text-light);
    margin-top: 0.25rem;
  }

  .filters-bar {
    margin-bottom: 1rem;
  }

  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem;
    color: var(--text-light);
  }

  .empty-state {
    text-align: center;
    padding: 3rem 1rem;
  }

  .empty-state-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
  }

  .empty-state-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--dark);
    margin-bottom: 0.5rem;
  }

  .select-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.8125rem;
  }

  .modal-lg {
    max-width: 700px;
  }

  /* Estilos para búsqueda de refacciones */
  .search-results {
    background: var(--light);
    padding: 1rem;
    border-radius: var(--radius);
  }

  .results-grid {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .result-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: white;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
    width: 100%;
  }

  .result-item:hover {
    border-color: var(--primary);
    background: var(--light);
  }

  .result-name {
    font-weight: 500;
    color: var(--dark);
  }

  .result-details {
    display: flex;
    gap: 1rem;
    font-size: 0.875rem;
    color: var(--text-light);
  }

  .result-details .price {
    color: var(--success);
    font-weight: 600;
  }

  .result-details .stock {
    color: var(--warning);
  }

  .items-section {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
  }

  .table-sm th,
  .table-sm td {
    padding: 0.5rem;
    font-size: 0.875rem;
  }

  .text-right {
    text-align: right;
  }

  /* Estilos para el modal de cobro */
  .summary-box {
    background: var(--light);
    padding: 1rem;
    border-radius: var(--radius);
    border: 2px solid var(--primary);
  }

  .summary-box h4 {
    margin-bottom: 0.75rem;
    color: var(--dark);
  }

  .summary-row {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--border);
  }

  .summary-row:last-child {
    border-bottom: none;
  }

  .summary-total {
    font-size: 1.125rem;
    font-weight: 700;
    color: var(--success);
    border-top: 2px solid var(--border);
    margin-top: 0.5rem;
    padding-top: 0.75rem;
  }

  .input-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.875rem;
  }

  .btn-success {
    background: var(--success);
    color: white;
  }

  .btn-success:hover {
    background: #16a34a;
  }

  .btn-danger {
    background: var(--danger);
    color: white;
  }

  .btn-danger:hover {
    background: #dc2626;
  }

  .text-muted {
    color: var(--text-light);
  }

  .text-sm {
    font-size: 0.875rem;
  }

  .mb-2 { margin-bottom: 0.5rem; }
  .mb-3 { margin-bottom: 0.75rem; }
  .mb-4 { margin-bottom: 1rem; }
  .mt-2 { margin-top: 0.5rem; }
  .mt-4 { margin-top: 1rem; }
  .mt-3 { margin-top: 0.75rem; }
  .p-3 { padding: 0.75rem; }
  .w-full { width: 100%; }
  .text-center { text-align: center; }

  /* Estilos para sección de refacciones en modal */
  .parts-section {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 2px solid var(--border);
  }

  .parts-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--dark);
    margin-bottom: 1rem;
  }

  .parts-list {
    max-height: 200px;
    overflow-y: auto;
  }

  .btn-xs {
    padding: 0.125rem 0.375rem;
    font-size: 0.75rem;
  }

  .search-results {
    max-height: 150px;
    overflow-y: auto;
    background: var(--light);
    padding: 0.5rem;
    border-radius: var(--radius-sm);
    margin-bottom: 0.75rem;
  }

  .result-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding: 0.5rem;
    background: white;
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    margin-bottom: 0.25rem;
    cursor: pointer;
    text-align: left;
  }

  .result-item:hover {
    border-color: var(--primary);
    background: var(--light);
  }

  .result-name {
    font-weight: 500;
    font-size: 0.875rem;
  }

  .result-details {
    font-size: 0.75rem;
    color: var(--text-light);
  }

  .result-details .price {
    color: var(--success);
    font-weight: 600;
  }

  .result-details .stock {
    color: var(--warning);
  }
</style>
