<script>
  let email = ''
  let password = ''
  let display_name = ''
  let tenant_id = 'alpha'
  let role = 'manager'
  let msg = ''
  const API = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

  async function submit() {
    msg = ''
    const fd = new FormData()
    fd.append('email', email)
    fd.append('password', password)
    fd.append('display_name', display_name)
    fd.append('tenant_id', tenant_id)
    fd.append('role', role)
    const res = await fetch(`${API}/auth/register`, { method: 'POST', body: fd })
    const t = await res.json()
    if (res.ok) {
      location.href = '/login'
    } else {
      msg = t.detail || 'Registrierung fehlgeschlagen'
    }
  }
</script>

<section class="p-10 max-w-md space-y-4">
  <h1 class="text-2xl font-bold">Registrieren</h1>
  <input class="input input-bordered w-full" placeholder="E‑Mail" bind:value={email} />
  <input class="input input-bordered w-full" type="password" placeholder="Passwort" bind:value={password} />
  <input class="input input-bordered w-full" placeholder="Name" bind:value={display_name} />
  <input class="input input-bordered w-full" placeholder="Tenant ID" bind:value={tenant_id} />
  <select class="select select-bordered w-full" bind:value={role}>
    <option value="viewer">Viewer</option>
    <option value="analyst">Analyst</option>
    <option value="manager">Manager</option>
  </select>
  <button class="btn btn-primary w-full" on:click={submit}>Registrieren</button>
  {#if msg}<div class="alert alert-error mt-2">{msg}</div>{/if}
</section>
