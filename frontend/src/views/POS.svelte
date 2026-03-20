<script>
  import { onMount } from 'svelte';
  import { api } from '../stores/api';
  import { notify } from '../stores/auth';
  import Layout from '../components/Layout.svelte';
  import QrScanner from 'qr-scanner';
  import { fileTypeFromBuffer } from 'file-type';

  // Componentes nuevos del POS
  import ToggleView from '../components/pos/ToggleView.svelte';
  import DeviceCard from '../components/pos/DeviceCard.svelte';
  import DeviceListItem from '../components/pos/DeviceListItem.svelte';
  import DeviceSearchBar from '../components/pos/DeviceSearchBar.svelte';
  import ReceptionModal from '../components/pos/ReceptionModal.svelte';
  import DeviceDetailModal from '../components/pos/DeviceDetailModal.svelte';
  import PhotoGallery from '../components/pos/PhotoGallery.svelte';
  import POSCart from '../components/pos/POSCart.svelte';
  import TicketModal from '../components/common/TicketModal.svelte';

  const ALLOWED_MIME_TYPES = new Set([
    'image/jpeg',
    'image/png',
    'image/webp',
    'video/mp4',
    'video/quicktime',
    'video/webm'
  ]);

  const MAX_IMAGE_SIZE = 5 * 1024 * 1024;
  const MAX_VIDEO_SIZE = 30 * 1024 * 1024;

  let viewMode = 'grid';
  let cartItems = [];

  // Datos para recepción de dispositivos
  let customers = [];
  let selectedCustomer = null;
  let showCustomerForm = false;
  let customerForm = {
    name: '',
    email: '',
    phone: '',
    whatsapp: '',
    telegram: '',
    address: ''
  };

  let deviceForm = {
    device_type: 'smartphone',
    brand: '',
    model: '',
    serial_number: '',
    color: '',
    storage: '',
    password_pattern: '',
    accessories: '',
    description: '',
    priority: 'normal'
  };

  let photos = [];
  let showCamera = false;
  let videoElement = null;
  let scanner = null;
  let isProcessing = false;

  // Dispositivos para mostrar
  let devices = [];
  let deviceSearch = '';
  let deviceFilters = {
    status: '',
    device_type: '',
    brand: ''
  };
  let showFilters = false;

  // Modales
  let showReceptionModal = false;
  let showDeviceDetailModal = false;
  let showPhotoGallery = false;
  let selectedDevice = null;
  let selectedDeviceRepairs = [];
  let galleryPhotos = [];
  let galleryCurrentIndex = 0;

  // Ticket
  let showTicket = false;
  let ticketData = null;
  let showPhotosModal = false;
  let showScanQR = false;

  // Cámara
  let cameraMode = 'photo';
  let isRecording = false;
  let mediaRecorder = null;
  let videoChunks = [];

  onMount(async () => {
    await Promise.all([loadCustomers(), loadDevicesForDelivery()]);
  });

  async function loadCustomers() {
    try {
      customers = await api.getCustomers({ limit: 100 });
    } catch (error) {
      notify('Error al cargar clientes', 'danger');
    }
  }

  async function loadDevicesForDelivery() {
    try {
      console.log('Cargando dispositivos...');
      const params = {};
      if (deviceSearch) {
        params.search = deviceSearch;
      }
      if (deviceFilters.status) {
        params.status = deviceFilters.status;
      }
      if (deviceFilters.device_type) {
        params.device_type = deviceFilters.device_type;
      }
      if (deviceFilters.brand) {
        params.brand = deviceFilters.brand;
      }
      console.log('Params:', params);
      devices = await api.getDevices(params);
      console.log('Devices loaded:', devices);
    } catch (error) {
      console.error('Error loading devices:', error);
      notify('Error al cargar dispositivos', 'danger');
    }
  }

  function filteredDevices() {
    if (!deviceSearch && !deviceFilters.status && !deviceFilters.device_type && !deviceFilters.brand) {
      return devices;
    }
    
    return devices.filter(device => {
      const customerName = device.customer?.name || '';
      const customerPhone = device.customer?.phone || '';
      const deviceName = `${device.brand} ${device.model}`.toLowerCase();
      const searchLower = deviceSearch.toLowerCase();
      
      const matchesSearch = !deviceSearch || 
        deviceName.includes(searchLower) ||
        customerName.toLowerCase().includes(searchLower) ||
        customerPhone.includes(deviceSearch);
      
      const matchesStatus = !deviceFilters.status || device.status === deviceFilters.status;
      const matchesType = !deviceFilters.device_type || device.device_type === deviceFilters.device_type;
      const matchesBrand = !deviceFilters.brand || device.brand.toLowerCase().includes(deviceFilters.brand.toLowerCase());
      
      return matchesSearch && matchesStatus && matchesType && matchesBrand;
    });
  }

  function openReceptionModal() {
    selectedCustomer = null;
    showCustomerForm = false;
    customerForm = { name: '', email: '', phone: '', whatsapp: '', telegram: '', address: '' };
    deviceForm = { device_type: 'smartphone', brand: '', model: '', serial_number: '', color: '', storage: '', password_pattern: '', accessories: '', description: '', priority: 'normal' };
    photos = [];
    showReceptionModal = true;
  }

  async function onViewDevice(device) {
    selectedDevice = device;
    try {
      selectedDeviceRepairs = await api.getRepairs({ device_id: device.id });
    } catch (error) {
      selectedDeviceRepairs = [];
    }
    showDeviceDetailModal = true;
  }

  function onEditDevice(device) {
    notify('Función de edición en desarrollo', 'info');
  }

  function onOpenGallery(device) {
    console.log('Opening gallery for device:', device);
    if (device.photos) {
      galleryPhotos = device.photos.split(',').filter(p => p.trim());
      console.log('Gallery photos:', galleryPhotos);
      galleryCurrentIndex = 0;
      showPhotoGallery = true;
      console.log('Gallery opened:', showPhotoGallery);
    } else {
      notify('Este dispositivo no tiene fotos', 'info');
    }
  }

  async function onStatusChange(device) {
    const newStatus = prompt(
      `Cambiar estado de ${device.brand} ${device.model}:\n\n` +
      `Estados disponibles:\n` +
      `- registered\n` +
      `- in_repair\n` +
      `- waiting_parts\n` +
      `- ready\n` +
      `- delivered\n\n` +
      `Nuevo estado:`
    );
    
    if (newStatus && ['registered', 'in_repair', 'waiting_parts', 'ready', 'delivered'].includes(newStatus)) {
      try {
        await api.updateDevice(device.id, { status: newStatus });
        notify('Estado actualizado correctamente', 'success');
        await loadDevicesForDelivery();
      } catch (error) {
        notify('Error al actualizar estado', 'danger');
      }
    } else if (newStatus) {
      notify('Estado no válido', 'warning');
    }
  }

  // Funciones de cámara
  async function openCamera(mode = 'photo') {
    cameraMode = mode;
    showCamera = true;
    await new Promise(resolve => setTimeout(resolve, 100));

    if (videoElement) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment' },
          audio: mode === 'video'
        });
        videoElement.srcObject = stream;

        if (mode === 'video') {
          mediaRecorder = new MediaRecorder(stream, {
            mimeType: MediaRecorder.isTypeSupported('video/webm') ? 'video/webm' : 'video/mp4'
          });

          mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
              videoChunks.push(event.data);
            }
          };

          mediaRecorder.onstop = async () => {
            const blob = new Blob(videoChunks, { type: 'video/mp4' });
            const videoUrl = URL.createObjectURL(blob);
            photos.push(videoUrl);
            videoChunks = [];
            notify('Video grabado', 'success');
            closeCamera();
          };
        }
      } catch (error) {
        notify('Error al abrir cámara: ' + error.message, 'danger');
        showCamera = false;
      }
    }
  }

  function closeCamera() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
    if (videoElement && videoElement.srcObject) {
      videoElement.srcObject.getTracks().forEach(track => track.stop());
    }
    showCamera = false;
  }

  async function takePhoto() {
    if (!videoElement) return;

    const canvas = document.createElement('canvas');
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    canvas.getContext('2d').drawImage(videoElement, 0, 0);

    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.8));
    const buffer = await blob.arrayBuffer();
    
    if (buffer.byteLength > MAX_IMAGE_SIZE) {
      notify('Imagen muy grande. Máximo 5MB', 'danger');
      return;
    }

    const photoUrl = URL.createObjectURL(blob);
    photos.push(photoUrl);
    notify('Foto tomada', 'success');
  }

  async function toggleRecording() {
    if (!mediaRecorder) return;

    if (isRecording) {
      mediaRecorder.stop();
      isRecording = false;
    } else {
      videoChunks = [];
      mediaRecorder.start();
      isRecording = true;
      notify('Grabando video... (30s máx)', 'info');

      setTimeout(() => {
        if (isRecording && mediaRecorder.state !== 'inactive') {
          mediaRecorder.stop();
          isRecording = false;
          notify('Video grabado', 'success');
          closeCamera();
        }
      }, 30000);
    }
  }

  // Escanear QR
  async function openQRScanner() {
    showScanQR = true;
    await new Promise(resolve => setTimeout(resolve, 100));

    const video = document.getElementById('qr-scanner-video');
    if (video) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment' }
        });
        video.srcObject = stream;

        const qrScanner = new QrScanner(video, async result => {
          try {
            const data = JSON.parse(result.data);
            if (data.repair_id) {
              const repairs = await api.getRepairs({});
              const repair = repairs.find(r => r.id === data.repair_id);
              if (repair) {
                notify(`Orden #${repair.repair_number} encontrada`, 'success');
                selectedDevice = repair.device;
                showPhotosModal = true;
                closeQRScanner();
              }
            }
          } catch (e) {
            console.error('Error parsing QR:', e);
          }
        }, {
          returnDetailedScanResult: true
        });

        await qrScanner.start();
        window.currentQRScanner = qrScanner;
      } catch (error) {
        notify('Error al abrir cámara: ' + error.message, 'danger');
        showScanQR = false;
      }
    }
  }

  function closeQRScanner() {
    if (window.currentQRScanner) {
      window.currentQRScanner.stop();
      window.currentQRScanner.destroy();
      window.currentQRScanner = null;
    }
    const video = document.getElementById('qr-scanner-video');
    if (video && video.srcObject) {
      video.srcObject.getTracks().forEach(track => track.stop());
    }
    showScanQR = false;
  }

  let printClass = '';
  function printTicket(data) {
    if (typeof data === 'string') {
      // Si recibimos un string, es un comando de impresión específica
      printClass = data;
      setTimeout(() => {
        window.print();
        // No reseteamos printClass aquí porque window.print es bloqueante en muchos navegadores,
        // pero queremos que se limpie DESPUÉS de imprimir.
        // Un truco común es usar un evento 'afterprint'
      }, 100);
      return;
    }
    ticketData = data;
    showTicket = true;
    printClass = '';
  }
  
  // Limpiar clase después de imprimir
  if (typeof window !== 'undefined') {
    window.onafterprint = () => { printClass = ''; };
  }

  function closeTicket() {
    showTicket = false;
    ticketData = null;
  }

  async function handleCheckout(cartData) {
    const { items, payment_method, amount_paid, total, change } = cartData;
    let saleResult = null;
    let currentAmount = amount_paid;

    try {
      isProcessing = true;
      const productItems = items.filter(i => i.type === 'product');
      const repairItems = items.filter(i => i.type === 'repair');

      // 1. Cobrar productos (Venta)
      if (productItems.length > 0) {
        const salePayload = {
          items: productItems.map(p => ({
            inventory_item_id: p.id,
            quantity: p.quantity,
            unit_price: p.price,
            subtotal: p.price * p.quantity
          })),
          payment_method: payment_method,
          amount_paid: amount_paid, // We can pass the whole amount_paid for now, the backend compares to total
          customer_id: selectedCustomer?.id || null
        };
        saleResult = await api.createSale(salePayload);
        // Decrease amount available for next steps if needed, though usually handled as single payment
      }

      // 2. Cobrar reparaciones
      for (const repairItem of repairItems) {
        // En un caso real, llamaríamos a api.createPayment de reparación o api.completeRepair
        // Aquí simulamos que cambia el estado a entregado
        const repairs = await api.getRepairs({});
        const realRepair = repairs.find(r => r.id === repairItem.id);
        if (realRepair) {
           await api.updateDevice(realRepair.device_id, { status: 'delivered' });
           await api.updateRepair(realRepair.id, { status: 'delivered' });
           
           // Registrar pago
           await api.createPayment({
              repair_id: realRepair.id,
              amount: repairItem.price,
              payment_method: payment_method,
              notes: "Pago en POS"
           });
        }
      }

      notify('Cobro realizado con éxito', 'success');
      
      // Imprimir ticket de venta
      let ticketItems = [];
      if (saleResult) {
        ticketItems = [...ticketItems, ...saleResult.items.map(i => ({
          name: i.name || 'Producto',
          quantity: i.quantity,
          sale_price: i.unit_price,
          subtotal: i.subtotal
        }))];
      }
      for (const r of repairItems) {
        ticketItems.push({
          name: r.name,
          quantity: 1,
          sale_price: r.price,
          subtotal: r.price
        });
      }

      printTicket({
        type: 'venta',
        customer: selectedCustomer || { name: 'Público General' },
        items: ticketItems,
        total: total,
        date: new Date().toISOString(),
        sale_number: saleResult?.sale_number
      });

      await loadDevicesForDelivery();
    } catch (error) {
      notify('Error al procesar el cobro: ' + error.message, 'danger');
      throw error;
    } finally {
      isProcessing = false;
    }
  }

  function handleAddToCart(device) {
    if (device.status !== 'ready') return;
    
    // We need the repair to add to cart
    api.getRepairs({ device_id: device.id }).then(repairs => {
      const activeRepair = repairs.find(r => r.status === 'ready' || r.status === 'completed' || r.status === 'in_progress');
      if (activeRepair) {
        // Find if already in cart
        if (!cartItems.find(i => i.id === activeRepair.id && i.type === 'repair')) {
          cartItems = [...cartItems, {
            id: activeRepair.id,
            type: 'repair',
            name: `Servicio: ${device.brand} ${device.model}`,
            price: activeRepair.final_cost || activeRepair.estimated_cost || 0,
            quantity: 1,
            max_quantity: 1
          }];
          notify('Añadido al carrito', 'success');
        }
      } else {
        notify('No se encontró orden de reparación activa', 'warning');
      }
    });
  }
</script>

<Layout>
  <div class="pos-page">
    <!-- Header -->
    <div class="pos-header">
      <div>
        <h1 class="page-title">Recepción de Dispositivos</h1>
        <p class="page-subtitle">Gestión de dispositivos para entrega</p>
      </div>
    </div>

    <!-- Vista de Dispositivos -->
    <div class="devices-view">
      <!-- Barra de herramientas -->
      <div class="devices-toolbar">
        <div class="toolbar-left">
          <ToggleView bind:viewMode />
        </div>
        <div class="toolbar-right">
          <button class="btn btn-icon-secondary" on:click={openQRScanner} title="Escanear QR">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="7" height="7"/>
              <rect x="14" y="3" width="7" height="7"/>
              <rect x="14" y="14" width="7" height="7"/>
              <rect x="3" y="14" width="7" height="7"/>
            </svg>
          </button>
          <button class="btn btn-primary" on:click={openReceptionModal}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            <span class="btn-text">Nueva Recepción</span>
          </button>
        </div>
      </div>

      <!-- Buscador -->
      <div style="padding: 1rem; background: white; margin-bottom: 1rem; border-radius: 8px;">
        <input 
          type="text" 
          class="input" 
          placeholder="Buscar..." 
          bind:value={deviceSearch}
          on:input={() => loadDevicesForDelivery()}
          style="max-width: 300px;"
        />
        <button class="btn btn-outline" on:click={loadDevicesForDelivery}>Buscar</button>
      </div>

      <!-- Lista de dispositivos -->
      <div class="pos-layout">
        <div class="pos-main">
          {#if devices.length === 0}
            <div class="empty-state">
              <div class="empty-state-icon">📱</div>
              <p class="empty-state-title">No hay dispositivos</p>
              <p class="empty-state-description">
                {deviceSearch || deviceFilters.status || deviceFilters.device_type || deviceFilters.brand
                  ? 'No se encontraron dispositivos con los filtros actuales'
                  : 'Comienza recibiendo un nuevo dispositivo'}
              </p>
              {#if !deviceSearch && !deviceFilters.status && !deviceFilters.device_type && !deviceFilters.brand}
                <button class="btn btn-primary mt-4" on:click={openReceptionModal}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="12" y1="5" x2="12" y2="19"/>
                    <line x1="5" y1="12" x2="19" y2="12"/>
                  </svg>
                  Recibir Dispositivo
                </button>
              {/if}
            </div>
          {:else}
            {#if viewMode === 'grid'}
              <div class="devices-grid">
                {#each devices as device}
                  <div class="device-card-wrapper">
                    <DeviceCard
                      {device}
                      customerName={device.customer?.name || 'Sin cliente'}
                      onView={onViewDevice}
                      onEdit={onEditDevice}
                      onStatusChange={onStatusChange}
                      onOpenGallery={onOpenGallery}
                    />
                    {#if device.status === 'ready'}
                      <button class="btn btn-success btn-block mt-2" on:click={() => handleAddToCart(device)}>
                        Cargar a Caja
                      </button>
                    {/if}
                  </div>
                {/each}
              </div>
            {:else}
              <div class="devices-list">
                {#each devices as device}
                  <div class="device-list-item-wrapper" style="display: flex; gap: 1rem; align-items: center;">
                    <div style="flex: 1;">
                      <DeviceListItem
                        {device}
                        customerName={device.customer?.name || 'Sin cliente'}
                        onView={onViewDevice}
                        onEdit={onEditDevice}
                        onStatusChange={onStatusChange}
                      />
                    </div>
                    {#if device.status === 'ready'}
                      <button class="btn btn-success" on:click={() => handleAddToCart(device)}>
                        Cobrar
                      </button>
                    {/if}
                  </div>
                {/each}
              </div>
            {/if}
          {/if}
        </div>
        <div class="pos-sidebar">
          <POSCart bind:cartItems onCheckout={handleCheckout} />
        </div>
      </div>
    </div>

    <!-- Modal de Recepción -->
    <ReceptionModal
      show={showReceptionModal}
      {customers}
      bind:selectedCustomer
      bind:showCustomerForm
      bind:customerForm
      bind:deviceForm
      bind:photos
      {isProcessing}
      onClose={() => showReceptionModal = false}
      onSuccess={async () => { await loadCustomers(); await loadDevicesForDelivery(); }}
      onPrintTicket={printTicket}
    />

    <!-- Modal de Detalle de Dispositivo -->
    <DeviceDetailModal
      show={showDeviceDetailModal}
      device={selectedDevice}
      customer={selectedDevice?.customer}
      repairs={selectedDeviceRepairs}
      onClose={() => showDeviceDetailModal = false}
      onEdit={onEditDevice}
      onStatusChange={onStatusChange}
    />

    <!-- Modal Cámara -->
    {#if showCamera}
      <div class="modal-overlay" on:click|self={closeCamera}>
        <div class="modal modal-lg camera-modal">
          <div class="modal-header">
            <h3>{cameraMode === 'photo' ? 'Tomar Foto' : 'Grabar Video'} del Dispositivo</h3>
            <button class="modal-close" on:click={closeCamera}>×</button>
          </div>
          <div class="modal-body">
            <video id="camera-video" bind:this={videoElement} autoplay playsinline></video>
            <div class="camera-controls">
              {#if cameraMode === 'photo'}
                <button class="btn btn-primary btn-lg" on:click={takePhoto}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
                    <circle cx="12" cy="13" r="4"/>
                  </svg>
                  Capturar Foto
                </button>
              {:else}
                <button
                  class="btn {isRecording ? 'btn-danger' : 'btn-primary'} btn-lg"
                  on:click={toggleRecording}
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    {#if isRecording}
                      <rect x="6" y="6" width="12" height="12"/>
                    {:else}
                      <polygon points="23 7 16 12 23 17 23 7"/>
                      <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                    {/if}
                  </svg>
                  {isRecording ? 'Detener Grabación' : 'Iniciar Grabación'}
                </button>
              {/if}
            </div>
            {#if cameraMode === 'video' && isRecording}
              <p class="text-center text-muted mt-2">
                <span class="spinner" style="display:inline; width:12px; height:12px; border-width:2px;"></span>
                Grabando... (máx 30s)
              </p>
            {/if}
          </div>
        </div>
      </div>
    {/if}

    <!-- Modal Escanear QR -->
    {#if showScanQR}
      <div class="modal-overlay" on:click|self={closeQRScanner}>
        <div class="modal modal-lg">
          <div class="modal-header">
            <h3>Escanear Código QR</h3>
            <button class="modal-close" on:click={closeQRScanner}>×</button>
          </div>
          <div class="modal-body">
            <p class="text-center text-muted">Apunte la cámara hacia el código QR de la orden</p>
            <video id="qr-scanner-video" autoplay playsinline style="width: 100%; max-width: 400px;"></video>
          </div>
        </div>
      </div>
    {/if}

    <!-- Ticket Modal Unificado -->
    <TicketModal
      show={showTicket}
      {ticketData}
      onClose={closeTicket}
    />

    <!-- Galería de Fotos -->
    <PhotoGallery
      show={showPhotoGallery}
      photos={galleryPhotos}
      currentIndex={galleryCurrentIndex}
      onClose={() => showPhotoGallery = false}
    />
  </div>
</Layout>

<style>
  .pos-page {
    max-width: 1400px;
    margin: 0 auto;
    padding-bottom: 4rem;
  }

  .pos-header {
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

  /* Devices View Layout */
  .pos-layout {
    display: flex;
    gap: 1.5rem;
    align-items: flex-start;
  }

  .pos-main {
    flex: 1;
    min-width: 0;
  }

  .pos-sidebar {
    width: 350px;
    position: sticky;
    top: 1.5rem;
    height: calc(100vh - 120px);
  }

  .devices-view {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .devices-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .toolbar-left,
  .toolbar-right {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  /* Botón de icono cuadrado para QR */
  .btn-icon-secondary {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 42px;
    height: 42px;
    padding: 0;
    background: var(--secondary);
    color: white;
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-icon-secondary:hover {
    background: #475569;
  }

  .btn-icon-secondary svg {
    width: 22px;
    height: 22px;
  }

  /* Asegurar que btn-primary tenga la misma altura */
  .toolbar-right .btn-primary {
    height: 42px;
    display: flex;
    align-items: center;
  }

  .devices-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
  }

  .devices-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  /* Empty state */
  .empty-state {
    text-align: center;
    padding: 4rem 1rem;
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
  }

  .empty-state-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.5;
  }

  .empty-state-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--dark);
    margin-bottom: 0.5rem;
  }

  .empty-state-description {
    color: var(--text-light);
    font-size: 0.9375rem;
    margin-bottom: 1.5rem;
  }

  /* Camera Modal */
  .camera-modal video {
    width: 100%;
    max-width: 500px;
    border-radius: var(--radius);
    background: #000;
  }

  .camera-controls {
    display: flex;
    justify-content: center;
    margin-top: 1rem;
    gap: 1rem;
  }

  .font-bold { font-weight: bold; }
  .italic { font-style: italic; }

  @media (max-width: 768px) {
    .devices-grid {
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    }

    .pos-header {
      flex-direction: column;
      align-items: flex-start;
    }
  }
</style>
