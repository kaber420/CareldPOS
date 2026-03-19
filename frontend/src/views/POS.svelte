<script>
  import { onMount } from 'svelte';
  import { api } from '../stores/api';
  import { notify } from '../stores/auth';
  import Layout from '../components/Layout.svelte';
  import QRCode from 'qrcode';
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

  // Datos para recepción de dispositivos
  let customers = [];
  let selectedCustomer = null;
  let showCustomerForm = false;
  let customerForm = {
    name: '',
    email: '',
    phone: '',
    address: ''
  };

  let deviceForm = {
    device_type: '',
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

  // QR y Ticket
  let showTicket = false;
  let ticketData = null;
  let qrCodeDataUrl = '';
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

  function printTicket(data) {
    ticketData = data;
    showTicket = true;

    setTimeout(() => {
      window.print();
      showTicket = false;
    }, 500);
  }

  function closeTicket() {
    showTicket = false;
    ticketData = null;
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
              <DeviceCard
                {device}
                customerName={device.customer?.name || 'Sin cliente'}
                onView={onViewDevice}
                onEdit={onEditDevice}
                onStatusChange={onStatusChange}
                onOpenGallery={onOpenGallery}
              />
            {/each}
          </div>
        {:else}
          <div class="devices-list">
            {#each devices as device}
              <DeviceListItem
                {device}
                customerName={device.customer?.name || 'Sin cliente'}
                onView={onViewDevice}
                onEdit={onEditDevice}
                onStatusChange={onStatusChange}
              />
            {/each}
          </div>
        {/if}
      {/if}
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
      onSuccess={loadDevicesForDelivery}
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

    <!-- Modal Ticket -->
    {#if showTicket && ticketData}
      <div class="modal-overlay" on:click|self={closeTicket}>
        <div class="modal modal-lg">
          <div class="modal-header">
            <h3>Ticket de Operación</h3>
            <button class="modal-close" on:click={closeTicket}>×</button>
          </div>
          <div class="modal-body">
            <div class="ticket" id="ticket-content">
              <div class="ticket-header">
                <h2>CareldPOS</h2>
                <p>Fecha: {new Date(ticketData.date).toLocaleString()}</p>
              </div>

              {#if ticketData.type === 'recepcion'}
                <div class="ticket-section">
                  <h4>RECEPCIÓN DE DISPOSITIVO</h4>
                  <p><strong>Cliente:</strong> {ticketData.customer.name}</p>
                  <p><strong>Teléfono:</strong> {ticketData.customer.phone}</p>
                </div>
                <div class="ticket-section">
                  <h4>Dispositivo</h4>
                  <p><strong>Tipo:</strong> {ticketData.device.device_type}</p>
                  <p><strong>Marca:</strong> {ticketData.device.brand}</p>
                  <p><strong>Modelo:</strong> {ticketData.device.model || 'N/A'}</p>
                  <p><strong>Color:</strong> {ticketData.device.color || 'N/A'}</p>
                  <p><strong>Accesorios:</strong> {ticketData.device.accessories || 'Ninguno'}</p>
                </div>
                <div class="ticket-section">
                  <h4>Orden de Reparación #{ticketData.repair.repair_number}</h4>
                  <p><strong>Estado:</strong> Pendiente</p>
                  <p><strong>Prioridad:</strong> {ticketData.repair.priority}</p>
                </div>
                {#if ticketData.qrCode}
                  <div class="ticket-qr">
                    <img src={ticketData.qrCode} alt="Código QR" />
                    <p class="text-sm text-muted">Escanee para ver el estado de su reparación</p>
                  </div>
                {/if}
              {:else if ticketData.type === 'venta'}
                <div class="ticket-section">
                  <h4>VENTA</h4>
                  <p><strong>Cliente:</strong> {ticketData.customer.name}</p>
                </div>
                <div class="ticket-section">
                  <table class="ticket-table">
                    <thead>
                      <tr>
                        <th>Cant.</th>
                        <th>Producto</th>
                        <th>Precio</th>
                        <th>Subtotal</th>
                      </tr>
                    </thead>
                    <tbody>
                      {#each ticketData.items as item}
                        <tr>
                          <td>{item.quantity}</td>
                          <td>{item.name}</td>
                          <td>${item.sale_price.toFixed(2)}</td>
                          <td>${(item.sale_price * item.quantity).toFixed(2)}</td>
                        </tr>
                      {/each}
                    </tbody>
                  </table>
                </div>
                <div class="ticket-total">
                  <strong>TOTAL: ${ticketData.total.toFixed(2)}</strong>
                </div>
              {/if}

              <div class="ticket-footer">
                <p>¡Gracias por su compra!</p>
                <p>Garantía: 30 días</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" on:click={closeTicket}>
              Cerrar
            </button>
            <button class="btn btn-primary" onclick="window.print()">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 6 2 18 2 18 9"/>
                <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
                <rect x="6" y="14" width="12" height="8"/>
              </svg>
              Imprimir
            </button>
          </div>
        </div>
      </div>
    {/if}

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

  /* Devices View */
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

  /* Ticket */
  .ticket {
    font-family: 'Courier New', monospace;
    padding: 1rem;
    background: white;
  }

  .ticket-qr {
    text-align: center;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 2px dashed #000;
  }

  .ticket-qr img {
    max-width: 200px;
  }

  .ticket-header {
    text-align: center;
    border-bottom: 2px dashed #000;
    padding-bottom: 1rem;
    margin-bottom: 1rem;
  }

  .ticket-section {
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px dashed #000;
  }

  .ticket-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8125rem;
  }

  .ticket-table th,
  .ticket-table td {
    padding: 0.5rem;
    text-align: left;
    border-bottom: 1px dashed #000;
  }

  .ticket-total {
    text-align: right;
    font-size: 1.125rem;
    margin-top: 1rem;
    padding-top: 0.5rem;
    border-top: 2px dashed #000;
  }

  .ticket-footer {
    text-align: center;
    padding-top: 1rem;
    font-size: 0.75rem;
    color: var(--text-light);
  }

  @media print {
    body * {
      visibility: hidden;
    }
    #ticket-content,
    #ticket-content * {
      visibility: visible;
    }
    #ticket-content {
      position: absolute;
      left: 0;
      top: 0;
      width: 80mm;
    }
    .modal-overlay {
      display: none !important;
    }
  }

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
