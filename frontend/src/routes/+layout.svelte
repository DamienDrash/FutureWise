<script lang="ts">
  import { onMount } from 'svelte';
  import '../app.css';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import Header from '$lib/components/Header.svelte';
  
  export let data;
  
  let token = '';
  let tenantId = '';
  let sidebarOpen = false;
  
  const API = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
  
  onMount(() => {
    token = localStorage.getItem('fw_token') || '';
    tenantId = localStorage.getItem('fw_tenant') || '';
  });
  
  async function logout() {
    await fetch(`${API}/auth/logout`, {
      method: 'POST',
      credentials: 'include',
    });
    localStorage.removeItem('fw_token');
    localStorage.removeItem('fw_tenant');
    location.href = '/';
  }

  function toggleSidebar() {
    sidebarOpen = !sidebarOpen;
  }
</script>

<div class="bg-background text-foreground min-h-screen flex">
  <!-- Sidebar for desktop -->
  <div class="hidden lg:flex lg:flex-shrink-0">
    <Sidebar user={data?.user} />
  </div>

  <!-- Mobile sidebar overlay -->
  {#if sidebarOpen}
    <div class="lg:hidden fixed inset-0 z-50 flex">
      <!-- Overlay -->
      <div 
        class="fixed inset-0 bg-background/80 backdrop-blur-sm" 
        on:click={toggleSidebar}
        on:keydown={(e) => e.key === 'Escape' && toggleSidebar()}
        role="button"
        tabindex="0"
        aria-label="Close sidebar">
      </div>
      <!-- Sidebar -->
      <div class="relative flex flex-col w-80 bg-sidebar">
        <Sidebar user={data?.user} />
      </div>
    </div>
  {/if}

  <!-- Main content area -->
  <div class="flex-1 flex flex-col overflow-hidden">
    <Header 
      user={data?.user} 
      onLogout={logout}
      onToggleSidebar={toggleSidebar} />
    
    <!-- Page content -->
    <main class="flex-1 overflow-y-auto bg-background">
      <div class="p-4 lg:p-6">
        <slot />
      </div>
    </main>
  </div>
</div>
