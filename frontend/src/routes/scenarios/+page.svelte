<script>
  import { onMount } from 'svelte'
  const API = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
  let tenantId = typeof localStorage !== 'undefined' ? (localStorage.getItem('fw_tenant') || 'alpha') : 'alpha'
  let scenarios = []
  let simMsg = ''
  let dateFrom = new Date(Date.now() - 7*24*3600*1000).toISOString().slice(0,10)
  let dateTo = new Date().toISOString().slice(0,10)

  async function loadScenarios() {
    const url = new URL(`${API}/scenarios`)
    url.searchParams.set('tenant_id', tenantId)
    const res = await fetch(url, { credentials: 'include' })
    const j = await res.json()
    scenarios = j.items || []
  }

  async function simulateExisting(sid) {
    simMsg = ''
    const fd = new FormData()
    fd.append('tenant_id', tenantId)
    fd.append('scenario_id', String(sid))
    fd.append('date_from', dateFrom)
    fd.append('date_to', dateTo)
    const res = await fetch(`${API}/scenarios/simulate`, { method: 'POST', body: fd, credentials: 'include' })
    const t = await res.text()
    simMsg = `${res.status} ${t}`
  }

  onMount(loadScenarios)
</script>

<section class="p-6 space-y-6">
  <h1 class="text-2xl font-bold">Szenarien</h1>

  <div class="card bg-base-100 shadow">
    <div class="card-body flex gap-4 items-end">
      <div>
        <label class="label"><span class="label-text">Von</span></label>
        <input class="input input-bordered" type="date" bind:value={dateFrom} />
      </div>
      <div>
        <label class="label"><span class="label-text">Bis</span></label>
        <input class="input input-bordered" type="date" bind:value={dateTo} />
      </div>
    </div>
  </div>

  <div class="card bg-base-100 shadow">
    <div class="card-body">
      <h2 class="card-title">Bestehende Szenarien</h2>
      <ul class="space-y-2">
        {#each scenarios as s}
          <li class="flex items-center justify-between border-b pb-2">
            <div>
              <div class="font-semibold">{s.name}</div>
              <div class="opacity-70 text-sm">#{s.scenario_id} · {s.kind}</div>
            </div>
            <button class="btn btn-sm" on:click={() => simulateExisting(s.scenario_id)}>Simulieren</button>
          </li>
        {/each}
      </ul>
      {#if simMsg}
        <div class="alert alert-info mt-3">{simMsg}</div>
      {/if}
    </div>
  </div>
</section>


