<script>
  export let show = false;
  export let photos = [];
  export let currentIndex = 0;
  export let onClose = () => {};

  function goToPrevious() {
    currentIndex = currentIndex > 0 ? currentIndex - 1 : photos.length - 1;
  }

  function goToNext() {
    currentIndex = currentIndex < photos.length - 1 ? currentIndex + 1 : 0;
  }

  function handleKeyDown(event) {
    if (event.key === 'ArrowLeft') goToPrevious();
    if (event.key === 'ArrowRight') goToNext();
    if (event.key === 'Escape') onClose();
  }
</script>

{#if show}
<div class="photo-gallery-overlay" on:click|self={onClose} on:keydown={handleKeyDown} tabindex="0">
  <div class="photo-gallery">
    <div class="gallery-header">
      <span class="gallery-counter">{currentIndex + 1} / {photos.length}</span>
      <button class="gallery-close" on:click={onClose}>×</button>
    </div>

    <div class="gallery-main">
      <button class="gallery-nav gallery-prev" on:click={goToPrevious} disabled={photos.length <= 1}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
      </button>

      <div class="gallery-image-container">
        {#if photos[currentIndex].includes('.mp4') || photos[currentIndex].includes('.mov') || photos[currentIndex].includes('video')}
        <video src={photos[currentIndex]} controls autoplay></video>
        {:else}
        <img src={photos[currentIndex]} alt="Foto {currentIndex + 1}" />
        {/if}
      </div>

      <button class="gallery-nav gallery-next" on:click={goToNext} disabled={photos.length <= 1}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6"/>
        </svg>
      </button>
    </div>

    {#if photos.length > 1}
    <div class="gallery-thumbnails">
      {#each photos as photo, index}
      <button 
        class="thumbnail {index === currentIndex ? 'active' : ''}"
        on:click={() => currentIndex = index}
      >
        {#if photo.includes('.mp4') || photo.includes('.mov') || photo.includes('video')}
        <span class="video-icon">🎥</span>
        {:else}
        <img src={photo} alt="Miniatura {index + 1}" />
        {/if}
      </button>
      {/each}
    </div>
    {/if}
  </div>
</div>
{/if}

<style>
  .photo-gallery-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.95);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    outline: none;
  }

  .photo-gallery {
    width: 95%;
    max-width: 1200px;
    height: 90vh;
    display: flex;
    flex-direction: column;
    background: #1a1a1a;
    border-radius: var(--radius-lg);
    overflow: hidden;
  }

  .gallery-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: #2a2a2a;
  }

  .gallery-counter {
    color: white;
    font-size: 1rem;
    font-weight: 600;
  }

  .gallery-close {
    background: none;
    border: none;
    color: white;
    font-size: 2rem;
    cursor: pointer;
    padding: 0.25rem 0.5rem;
    line-height: 1;
    transition: color 0.2s;
  }

  .gallery-close:hover {
    color: var(--danger);
  }

  .gallery-main {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    padding: 1rem;
    overflow: hidden;
  }

  .gallery-nav {
    background: rgba(255, 255, 255, 0.1);
    border: none;
    color: white;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    flex-shrink: 0;
  }

  .gallery-nav:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.2);
  }

  .gallery-nav:disabled {
    opacity: 0.3;
    cursor: not-allowed;
  }

  .gallery-nav svg {
    width: 24px;
    height: 24px;
  }

  .gallery-image-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }

  .gallery-image-container img,
  .gallery-image-container video {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    border-radius: var(--radius);
  }

  .gallery-thumbnails {
    display: flex;
    gap: 0.5rem;
    padding: 1rem;
    background: #2a2a2a;
    overflow-x: auto;
  }

  .thumbnail {
    width: 80px;
    height: 80px;
    border-radius: var(--radius-sm);
    overflow: hidden;
    border: 2px solid transparent;
    cursor: pointer;
    transition: all 0.2s;
    background: #3a3a3a;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .thumbnail:hover {
    border-color: var(--primary);
  }

  .thumbnail.active {
    border-color: var(--primary);
    box-shadow: 0 0 0 2px var(--primary);
  }

  .thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .video-icon {
    font-size: 2rem;
  }

  @media (max-width: 768px) {
    .photo-gallery {
      width: 100%;
      height: 100vh;
      border-radius: 0;
    }

    .gallery-nav {
      width: 40px;
      height: 40px;
    }

    .gallery-nav svg {
      width: 20px;
      height: 20px;
    }

    .thumbnail {
      width: 60px;
      height: 60px;
    }
  }
</style>
