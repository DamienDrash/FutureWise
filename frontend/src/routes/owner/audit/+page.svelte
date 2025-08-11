<script lang="ts">
    import { onMount } from "svelte";
    import { authStore } from "$lib/stores/auth";
    import RoleGuard from "$lib/components/RoleGuard.svelte";
    import type { User } from "$lib/types";

    const API = import.meta.env.VITE_API_BASE || "http://localhost:8000";

    let auditEntries: any[] = [];
    let loading = true;
    let error = "";

    $: user = $authStore?.user as User | null;

    async function loadAuditLog() {
        loading = true;
        error = "";
        try {
            const res = await fetch(`${API}/owner/audit-log`, {
                credentials: "include",
            });

            if (res.ok) {
                const data = await res.json();
                auditEntries = data.audit_entries || [];
            } else {
                const errorData = await res.json();
                error = errorData.detail || "Failed to load audit log";
            }
        } catch (err) {
            error = "Failed to load audit log: " + err;
            console.error("Audit log error:", err);
        } finally {
            loading = false;
        }
    }

    onMount(() => {
        loadAuditLog();
    });

    function formatDate(dateStr: string): string {
        return new Date(dateStr).toLocaleString("de-DE");
    }

    function getActionColor(action: string): string {
        switch (action) {
            case "CREATE":
                return "bg-green-100 text-green-800";
            case "UPDATE":
                return "bg-blue-100 text-blue-800";
            case "DELETE":
                return "bg-red-100 text-red-800";
            case "LOGIN":
                return "bg-purple-100 text-purple-800";
            default:
                return "bg-gray-100 text-gray-800";
        }
    }

    function getActionIcon(action: string): string {
        switch (action) {
            case "CREATE":
                return "M12 4.5v15m7.5-7.5h-15";
            case "UPDATE":
                return "M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10";
            case "DELETE":
                return "M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0";
            default:
                return "M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z";
        }
    }

    function formatDetails(details: any): string {
        if (!details) return "";
        try {
            const parsed =
                typeof details === "string" ? JSON.parse(details) : details;
            if (parsed.changes) {
                const changes = Object.entries(parsed.changes)
                    .map(
                        ([key, value]: [string, any]) =>
                            `${key}: ${value.old} → ${value.new}`,
                    )
                    .join(", ");
                return `Geändert: ${changes}`;
            }
            if (parsed.email) {
                return `Email: ${parsed.email}`;
            }
            return JSON.stringify(parsed);
        } catch (e) {
            return String(details);
        }
    }
</script>

<RoleGuard minRole="owner">
    <div class="space-y-6">
        <!-- Header -->
        <div class="border-b border-border pb-6">
            <h1 class="text-3xl font-bold text-foreground">Audit Log</h1>
            <p class="text-muted-foreground mt-2">
                Systemweite Aktivitäten und Änderungen verfolgen
            </p>
        </div>

        {#if loading}
            <div class="flex items-center justify-center h-64">
                <div class="text-muted-foreground">Lade Audit Log...</div>
            </div>
        {:else if error}
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <p class="text-red-800">Fehler beim Laden: {error}</p>
                <button
                    on:click={loadAuditLog}
                    class="mt-2 bg-red-600 text-white px-4 py-2 rounded-md text-sm hover:bg-red-700"
                >
                    Erneut versuchen
                </button>
            </div>
        {:else}
            <!-- Audit Entries -->
            <div class="bg-card border border-border rounded-lg p-6">
                <div class="flex items-center justify-between mb-6">
                    <h3 class="text-lg font-semibold text-foreground">
                        Systemaktivitäten
                    </h3>
                    <button
                        on:click={loadAuditLog}
                        class="bg-secondary text-secondary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-secondary/90"
                    >
                        Aktualisieren
                    </button>
                </div>

                {#if auditEntries.length === 0}
                    <div class="text-center py-8 text-muted-foreground">
                        Keine Audit-Einträge gefunden
                    </div>
                {:else}
                    <div class="space-y-4">
                        {#each auditEntries as entry}
                            <div
                                class="flex items-start gap-4 p-4 border border-border rounded-lg hover:bg-muted/30 transition-colors"
                            >
                                <!-- Action Icon -->
                                <div
                                    class="w-10 h-10 rounded-full bg-muted flex items-center justify-center flex-shrink-0"
                                >
                                    <svg
                                        class="w-5 h-5 text-foreground"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="1.5"
                                            d={getActionIcon(entry.action_type)}
                                        />
                                    </svg>
                                </div>

                                <!-- Content -->
                                <div class="flex-1 min-w-0">
                                    <div class="flex items-center gap-2 mb-2">
                                        <span
                                            class="text-xs font-medium px-2 py-1 rounded {getActionColor(
                                                entry.action_type,
                                            )}"
                                        >
                                            {entry.action_type}
                                        </span>
                                        <span
                                            class="text-sm font-medium text-foreground"
                                        >
                                            {entry.entity_type}
                                        </span>
                                        <span
                                            class="text-sm text-muted-foreground"
                                        >
                                            ID: {entry.entity_id}
                                        </span>
                                    </div>

                                    <div class="text-sm text-foreground mb-2">
                                        <span class="font-medium">
                                            {entry.user_name ||
                                                entry.user_email ||
                                                "System"}
                                        </span>
                                        hat
                                        {#if entry.action_type === "CREATE"}
                                            {entry.entity_type} erstellt
                                        {:else if entry.action_type === "UPDATE"}
                                            {entry.entity_type} aktualisiert
                                        {:else if entry.action_type === "DELETE"}
                                            {entry.entity_type} gelöscht
                                        {:else}
                                            Aktion {entry.action_type} auf {entry.entity_type}
                                            ausgeführt
                                        {/if}
                                    </div>

                                    {#if entry.details}
                                        <div
                                            class="text-xs text-muted-foreground mb-2"
                                        >
                                            {formatDetails(entry.details)}
                                        </div>
                                    {/if}

                                    <div class="text-xs text-muted-foreground">
                                        {formatDate(entry.created_at)}
                                    </div>
                                </div>
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
        {/if}
    </div>
</RoleGuard>
