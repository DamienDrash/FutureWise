<script>
  const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:8000";
  let health = "...";
  let tenants = [];

  let dateFrom = "2025-08-01";
  let dateTo = "2025-08-10";
  let selectedTenant = "alpha";
  let summary = null;
  let events = [];
  let selectedEventErrors = [];

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

  async function loadEvents() {
    try {
      const url = new URL(`${apiBase}/imports/events`);
      url.searchParams.set("tenant_id", selectedTenant);
      url.searchParams.set("limit", "10");
      const res = await fetch(url.toString());
      const json = await res.json();
      events = json.items || [];
    } catch (e) {
      events = [];
    }
  }

  async function loadEventErrors(event_id) {
    selectedEventErrors = [];
    try {
      const res = await fetch(`${apiBase}/imports/events/${event_id}/errors`);
      const json = await res.json();
      selectedEventErrors = json.items || [];
    } catch (e) {
      selectedEventErrors = [];
    }
  }

  loadHealth();
  loadTenants();
  loadEvents();
</script>

<main class="p-6 min-h-screen bg-base-200">
  <div class="max-w-4xl mx-auto space-y-6">
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
          <select bind:value={selectedTenant} class="select select-bordered w-full max-w-xs" on:change={() => { loadSummary(); loadEvents(); }}>
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

    <div class="card bg-base-100 shadow">
      <div class="card-body space-y-2">
        <h2 class="card-title">Letzte Importe</h2>
        {#if events.length === 0}
          <p class="text-sm opacity-70">Keine Events.</p>
        {:else}
          <table class="table">
            <thead>
              <tr><th>ID</th><th>Source</th><th>Filename</th><th>Inserted</th><th>Errors</th><th>Status</th><th>Aktion</th></tr>
            </thead>
            <tbody>
              {#each events as e}
                <tr>
                  <td>{e.event_id}</td>
                  <td>{e.source}</td>
                  <td>{e.filename || '-'}</td>
                  <td>{e.inserted_count}</td>
                  <td>{e.error_count}</td>
                  <td>
                    <div class="badge" class:badge-success={e.status==='success'} class:badge-warning={e.status==='partial'} class:badge-error={e.status==='failed'}>
                      {e.status}
                    </div>
                  </td>
                  <td>
                    {#if e.error_count > 0}
                      <button class="btn btn-xs" on:click={() => loadEventErrors(e.event_id)}>Fehler</button>
                    {:else}
                      <span class="opacity-50">-</span>
                    {/if}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
          {#if selectedEventErrors.length > 0}
            <div class="mt-2">
              <h3 class="font-semibold">Fehlerdetails</h3>
              <ul class="menu bg-base-100">
                {#each selectedEventErrors as er}
                  <li><span>Row {er.row_index}: {er.error}</span></li>
                {/each}
              </ul>
            </div>
          {/if}
        {/else}
      </div>
    </div>
  </div>
</main>

<style>
</style>
