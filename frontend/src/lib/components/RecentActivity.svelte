<script lang="ts">
    import { onMount } from "svelte";

    const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

    let activities: any[] = [];
    let isLoading = true;

    const activityIcons = {
        import: "M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10",
        scenario:
            "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
        user: "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z",
        api: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
    };

    const activityColors = {
        import: "text-green-500",
        scenario: "text-chart-2",
        user: "text-chart-3",
        api: "text-muted-foreground",
    };

    async function loadRecentActivity() {
        isLoading = true;
        try {
            const tenantId = localStorage.getItem("fw_tenant") || "alpha";
            const res = await fetch(
                `${API_BASE}/imports/events?tenant_id=${tenantId}&limit=5`,
                {
                    credentials: "include",
                },
            );

            if (res.ok) {
                const data = await res.json();
                activities = (data.items || []).map((item: any) => ({
                    id: item.id,
                    type: "import",
                    title: `Import ${item.status}`,
                    description: `${item.filename} - ${item.records_imported} records`,
                    timestamp: formatTimestamp(item.created_at),
                    icon: activityIcons.import,
                    color:
                        item.status === "completed"
                            ? activityColors.import
                            : "text-red-500",
                }));
            }
        } catch (error) {
            console.error("Failed to load recent activity:", error);
            activities = [];
        } finally {
            isLoading = false;
        }
    }

    function formatTimestamp(dateStr: string) {
        const date = new Date(dateStr);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffMins < 60) return `${diffMins} Minuten her`;
        if (diffHours < 24) return `${diffHours} Stunden her`;
        return `${diffDays} Tage her`;
    }

    onMount(() => {
        loadRecentActivity();
    });
</script>

<div class="bg-card border border-border rounded-lg p-6 shadow-sm">
    <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-card-foreground">
            Recent Activity
        </h3>
        <a
            href="/activity"
            class="text-sm text-primary hover:text-primary/80 font-medium"
        >
            View all
        </a>
    </div>

    <div class="space-y-4">
        {#if isLoading}
            <div class="text-sm text-muted-foreground">Lädt...</div>
        {:else if activities.length === 0}
            <div class="text-sm text-muted-foreground">
                Keine Aktivitäten vorhanden
            </div>
        {:else}
            {#each activities as activity}
                <div class="flex items-start space-x-3">
                    <div
                        class="flex-shrink-0 w-8 h-8 bg-muted rounded-full flex items-center justify-center"
                    >
                        <svg
                            class="w-4 h-4 {activity.color}"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d={activity.icon}
                            ></path>
                        </svg>
                    </div>
                    <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-card-foreground">
                            {activity.title}
                        </p>
                        <p class="text-xs text-muted-foreground mt-1">
                            {activity.description}
                        </p>
                        <p class="text-xs text-muted-foreground mt-1">
                            {activity.timestamp}
                        </p>
                    </div>
                </div>
            {/each}
        {/if}
    </div>
</div>
