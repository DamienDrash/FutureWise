<script lang="ts">
    import { onMount } from "svelte";
    import RoleGuard from "$lib/components/RoleGuard.svelte";

    const API = import.meta.env.VITE_API_BASE || "http://localhost:8000";

    let tenantId =
        typeof localStorage !== "undefined"
            ? localStorage.getItem("fw_tenant") || "alpha"
            : "alpha";
    let dateFrom = new Date(Date.now() - 7 * 24 * 3600 * 1000)
        .toISOString()
        .slice(0, 10);
    let dateTo = new Date().toISOString().slice(0, 10);
    let summary: any = null;
    let events: any[] = [];
    let uploading = false;
    let error = "";
    let success = "";
    let isLoading = false;

    async function loadSummary() {
        isLoading = true;
        try {
            const url = new URL(`${API}/imports/summary`);
            url.searchParams.set("tenant_id", tenantId);
            url.searchParams.set("date_from", dateFrom);
            url.searchParams.set("date_to", dateTo);
            const res = await fetch(url, { credentials: "include" });
            summary = await res.json();
        } catch (e) {
            summary = { error: true };
            error = "Failed to load summary";
        } finally {
            isLoading = false;
        }
    }

    async function loadEvents() {
        try {
            const url = new URL(`${API}/imports/events`);
            url.searchParams.set("tenant_id", tenantId);
            url.searchParams.set("limit", "20");
            const res = await fetch(url, { credentials: "include" });
            const j = await res.json();
            events = j.items || [];
        } catch (e) {
            events = [];
        }
    }

    async function uploadCsv(e: Event) {
        const input = e.target as HTMLInputElement;
        const file = input.files?.[0];
        if (!file) return;

        uploading = true;
        error = "";
        success = "";

        try {
            const fd = new FormData();
            fd.append("tenant_id", tenantId);
            fd.append("file", file);

            const res = await fetch(`${API}/imports/csv`, {
                method: "POST",
                body: fd,
                credentials: "include",
            });

            if (res.ok) {
                success = `File "${file.name}" uploaded successfully`;
                await Promise.all([loadSummary(), loadEvents()]);
            } else {
                const errorData = await res.json();
                error = errorData.detail || `Upload failed: ${res.status}`;
            }
        } catch (e) {
            error = "Upload failed due to network error";
        } finally {
            uploading = false;
            input.value = "";
        }
    }

    function formatRevenue(cents: number) {
        return "€" + (cents / 100).toLocaleString();
    }

    function formatTimestamp(dateStr: string) {
        return new Date(dateStr).toLocaleString("de-DE");
    }

    function getStatusColor(status: string) {
        switch (status) {
            case "success":
                return "text-green-600 bg-green-50";
            case "error":
                return "text-red-600 bg-red-50";
            default:
                return "text-yellow-600 bg-yellow-50";
        }
    }

    onMount(async () => {
        await Promise.all([loadSummary(), loadEvents()]);
    });
</script>

<RoleGuard requiredRole="tenant_user">
    <div class="max-w-6xl mx-auto p-6">
        <div class="mb-8">
            <h1 class="text-2xl font-bold text-foreground mb-2">
                Data Import Management
            </h1>
            <p class="text-muted-foreground">
                Upload and manage your KPI data imports
            </p>
        </div>

        <!-- Messages -->
        {#if error}
            <div
                class="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 text-red-800"
            >
                {error}
            </div>
        {/if}
        {#if success}
            <div
                class="mb-6 p-4 rounded-lg bg-green-50 border border-green-200 text-green-800"
            >
                {success}
            </div>
        {/if}

        <div class="grid gap-6 lg:grid-cols-3">
            <!-- Upload Section -->
            <div class="lg:col-span-1">
                <div
                    class="bg-card border border-border rounded-lg p-6 shadow-sm"
                >
                    <h2 class="text-lg font-semibold text-foreground mb-4">
                        Upload CSV File
                    </h2>

                    <div class="space-y-4">
                        <div
                            class="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors"
                        >
                            <svg
                                class="w-12 h-12 text-muted-foreground mx-auto mb-4"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"
                                ></path>
                            </svg>

                            <input
                                type="file"
                                accept=".csv,.xlsx,.xls"
                                class="hidden"
                                id="file-upload"
                                on:change={uploadCsv}
                                disabled={uploading}
                            />

                            <label
                                for="file-upload"
                                class="cursor-pointer inline-flex items-center px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
                            >
                                {#if uploading}
                                    Uploading...
                                {:else}
                                    Choose File
                                {/if}
                            </label>

                            <p class="text-sm text-muted-foreground mt-2">
                                CSV, XLS, or XLSX files up to 10MB
                            </p>
                        </div>

                        <div class="text-sm text-muted-foreground">
                            <p class="font-medium mb-2">Required columns:</p>
                            <ul class="space-y-1 text-xs">
                                <li>• date (YYYY-MM-DD)</li>
                                <li>• sessions</li>
                                <li>• orders</li>
                                <li>• revenue_cents</li>
                                <li>• conversion_rate</li>
                                <li>• inventory_units</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Summary Section -->
            <div class="lg:col-span-2">
                <div
                    class="bg-card border border-border rounded-lg p-6 shadow-sm"
                >
                    <div class="flex items-center justify-between mb-6">
                        <h2 class="text-lg font-semibold text-foreground">
                            Data Summary
                        </h2>
                        <div class="flex items-center space-x-4">
                            <div class="flex items-center space-x-2">
                                <label
                                    for="date-from"
                                    class="text-sm font-medium text-foreground"
                                    >From:</label
                                >
                                <input
                                    id="date-from"
                                    type="date"
                                    bind:value={dateFrom}
                                    class="px-3 py-1 text-sm border border-border rounded bg-background"
                                />
                            </div>
                            <div class="flex items-center space-x-2">
                                <label
                                    for="date-to"
                                    class="text-sm font-medium text-foreground"
                                    >To:</label
                                >
                                <input
                                    id="date-to"
                                    type="date"
                                    bind:value={dateTo}
                                    class="px-3 py-1 text-sm border border-border rounded bg-background"
                                />
                            </div>
                            <button
                                class="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
                                on:click={loadSummary}
                                disabled={isLoading}
                            >
                                {isLoading ? "Loading..." : "Refresh"}
                            </button>
                        </div>
                    </div>

                    {#if summary?.error}
                        <div class="text-center py-8 text-muted-foreground">
                            Failed to load summary data
                        </div>
                    {:else if summary}
                        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                            <div class="bg-primary/5 rounded-lg p-4">
                                <div
                                    class="text-sm font-medium text-muted-foreground"
                                >
                                    Days
                                </div>
                                <div class="text-2xl font-bold text-foreground">
                                    {summary?.summary?.num_days ?? 0}
                                </div>
                            </div>
                            <div class="bg-chart-1/10 rounded-lg p-4">
                                <div
                                    class="text-sm font-medium text-muted-foreground"
                                >
                                    Sessions
                                </div>
                                <div class="text-2xl font-bold text-foreground">
                                    {(
                                        summary?.summary?.sessions_sum ?? 0
                                    ).toLocaleString()}
                                </div>
                            </div>
                            <div class="bg-chart-2/10 rounded-lg p-4">
                                <div
                                    class="text-sm font-medium text-muted-foreground"
                                >
                                    Orders
                                </div>
                                <div class="text-2xl font-bold text-foreground">
                                    {(
                                        summary?.summary?.orders_sum ?? 0
                                    ).toLocaleString()}
                                </div>
                            </div>
                            <div class="bg-chart-3/10 rounded-lg p-4">
                                <div
                                    class="text-sm font-medium text-muted-foreground"
                                >
                                    Revenue
                                </div>
                                <div class="text-2xl font-bold text-foreground">
                                    {formatRevenue(
                                        summary?.summary?.revenue_gross_sum ??
                                            0,
                                    )}
                                </div>
                            </div>
                        </div>
                    {:else}
                        <div class="text-center py-8 text-muted-foreground">
                            Loading summary...
                        </div>
                    {/if}
                </div>
            </div>
        </div>

        <!-- Import Events -->
        <div class="mt-8 bg-card border border-border rounded-lg shadow-sm">
            <div class="px-6 py-4 border-b border-border">
                <h2 class="text-lg font-semibold text-foreground">
                    Recent Import Events
                </h2>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead class="border-b border-border">
                        <tr class="text-left">
                            <th
                                class="px-6 py-3 text-sm font-medium text-muted-foreground"
                                >Event</th
                            >
                            <th
                                class="px-6 py-3 text-sm font-medium text-muted-foreground"
                                >Source</th
                            >
                            <th
                                class="px-6 py-3 text-sm font-medium text-muted-foreground"
                                >Records</th
                            >
                            <th
                                class="px-6 py-3 text-sm font-medium text-muted-foreground"
                                >Status</th
                            >
                            <th
                                class="px-6 py-3 text-sm font-medium text-muted-foreground"
                                >Date</th
                            >
                        </tr>
                    </thead>
                    <tbody>
                        {#each events as event}
                            <tr
                                class="border-b border-border hover:bg-muted/50"
                            >
                                <td class="px-6 py-4">
                                    <div class="flex items-center space-x-3">
                                        <div
                                            class="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center"
                                        >
                                            <span
                                                class="text-xs font-medium text-primary"
                                                >#{event.event_id}</span
                                            >
                                        </div>
                                        <div>
                                            <div
                                                class="font-medium text-foreground"
                                            >
                                                {event.filename ||
                                                    "Manual Import"}
                                            </div>
                                        </div>
                                    </div>
                                </td>
                                <td class="px-6 py-4">
                                    <span
                                        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-secondary text-secondary-foreground"
                                    >
                                        {event.source}
                                    </span>
                                </td>
                                <td class="px-6 py-4 text-sm text-foreground">
                                    <div>
                                        {event.inserted_count.toLocaleString()} inserted
                                    </div>
                                    {#if event.error_count > 0}
                                        <div class="text-red-600">
                                            {event.error_count} errors
                                        </div>
                                    {/if}
                                </td>
                                <td class="px-6 py-4">
                                    <span
                                        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getStatusColor(
                                            event.status,
                                        )}"
                                    >
                                        {event.status}
                                    </span>
                                </td>
                                <td
                                    class="px-6 py-4 text-sm text-muted-foreground"
                                >
                                    {formatTimestamp(event.created_at)}
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>

                {#if events.length === 0}
                    <div class="text-center py-8 text-muted-foreground">
                        No import events found
                    </div>
                {/if}
            </div>
        </div>
    </div>
</RoleGuard>
