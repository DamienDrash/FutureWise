<script lang="ts">
    import { onMount } from "svelte";
    import { authStore } from "../stores/auth";

    const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

    let chartData: any[] = [];
    let isLoading = true;
    let chartType = "revenue";

    async function loadChartData() {
        isLoading = true;
        try {
            // Use fixed date range that matches our seeded data (July 12 - August 10, 2025)
            const dateFrom = "2025-07-12";
            const dateTo = "2025-08-10";

            // Check if user is system-level (owner/system_manager) or tenant-specific
            const user = $authStore.user;
            let apiUrl;

            if (
                user &&
                (user.role === "owner" || user.role === "system_manager")
            ) {
                // For system users, show example data from alpha tenant (TODO: aggregate later)
                apiUrl = `${API_BASE}/imports/daily?tenant_id=alpha&date_from=${dateFrom}&date_to=${dateTo}`;
            } else {
                // For tenant users, use their specific tenant or fallback to alpha
                const tenantId =
                    user?.tenant_id ||
                    localStorage.getItem("fw_tenant") ||
                    "alpha";
                apiUrl = `${API_BASE}/imports/daily?tenant_id=${tenantId}&date_from=${dateFrom}&date_to=${dateTo}`;
            }

            const res = await fetch(apiUrl, { credentials: "include" });

            if (res.ok) {
                const data = await res.json();
                chartData = (data.items || []).slice(-14); // Last 14 days
            }
        } catch (error) {
            console.error("Failed to load chart data:", error);
            chartData = [];
        } finally {
            isLoading = false;
        }
    }

    onMount(() => {
        loadChartData();
    });

    function formatDate(dateStr: string) {
        return new Date(dateStr).toLocaleDateString("de-DE", {
            month: "short",
            day: "numeric",
        });
    }

    function getMaxValue() {
        if (chartData.length === 0) return 100;

        let values = [];
        switch (chartType) {
            case "revenue":
                values = chartData.map(
                    (d) => (d.revenue_cents_gross || 0) / 100,
                );
                break;
            case "orders":
                values = chartData.map((d) => d.orders || 0);
                break;
            case "sessions":
                values = chartData.map((d) => d.sessions || 0);
                break;
        }

        const max = Math.max(...values);
        return max > 0 ? max * 1.1 : 100;
    }

    function getValue(item: any) {
        switch (chartType) {
            case "revenue":
                return (item.revenue_cents_gross || 0) / 100;
            case "orders":
                return item.orders || 0;
            case "sessions":
                return item.sessions || 0;
            default:
                return 0;
        }
    }

    function formatValue(value: number) {
        switch (chartType) {
            case "revenue":
                return (
                    "€" +
                    value.toLocaleString("de-DE", {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                    })
                );
            case "orders":
                return value.toLocaleString() + " Bestellungen";
            case "sessions":
                return value.toLocaleString() + " Sessions";
            default:
                return value.toLocaleString();
        }
    }

    function getColorClass(type: string) {
        switch (type) {
            case "revenue":
                return "bg-green-500 hover:bg-green-600";
            case "orders":
                return "bg-blue-500 hover:bg-blue-600";
            case "sessions":
                return "bg-purple-500 hover:bg-purple-600";
            default:
                return "bg-primary hover:bg-primary/80";
        }
    }

    function getShortValue(value: number) {
        switch (chartType) {
            case "revenue":
                if (value >= 1000) {
                    return `€${Math.round(value / 1000)}k`;
                }
                return `€${Math.round(value)}`;
            case "orders":
                return Math.round(value).toString();
            case "sessions":
                return Math.round(value).toString();
            default:
                return Math.round(value).toString();
        }
    }

    function getTotalFormatted() {
        let total = 0;
        switch (chartType) {
            case "revenue":
                total = chartData.reduce(
                    (sum, item) => sum + (item.revenue_cents_gross || 0) / 100,
                    0,
                );
                return (
                    "€" +
                    total.toLocaleString("de-DE", {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                    })
                );
            case "orders":
                total = chartData.reduce(
                    (sum, item) => sum + (item.orders || 0),
                    0,
                );
                return total.toLocaleString() + " Bestellungen";
            case "sessions":
                total = chartData.reduce(
                    (sum, item) => sum + (item.sessions || 0),
                    0,
                );
                return total.toLocaleString() + " Sessions";
            default:
                return "0";
        }
    }

    $: maxValue = getMaxValue();

    // Debug: Log when chartType changes
    $: console.log(
        "Chart type changed to:",
        chartType,
        "Max value:",
        maxValue,
        "Data length:",
        chartData.length,
    );
</script>

<div class="bg-card border border-border rounded-lg p-6 shadow-sm">
    <div class="flex items-center justify-between mb-6">
        <h3 class="text-lg font-semibold text-card-foreground">
            Analytics Overview
        </h3>
        <div class="flex space-x-2">
            <button
                class="px-3 py-1.5 text-sm font-medium rounded-md transition-colors {chartType ===
                'revenue'
                    ? 'bg-green-500 text-white'
                    : 'bg-muted text-muted-foreground hover:bg-muted/80'}"
                on:click={() => {
                    console.log("Revenue button clicked");
                    chartType = "revenue";
                }}
            >
                Umsatz
            </button>
            <button
                class="px-3 py-1.5 text-sm font-medium rounded-md transition-colors {chartType ===
                'orders'
                    ? 'bg-blue-500 text-white'
                    : 'bg-muted text-muted-foreground hover:bg-muted/80'}"
                on:click={() => {
                    console.log("Orders button clicked");
                    chartType = "orders";
                }}
            >
                Bestellungen
            </button>
            <button
                class="px-3 py-1.5 text-sm font-medium rounded-md transition-colors {chartType ===
                'sessions'
                    ? 'bg-purple-500 text-white'
                    : 'bg-muted text-muted-foreground hover:bg-muted/80'}"
                on:click={() => {
                    console.log("Sessions button clicked");
                    chartType = "sessions";
                }}
            >
                Sessions
            </button>
        </div>
    </div>

    {#if isLoading}
        <div class="flex justify-center items-center h-64">
            <div class="text-muted-foreground">Loading chart...</div>
        </div>
    {:else if chartData.length === 0}
        <div class="flex justify-center items-center h-64">
            <div class="text-muted-foreground">No data available</div>
        </div>
    {:else}
        <!-- Chart Container -->
        <div class="h-64 relative">
            <div class="flex items-end justify-between h-full space-x-1">
                {#each chartData as item, index (item.date + chartType)}
                    {@const value = getValue(item)}
                    {@const currentMaxValue = getMaxValue()}
                    {@const height = Math.max(
                        (value / currentMaxValue) * 100,
                        2,
                    )}
                    {@const colorClass = getColorClass(chartType)}

                    <div
                        class="flex-1 flex flex-col items-center group relative h-full justify-end"
                    >
                        <!-- Bar -->
                        <div
                            class="w-full {colorClass} rounded-t-sm transition-all duration-200 hover:opacity-80 relative"
                            style="height: {height}%;"
                        >
                            <!-- Debug Value on Bar -->
                            <div
                                class="absolute inset-0 flex items-center justify-center text-xs text-white font-bold opacity-70"
                            >
                                {getShortValue(value)}
                            </div>

                            <!-- Tooltip -->
                            <div
                                class="absolute -top-10 left-1/2 transform -translate-x-1/2 bg-popover border border-border rounded px-2 py-1 text-xs text-popover-foreground opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 whitespace-nowrap shadow-md"
                            >
                                {formatDate(item.date)}: {formatValue(value)} (Height:
                                {Math.round(height)}%)
                            </div>
                        </div>

                        <!-- Date Label -->
                        <div
                            class="text-xs text-muted-foreground mt-2 text-center"
                        >
                            {formatDate(item.date)}
                        </div>
                    </div>
                {/each}
            </div>
        </div>

        <!-- Chart Legend -->
        <div
            class="flex justify-between items-center mt-4 pt-4 border-t border-border"
        >
            <div class="text-sm text-muted-foreground">Last 14 days</div>
            <div class="text-sm text-muted-foreground">
                Total: {getTotalFormatted()}
            </div>
        </div>
    {/if}
</div>
