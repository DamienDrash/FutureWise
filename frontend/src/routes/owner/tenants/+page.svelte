<script lang="ts">
    import { onMount } from "svelte";
    import { authStore } from "$lib/stores/auth";
    import RoleGuard from "$lib/components/RoleGuard.svelte";
    import type { User } from "$lib/types";

    const API = import.meta.env.VITE_API_BASE || "http://localhost:8000";

    let tenants: any[] = [];
    let loading = true;
    let error = "";

    // New tenant form
    let showCreateTenant = false;
    let newTenant = {
        tenant_id: "",
        name: "",
        plan_id: "starter",
    };

    $: user = $authStore?.user as User | null;

    onMount(async () => {
        await loadTenants();
    });

    async function loadTenants() {
        loading = true;
        error = "";

        try {
            const res = await fetch(`${API}/owner/tenants`, {
                credentials: "include",
            });

            if (res.ok) {
                const data = await res.json();
                tenants = data.tenants;
            } else {
                error = "Failed to load tenants";
            }
        } catch (err) {
            error = "Failed to load tenants: " + err;
            console.error("Tenants error:", err);
        } finally {
            loading = false;
        }
    }

    async function createTenant() {
        if (!newTenant.tenant_id || !newTenant.name) {
            alert("Bitte alle Felder ausfüllen");
            return;
        }

        try {
            const res = await fetch(`${API}/owner/tenants`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify(newTenant),
            });

            if (res.ok) {
                newTenant = { tenant_id: "", name: "", plan_id: "starter" };
                showCreateTenant = false;
                await loadTenants();
            } else {
                const errorData = await res.json();
                alert("Fehler: " + errorData.detail);
            }
        } catch (err) {
            alert("Fehler beim Erstellen: " + err);
        }
    }

    async function deleteTenant(tenantId: string) {
        if (
            !confirm(
                `Tenant ${tenantId} wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.`,
            )
        ) {
            return;
        }

        try {
            const res = await fetch(`${API}/owner/tenants/${tenantId}`, {
                method: "DELETE",
                credentials: "include",
            });

            if (res.ok) {
                await loadTenants();
            } else {
                const errorData = await res.json();
                alert("Fehler beim Löschen: " + errorData.detail);
            }
        } catch (err) {
            alert("Fehler beim Löschen: " + err);
        }
    }

    function formatCurrency(cents: number): string {
        return `€${(cents / 100).toLocaleString("de-DE", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        })}`;
    }

    function formatDate(dateStr: string): string {
        return new Date(dateStr).toLocaleDateString("de-DE");
    }

    function getPlanBadgeColor(planName: string): string {
        switch (planName?.toLowerCase()) {
            case "starter":
                return "bg-green-100 text-green-800";
            case "professional":
                return "bg-blue-100 text-blue-800";
            case "enterprise":
                return "bg-purple-100 text-purple-800";
            default:
                return "bg-gray-100 text-gray-800";
        }
    }

    function getStatusBadgeColor(status: string): string {
        switch (status) {
            case "active":
                return "bg-green-100 text-green-800";
            case "pending":
                return "bg-yellow-100 text-yellow-800";
            case "cancelled":
                return "bg-red-100 text-red-800";
            default:
                return "bg-gray-100 text-gray-800";
        }
    }
</script>

<RoleGuard minRole="owner">
    <div class="space-y-6">
        <!-- Header -->
        <div class="border-b border-border pb-6">
            <h1 class="text-3xl font-bold text-foreground">
                Tenant Management
            </h1>
            <p class="text-muted-foreground mt-2">
                Verwalte alle Tenants, Subscriptions und Billing
            </p>
        </div>

        {#if loading}
            <div class="flex items-center justify-center h-64">
                <div class="text-muted-foreground">Lade Tenants...</div>
            </div>
        {:else if error}
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <h3 class="text-red-800 font-medium">Fehler beim Laden</h3>
                <p class="text-red-600 text-sm mt-1">{error}</p>
            </div>
        {:else}
            <!-- Create Tenant Button -->
            <div class="flex justify-between items-center">
                <div>
                    <h2 class="text-xl font-semibold text-foreground">
                        Alle Tenants ({tenants.length})
                    </h2>
                    <p class="text-sm text-muted-foreground">
                        Übersicht aller registrierten Tenants und deren Status
                    </p>
                </div>
                <button
                    on:click={() => (showCreateTenant = true)}
                    class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
                >
                    Neuen Tenant erstellen
                </button>
            </div>

            <!-- Create Tenant Form -->
            {#if showCreateTenant}
                <div class="bg-muted border border-border rounded-lg p-6">
                    <h3 class="font-medium text-foreground mb-4">
                        Neuer Tenant
                    </h3>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label
                                for="tenant_id"
                                class="block text-sm font-medium text-foreground mb-1"
                            >
                                Tenant ID
                            </label>
                            <input
                                id="tenant_id"
                                bind:value={newTenant.tenant_id}
                                placeholder="z.B. acme-corp"
                                class="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground"
                            />
                        </div>
                        <div>
                            <label
                                for="tenant_name"
                                class="block text-sm font-medium text-foreground mb-1"
                            >
                                Name
                            </label>
                            <input
                                id="tenant_name"
                                bind:value={newTenant.name}
                                placeholder="ACME Corporation"
                                class="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground"
                            />
                        </div>
                        <div>
                            <label
                                for="plan_id"
                                class="block text-sm font-medium text-foreground mb-1"
                            >
                                Plan
                            </label>
                            <select
                                id="plan_id"
                                bind:value={newTenant.plan_id}
                                class="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground"
                            >
                                <option value="starter"
                                    >Starter (€29/Monat)</option
                                >
                                <option value="professional"
                                    >Professional (€99/Monat)</option
                                >
                                <option value="enterprise"
                                    >Enterprise (€299/Monat)</option
                                >
                            </select>
                        </div>
                    </div>
                    <div class="flex gap-2 mt-4">
                        <button
                            on:click={createTenant}
                            class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90"
                        >
                            Erstellen
                        </button>
                        <button
                            on:click={() => (showCreateTenant = false)}
                            class="bg-secondary text-secondary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-secondary/90"
                        >
                            Abbrechen
                        </button>
                    </div>
                </div>
            {/if}

            <!-- Tenants Table -->
            <div class="bg-card border border-border rounded-lg p-6">
                <div class="overflow-x-auto">
                    <table class="w-full border-collapse">
                        <thead>
                            <tr class="border-b border-border">
                                <th
                                    class="text-left py-3 px-4 font-medium text-foreground"
                                >
                                    Tenant
                                </th>
                                <th
                                    class="text-left py-3 px-4 font-medium text-foreground"
                                >
                                    Plan
                                </th>
                                <th
                                    class="text-left py-3 px-4 font-medium text-foreground"
                                >
                                    Status
                                </th>
                                <th
                                    class="text-left py-3 px-4 font-medium text-foreground"
                                >
                                    Users
                                </th>
                                <th
                                    class="text-left py-3 px-4 font-medium text-foreground"
                                >
                                    Monthly Revenue
                                </th>
                                <th
                                    class="text-left py-3 px-4 font-medium text-foreground"
                                >
                                    Started
                                </th>
                                <th
                                    class="text-left py-3 px-4 font-medium text-foreground"
                                >
                                    Aktivität
                                </th>
                                <th
                                    class="text-left py-3 px-4 font-medium text-foreground"
                                >
                                    Aktionen
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each tenants as tenant}
                                <tr
                                    class="border-b border-border hover:bg-muted/50"
                                >
                                    <td class="py-3 px-4">
                                        <div>
                                            <div
                                                class="font-medium text-foreground"
                                            >
                                                {tenant.name}
                                            </div>
                                            <div
                                                class="text-sm text-muted-foreground"
                                            >
                                                {tenant.tenant_id}
                                            </div>
                                        </div>
                                    </td>
                                    <td class="py-3 px-4">
                                        <span
                                            class="text-sm {getPlanBadgeColor(
                                                tenant.plan_name,
                                            )} px-2 py-1 rounded"
                                        >
                                            {tenant.plan_name || "Kein Plan"}
                                        </span>
                                    </td>
                                    <td class="py-3 px-4">
                                        <span
                                            class="text-sm {getStatusBadgeColor(
                                                tenant.subscription_status,
                                            )} px-2 py-1 rounded"
                                        >
                                            {tenant.subscription_status ||
                                                "Inactive"}
                                        </span>
                                    </td>
                                    <td class="py-3 px-4 text-foreground">
                                        {tenant.user_count}
                                    </td>
                                    <td class="py-3 px-4 text-foreground">
                                        {formatCurrency(
                                            tenant.monthly_revenue || 0,
                                        )}
                                    </td>
                                    <td
                                        class="py-3 px-4 text-sm text-muted-foreground"
                                    >
                                        {tenant.subscription_started
                                            ? formatDate(
                                                  tenant.subscription_started,
                                              )
                                            : "-"}
                                    </td>
                                    <td class="py-3 px-4">
                                        <div
                                            class="text-sm text-muted-foreground"
                                        >
                                            {tenant.monthly_logins || 0} Logins<br
                                            />
                                            {tenant.monthly_imports || 0} Imports
                                        </div>
                                    </td>
                                    <td class="py-3 px-4">
                                        <div class="flex gap-2">
                                            <button
                                                class="text-blue-600 hover:text-blue-800 text-sm font-medium"
                                            >
                                                Bearbeiten
                                            </button>
                                            <button
                                                on:click={() =>
                                                    deleteTenant(
                                                        tenant.tenant_id,
                                                    )}
                                                class="text-red-600 hover:text-red-800 text-sm font-medium"
                                            >
                                                Löschen
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            </div>
        {/if}
    </div>
</RoleGuard>
