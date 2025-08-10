<script lang="ts">
    import RoleGuard from "$lib/components/RoleGuard.svelte";
    import RoleBadge from "$lib/components/RoleBadge.svelte";
    import { onMount } from "svelte";
    import type { Tenant, TenantStatus } from "$lib/types";
    import { tenantStatusColors } from "$lib/types";

    export const data = undefined;

    let tenants: Tenant[] = [];
    let showCreateModal = false;
    let newTenantName = "";
    let isLoading = false;

    const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

    async function loadTenants() {
        isLoading = true;
        try {
            const res = await fetch(`${API_BASE}/tenants`, {
                credentials: "include",
            });
            const data = await res.json();
            tenants = data.items || [];
        } catch (error) {
            console.error("Failed to load tenants:", error);
        } finally {
            isLoading = false;
        }
    }

    onMount(() => {
        loadTenants();
    });

    async function createTenant() {
        if (!newTenantName.trim()) return;

        isLoading = true;
        try {
            const fd = new FormData();
            fd.append("name", newTenantName.trim());

            const res = await fetch(`${API_BASE}/tenants/create`, {
                method: "POST",
                body: fd,
                credentials: "include",
            });

            if (res.ok) {
                showCreateModal = false;
                newTenantName = "";
                await loadTenants(); // Reload from database
            } else {
                console.error("Failed to create tenant");
            }
        } catch (error) {
            console.error("Error creating tenant:", error);
        } finally {
            isLoading = false;
        }
    }

    function getStatusBadge(status: TenantStatus) {
        return tenantStatusColors[status] || tenantStatusColors.trial;
    }
</script>

<RoleGuard
    requiredRole="owner"
    fallback="Zugriff verweigert: Owner Berechtigung erforderlich"
>
    <div class="space-y-6">
        <!-- Header -->
        <div
            class="flex flex-col gap-4
               sm:flex-row sm:items-center sm:justify-between"
        >
            <div>
                <h1 class="text-2xl font-bold text-foreground">
                    Tenant Management
                </h1>
                <p class="text-muted-foreground">
                    Übersicht und Verwaltung aller Tenants im System
                </p>
            </div>
            <button
                class="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium
               hover:bg-primary/90
               transition-colors"
                on:click={() => (showCreateModal = true)}
            >
                Neuen Tenant erstellen
            </button>
        </div>

        <!-- Tenants Grid -->
        <div class="grid gap-6">
            {#each tenants as tenant}
                <div
                    class="bg-card border border-border rounded-lg p-6
                   hover:shadow-md
                   transition-shadow"
                >
                    <div class="flex items-center justify-between mb-4">
                        <div>
                            <h3
                                class="text-lg font-semibold text-card-foreground"
                            >
                                {tenant.name}
                            </h3>
                            <div class="flex items-center gap-2 mt-1">
                                <span class="text-sm text-muted-foreground"
                                    >ID: {tenant.tenant_id}</span
                                >
                                <span
                                    class="px-2 py-1 rounded-full text-xs font-medium {getStatusBadge(
                                        tenant.status,
                                    )}"
                                >
                                    {tenant.status}
                                </span>
                            </div>
                        </div>
                        <div class="flex gap-2">
                            <button
                                class="px-3 py-1 text-sm bg-muted text-muted-foreground rounded hover:bg-muted/80"
                            >
                                Bearbeiten
                            </button>
                            <button
                                class="px-3 py-1 text-sm bg-primary text-primary-foreground rounded hover:bg-primary/90"
                            >
                                Details
                            </button>
                        </div>
                    </div>

                    <!-- Tenant Stats -->
                    <div class="grid grid-cols-4 gap-4">
                        <div class="text-center">
                            <div
                                class="text-2xl font-bold text-card-foreground"
                            >
                                {tenant.users}
                            </div>
                            <div class="text-xs text-muted-foreground">
                                Benutzer
                            </div>
                        </div>
                        <div class="text-center">
                            <div
                                class="text-2xl font-bold text-card-foreground"
                            >
                                {tenant.scenarios}
                            </div>
                            <div class="text-xs text-muted-foreground">
                                Szenarien
                            </div>
                        </div>
                        <div class="text-center">
                            <div
                                class="text-2xl font-bold text-card-foreground"
                            >
                                €{(tenant.revenue / 100).toFixed(0)}
                            </div>
                            <div class="text-xs text-muted-foreground">
                                Umsatz
                            </div>
                        </div>
                        <div class="text-center">
                            <div
                                class="text-sm font-medium text-card-foreground"
                            >
                                {tenant.created_at}
                            </div>
                            <div class="text-xs text-muted-foreground">
                                Erstellt
                            </div>
                        </div>
                    </div>
                </div>
            {/each}
        </div>

        {#if tenants.length === 0}
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
                            d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                        ></path>
                    </svg>
                </div>
                <h3 class="text-lg font-medium text-card-foreground mb-2">
                    Keine Tenants vorhanden
                </h3>
                <p class="text-muted-foreground mb-4">
                    Erstellen Sie den ersten Tenant um zu beginnen
                </p>
            </div>
        {/if}
    </div>

    <!-- Create Tenant Modal -->
    {#if showCreateModal}
        <div
            class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm"
        >
            <div
                class="bg-card border border-border rounded-lg shadow-lg max-w-md w-full p-6"
            >
                <h3 class="text-lg font-semibold text-card-foreground mb-4">
                    Neuen Tenant erstellen
                </h3>
                <div class="space-y-4">
                    <div>
                        <label
                            for="tenant-name"
                            class="block text-sm font-medium text-card-foreground mb-2"
                        >
                            Tenant Name
                        </label>
                        <input
                            id="tenant-name"
                            class="w-full px-3 py-2 bg-background border border-input rounded-md text-foreground
                     focus:outline-none focus:ring-2 focus:ring-ring"
                            type="text"
                            placeholder="z.B. Acme Corporation"
                            bind:value={newTenantName}
                        />
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
                        disabled={!newTenantName.trim() || isLoading}
                        on:click={createTenant}
                    >
                        {isLoading ? "Erstellt..." : "Erstellen"}
                    </button>
                </div>
            </div>
        </div>
    {/if}
</RoleGuard>
