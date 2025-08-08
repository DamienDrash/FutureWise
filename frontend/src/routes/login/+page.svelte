<script>
  let email = "";
  let password = "";
  let tenant_id = "alpha";
  let msg = "";
  const API = import.meta.env.VITE_API_BASE || "http://localhost:8000";

  async function submit() {
    msg = "";
    const fd = new FormData();
    fd.append("email", email);
    fd.append("password", password);
    fd.append("tenant_id", tenant_id);
    const res = await fetch(`${API}/auth/login`, {
      method: "POST",
      body: fd,
      credentials: "include",
    });
    const t = await res.json();
    if (res.ok) {
      localStorage.setItem("fw_tenant", tenant_id);
      location.href = "/";
    } else {
      msg = t.detail || "Login fehlgeschlagen";
    }
  }
</script>

<section class="p-10 max-w-md space-y-4">
  <h1 class="text-2xl font-bold">Login</h1>
  <input
    class="input input-bordered w-full"
    placeholder="E‑Mail"
    bind:value={email}
  />
  <input
    class="input input-bordered w-full"
    type="password"
    placeholder="Passwort"
    bind:value={password}
  />
  <input
    class="input input-bordered w-full"
    placeholder="Tenant ID"
    bind:value={tenant_id}
  />
  <button class="btn btn-primary w-full" on:click={submit}>Login</button>
  {#if msg}<div class="alert alert-error mt-2">{msg}</div>{/if}
</section>
