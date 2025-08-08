<script>
  import { onMount } from 'svelte'
  export let data
  let token = ''
  let tenantId = ''
  const API = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
  onMount(() => {
    token = localStorage.getItem('fw_token') || ''
    tenantId = localStorage.getItem('fw_tenant') || ''
  })
  async function logout() {
    await fetch(`${API}/auth/logout`, { method: 'POST', credentials: 'include' })
    localStorage.removeItem('fw_token')
    localStorage.removeItem('fw_tenant')
    location.href = '/'
  }
</script>

<div class="drawer lg:drawer-open">
  <input id="drawer" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content">
    <div class="navbar bg-base-100 border-b border-base-200">
      <div class="flex-none lg:hidden">
        <label for="drawer" class="btn btn-ghost btn-square">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-6 h-6 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
        </label>
      </div>
      <div class="flex-1 px-2"><a href="/">FutureWise</a></div>
      <div class="flex-none">
        {#if token}
          <button class="btn btn-ghost" on:click={logout}>Logout</button>
        {:else}
          <a class="btn btn-ghost" href="/login">Login</a>
          <a class="btn btn-primary" href="/register">Register</a>
        {/if}
      </div>
    </div>
    <slot />
  </div>
  <div class="drawer-side">
    <label for="drawer" class="drawer-overlay"></label>
    <aside class="menu p-4 w-80 bg-base-200">
      <p class="menu-title">Navigation</p>
      <ul>
        <li><a href="/">Dashboard</a></li>
        <li><a href="/imports">Imports</a></li>
        <li><a href="/scenarios">Szenarien</a></li>
        <li><a href="/management">Management</a></li>
        <li><a href="/pricing">Pricing</a></li>
      </ul>
    </aside>
  </div>
</div>
