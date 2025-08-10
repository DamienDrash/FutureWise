<script lang="ts">
  import { DEMO_USERS, ROLE_DESCRIPTIONS } from "$lib/demo-users";
  import RoleBadge from "$lib/components/RoleBadge.svelte";
  import type { UserRole } from "$lib/types";
  import { roleLabels } from "$lib/types";

  let email = "";
  let password = "";
  let tenant_id: string | null = null;
  let msg = "";
  let showDemoUsers = false;

  const API = import.meta.env.VITE_API_BASE || "http://localhost:8000";

  async function submit() {
    msg = "";
    const fd = new FormData();
    fd.append("email", email);
    fd.append("password", password);
    if (tenant_id) fd.append("tenant_id", tenant_id);
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

  function loginAsDemo(demoUser: any) {
    email = demoUser.email;
    password = demoUser.password;
    tenant_id = demoUser.tenant_id;
    submit();
  }

  function labelFor(role: string): string {
    // Avoid TS assertions in markup; map safely at runtime
    return (roleLabels as Record<string, string>)[role] ?? role;
  }
</script>

<div class="max-w-4xl mx-auto p-6">
  <div class="grid gap-8 lg:grid-cols-2">
    <!-- Login Form -->
    <div class="bg-card border border-border rounded-lg p-6">
      <h1 class="text-2xl font-bold text-card-foreground mb-6">Login</h1>

      <div class="space-y-4">
        <div>
          <label
            for="email"
            class="block text-sm font-medium text-card-foreground mb-2"
          >
            E-Mail
          </label>
          <input
            id="email"
            class="w-full px-3 py-2 bg-background border border-input rounded-md text-foreground
                   focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="user@example.com"
            bind:value={email}
          />
        </div>

        <div>
          <label
            for="password"
            class="block text-sm font-medium text-card-foreground mb-2"
          >
            Passwort
          </label>
          <input
            id="password"
            class="w-full px-3 py-2 bg-background border border-input rounded-md text-foreground
                   focus:outline-none focus:ring-2 focus:ring-ring"
            type="password"
            placeholder="••••••••"
            bind:value={password}
          />
        </div>

        <!-- Optional Tenant Felder entfernen: Tenant wird vom Server anhand der Zuordnung gewählt -->

        <button
          class="w-full px-4 py-2 bg-primary text-primary-foreground rounded-md font-medium
                 hover:bg-primary/90
                 transition-colors"
          on:click={submit}
        >
          Login
        </button>

        {#if msg}
          <div
            class="p-3 bg-destructive/10 border border-destructive/20 rounded-md"
          >
            <p class="text-destructive text-sm">{msg}</p>
          </div>
        {/if}
      </div>
    </div>

    <!-- Demo Users -->
    <div class="bg-card border border-border rounded-lg p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold text-card-foreground">Demo Logins</h2>
        <button
          class="text-sm text-primary hover:text-primary/80 font-medium"
          on:click={() => (showDemoUsers = !showDemoUsers)}
        >
          {showDemoUsers ? "Ausblenden" : "Anzeigen"}
        </button>
      </div>

      {#if showDemoUsers}
        <div class="space-y-3">
          <p class="text-sm text-muted-foreground mb-4">
            Klicken Sie auf einen Demo-User um sich direkt einzuloggen:
          </p>

          {#each Object.values(DEMO_USERS) as demoUser}
            <button
              class="w-full text-left p-3 rounded-lg border border-border
                     hover:bg-muted/50
                     transition-colors"
              on:click={() => loginAsDemo(demoUser)}
            >
              <div class="flex items-center justify-between mb-2">
                <span class="font-medium text-card-foreground"
                  >{demoUser.display_name}</span
                >
                <RoleBadge role={demoUser.role} />
              </div>
              <div class="text-xs text-muted-foreground">
                <div>{demoUser.email}</div>
                <div>
                  Tenant: {demoUser.tenant_id} • Passwort: {demoUser.password}
                </div>
              </div>
              <div class="text-xs text-muted-foreground mt-2">{labelFor(demoUser.role)}</div>
            </button>
          {/each}
        </div>
      {:else}
        <p class="text-sm text-muted-foreground">
          Für Demo-Zwecke stehen verschiedene Benutzerrollen zur Verfügung. Alle
          Demo-Accounts verwenden das Passwort "secret".
        </p>
      {/if}
    </div>
  </div>
</div>
