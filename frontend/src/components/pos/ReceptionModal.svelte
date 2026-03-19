<script>
  import { api } from '../../stores/api';
  import { notify } from '../../stores/auth';
  import QRCode from 'qrcode';
  import DeviceForm from '../devices/DeviceForm.svelte';

  export let show = false;
  export let customers = [];
  export let selectedCustomer = null;
  export let showCustomerForm = false;
  export let customerForm = { name: '', email: '', phone: '', whatsapp: '', telegram: '', address: '' };
  export let deviceForm = {
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
  export let photos = [];
  export let isProcessing = false;
  export let onClose = () => {};
  export let onSuccess = () => {};
  export let onPrintTicket = () => {};

  let createdDevice = null;

  async function handleFormSubmit(result) {
    try {
      const createdDevice = result.device;
      const repair = result.repair;

      if (repair) {
        // Generar QR
        const qrData = JSON.stringify({
          repair_id: repair.id,
          repair_number: repair.repair_number,
          device: createdDevice.brand + ' ' + createdDevice.model,
          customer: result.customer.name
        });
        const qrCodeDataUrl = await QRCode.toDataURL(qrData, { width: 300 });

        // Imprimir ticket
        onPrintTicket({
          type: 'recepcion',
          customer: result.customer,
          device: createdDevice,
          repair: repair,
          qrCode: qrCodeDataUrl,
          photos: photos,
          date: new Date().toISOString()
        });
      }

      notify('Dispositivo recibido correctamente', 'success');
      onSuccess();
      onClose();
    } catch (error) {
      notify('Error: ' + error.message, 'danger');
    }
  }

  function handleClose() {
    deviceForm = { device_type: '', brand: '', model: '', serial_number: '', color: '', storage: '', password_pattern: '', accessories: '', description: '', priority: 'normal' };
    photos = [];
    selectedCustomer = null;
    customerForm = { name: '', email: '', phone: '', whatsapp: '', telegram: '', address: '' };
    showCustomerForm = false;
    onClose();
  }
</script>

{#if show}
<div class="modal-overlay" on:click|self={handleClose}>
  <div class="modal modal-xl">
    <div class="modal-header">
      <div><h3 class="modal-title">Nueva Recepción</h3><p class="modal-subtitle">Registro de dispositivo y reparación</p></div>
      <button class="modal-close" on:click={handleClose}>×</button>
    </div>
    <div class="modal-body">
      <DeviceForm
        {customers}
        bind:selectedCustomer
        bind:showCustomerForm
        bind:customerForm
        bind:deviceForm
        bind:photos
        {isProcessing}
        showPhotos={true}
        showDescription={true}
        submitLabel="Recibir Dispositivo"
        onSubmit={handleFormSubmit}
        onClose={handleClose}
      />
    </div>
  </div>
</div>
{/if}

<style>
  .modal-xl { max-width: 900px; }
  .modal-header { border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 1rem; }
  .modal-title { margin: 0; }
  .modal-subtitle { font-size: 0.875rem; color: var(--text-light); margin: 0.25rem 0 0; }
</style>
