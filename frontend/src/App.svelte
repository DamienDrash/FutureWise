<script>
  const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:8000";
  let health = "...";
  let tenants = [];

  async function loadHealth() {
    try {
      const res = await fetch(`${apiBase}/health/ready`);
      const json = await res.json();
      health = json.status;
    } catch (e) {
      health = "error";
    }
  }

  async function loadTenants() {
    try {
      const res = await fetch(`${apiBase}/tenants`);
      const json = await res.json();
      tenants = json.items || [];
    } catch (e) {
      tenants = [];
    }
  }

  loadHealth();
  loadTenants();
</script>

<main class="p-6 min-h-screen bg-base-200">
  <div class="max-w-3xl mx-auto space-y-6">
    <h1 class="text-2xl font-bold">FutureWise</h1>

    <div class="card bg-base-100 shadow">
      <div class="card-body">
        <h2 class="card-title">System Health</h2>
        <div class="badge" class:badge-success={health === 'ok'} class:badge-error={health !== 'ok'}>
          {health}
        </div>
      </div>
    </div>

    <div class="card bg-base-100 shadow">
      <div class="card-body">
        <h2 class="card-title">Tenants</h2>
        {#if tenants.length === 0}
          <p class="text-sm opacity-70">Keine Tenants gefunden.</p>
        {:else}
          <ul class="menu bg-base-100 w-full">
            {#each tenants as t}
              <li><span>{t.name} <small class="opacity-60">({t.tenant_id})</small></span></li>
            {/each}
          </ul>
        {/if}
      </div>
    </div>
  </div>
</main>

<style>
</style>
