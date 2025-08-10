<script lang="ts">
    import { onMount } from "svelte";
    import type { Scenario } from "$lib/types";
    import RoleGuard from "$lib/components/RoleGuard.svelte";
    import { authStore, isSystemManager } from "$lib/stores/auth";

    const API = import.meta.env.VITE_API_BASE || "http://localhost:8000";

    let tenantId =
        typeof localStorage !== "undefined"
            ? localStorage.getItem("fw_tenant") || "alpha"
            : "alpha";
    let availableTenants: any[] = [];
    let showTenantSelector = false;
    let scenarios: Scenario[] = [];
    let simMsg = "";
    let isLoading = false;
    let showCreateModal = false;
    let newScenarioName = "";
    let newScenarioKind = "forecast";

    // Set default dates
    let dateFrom = new Date(Date.now() - 7 * 24 * 3600 * 1000)
        .toISOString()
        .slice(0, 10);
    let dateTo = new Date().toISOString().slice(0, 10);

    async function loadTenants() {
        try {
            const res = await fetch(`${API}/tenants`, {
                credentials: "include",
            });
            const data = await res.json();
            availableTenants = data.items || [];
        } catch (error) {
            console.error("Failed to load tenants:", error);
        }
    }

    async function loadScenarios() {
        isLoading = true;
        try {
            const url = new URL(`${API}/scenarios`);
            url.searchParams.set("tenant_id", tenantId);
            const res = await fetch(url, { credentials: "include" });
            const j = await res.json();
            scenarios = j.items || [];
        } catch (error) {
            console.error("Failed to load scenarios:", error);
            simMsg = "Fehler beim Laden der Szenarien";
        } finally {
            isLoading = false;
        }
    }

    async function changeTenant(newTenantId: string) {
        tenantId = newTenantId;
        if (typeof localStorage !== "undefined") {
            localStorage.setItem("fw_tenant", tenantId);
        }
        await loadScenarios();
    }

    async function simulateExisting(sid: string) {
        simMsg = "";
        isLoading = true;
        try {
            const fd = new FormData();
            fd.append("tenant_id", tenantId);
            fd.append("scenario_id", String(sid));
            fd.append("date_from", dateFrom);
            fd.append("date_to", dateTo);

            const res = await fetch(`${API}/scenarios/simulate`, {
                method: "POST",
                body: fd,
                credentials: "include",
            });
            const t = await res.text();
            simMsg = `${res.status === 200 ? "Erfolgreich" : "Fehler"}: ${t}`;
        } catch (error) {
            simMsg = "Fehler bei der Simulation";
        } finally {
            isLoading = false;
        }
    }

    async function createScenario() {
        if (!newScenarioName.trim()) return;

        isLoading = true;
        try {
            const fd = new FormData();
            fd.append("tenant_id", tenantId);
            fd.append("name", newScenarioName.trim());
            fd.append("kind", newScenarioKind);

            const res = await fetch(`${API}/scenarios`, {
                method: "POST",
                body: fd,
                credentials: "include",
            });

            if (res.ok) {
                showCreateModal = false;
                newScenarioName = "";
                await loadScenarios();
                simMsg = "Szenario erfolgreich erstellt";
            } else {
                simMsg = "Fehler beim Erstellen des Szenarios";
            }
        } catch (error) {
            simMsg = "Fehler beim Erstellen des Szenarios";
        } finally {
            isLoading = false;
        }
    }

    onMount(async () => {
        // Check if user is system manager and load tenants
        if ($authStore.user && isSystemManager($authStore.user.role)) {
            showTenantSelector = true;
            await loadTenants();
        }
        await loadScenarios();
    });
</script>

<RoleGuard requiredRole="tenant_user">
    <div class="space-y-6">
        <!-- Header -->
        <div
            class="flex flex-col gap-4
             sm:flex-row sm:items-center sm:justify-between"
        >
            <div>
                <h1 class="text-2xl font-bold text-foreground">
                    Szenario-Management
                </h1>
                <p class="text-muted-foreground">
                    Erstelle und simuliere ML-basierte E-Commerce Szenarien
                </p>

                <!-- Tenant Selector for System Managers -->
                {#if showTenantSelector}
                    <div class="flex items-center space-x-4 mt-4">
                        <label
                            for="tenant-select"
                            class="text-sm font-medium text-foreground"
                        >
                            Tenant:
                        </label>
                        <select
                            id="tenant-select"
                            bind:value={tenantId}
                            on:change={(e) => changeTenant(e.target.value)}
                            class="px-3 py-2 border border-border rounded-md bg-background text-foreground"
                        >
                            {#each availableTenants as tenant}
                                <option value={tenant.tenant_id}
                                    >{tenant.name}</option
                                >
                            {/each}
                        </select>
                    </div>
                {/if}
            </div>
            <button
                class="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium
             hover:bg-primary/90
             transition-colors"
                on:click={() => (showCreateModal = true)}
            >
                Neues Szenario
            </button>
        </div>

        <!-- Date Range Selection -->
        <div class="bg-card border border-border rounded-lg p-6">
            <h3 class="text-lg font-semibold text-card-foreground mb-4">
                Simulationszeitraum
            </h3>
            <div
                class="grid gap-4
               sm:grid-cols-2
               lg:grid-cols-4"
            >
                <div>
                    <label
                        for="date-from"
                        class="block text-sm font-medium text-card-foreground mb-2"
                    >
                        Von
                    </label>
                    <input
                        id="date-from"
                        class="w-full px-3 py-2 bg-background border border-input rounded-md text-foreground
                 focus:outline-none focus:ring-2 focus:ring-ring"
                        type="date"
                        bind:value={dateFrom}
                    />
                </div>
                <div>
                    <label
                        for="date-to"
                        class="block text-sm font-medium text-card-foreground mb-2"
                    >
                        Bis
                    </label>
                    <input
                        id="date-to"
                        class="w-full px-3 py-2 bg-background border border-input rounded-md text-foreground
                 focus:outline-none focus:ring-2 focus:ring-ring"
                        type="date"
                        bind:value={dateTo}
                    />
                </div>
            </div>
        </div>

        <!-- Scenarios List -->
        <div class="bg-card border border-border rounded-lg p-6">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-card-foreground">
                    Verfügbare Szenarien
                </h3>
                {#if isLoading}
                    <div class="text-sm text-muted-foreground">Lädt...</div>
                {/if}
            </div>

            {#if scenarios.length === 0 && !isLoading}
                <div class="text-center py-8">
                    <div
                        class="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4"
                    >
                        <svg
                            class="w-8 h-8 text-muted-foreground"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                            ></path>
                        </svg>
                    </div>
                    <h3 class="text-lg font-medium text-card-foreground mb-2">
                        Keine Szenarien vorhanden
                    </h3>
                    <p class="text-muted-foreground mb-4">
                        Erstelle dein erstes Szenario um zu beginnen
                    </p>
                    <button
                        class="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium
                 hover:bg-primary/90
                 transition-colors"
                        on:click={() => (showCreateModal = true)}
                    >
                        Erstes Szenario erstellen
                    </button>
                </div>
            {:else}
                <div class="grid gap-4">
                    {#each scenarios as scenario}
                        <div
                            class="border border-border rounded-lg p-4
                     hover:bg-muted/50
                     transition-colors"
                        >
                            <div class="flex items-center justify-between">
                                <div class="flex-1">
                                    <h4
                                        class="font-semibold text-card-foreground"
                                    >
                                        {scenario.name}
                                    </h4>
                                    <div
                                        class="flex items-center gap-4 mt-1 text-sm text-muted-foreground"
                                    >
                                        <span>ID: #{scenario.scenario_id}</span>
                                        <span
                                            class="px-2 py-1 bg-secondary text-secondary-foreground rounded text-xs"
                                        >
                                            {scenario.kind}
                                        </span>
                                    </div>
                                </div>
                                <button
                                    class="px-4 py-2 bg-primary text-primary-foreground rounded-md font-medium
                       hover:bg-primary/90
                       disabled:opacity-50 disabled:cursor-not-allowed
                       transition-colors"
                                    disabled={isLoading}
                                    on:click={() =>
                                        simulateExisting(scenario.scenario_id)}
                                >
                                    {isLoading ? "Simuliert..." : "Simulieren"}
                                </button>
                            </div>
                        </div>
                    {/each}
                </div>
            {/if}

            <!-- Simulation Message -->
            {#if simMsg}
                <div class="mt-4 p-4 bg-muted border border-border rounded-lg">
                    <p class="text-sm text-card-foreground">{simMsg}</p>
                </div>
            {/if}
        </div>
    </div>

    <!-- Create Scenario Modal -->
    {#if showCreateModal}
        <div
            class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm"
        >
            <div
                class="bg-card border border-border rounded-lg shadow-lg max-w-md w-full p-6"
            >
                <h3 class="text-lg font-semibold text-card-foreground mb-4">
                    Neues Szenario erstellen
                </h3>
                <div class="space-y-4">
                    <div>
                        <label
                            for="scenario-name"
                            class="block text-sm font-medium text-card-foreground mb-2"
                        >
                            Szenario-Name
                        </label>
                        <input
                            id="scenario-name"
                            class="w-full px-3 py-2 bg-background border border-input rounded-md text-foreground
                   focus:outline-none focus:ring-2 focus:ring-ring"
                            type="text"
                            placeholder="z.B. Q4 2024 Wachstumsprognose"
                            bind:value={newScenarioName}
                        />
                    </div>
                    <div>
                        <label
                            for="scenario-kind"
                            class="block text-sm font-medium text-card-foreground mb-2"
                        >
                            Szenario-Typ
                        </label>
                        <select
                            id="scenario-kind"
                            class="w-full px-3 py-2 bg-background border border-input rounded-md text-foreground
                   focus:outline-none focus:ring-2 focus:ring-ring"
                            bind:value={newScenarioKind}
                        >
                            <option value="forecast">Prognose</option>
                            <option value="what-if">What-If Analyse</option>
                            <option value="optimization">Optimierung</option>
                        </select>
                    </div>
                </div>
                <div class="flex gap-3 mt-6">
                    <button
                        class="flex-1 px-4 py-2 bg-background border border-border text-foreground rounded-md
                 hover:bg-muted
                 transition-colors"
                        on:click={() => (showCreateModal = false)}
                    >
                        Abbrechen
                    </button>
                    <button
                        class="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-md
                 hover:bg-primary/90
                 disabled:opacity-50 disabled:cursor-not-allowed
                 transition-colors"
                        disabled={!newScenarioName.trim() || isLoading}
                        on:click={createScenario}
                    >
                        {isLoading ? "Erstellt..." : "Erstellen"}
                    </button>
                </div>
            </div>
        </div>
    {/if}
</RoleGuard>
