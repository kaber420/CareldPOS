<script>
  import { navigate } from 'svelte-routing';
  import { user, clearAuth, notify } from '../../../stores/auth';
  import { isCartOpen } from '../../../stores/cartUI';
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import FloatingPartnerCart from './FloatingPartnerCart.svelte';

  export let title = "Partner Hub";
  export let activeTab = 'repairs';

  function handleLogout() {
    clearAuth();
    notify('Sesión cerrada correctamente', 'info');
    navigate('/login');
  }

  onMount(() => {
    // Asegurar que Outfit esté cargado
    if (!document.getElementById('google-fonts-outfit')) {
      const link = document.createElement('link');
      link.id = 'google-fonts-outfit';
      link.rel = 'stylesheet';
      link.href = 'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;900&display=swap';
      document.head.appendChild(link);
    }
  });
</script>

<div id="partner-hub-root" class="partner-layout">
  <div class="ambient-light light-1"></div>
  <div class="ambient-light light-2"></div>

  <aside>
    <div class="user-profile">
      <div class="avatar">
        {$user?.full_name?.substring(0, 2).toUpperCase() || 'P'}
      </div>
      <div class="user-info">
        <h3>{$user?.full_name || $user?.username}</h3>
        <p>Distribuidor Autorizado</p>
      </div>
    </div>

    <nav>
      <ul>
        <li>
          <button 
            on:click={() => navigate('/partner-dashboard?tab=repairs')}
            class="nav-link {activeTab === 'repairs' ? 'active' : ''}"
          >
            <span>📊</span> Reparaciones
          </button>
        </li>
        <li>
          <button 
            on:click={() => navigate('/partner-dashboard?tab=parts')} 
            class="nav-link {activeTab === 'parts' ? 'active' : ''}"
          >
            <span>📦</span> Refacciones
          </button>
        </li>
        <li>
          <button 
            on:click={() => isCartOpen.update(v => !v)}
            class="nav-link"
          >
            <span>🛒</span> Carrito
          </button>
        </li>
        <li>
          <button class="nav-link" disabled style="opacity: 0.5; cursor: not-allowed;">
            <span>👤</span> Mi Cuenta
          </button>
        </li>
      </ul>
    </nav>

    <button on:click={handleLogout} class="logout-btn">
      <span>🚪</span> Cerrar Sesión
    </button>
  </aside>

  <main>
    <header>
      <div class="header-title">
        <h1>{title}</h1>
        <p>Gestión de servicios y refacciones en tiempo real.</p>
      </div>
    </header>

    <div class="content-view">
      <slot />
    </div>
  </main>
</div>

<FloatingPartnerCart />

<style>
  #partner-hub-root.partner-layout {
    --primary: #6366f1;
    --primary-light: #818cf8;
    --secondary: #a855f7;
    --bg-dark: #0f172a;
    --sidebar-bg: rgba(15, 23, 42, 0.8);
    --card-bg: rgba(30, 41, 59, 0.5);
    --text-main: #f1f5f9;
    --text-dim: #94a3b8;
    --glass-border: rgba(255, 255, 255, 0.1);
    --glass-blur: blur(12px);

    background-color: var(--bg-dark);
    color: var(--text-main);
    min-height: 100vh;
    display: flex;
    font-family: 'Outfit', sans-serif;
    position: relative;
    overflow-x: hidden;
  }

  /* Ambient Background Shadows */
  .ambient-light {
    position: fixed;
    width: 600px;
    height: 600px;
    border-radius: 50%;
    filter: blur(120px);
    z-index: 0;
    opacity: 0.15;
    pointer-events: none;
  }
  .light-1 { top: -100px; left: -100px; background: var(--primary); }
  .light-2 { bottom: -100px; right: -100px; background: var(--secondary); }

  aside {
    width: 280px;
    background: var(--sidebar-bg);
    backdrop-filter: var(--glass-blur);
    border-right: 1px solid var(--glass-border);
    display: flex;
    flex-direction: column;
    padding: 2rem 1.75rem;
    height: 100vh;
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .user-profile {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 3rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid var(--glass-border);
  }

  .avatar {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 1.1rem;
    color: white;
  }

  .user-info h3 { font-size: 1rem; margin: 0; font-weight: 700; color: white; }
  .user-info p { font-size: 0.75rem; color: var(--text-dim); margin: 0; margin-top: 2px; }

  nav { flex: 1; }
  nav ul { list-style: none; padding: 0; margin: 0; }
  nav li { margin-bottom: 0.75rem; }

  .nav-link {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.85rem 1.25rem;
    border-radius: 14px;
    text-decoration: none;
    color: var(--text-dim);
    transition: background 0.2s, color 0.2s;
    font-weight: 600;
    font-size: 0.9rem;
    background: transparent;
    border: 1px solid transparent;
    cursor: pointer;
    text-align: left;
  }

  .nav-link.active {
    background: rgba(99, 102, 241, 0.12);
    color: white;
    border: 1px solid rgba(129, 140, 248, 0.3);
  }

  .nav-link:hover:not(.active) {
    background: rgba(255, 255, 255, 0.04);
    color: white;
  }

  .logout-btn {
    margin-top: auto;
    color: #f87171;
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.85rem 1.25rem;
    text-decoration: none;
    font-weight: 700;
    font-size: 0.9rem;
    border-radius: 14px;
    transition: background 0.2s;
    background: transparent;
    border: 1px solid transparent;
    cursor: pointer;
    width: 100%;
  }
  .logout-btn:hover { background: rgba(239, 68, 68, 0.1); }

  main {
    flex: 1;
    padding: 3.5rem;
    z-index: 10;
    position: relative;
  }

  header {
    margin-bottom: 4rem;
  }

  .header-title h1 {
    font-size: 2.8rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    margin-bottom: 0.5rem;
    color: white;
  }
  .header-title p { color: var(--text-dim); font-size: 1.15rem; font-weight: 500; }

  .content-view {
    max-width: 1300px;
    margin: 0 auto;
  }

  /* Custom scrollbar for better look */
  main::-webkit-scrollbar {
    width: 6px;
  }
  main::-webkit-scrollbar-track {
    background: transparent;
  }
  main::-webkit-scrollbar-thumb {
    background: rgba(99, 102, 241, 0.1);
    border-radius: 10px;
  }
  main::-webkit-scrollbar-thumb:hover {
    background: rgba(99, 102, 241, 0.2);
  }
</style>
