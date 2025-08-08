<script>
    import { onMount } from "svelte";
    const API = import.meta.env.VITE_API_BASE || "http://localhost:8000";
    let tenantId =
        typeof localStorage !== "undefined"
            ? localStorage.getItem("fw_tenant") || "alpha"
            : "alpha";
    let dateFrom = new Date(Date.now() - 7 * 24 * 3600 * 1000)
        .toISOString()
        .slice(0, 10);
    let dateTo = new Date().toISOString().slice(0, 10);
    let summary = null;
    let events = [];
    let uploading = false;
    let error = "";

    async function loadSummary() {
        try {
            const url = new URL(`${API}/imports/summary`);
            url.searchParams.set("tenant_id", tenantId);
            url.searchParams.set("date_from", dateFrom);
            url.searchParams.set("date_to", dateTo);
            const res = await fetch(url, { credentials: "include" });
            summary = await res.json();
        } catch (e) {
            summary = { error: true };
        }
    }

    async function loadEvents() {
        try {
            const url = new URL(`${API}/imports/events`);
            url.searchParams.set("tenant_id", tenantId);
            url.searchParams.set("limit", "10");
            const res = await fetch(url, { credentials: "include" });
            const j = await res.json();
            events = j.items || [];
        } catch (e) {
            events = [];
        }
    }

    async function uploadCsv(e) {
        const file = e.target.files?.[0];
        if (!file) return;
        uploading = true;
        error = "";
        try {
            const fd = new FormData();
            fd.append("tenant_id", tenantId);
            fd.append("file", file);
            const res = await fetch(`${API}/imports/csv`, {
                method: "POST",
                body: fd,
                credentials: "include",
            });
            if (!res.ok) {
                const t = await res.text();
                error = `Upload fehlgeschlagen: ${res.status} ${t}`;
            }
            await Promise.all([loadSummary(), loadEvents()]);
        } finally {
            uploading = false;
            e.target.value = "";
        }
    }

    onMount(async () => {
        await Promise.all([loadSummary(), loadEvents()]);
    });
</script>

<section class="p-6 space-y-6">
    <h1 class="text-2xl font-bold">Imports</h1>

    <div class="card bg-base-100 shadow">
        <div class="card-body flex gap-4 items-end">
            <div>
                <label class="label"><span class="label-text">Von</span></label>
                <input
                    class="input input-bordered"
                    type="date"
                    bind:value={dateFrom}
                />
            </div>
            <div>
                <label class="label"><span class="label-text">Bis</span></label>
                <input
                    class="input input-bordered"
                    type="date"
                    bind:value={dateTo}
                />
            </div>
            <button class="btn" on:click={loadSummary}
                >Zusammenfassung laden</button
            >
        </div>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title">Zusammenfassung</h2>
            {#if summary?.error}
                <div class="alert alert-error">Fehler beim Laden.</div>
            {:else}
                <div class="stats shadow">
                    <div class="stat">
                        <div class="stat-title">Tage</div>
                        <div class="stat-value">
                            {summary?.summary?.num_days ?? 0}
                        </div>
                    </div>
                    <div class="stat">
                        <div class="stat-title">Sessions</div>
                        <div class="stat-value">
                            {summary?.summary?.sessions_sum ?? 0}
                        </div>
                    </div>
                    <div class="stat">
                        <div class="stat-title">Orders</div>
                        <div class="stat-value">
                            {summary?.summary?.orders_sum ?? 0}
                        </div>
                    </div>
                    <div class="stat">
                        <div class="stat-title">Revenue Gross</div>
                        <div class="stat-value">
                            {summary?.summary?.revenue_gross_sum ?? 0}
                        </div>
                    </div>
                    <div class="stat">
                        <div class="stat-title">Revenue Net</div>
                        <div class="stat-value">
                            {summary?.summary?.revenue_net_sum ?? 0}
                        </div>
                    </div>
                </div>
            {/if}
        </div>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title">Datei-Upload (CSV)</h2>
            <input
                type="file"
                accept=".csv"
                class="file-input file-input-bordered"
                on:change={uploadCsv}
                disabled={uploading}
            />
            {#if error}
                <div class="alert alert-error mt-2">{error}</div>
            {/if}
        </div>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title">Letzte Events</h2>
            <ul class="space-y-2">
                {#each events as ev}
                    <li class="flex justify-between border-b pb-2">
                        <span>#{ev.event_id} · {ev.source} · {ev.status}</span>
                        <span
                            >{ev.inserted_count} insert · {ev.error_count} errors</span
                        >
                    </li>
                {/each}
            </ul>
        </div>
    </div>
</section>
