<script>
  let token = ''
  if (typeof localStorage !== 'undefined') {
    token = localStorage.getItem('fw_token') || ''
  }
</script>

{#if !token}
<section class="p-10 space-y-6">
  <h1 class="text-3xl font-bold">FutureWise – E‑Commerce Scenario Management</h1>
  <p class="opacity-80 max-w-3xl">Importiere historische KPIs, simuliere ML‑basierte Szenarien und treffe bessere Entscheidungen. Multi‑Tenant, RBAC‑ready, API‑first.</p>
  <div class="flex gap-3">
    <a class="btn btn-primary" href="/register">Kostenlos starten</a>
    <a class="btn" href="/pricing">Pricing ansehen</a>
  </div>
</section>
{:else}
<section class="p-6">
  <h2 class="text-xl font-semibold">Willkommen zurück</h2>
  <p class="opacity-70">Wähle links eine Sektion aus (Imports, Szenarien, Management).</p>
</section>
{/if}
