<script>
  import { onMount } from 'svelte'
  const API = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
  let token = ''
  let tenant = ''
  let roleInfo = null
  let msg = ''

  let inviteEmail = ''
  let inviteRole = 'viewer'

  let currency = 'EUR'
  let tax = 0.19
  let channel = 'general'

  onMount(async () => {
    token = localStorage.getItem('fw_token') || ''
    tenant = localStorage.getItem('fw_tenant') || ''
    if (!token) { msg = 'Bitte einloggen.'; return }
    await loadSettings()
  })

  async function loadSettings() {
    const res = await fetch(`${API}/tenants/${tenant}/settings`)
    const j = await res.json()
    currency = j.default_currency
    tax = j.default_tax_rate
    channel = j.default_channel
  }

  async function saveSettings() {
    const params = new URLSearchParams({ default_currency: currency, default_tax_rate: String(tax), default_channel: channel })
    const res = await fetch(`${API}/tenants/${tenant}/settings?${params.toString()}`, { method: 'PUT', headers: { Authorization: `Bearer ${token}` }})
    msg = res.ok ? 'Gespeichert' : 'Fehler'
  }

  async function sendInvite() {
    const fd = new FormData()
    fd.append('email', inviteEmail)
    fd.append('role', inviteRole)
    const res = await fetch(`${API}/tenants/${tenant}/invite`, { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: fd })
    const j = await res.json()
    msg = res.ok ? `Invite Token: ${j.invite_token}` : (j.detail || 'Fehler')
  }
</script>

<section class="p-8 space-y-6">
  <h1 class="text-2xl font-bold">Management</h1>
  {#if !token}
    <div class="alert alert-warning">Bitte einloggen.</div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="card bg-base-100 shadow">
        <div class="card-body space-y-3">
          <h2 class="card-title">Tenant Settings</h2>
          <input class="input input-bordered" placeholder="Currency" bind:value={currency} />
          <input class="input input-bordered" type="number" step="0.01" placeholder="Tax Rate" bind:value={tax} />
          <input class="input input-bordered" placeholder="Default Channel" bind:value={channel} />
          <button class="btn btn-primary" on:click={saveSettings}>Speichern</button>
        </div>
      </div>
      <div class="card bg-base-100 shadow">
        <div class="card-body space-y-3">
          <h2 class="card-title">Benutzer einladen</h2>
          <input class="input input-bordered" placeholder="E‑Mail" bind:value={inviteEmail} />
          <select class="select select-bordered" bind:value={inviteRole}>
            <option value="viewer">Viewer</option>
            <option value="analyst">Analyst</option>
            <option value="manager">Manager</option>
          </select>
          <button class="btn" on:click={sendInvite}>Einladung senden</button>
        </div>
      </div>
    </div>
    {#if msg}<div class="alert mt-3">{msg}</div>{/if}
  {/if}
</section>
