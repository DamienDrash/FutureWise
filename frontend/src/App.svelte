<script>
  const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:8000";
  let health = "...";
  let tenants = [];

  let dateFrom = "2025-08-01";
  let dateTo = "2025-08-10";
  let selectedTenant = "alpha";
  let summary = null;

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
      if (tenants.length > 0 && !selectedTenant) {
        selectedTenant = tenants[0].tenant_id;
      }
    } catch (e) {
      tenants = [];
    }
  }

  async function loadSummary() {
    try {
      const url = new URL(`${apiBase}/imports/summary`);
      url.searchParams.set("tenant_id", selectedTenant);
      url.searchParams.set("date_from", dateFrom);
      url.searchParams.set("date_to", dateTo);
      const res = await fetch(url.toString());
      summary = await res.json();
    } catch (e) {
      summary = { error: true };
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
      <div class="card-body space-y-4">
        <h2 class="card-title">Tenants</h2>
        {#if tenants.length === 0}
          <p class="text-sm opacity-70">Keine Tenants gefunden.</p>
        {:else}
          <select bind:value={selectedTenant} class="select select-bordered w-full max-w-xs">
            {#each tenants as t}
              <option value={t.tenant_id}>{t.name} ({t.tenant_id})</option>
            {/each}
          </select>
        {/if}
      </div>
    </div>

    <div class="card bg-base-100 shadow">
      <div class="card-body space-y-4">
        <h2 class="card-title">Import Zusammenfassung</h2>
        <div class="flex gap-2 items-end">
          <div>
            <label class="label"><span class="label-text">Von</span></label>
            <input type="date" bind:value={dateFrom} class="input input-bordered" />
          </div>
          <div>
            <label class="label"><span class="label-text">Bis</span></label>
            <input type="date" bind:value={dateTo} class="input input-bordered" />
          </div>
          <button class="btn btn-primary" on:click={loadSummary}>Laden</button>
        </div>
        {#if summary}
          {#if summary.error}
            <div class="alert alert-error">Fehler beim Laden.</div>
          {:else}
            <div class="stats shadow">
              <div class="stat">
                <div class="stat-title">Tage</div>
                <div class="stat-value">{summary.summary?.num_days ?? 0}</div>
              </div>
              <div class="stat">
                <div class="stat-title">Sessions</div>
                <div class="stat-value">{summary.summary?.sessions_sum ?? 0}</div>
              </div>
              <div class="stat">
                <div class="stat-title">Orders</div>
                <div class="stat-value">{summary.summary?.orders_sum ?? 0}</div>
              </div>
              <div class="stat">
                <div class="stat-title">Revenue Gross (cents)</div>
                <div class="stat-value">{summary.summary?.revenue_gross_sum ?? 0}</div>
              </div>
              <div class="stat">
                <div class="stat-title">Revenue Net (cents)</div>
                <div class="stat-value">{summary.summary?.revenue_net_sum ?? 0}</div>
              </div>
            </div>
          {/if}
        {/if}
      </div>
    </div>
  </div>
</main>

<style>
</style>
