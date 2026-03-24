<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  const dispatch = createEventDispatcher();

  export let photos = [];
  export let isOpen = false;
  export let currentIndex = 0;

  function close() {
    dispatch('close');
  }

  function next() {
    if (photos.length === 0) return;
    currentIndex = (currentIndex + 1) % photos.length;
  }

  function prev() {
    if (photos.length === 0) return;
    currentIndex = (currentIndex - 1 + photos.length) % photos.length;
  }

  function handleKeydown(e) {
    if (!isOpen) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowRight') next();
    if (e.key === 'ArrowLeft') prev();
  }

  onMount(() => {
    window.addEventListener('keydown', handleKeydown);
    return () => window.removeEventListener('keydown', handleKeydown);
  });
</script>

{#if isOpen}
  <div class="carousel-overlay" transition:fade={{ duration: 200 }} on:click|self={close}>
    <button class="close-btn" on:click={close}>&times;</button>
    
    <div class="carousel-content">
      {#if photos.length > 1}
        <button class="nav-btn prev" on:click={prev}>&#10094;</button>
      {/if}

      <div class="image-container">
        {#if photos.length > 0}
          <img src={photos[currentIndex]} alt="Device photo {currentIndex + 1}">
        {:else}
          <div class="no-photo">Sin fotografía disponible</div>
        {/if}
      </div>

      {#if photos.length > 1}
        <button class="nav-btn next" on:click={next}>&#10095;</button>
      {/if}
    </div>

    {#if photos.length > 1}
      <div class="counter">{currentIndex + 1} / {photos.length}</div>
    {/if}
  </div>
{/if}

<style>
  .carousel-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(15, 23, 42, 0.95);
    backdrop-filter: blur(8px);
    z-index: 1000;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  .carousel-content {
    display: flex;
    align-items: center;
    gap: 2rem;
    max-width: 90vw;
    max-height: 80vh;
  }

  .image-container {
    background: #000;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 0 50px rgba(0,0,0,0.5);
    border: 1px solid rgba(255,255,255,0.1);
  }

  img {
    max-width: 100%;
    max-height: 80vh;
    display: block;
  }

  .no-photo {
    width: 300px;
    height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #94a3b8;
    font-size: 1rem;
    font-weight: 600;
  }

  .nav-btn {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    color: white;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 1.5rem;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .nav-btn:hover {
    background: #6366f1;
    border-color: #6366f1;
  }

  .close-btn {
    position: absolute;
    top: 2rem;
    right: 2rem;
    background: transparent;
    border: none;
    color: white;
    font-size: 3rem;
    cursor: pointer;
    line-height: 1;
    opacity: 0.6;
    transition: opacity 0.2s;
  }

  .close-btn:hover {
    opacity: 1;
  }

  .counter {
    margin-top: 2rem;
    color: #94a3b8;
    font-weight: 700;
    letter-spacing: 2px;
    background: rgba(255,255,255,0.05);
    padding: 0.5rem 1.25rem;
    border-radius: 20px;
    font-size: 0.9rem;
  }
</style>
