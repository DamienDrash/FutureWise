<script>
  import { onDestroy } from "svelte";
  const apiBase = import.meta.env.VITE_API_BASE || "http://localhost:8000";
  let health = "...";
  let tenants = [];

  let dateFrom = "2025-08-01";
  let dateTo = "2025-08-10";
  let selectedTenant = "alpha";
  let summary = null;
  let events = [];
  let selectedEventErrors = [];

  // Import Upload
  let uploadFile = null;
  let uploadMsg = "";

  async function handleUpload() {
    uploadMsg = "";
    try {
      if (!uploadFile) {
        uploadMsg = "Bitte Datei wählen (.csv/.xlsx/.xls)";
        return;
      }
      const name = uploadFile.name.toLowerCase();
      const fd = new FormData();
      fd.append("tenant_id", selectedTenant);
      fd.append("file", uploadFile);
      let url = "";
      if (name.endsWith(".csv")) {
        url = `${apiBase}/imports/csv`;
      } else if (name.endsWith(".xlsx") || name.endsWith(".xls")) {
        url = `${apiBase}/imports/xls`;
      } else {
        uploadMsg = "Ungültige Dateiendung. Erlaubt: .csv/.xlsx/.xls";
        return;
      }
      const res = await fetch(url, { method: "POST", body: fd });
      const txt = await res.text();
      uploadMsg = `${res.status} ${txt}`;
      // Refresh
      await loadEvents();
      await loadSummary();
    } catch (e) {
      uploadMsg = `Fehler: ${e}`;
    }
  }

  // Scenarios
  let scenarios = [];
  let scenarioName = "Price -5%";
  let priceChangePct = -0.05;
  let promoUplift = 0.1;
  let trafficChange = 0.0;
  let simMsg = "";

  async function loadScenarios() {
    try {
      const res = await fetch(
        `${apiBase}/scenarios?tenant_id=${encodeURIComponent(selectedTenant)}`,
      );
      const json = await res.json();
      scenarios = json.items || [];
    } catch (e) {
      scenarios = [];
    }
  }

  async function saveScenario() {
    simMsg = "";
    try {
      const params = {
        name: scenarioName,
        price_change_pct: Number(priceChangePct),
        promo_uplift_orders: Number(promoUplift),
        traffic_change_pct: Number(trafficChange),
      };
      const url = new URL(`${apiBase}/scenarios`);
      url.searchParams.set("tenant_id", selectedTenant);
      url.searchParams.set("name", scenarioName);
      url.searchParams.set("kind", "custom");
      url.searchParams.set("params", JSON.stringify(params));
      const res = await fetch(url.toString(), { method: "POST" });
      const txt = await res.text();
      simMsg = `${res.status} ${txt}`;
      await loadScenarios();
    } catch (e) {
      simMsg = `Fehler: ${e}`;
    }
  }

  async function simulateAdhoc() {
    simMsg = "";
    try {
      const fd = new FormData();
      fd.append("tenant_id", selectedTenant);
      fd.append(
        "params",
        JSON.stringify({
          name: scenarioName,
          price_change_pct: Number(priceChangePct),
          promo_uplift_orders: Number(promoUplift),
          traffic_change_pct: Number(trafficChange),
        }),
      );
      fd.append("date_from", dateFrom);
      fd.append("date_to", dateTo);
      const res = await fetch(`${apiBase}/scenarios/simulate`, {
        method: "POST",
        body: fd,
      });
      const txt = await res.text();
      simMsg = `${res.status} ${txt}`;
      await loadScenarios();
    } catch (e) {
      simMsg = `Fehler: ${e}`;
    }
  }

  async function simulateExisting(sid) {
    simMsg = "";
    try {
      const fd = new FormData();
      fd.append("tenant_id", selectedTenant);
      fd.append("scenario_id", String(sid));
      fd.append("date_from", dateFrom);
      fd.append("date_to", dateTo);
      const res = await fetch(`${apiBase}/scenarios/simulate`, {
        method: "POST",
        body: fd,
      });
      const txt = await res.text();
      simMsg = `${res.status} ${txt}`;
    } catch (e) {
      simMsg = `Fehler: ${e}`;
    }
  }

  async function loadHealth() {
    try {
      const res = await fetch(`${apiBase}/health/ready`);
      const json = await res.json();
      health = json.status;
    } catch (e) {
      health = "error";
    }
  }

  async function loadTenants() {
    try {
      const res = await fetch(`${apiBase}/tenants`);
      const json = await res.json();
      tenants = json.items || [];
      if (tenants.length > 0 && !selectedTenant) {
        selectedTenant = tenants[0].tenant_id;
      }
    } catch (e) {
      tenants = [];
    }
  }

  async function loadSummary() {
    try {
      const url = new URL(`${apiBase}/imports/summary`);
      url.searchParams.set("tenant_id", selectedTenant);
      url.searchParams.set("date_from", dateFrom);
      url.searchParams.set("date_to", dateTo);
      const res = await fetch(url.toString());
      summary = await res.json();
    } catch (e) {
      summary = { error: true };
    }
  }

  async function loadEvents() {
    try {
      const url = new URL(`${apiBase}/imports/events`);
      url.searchParams.set("tenant_id", selectedTenant);
      url.searchParams.set("limit", "10");
      const res = await fetch(url.toString());
      const json = await res.json();
      events = json.items || [];
    } catch (e) {
      events = [];
    }
  }

  async function loadEventErrors(event_id) {
    selectedEventErrors = [];
    try {
      const res = await fetch(`${apiBase}/imports/events/${event_id}/errors`);
      const json = await res.json();
      selectedEventErrors = json.items || [];
    } catch (e) {
      selectedEventErrors = [];
    }
  }

  // Compare Chart
  import Chart from "chart.js/auto";
  let selectedScenarioForCompare = null;
  let compareSeries = null;
  let ordersChartEl;
  let revenueChartEl;
  let ordersChart;
  let revenueChart;

  // Vergleichsoptionen
  let compareMetric = "orders"; // orders | revenue | sessions
  let compareAsIndex = false;

  function destroyCharts() {
    if (ordersChart) {
      ordersChart.destroy();
      ordersChart = null;
    }
    if (revenueChart) {
      revenueChart.destroy();
      revenueChart = null;
    }
  }
  onDestroy(destroyCharts);

  function formatNumber(n) {
    return new Intl.NumberFormat("de-DE").format(n ?? 0);
  }
  function formatEuroCents(c) {
    const v = (Number(c || 0) / 100);
    return new Intl.NumberFormat("de-DE", { style: "currency", currency: "EUR" }).format(v);
  }

  function alignSeries(series) {
    // merged, sort labels
    const dates = Array.from(new Set([
      ...series.baseline.map((x) => x.date),
      ...series.scenario.map((x) => x.date),
    ])).sort();
    function pick(arr, key) {
      const map = new Map(arr.map((x) => [x.date, x[key]]));
      return dates.map((d) => (map.has(d) ? map.get(d) : null));
    }
    return {
      labels: dates,
      baseline: {
        orders: pick(series.baseline, "orders"),
        revenue: pick(series.baseline, "revenue_cents_gross"),
        sessions: pick(series.baseline, "sessions"),
      },
      scenario: {
        orders: pick(series.scenario, "orders"),
        revenue: pick(series.scenario, "revenue_cents_gross"),
        sessions: pick(series.scenario, "sessions"),
      },
    };
  }

  function indexValues(baseArr, scenArr) {
    // index as daily ratio*100 (scenario vs baseline)
    const idx = scenArr.map((v, i) => {
      const b = baseArr[i] ?? 0;
      if (!b || v == null) return null;
      return (v / b) * 100;
    });
    return idx;
  }

  // KPI Summary für Vergleich
  let compareStats = null;
  function computeStats(aligned, metric) {
    const sum = (arr) => arr.reduce((a, b) => a + (Number(b || 0)), 0);
    const b = sum(aligned.baseline[metric]);
    const s = sum(aligned.scenario[metric]);
    const delta = s - b;
    const pct = b ? (delta / b) * 100 : 0;
    return { baseline: b, scenario: s, delta, pct };
  }

  async function loadCompare() {
    compareSeries = null;
    compareStats = null;
    destroyCharts();
    if (!selectedScenarioForCompare) return;
    const url = new URL(
      `${apiBase}/scenarios/${selectedScenarioForCompare}/series`,
    );
    url.searchParams.set("tenant_id", selectedTenant);
    url.searchParams.set("date_from", dateFrom);
    url.searchParams.set("date_to", dateTo);
    const res = await fetch(url.toString());
    const raw = await res.json();
    const aligned = alignSeries(raw);
    compareSeries = aligned;
    compareStats = computeStats(aligned, compareMetric);
    drawCharts();
  }

  function drawCharts() {
    destroyCharts();
    if (!compareSeries) return;

    const labels = compareSeries.labels;
    const metricKey = compareMetric;

    let baselineValues = compareSeries.baseline[metricKey];
    let scenarioValues = compareSeries.scenario[metricKey];

    if (compareAsIndex) {
      const idx = indexValues(baselineValues, scenarioValues);
      baselineValues = baselineValues.map((v, i) => (baselineValues[i] ? 100 : null));
      scenarioValues = idx;
    }

    ordersChart = new Chart(ordersChartEl, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: compareAsIndex ? "Baseline (Index)" : "Baseline",
            data: baselineValues,
            borderColor: "#60a5fa",
          },
          {
            label: compareAsIndex ? "Scenario (Index)" : "Scenario",
            data: scenarioValues,
            borderColor: "#f59e0b",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const v = ctx.parsed.y;
                if (compareAsIndex) return `${ctx.dataset.label}: ${v?.toFixed(1)}%`;
                if (compareMetric === "revenue") return `${ctx.dataset.label}: ${formatEuroCents(v)}`;
                return `${ctx.dataset.label}: ${formatNumber(v)}`;
              },
            },
          },
        },
        scales: {
          y: {
            ticks: {
              callback: (value) => {
                if (compareAsIndex) return `${value}%`;
                if (compareMetric === "revenue") return formatEuroCents(value);
                return formatNumber(value);
              },
            },
          },
        },
      },
    });

    // Zweites Chart optional für Revenue, wenn nicht ausgewählt
    const showSecond = compareMetric !== "revenue";
    if (showSecond) {
      const bRev = compareSeries.baseline.revenue;
      const sRev = compareSeries.scenario.revenue;
      revenueChart = new Chart(revenueChartEl, {
        type: "line",
        data: {
          labels,
          datasets: [
            { label: "Revenue Gross (Baseline)", data: bRev, borderColor: "#22c55e" },
            { label: "Revenue Gross (Scenario)", data: sRev, borderColor: "#ef4444" },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: { y: { ticks: { callback: (v) => formatEuroCents(v) } } },
        },
      });
    }
  }

  function onCompareOptionChange() {
    if (compareSeries) {
      compareStats = computeStats(compareSeries, compareMetric);
      drawCharts();
    }
  }

  loadHealth();
  loadTenants();
  loadEvents();
  loadScenarios();
</script>

<main class="p-6 min-h-screen bg-base-200">
  <div class="max-w-5xl mx-auto space-y-6">
    <h1 class="text-2xl font-bold">FutureWise</h1>

    <div class="card bg-base-100 shadow">
      <div class="card-body">
        <h2 class="card-title">System Health</h2>
        <div
          class="badge"
          class:badge-success={health === "ok"}
          class:badge-error={health !== "ok"}
        >
          {health}
        </div>
      </div>
    </div>

    <div class="card bg-base-100 shadow">
      <div class="card-body space-y-4">
        <h2 class="card-title">Tenants</h2>
        {#if tenants.length === 0}
          <p class="text-sm opacity-70">Keine Tenants gefunden.</p>
        {:else}
          <select
            bind:value={selectedTenant}
            class="select select-bordered w-full max-w-xs"
            on:change={() => {
              loadSummary();
              loadEvents();
              loadScenarios();
            }}
          >
            {#each tenants as t}
              <option value={t.tenant_id}>{t.name} ({t.tenant_id})</option>
            {/each}
          </select>
        {/if}
      </div>
    </div>

    <div class="card bg-base-100 shadow">
      <div class="card-body space-y-4">
        <h2 class="card-title">Import Upload (CSV/XLS)</h2>
        <div class="flex gap-2 items-center">
          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            class="file-input file-input-bordered w-full max-w-md"
            on:change={(e) => (uploadFile = e.currentTarget.files?.[0])}
          />
          <button class="btn btn-primary" on:click={handleUpload}
            >Importieren</button
          >
        </div>
        {#if uploadMsg}
          <div class="text-xs opacity-70 break-all">{uploadMsg}</div>
        {/if}
      </div>
    </div>

    <div class="card bg-base-100 shadow">
      <div class="card-body space-y-4">
        <h2 class="card-title">Import Zusammenfassung</h2>
        <div class="flex gap-2 items-end">
          <div>
            <label class="label"><span class="label-text">Von</span></label>
            <input
              type="date"
              bind:value={dateFrom}
              class="input input-bordered"
            />
          </div>
          <div>
            <label class="label"><span class="label-text">Bis</span></label>
            <input
              type="date"
              bind:value={dateTo}
              class="input input-bordered"
            />
          </div>
          <button class="btn btn-primary" on:click={loadSummary}>Laden</button>
        </div>
        {#if summary}
          {#if summary.error}
            <div class="alert alert-error">Fehler beim Laden.</div>
          {:else}
            <div class="stats shadow">
              <div class="stat">
                <div class="stat-title">Tage</div>
                <div class="stat-value">{summary.summary?.num_days ?? 0}</div>
              </div>
              <div class="stat">
                <div class="stat-title">Sessions</div>
                <div class="stat-value">
                  {summary.summary?.sessions_sum ?? 0}
                </div>
              </div>
              <div class="stat">
                <div class="stat-title">Orders</div>
                <div class="stat-value">{summary.summary?.orders_sum ?? 0}</div>
              </div>
              <div class="stat">
                <div class="stat-title">Revenue Gross (cents)</div>
                <div class="stat-value">
                  {summary.summary?.revenue_gross_sum ?? 0}
                </div>
              </div>
              <div class="stat">
                <div class="stat-title">Revenue Net (cents)</div>
                <div class="stat-value">
                  {summary.summary?.revenue_net_sum ?? 0}
                </div>
              </div>
            </div>
          {/if}
        {/if}
      </div>
    </div>

    <div class="card bg-base-100 shadow">
      <div class="card-body space-y-3">
        <h2 class="card-title">Szenarien</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="space-y-2">
            <label class="label"><span class="label-text">Name</span></label>
            <input
              class="input input-bordered w-full"
              bind:value={scenarioName}
            />
            <div class="grid grid-cols-3 gap-2">
              <div>
                <label class="label"
                  ><span class="label-text">Price Δ%</span></label
                >
                <input
                  class="input input-bordered w-full"
                  type="number"
                  step="0.01"
                  bind:value={priceChangePct}
                />
              </div>
              <div>
                <label class="label"
                  ><span class="label-text">Promo Uplift</span></label
                >
                <input
                  class="input input-bordered w-full"
                  type="number"
                  step="0.01"
                  bind:value={promoUplift}
                />
              </div>
              <div>
                <label class="label"
                  ><span class="label-text">Traffic Δ%</span></label
                >
                <input
                  class="input input-bordered w-full"
                  type="number"
                  step="0.01"
                  bind:value={trafficChange}
                />
              </div>
            </div>
            <div class="flex gap-2">
              <button class="btn" on:click={saveScenario}>Speichern</button>
              <button class="btn btn-primary" on:click={simulateAdhoc}
                >Ad-hoc simulieren</button
              >
            </div>
            {#if simMsg}
              <div class="text-xs opacity-70 break-all">{simMsg}</div>
            {/if}
          </div>
          <div>
            <label class="label"
              ><span class="label-text">Vorhandene Szenarien</span></label
            >
            {#if scenarios.length === 0}
              <p class="text-sm opacity-70">Keine Szenarien.</p>
            {:else}
              <ul class="menu bg-base-100">
                {#each scenarios as s}
                  <li>
                    <div class="flex items-center justify-between gap-2">
                      <span
                        >{s.name}
                        <small class="opacity-60">#{s.scenario_id}</small></span
                      >
                      <button
                        class="btn btn-xs"
                        on:click={() => simulateExisting(s.scenario_id)}
                        >Simulieren</button
                      >
                    </div>
                  </li>
                {/each}
              </ul>
            {/if}
          </div>
        </div>
      </div>
    </div>

    <div class="card bg-base-100 shadow">
      <div class="card-body space-y-2">
        <h2 class="card-title">Letzte Importe</h2>
        {#if events.length === 0}
          <p class="text-sm opacity-70">Keine Events.</p>
        {:else}
          <table class="table">
            <thead>
              <tr
                ><th>ID</th><th>Source</th><th>Filename</th><th>Inserted</th><th
                  >Errors</th
                ><th>Status</th><th>Aktion</th></tr
              >
            </thead>
            <tbody>
              {#each events as e}
                <tr>
                  <td>{e.event_id}</td>
                  <td>{e.source}</td>
                  <td>{e.filename || "-"}</td>
                  <td>{e.inserted_count}</td>
                  <td>{e.error_count}</td>
                  <td>
                    <div
                      class="badge"
                      class:badge-success={e.status === "success"}
                      class:badge-warning={e.status === "partial"}
                      class:badge-error={e.status === "failed"}
                    >
                      {e.status}
                    </div>
                  </td>
                  <td>
                    {#if e.error_count > 0}
                      <button
                        class="btn btn-xs"
                        on:click={() => loadEventErrors(e.event_id)}
                        >Fehler</button
                      >
                    {:else}
                      <span class="opacity-50">-</span>
                    {/if}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
          {#if selectedEventErrors.length > 0}
            <div class="mt-2">
              <h3 class="font-semibold">Fehlerdetails</h3>
              <ul class="menu bg-base-100">
                {#each selectedEventErrors as er}
                  <li><span>Row {er.row_index}: {er.error}</span></li>
                {/each}
              </ul>
            </div>
          {/if}
        {/if}
      </div>
    </div>

    <!-- Vergleich Panel -->
    <div class="card bg-base-100 shadow">
      <div class="card-body space-y-3">
        <h2 class="card-title">Vergleich Baseline vs. Szenario</h2>
        <div class="flex flex-wrap gap-2 items-end">
          <select
            class="select select-bordered max-w-xs"
            bind:value={selectedScenarioForCompare}
          >
            <option value={null} disabled selected>Scenario wählen</option>
            {#each scenarios as s}
              <option value={s.scenario_id}>{s.name} (#{s.scenario_id})</option>
            {/each}
          </select>
          <select class="select select-bordered" bind:value={compareMetric} on:change={onCompareOptionChange}>
            <option value="orders">Orders</option>
            <option value="revenue">Revenue Gross</option>
            <option value="sessions">Sessions</option>
          </select>
          <label class="label cursor-pointer gap-2">
            <span class="label-text">Index 100 = Baseline</span>
            <input type="checkbox" class="toggle" bind:checked={compareAsIndex} on:change={onCompareOptionChange} />
          </label>
          <button class="btn btn-primary" on:click={loadCompare}
            >Vergleich laden</button
          >
        </div>

        {#if compareStats}
          <div class="stats shadow">
            <div class="stat">
              <div class="stat-title">Baseline</div>
              <div class="stat-value text-base">
                {compareMetric === 'revenue' ? formatEuroCents(compareStats.baseline) : formatNumber(compareStats.baseline)}
              </div>
            </div>
            <div class="stat">
              <div class="stat-title">Scenario</div>
              <div class="stat-value text-base">
                {compareMetric === 'revenue' ? formatEuroCents(compareStats.scenario) : formatNumber(compareStats.scenario)}
              </div>
            </div>
            <div class="stat">
              <div class="stat-title">Delta</div>
              <div class="stat-value text-base">
                {compareMetric === 'revenue' ? formatEuroCents(compareStats.delta) : formatNumber(compareStats.delta)}
                <span class={compareStats.pct >= 0 ? 'badge badge-success ml-2' : 'badge badge-error ml-2'}>
                  {compareStats.pct.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        {/if}

        {#if compareSeries}
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 h-[360px]">
            <div class="bg-base-200 rounded p-2"><canvas bind:this={ordersChartEl}></canvas></div>
            {#if compareMetric !== 'revenue'}
              <div class="bg-base-200 rounded p-2"><canvas bind:this={revenueChartEl}></canvas></div>
            {/if}
          </div>
        {/if}
      </div>
    </div>

  </div>
</main>

<style>
</style>
