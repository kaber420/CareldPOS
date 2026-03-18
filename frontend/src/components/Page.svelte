<script>
  import { navigate } from 'svelte-routing';
  import { user, clearAuth, notify, notifications, removeNotification } from '../stores/auth';
  import Layout from './Layout.svelte';

  export let title = '';

  let sidebarOpen = true;

  function handleLogout() {
    clearAuth();
    notify('Sesión cerrada correctamente', 'info');
    navigate('/login');
  }

  function toggleSidebar() {
    sidebarOpen = !sidebarOpen;
  }
</script>

<Layout
  {sidebarOpen}
  {user}
  {notifications}
  on:toggleSidebar={toggleSidebar}
  on:logout={handleLogout}
  on:removeNotification={removeNotification}
>
  <slot />
</Layout>
