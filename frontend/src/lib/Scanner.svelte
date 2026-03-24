<script>
  import { onMount, onDestroy } from 'svelte';
  import QrScanner from 'qr-scanner';

  export let onScan = () => {};
  export let placeholder = 'Escaneando...';

  let videoElement;
  let qrScanner;
  let hasCamera = true;
  let errorMessage = '';

  onMount(async () => {
    if (videoElement) {
      try {
        qrScanner = new QrScanner(
          videoElement,
          (result) => {
            if (result && result.data) {
              onScan(result.data);
            }
          },
          {
            returnDetailedScanResult: true,
            highlightScanRegion: true,
            highlightCodeOutline: true,
          }
        );

        await qrScanner.start();
      } catch (error) {
        console.error('Error starting QR Scanner:', error);
        hasCamera = false;
        errorMessage = 'No se pudo acceder a la cámara. Por favor, asegúrate de dar los permisos necesarios.';
      }
    }
  });

  onDestroy(() => {
    if (qrScanner) {
      qrScanner.stop();
      qrScanner.destroy();
    }
  });
</script>

<div class="scanner-container">
  {#if hasCamera}
    <div class="video-wrapper">
      <video bind:this={videoElement} playsinline></video>
      <div class="scan-overlay">
        <div class="scan-frame"></div>
        <p class="scan-placeholder">{placeholder}</p>
      </div>
    </div>
  {:else}
    <div class="scanner-error">
      <span class="error-icon">⚠️</span>
      <p>{errorMessage}</p>
    </div>
  {/if}
</div>

<style>
  .scanner-container {
    width: 100%;
    max-width: 500px;
    margin: 0 auto;
    aspect-ratio: 4 / 3;
    background: #000;
    border-radius: 12px;
    overflow: hidden;
    position: relative;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  }

  .video-wrapper {
    width: 100%;
    height: 100%;
    position: relative;
  }

  video {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .scan-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    pointer-events: none;
    background: rgba(0, 0, 0, 0.2);
  }

  .scan-frame {
    width: 250px;
    height: 250px;
    border: 2px solid var(--primary, #007bff);
    border-radius: 16px;
    position: relative;
    box-shadow: 0 0 0 100vmax rgba(0, 0, 0, 0.4);
  }

  .scan-frame::before {
    content: '';
    position: absolute;
    top: 10%;
    left: 10%;
    right: 10%;
    height: 2px;
    background: var(--primary, #007bff);
    box-shadow: 0 0 8px var(--primary, #007bff);
    animation: scan 2s linear infinite;
  }

  @keyframes scan {
    0% { top: 10%; }
    50% { top: 90%; }
    100% { top: 10%; }
  }

  .scan-placeholder {
    margin-top: 2rem;
    color: white;
    font-weight: 500;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
    z-index: 10;
  }

  .scanner-error {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    text-align: center;
    color: white;
  }

  .error-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }
</style>
