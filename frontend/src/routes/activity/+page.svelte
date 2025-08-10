<script lang="ts">
    import { onMount } from "svelte";
    import RoleGuard from "$lib/components/RoleGuard.svelte";

    const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

    let activities: any[] = [];
    let isLoading = true;
    let page = 1;
    let limit = 20;
    let total = 0;

    async function loadActivities() {
        isLoading = true;
        try {
            const tenantId = localStorage.getItem("fw_tenant") || "alpha";
            const res = await fetch(
                `${API_BASE}/imports/events?tenant_id=${tenantId}&limit=${limit}&offset=${(page - 1) * limit}`,
                {
                    credentials: "include",
                },
            );

            if (res.ok) {
                const data = await res.json();
                activities = data.items || [];
                total = data.total || activities.length;
            }
        } catch (error) {
            console.error("Failed to load activities:", error);
            activities = [];
        } finally {
            isLoading = false;
        }
    }

    function formatTimestamp(dateStr: string) {
        return new Date(dateStr).toLocaleString("de-DE");
    }

    function formatBytes(bytes: number) {
        return (bytes / 1000).toLocaleString() + " records";
    }

    onMount(() => {
        loadActivities();
    });

    $: totalPages = Math.ceil(total / limit);
</script>

<RoleGuard requiredRole="tenant_user">
    <div class="max-w-6xl mx-auto p-6">
        <div class="mb-6">
            <h1 class="text-2xl font-bold text-foreground mb-2">
                Activity Overview
            </h1>
            <p class="text-muted-foreground">
                Complete history of import events and system activities
            </p>
        </div>

        {#if isLoading}
            <div class="flex justify-center py-8">
                <div class="text-muted-foreground">Loading activities...</div>
            </div>
        {:else if activities.length === 0}
            <div class="text-center py-8">
                <div class="text-muted-foreground">No activities found</div>
            </div>
        {:else}
            <div class="bg-card border border-border rounded-lg shadow-sm">
                <div class="overflow-x-auto">
                    <table class="w-full">
                        <thead class="border-b border-border">
                            <tr class="text-left">
                                <th
                                    class="px-6 py-4 text-sm font-medium text-muted-foreground"
                                    >Event</th
                                >
                                <th
                                    class="px-6 py-4 text-sm font-medium text-muted-foreground"
                                    >Source</th
                                >
                                <th
                                    class="px-6 py-4 text-sm font-medium text-muted-foreground"
                                    >Records</th
                                >
                                <th
                                    class="px-6 py-4 text-sm font-medium text-muted-foreground"
                                    >Status</th
                                >
                                <th
                                    class="px-6 py-4 text-sm font-medium text-muted-foreground"
                                    >Date</th
                                >
                            </tr>
                        </thead>
                        <tbody>
                            {#each activities as activity}
                                <tr
                                    class="border-b border-border hover:bg-muted/50"
                                >
                                    <td class="px-6 py-4">
                                        <div
                                            class="flex items-center space-x-3"
                                        >
                                            <div
                                                class="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center"
                                            >
                                                <svg
                                                    class="w-4 h-4 text-primary"
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
                                            </div>
                                            <div>
                                                <div
                                                    class="font-medium text-foreground"
                                                >
                                                    {activity.filename ||
                                                        "Import Event"}
                                                </div>
                                                <div
                                                    class="text-sm text-muted-foreground"
                                                >
                                                    Event #{activity.event_id}
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4">
                                        <span
                                            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-secondary text-secondary-foreground"
                                        >
                                            {activity.source}
                                        </span>
                                    </td>
                                    <td
                                        class="px-6 py-4 text-sm text-foreground"
                                    >
                                        {formatBytes(activity.inserted_count)}
                                    </td>
                                    <td class="px-6 py-4">
                                        <span
                                            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                      {activity.status === 'success'
                                                ? 'bg-green-100 text-green-800'
                                                : activity.status === 'error'
                                                  ? 'bg-red-100 text-red-800'
                                                  : 'bg-yellow-100 text-yellow-800'}"
                                        >
                                            {activity.status}
                                        </span>
                                    </td>
                                    <td
                                        class="px-6 py-4 text-sm text-muted-foreground"
                                    >
                                        {formatTimestamp(activity.created_at)}
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>

                <!-- Pagination -->
                {#if totalPages > 1}
                    <div
                        class="px-6 py-4 border-t border-border flex items-center justify-between"
                    >
                        <div class="text-sm text-muted-foreground">
                            Showing {(page - 1) * limit + 1} to {Math.min(
                                page * limit,
                                total,
                            )} of {total} activities
                        </div>
                        <div class="flex space-x-2">
                            <button
                                class="px-3 py-1 text-sm border border-border rounded hover:bg-muted disabled:opacity-50"
                                disabled={page <= 1}
                                on:click={() => {
                                    page--;
                                    loadActivities();
                                }}
                            >
                                Previous
                            </button>
                            <span
                                class="px-3 py-1 text-sm bg-primary text-primary-foreground rounded"
                            >
                                {page}
                            </span>
                            <button
                                class="px-3 py-1 text-sm border border-border rounded hover:bg-muted disabled:opacity-50"
                                disabled={page >= totalPages}
                                on:click={() => {
                                    page++;
                                    loadActivities();
                                }}
                            >
                                Next
                            </button>
                        </div>
                    </div>
                {/if}
            </div>
        {/if}
    </div>
</RoleGuard>
