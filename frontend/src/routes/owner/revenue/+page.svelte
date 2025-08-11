<script lang="ts">
    import { onMount } from "svelte";
    import { authStore } from "$lib/stores/auth";
    import RoleGuard from "$lib/components/RoleGuard.svelte";
    import type { User } from "$lib/types";

    const API = import.meta.env.VITE_API_BASE || "http://localhost:8000";

    let revenueMetrics: any = null;
    let saasMetrics: any = null;
    let loading = true;
    let error = "";

    $: user = $authStore?.user as User | null;

    onMount(async () => {
        await loadRevenueData();
    });

    async function loadRevenueData() {
        loading = true;
        error = "";

        try {
            const [revenueRes, saasRes] = await Promise.all([
                fetch(`${API}/owner/revenue`, { credentials: "include" }),
                fetch(`${API}/owner/saas-metrics`, { credentials: "include" }),
            ]);

            if (revenueRes.ok) {
                revenueMetrics = await revenueRes.json();
            }
            if (saasRes.ok) {
                saasMetrics = await saasRes.json();
            }
        } catch (err) {
            error = "Failed to load revenue data: " + err;
            console.error("Revenue error:", err);
        } finally {
            loading = false;
        }
    }

    function formatCurrency(cents: number): string {
        return `€${(cents / 100).toLocaleString("de-DE", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        })}`;
    }

    function formatPercentage(value: number): string {
        return `${value.toFixed(1)}%`;
    }

    function getPlanColor(planName: string): string {
        switch (planName?.toLowerCase()) {
            case "starter":
                return "text-green-600";
            case "professional":
                return "text-blue-600";
            case "enterprise":
                return "text-purple-600";
            default:
                return "text-gray-600";
        }
    }
</script>

<RoleGuard minRole="owner">
    <div class="space-y-6">
        <!-- Header -->
        <div class="border-b border-border pb-6">
            <h1 class="text-3xl font-bold text-foreground">
                Revenue Analytics
            </h1>
            <p class="text-muted-foreground mt-2">
                Detaillierte Umsatzanalyse, Forecasting und Financial KPIs
            </p>
        </div>

        {#if loading}
            <div class="flex items-center justify-center h-64">
                <div class="text-muted-foreground">
                    Lade Revenue Analytics...
                </div>
            </div>
        {:else if error}
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <h3 class="text-red-800 font-medium">Fehler beim Laden</h3>
                <p class="text-red-600 text-sm mt-1">{error}</p>
            </div>
        {:else}
            <!-- Revenue KPIs -->
            {#if saasMetrics?.current_metrics}
                <div
                    class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
                >
                    <div class="bg-card border border-border rounded-lg p-6">
                        <div class="flex items-center justify-between">
                            <div>
                                <p
                                    class="text-sm font-medium text-muted-foreground"
                                >
                                    Monthly Recurring Revenue
                                </p>
                                <p class="text-2xl font-bold text-foreground">
                                    {formatCurrency(
                                        saasMetrics.current_metrics.mrr_cents,
                                    )}
                                </p>
                            </div>
                            <div
                                class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center"
                            >
                                <svg
                                    class="w-4 h-4 text-green-600"
                                    fill="currentColor"
                                    viewBox="0 0 20 20"
                                >
                                    <path
                                        d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"
                                    />
                                </svg>
                            </div>
                        </div>
                    </div>

                    <div class="bg-card border border-border rounded-lg p-6">
                        <div class="flex items-center justify-between">
                            <div>
                                <p
                                    class="text-sm font-medium text-muted-foreground"
                                >
                                    Annual Recurring Revenue
                                </p>
                                <p class="text-2xl font-bold text-foreground">
                                    {formatCurrency(
                                        saasMetrics.current_metrics.arr_cents,
                                    )}
                                </p>
                            </div>
                            <div
                                class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center"
                            >
                                <svg
                                    class="w-4 h-4 text-blue-600"
                                    fill="currentColor"
                                    viewBox="0 0 20 20"
                                >
                                    <path
                                        d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z"
                                    />
                                </svg>
                            </div>
                        </div>
                    </div>

                    <div class="bg-card border border-border rounded-lg p-6">
                        <div class="flex items-center justify-between">
                            <div>
                                <p
                                    class="text-sm font-medium text-muted-foreground"
                                >
                                    Monthly Revenue
                                </p>
                                <p class="text-2xl font-bold text-foreground">
                                    {formatCurrency(
                                        saasMetrics.current_metrics
                                            .monthly_revenue,
                                    )}
                                </p>
                            </div>
                            <div
                                class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center"
                            >
                                <svg
                                    class="w-4 h-4 text-purple-600"
                                    fill="currentColor"
                                    viewBox="0 0 20 20"
                                >
                                    <path
                                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                                    />
                                </svg>
                            </div>
                        </div>
                    </div>

                    <div class="bg-card border border-border rounded-lg p-6">
                        <div class="flex items-center justify-between">
                            <div>
                                <p
                                    class="text-sm font-medium text-muted-foreground"
                                >
                                    Pending Invoices
                                </p>
                                <p class="text-2xl font-bold text-foreground">
                                    {saasMetrics.current_metrics
                                        .pending_invoices}
                                </p>
                            </div>
                            <div
                                class="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center"
                            >
                                <svg
                                    class="w-4 h-4 text-orange-600"
                                    fill="currentColor"
                                    viewBox="0 0 20 20"
                                >
                                    <path
                                        fill-rule="evenodd"
                                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                                        clip-rule="evenodd"
                                    />
                                </svg>
                            </div>
                        </div>
                    </div>
                </div>
            {/if}

            <!-- Revenue by Plan -->
            {#if revenueMetrics?.revenue_by_plan}
                <div class="bg-card border border-border rounded-lg p-6">
                    <h3 class="text-lg font-semibold text-foreground mb-6">
                        Revenue by Plan (Letzte 6 Monate)
                    </h3>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {#each revenueMetrics.revenue_by_plan as plan}
                            <div class="border border-border rounded-lg p-4">
                                <div
                                    class="flex items-center justify-between mb-3"
                                >
                                    <h4
                                        class="font-medium text-foreground {getPlanColor(
                                            plan.plan_name,
                                        )}"
                                    >
                                        {plan.plan_name}
                                    </h4>
                                    <span class="text-sm text-muted-foreground">
                                        {plan.tenant_count} Tenants
                                    </span>
                                </div>
                                <div class="space-y-2">
                                    <div>
                                        <div
                                            class="text-2xl font-bold text-foreground"
                                        >
                                            {formatCurrency(plan.total_revenue)}
                                        </div>
                                        <div
                                            class="text-sm text-muted-foreground"
                                        >
                                            Total Revenue
                                        </div>
                                    </div>
                                    <div>
                                        <div
                                            class="text-lg font-semibold text-foreground"
                                        >
                                            {formatCurrency(
                                                plan.avg_invoice_amount,
                                            )}
                                        </div>
                                        <div
                                            class="text-sm text-muted-foreground"
                                        >
                                            Avg. Invoice
                                        </div>
                                    </div>
                                </div>
                            </div>
                        {/each}
                    </div>
                </div>
            {/if}

            <!-- Monthly Revenue Trend -->
            {#if revenueMetrics?.monthly_trend}
                <div class="bg-card border border-border rounded-lg p-6">
                    <h3 class="text-lg font-semibold text-foreground mb-6">
                        Monthly Revenue Trend
                    </h3>
                    <div class="overflow-x-auto">
                        <table class="w-full border-collapse">
                            <thead>
                                <tr class="border-b border-border">
                                    <th
                                        class="text-left py-3 px-4 font-medium text-foreground"
                                        >Monat</th
                                    >
                                    <th
                                        class="text-left py-3 px-4 font-medium text-foreground"
                                        >Paid Revenue</th
                                    >
                                    <th
                                        class="text-left py-3 px-4 font-medium text-foreground"
                                        >Pending Revenue</th
                                    >
                                    <th
                                        class="text-left py-3 px-4 font-medium text-foreground"
                                        >Paying Tenants</th
                                    >
                                    <th
                                        class="text-left py-3 px-4 font-medium text-foreground"
                                        >ARPU</th
                                    >
                                </tr>
                            </thead>
                            <tbody>
                                {#each revenueMetrics.monthly_trend as month}
                                    <tr
                                        class="border-b border-border hover:bg-muted/50"
                                    >
                                        <td
                                            class="py-3 px-4 font-medium text-foreground"
                                        >
                                            {month.month}
                                        </td>
                                        <td class="py-3 px-4 text-foreground">
                                            {formatCurrency(month.paid_revenue)}
                                        </td>
                                        <td class="py-3 px-4 text-foreground">
                                            {formatCurrency(
                                                month.pending_revenue,
                                            )}
                                        </td>
                                        <td class="py-3 px-4 text-foreground">
                                            {month.paying_tenants}
                                        </td>
                                        <td class="py-3 px-4 text-foreground">
                                            {month.paying_tenants > 0
                                                ? formatCurrency(
                                                      Math.round(
                                                          month.paid_revenue /
                                                              month.paying_tenants,
                                                      ),
                                                  )
                                                : "-"}
                                        </td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                </div>
            {/if}

            <!-- Plan Performance Insights -->
            {#if saasMetrics?.plan_distribution}
                <div class="bg-card border border-border rounded-lg p-6">
                    <h3 class="text-lg font-semibold text-foreground mb-6">
                        Plan Performance & Insights
                    </h3>

                    <!-- Total MRR Breakdown -->
                    <div class="mb-8">
                        <h4 class="font-medium text-foreground mb-4">
                            MRR Distribution
                        </h4>
                        <div class="space-y-3">
                            {#each saasMetrics.plan_distribution as plan}
                                {@const percentage =
                                    saasMetrics.current_metrics.mrr_cents > 0
                                        ? (plan.total_mrr_cents /
                                              saasMetrics.current_metrics
                                                  .mrr_cents) *
                                          100
                                        : 0}
                                <div class="flex items-center justify-between">
                                    <div class="flex items-center gap-3">
                                        <div
                                            class="w-4 h-4 rounded {plan.plan_name ===
                                            'Enterprise'
                                                ? 'bg-purple-500'
                                                : plan.plan_name ===
                                                    'Professional'
                                                  ? 'bg-blue-500'
                                                  : 'bg-green-500'}"
                                        ></div>
                                        <span
                                            class="font-medium text-foreground"
                                            >{plan.plan_name}</span
                                        >
                                    </div>
                                    <div class="text-right">
                                        <div
                                            class="font-medium text-foreground"
                                        >
                                            {formatCurrency(
                                                plan.total_mrr_cents,
                                            )}
                                        </div>
                                        <div
                                            class="text-sm text-muted-foreground"
                                        >
                                            {formatPercentage(percentage)}
                                        </div>
                                    </div>
                                </div>
                                <div
                                    class="w-full bg-gray-200 rounded-full h-2"
                                >
                                    <div
                                        class="h-2 rounded-full {plan.plan_name ===
                                        'Enterprise'
                                            ? 'bg-purple-500'
                                            : plan.plan_name === 'Professional'
                                              ? 'bg-blue-500'
                                              : 'bg-green-500'}"
                                        style="width: {percentage}%"
                                    ></div>
                                </div>
                            {/each}
                        </div>
                    </div>

                    <!-- Key Metrics -->
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div
                            class="text-center p-4 border border-border rounded-lg"
                        >
                            <div class="text-2xl font-bold text-foreground">
                                {formatCurrency(
                                    saasMetrics.current_metrics.mrr_cents /
                                        saasMetrics.current_metrics
                                            .active_tenants,
                                )}
                            </div>
                            <div class="text-sm text-muted-foreground">
                                Average Revenue per Tenant
                            </div>
                        </div>

                        <div
                            class="text-center p-4 border border-border rounded-lg"
                        >
                            <div class="text-2xl font-bold text-foreground">
                                {formatPercentage(
                                    (saasMetrics.current_metrics
                                        .active_tenants /
                                        saasMetrics.current_metrics
                                            .total_tenants) *
                                        100,
                                )}
                            </div>
                            <div class="text-sm text-muted-foreground">
                                Active Tenant Rate
                            </div>
                        </div>

                        <div
                            class="text-center p-4 border border-border rounded-lg"
                        >
                            <div class="text-2xl font-bold text-foreground">
                                {Math.round(
                                    saasMetrics.current_metrics.arr_cents /
                                        12 /
                                        100,
                                ).toLocaleString()}
                            </div>
                            <div class="text-sm text-muted-foreground">
                                Monthly Target (ARR/12)
                            </div>
                        </div>
                    </div>
                </div>
            {/if}
        {/if}
    </div>
</RoleGuard>
