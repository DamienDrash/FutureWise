<script>
  import { onMount } from 'svelte'
  const API = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
  let tokenParam = ''
  let user_id = ''
  let msg = ''

  onMount(() => {
    const u = new URL(location.href)
    tokenParam = u.searchParams.get('token') || ''
  })

  async function accept() {
    msg = ''
    const fd = new FormData()
    fd.append('token', tokenParam)
    fd.append('user_id', user_id)
    const res = await fetch(`${API}/tenants/invite/accept`, { method: 'POST', body: fd })
    const j = await res.json()
    msg = res.ok ? 'Einladung akzeptiert' : (j.detail || 'Fehler')
  }
</script>

<section class="p-10 max-w-md space-y-4">
  <h1 class="text-2xl font-bold">Einladung annehmen</h1>
  <input class="input input-bordered w-full" placeholder="Invite Token" bind:value={tokenParam} />
  <input class="input input-bordered w-full" placeholder="User ID" bind:value={user_id} />
  <button class="btn btn-primary w-full" on:click={accept}>Annehmen</button>
  {#if msg}<div class="alert mt-2">{msg}</div>{/if}
</section>
