<script lang="ts">
    import RoleGuard from "$lib/components/RoleGuard.svelte";
    import RoleBadge from "$lib/components/RoleBadge.svelte";
    import { onMount } from "svelte";

    export let data;

    let systemStats = {
        totalUsers: 0,
        totalTenants: 0,
        systemRevenue: 0,
        activeScenarios: 0,
    };

    let recentSystemActivity: any[] = [];
    let loading = true;
    let error = "";

    const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

    onMount(async () => {
        try {
            // Load real system stats from backend
            const statsRes = await fetch(`${API_BASE}/system/stats`, {
                credentials: "include",
            });

            if (statsRes.ok) {
                const stats = await statsRes.json();
                systemStats = {
                    totalUsers: stats.total_users || 0,
                    totalTenants: stats.total_tenants || 0,
                    systemRevenue: stats.system_revenue || 0,
                    activeScenarios: stats.active_scenarios || 0,
                };
            }

            // Load recent audit events as system activity
            const auditRes = await fetch(`${API_BASE}/owner/audit-log?limit=5`, {
                credentials: "include",
            });

            if (auditRes.ok) {
                const auditData = await auditRes.json();
                recentSystemActivity = (auditData.audit_entries || []).map((entry: any) => ({
                    type: entry.action_type.toLowerCase(),
                    message: `${entry.action_type} ${entry.entity_type} (ID: ${entry.entity_id})`,
                    timestamp: new Date(entry.created_at).toLocaleString("de-DE"),
                    user: entry.user_email || "System",
                }));
            }
        } catch (err) {
            console.error("Failed to load system data:", err);
            error = "Fehler beim Laden der Systemdaten";
        } finally {
            loading = false;
        }
    });
</script>

<RoleGuard
    requiredRole="system_manager"
    fallback="Zugriff verweigert: System Manager Berechtigung erforderlich"
>
    <div class="space-y-6">
        <!-- Header -->
        <div
            class="flex flex-col gap-4
               sm:flex-row sm:items-center sm:justify-between"
        >
            <div>
                <h1 class="text-2xl font-bold text-foreground">
                    System Management
                </h1>
                <p class="text-muted-foreground">
                    Übersicht und Verwaltung des gesamten FutureWise Systems
                </p>
            </div>
            <RoleBadge role={data?.user?.role || "viewer"} />
        </div>

        <!-- System Statistics -->
        <div
            class="grid gap-6
               sm:grid-cols-2
               lg:grid-cols-4"
        >
            <div class="bg-card border border-border rounded-lg p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-muted-foreground text-sm font-medium">
                            Gesamt Tenants
                        </p>
                        <p class="text-2xl font-bold text-card-foreground mt-2">
                            {systemStats.totalTenants}
                        </p>
                    </div>
                    <div
                        class="w-12 h-12 bg-chart-1/10 rounded-lg flex items-center justify-center"
                    >
                        <svg
                            class="w-6 h-6 text-chart-1"
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
                </div>
            </div>

            <div class="bg-card border border-border rounded-lg p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-muted-foreground text-sm font-medium">
                            Gesamt Benutzer
                        </p>
                        <p class="text-2xl font-bold text-card-foreground mt-2">
                            {systemStats.totalUsers}
                        </p>
                    </div>
                    <div
                        class="w-12 h-12 bg-chart-2/10 rounded-lg flex items-center justify-center"
                    >
                        <svg
                            class="w-6 h-6 text-chart-2"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
                            ></path>
                        </svg>
                    </div>
                </div>
            </div>

            <div class="bg-card border border-border rounded-lg p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-muted-foreground text-sm font-medium">
                            System Umsatz
                        </p>
                        <p class="text-2xl font-bold text-card-foreground mt-2">
                            €{(systemStats.systemRevenue / 1000).toFixed(1)}k
                        </p>
                    </div>
                    <div
                        class="w-12 h-12 bg-chart-3/10 rounded-lg flex items-center justify-center"
                    >
                        <svg
                            class="w-6 h-6 text-chart-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"
                            ></path>
                        </svg>
                    </div>
                </div>
            </div>

            <div class="bg-card border border-border rounded-lg p-6">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-muted-foreground text-sm font-medium">
                            Aktive Szenarien
                        </p>
                        <p class="text-2xl font-bold text-card-foreground mt-2">
                            {systemStats.activeScenarios}
                        </p>
                    </div>
                    <div
                        class="w-12 h-12 bg-chart-4/10 rounded-lg flex items-center justify-center"
                    >
                        <svg
                            class="w-6 h-6 text-chart-4"
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
                </div>
            </div>
        </div>

        <!-- Quick Actions Grid -->
        <div
            class="grid gap-6
               lg:grid-cols-2"
        >
            <!-- System Actions -->
            <div class="bg-card border border-border rounded-lg p-6">
                <h3 class="text-lg font-semibold text-card-foreground mb-4">
                    System Aktionen
                </h3>
                <div class="grid gap-3">
                    <a
                        href="/tenants"
                        class="flex items-center p-3 rounded-lg border border-border hover:bg-muted/50 transition-colors"
                    >
                        <div
                            class="w-10 h-10 bg-chart-1/10 rounded-lg flex items-center justify-center mr-3"
                        >
                            <svg
                                class="w-5 h-5 text-chart-1"
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
                        <div>
                            <p class="text-sm font-medium text-card-foreground">
                                Alle Tenants verwalten
                            </p>
                            <p class="text-xs text-muted-foreground">
                                Tenants erstellen, bearbeiten und löschen
                            </p>
                        </div>
                    </a>

                    <button
                        class="flex items-center p-3 rounded-lg border border-border hover:bg-muted/50 transition-colors"
                    >
                        <div
                            class="w-10 h-10 bg-chart-2/10 rounded-lg flex items-center justify-center mr-3"
                        >
                            <svg
                                class="w-5 h-5 text-chart-2"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                                ></path>
                            </svg>
                        </div>
                        <div>
                            <p class="text-sm font-medium text-card-foreground">
                                System Health Check
                            </p>
                            <p class="text-xs text-muted-foreground">
                                Überprüfung aller System-Komponenten
                            </p>
                        </div>
                    </button>

                    <button
                        class="flex items-center p-3 rounded-lg border border-border hover:bg-muted/50 transition-colors"
                    >
                        <div
                            class="w-10 h-10 bg-chart-3/10 rounded-lg flex items-center justify-center mr-3"
                        >
                            <svg
                                class="w-5 h-5 text-chart-3"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                                ></path>
                            </svg>
                        </div>
                        <div>
                            <p class="text-sm font-medium text-card-foreground">
                                System Reports
                            </p>
                            <p class="text-xs text-muted-foreground">
                                Umfassende System-Berichte generieren
                            </p>
                        </div>
                    </button>
                </div>
            </div>

            <!-- Recent Activity -->
            <div class="bg-card border border-border rounded-lg p-6">
                <h3 class="text-lg font-semibold text-card-foreground mb-4">
                    Letzte System-Aktivitäten
                </h3>
                <div class="space-y-4">
                    {#each recentSystemActivity as activity}
                        <div class="flex items-start space-x-3">
                            <div
                                class="w-8 h-8 bg-muted rounded-full flex items-center justify-center"
                            >
                                {#if activity.type === "tenant_created"}
                                    <svg
                                        class="w-4 h-4 text-chart-1"
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
                                {:else if activity.type === "user_registered"}
                                    <svg
                                        class="w-4 h-4 text-chart-2"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="2"
                                            d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
                                        ></path>
                                    </svg>
                                {:else}
                                    <svg
                                        class="w-4 h-4 text-muted-foreground"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="2"
                                            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                                        ></path>
                                    </svg>
                                {/if}
                            </div>
                            <div class="flex-1 min-w-0">
                                <p
                                    class="text-sm font-medium text-card-foreground"
                                >
                                    {activity.message}
                                </p>
                                <div
                                    class="flex items-center gap-2 text-xs text-muted-foreground mt-1"
                                >
                                    <span>{activity.timestamp}</span>
                                    {#if activity.user}
                                        <span>• {activity.user}</span>
                                    {/if}
                                    {#if activity.tenant}
                                        <span>• Tenant: {activity.tenant}</span>
                                    {/if}
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>
        </div>
    </div>
</RoleGuard>
