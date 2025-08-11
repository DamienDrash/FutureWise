<script lang="ts">
  import { onMount } from "svelte";
  import KPICard from "$lib/components/KPICard.svelte";
  import QuickActions from "$lib/components/QuickActions.svelte";
  import RecentActivity from "$lib/components/RecentActivity.svelte";
  import RoleGuard from "$lib/components/RoleGuard.svelte";
  import RoleBadge from "$lib/components/RoleBadge.svelte";
  import AnalyticsChart from "$lib/components/AnalyticsChart.svelte";
  import {
    isSystemManager,
    isTenantAdmin,
    isOwner,
    getUserDisplayInfo,
  } from "$lib/stores/auth";

  export let data;

  let token = "";
  let kpiData: any[] = [];
  let isLoading = true;
  let ownerSaasData: any = null;

  const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

  onMount(() => {
    if (typeof localStorage !== "undefined") {
      token = localStorage.getItem("fw_token") || "";
    }
    loadKPIData();
  });

  $: userInfo = getUserDisplayInfo(data?.user);
  $: isOwnerRole = data?.user && isOwner(data.user.role);
  $: isSystemRole = data?.user && isSystemManager(data.user.role);
  $: isTenantAdminRole = data?.user && isTenantAdmin(data.user.role);

  async function loadKPIData() {
    isLoading = true;
    try {
      // Owner sieht das SaaS Overview Dashboard direkt auf der Hauptseite
      if (isOwnerRole) {
        // Load SaaS metrics for owner
        const [metricsRes, revenueRes] = await Promise.all([
          fetch(`${API_BASE}/owner/saas-metrics`, { credentials: "include" }),
          fetch(`${API_BASE}/owner/revenue`, { credentials: "include" }),
        ]);

        if (metricsRes.ok && revenueRes.ok) {
          const saasData = await metricsRes.json();
          const revenueData = await revenueRes.json();

          kpiData = [
            {
              title: "Monthly Recurring Revenue",
              value: `€${(saasData.current_metrics.mrr_cents / 100).toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
              change: null,
              icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1",
              color: "chart-1",
            },
            {
              title: "Annual Recurring Revenue",
              value: `€${(saasData.current_metrics.arr_cents / 100).toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
              change: null,
              icon: "M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z",
              color: "chart-2",
            },
            {
              title: "Aktive Tenants",
              value: `${saasData.current_metrics.active_tenants}`,
              change: null,
              icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4",
              color: "chart-3",
            },
            {
              title: "Total Users",
              value: `${saasData.current_metrics.total_users}`,
              change: null,
              icon: "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z",
              color: "chart-4",
            },
          ];

          // Store additional SaaS data for display
          ownerSaasData = {
            metrics: saasData,
            revenue: revenueData,
          };
        }
        isLoading = false;
        return;
      }

      const tenantId = localStorage.getItem("fw_tenant") || "alpha";

      if (isSystemRole) {
        // Load system-wide KPIs
        const [tenantsRes, usersRes] = await Promise.all([
          fetch(`${API_BASE}/tenants`, { credentials: "include" }),
          fetch(`${API_BASE}/system/stats`, { credentials: "include" }).catch(
            () => ({ ok: false }),
          ),
        ]);

        const tenantsData = tenantsRes.ok
          ? await tenantsRes.json()
          : { items: [] };
        const usersData = usersRes.ok
          ? await usersRes.json()
          : { total_users: 0, system_revenue: 0, active_scenarios: 0 };

        kpiData = [
          {
            title: "Total Tenants",
            value: String(tenantsData.items?.length || 0),
            change: null,
            icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4",
            color: "chart-1",
          },
          {
            title: "System Users",
            value: String(usersData.total_users || 0),
            change: null,
            icon: "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z",
            color: "chart-2",
          },
          {
            title: "System Revenue",
            value: `€${((usersData.system_revenue || 0) / 100).toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
            change: null,
            icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1",
            color: "chart-3",
          },
          {
            title: "Active Scenarios",
            value: String(usersData.active_scenarios || 0),
            change: null,
            icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
            color: "chart-4",
          },
        ];
      } else {
        // Load tenant-specific KPIs
        const [summaryRes, scenariosRes] = await Promise.all([
          fetch(
            `${API_BASE}/imports/summary?tenant_id=${tenantId}&date_from=${getDateWeekAgo()}&date_to=${getTodayDate()}`,
            { credentials: "include" },
          ),
          fetch(`${API_BASE}/scenarios?tenant_id=${tenantId}`, {
            credentials: "include",
          }),
        ]);

        const summaryData = summaryRes.ok ? await summaryRes.json() : {};
        const scenariosData = scenariosRes.ok
          ? await scenariosRes.json()
          : { items: [] };

        kpiData = [
          {
            title: "Total Revenue",
            value: `€${((summaryData.summary?.revenue_gross_sum || 0) / 100).toLocaleString()}`,
            change: null,
            icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1",
            color: "chart-1",
          },
          {
            title: "Active Scenarios",
            value: String(scenariosData.items?.length || 0),
            change: null,
            icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
            color: "chart-2",
          },
          {
            title: "Total Orders",
            value: String(summaryData.summary?.orders_sum || 0),
            change: null,
            icon: "M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z",
            color: "chart-3",
          },
          {
            title: "Total Sessions",
            value: String(summaryData.summary?.sessions_sum || 0),
            change: null,
            icon: "M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z",
            color: "chart-4",
          },
        ];
      }
    } catch (error) {
      console.error("Failed to load KPI data:", error);
      kpiData = [];
    } finally {
      isLoading = false;
    }
  }

  function getDateWeekAgo() {
    const date = new Date();
    date.setDate(date.getDate() - 7);
    return date.toISOString().split("T")[0];
  }

  function getTodayDate() {
    return new Date().toISOString().split("T")[0];
  }

  // KPI data is now loaded from database via loadKPIData function
</script>

{#if !token && !data?.user}
  <!-- Landing Page for Non-Authenticated Users -->
  <div class="max-w-6xl mx-auto">
    <!-- Hero Section -->
    <div class="text-center py-12 px-4">
      <h1
        class="text-4xl font-bold text-foreground mb-4
                 sm:text-5xl
                 lg:text-6xl"
      >
        FutureWise
      </h1>
      <p
        class="text-xl text-muted-foreground mb-6 max-w-3xl mx-auto
               sm:text-2xl"
      >
        E-Commerce Scenario Management
      </p>
      <p class="text-muted-foreground mb-8 max-w-4xl mx-auto text-lg">
        Importiere historische KPIs, simuliere ML-basierte Szenarien und treffe
        bessere Entscheidungen. Multi-Tenant, RBAC-ready, API-first.
      </p>

      <div
        class="flex flex-col gap-4 justify-center items-center
                  sm:flex-row
                  sm:gap-6"
      >
        <a
          href="/register"
          class="px-8 py-3 bg-primary text-primary-foreground font-semibold rounded-lg shadow-lg
                 hover:bg-primary/90
                 transition-colors"
        >
          Kostenlos starten
        </a>
        <a
          href="/pricing"
          class="px-8 py-3 bg-background border border-border text-foreground font-semibold rounded-lg
                 hover:bg-muted
                 transition-colors"
        >
          Pricing ansehen
        </a>
      </div>
    </div>

    <!-- Features Grid -->
    <div
      class="grid gap-8 py-12 px-4
               md:grid-cols-2
               lg:grid-cols-3"
    >
      <div class="bg-card border border-border rounded-lg p-6 text-center">
        <div
          class="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4"
        >
          <svg
            class="w-6 h-6 text-primary"
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
        <h3 class="text-lg font-semibold text-card-foreground mb-2">
          Data Import
        </h3>
        <p class="text-muted-foreground">
          Einfacher Import historischer KPI-Daten aus CSV, Excel oder API
        </p>
      </div>

      <div class="bg-card border border-border rounded-lg p-6 text-center">
        <div
          class="w-12 h-12 bg-chart-2/10 rounded-lg flex items-center justify-center mx-auto mb-4"
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
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            ></path>
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-card-foreground mb-2">
          Scenario Analysis
        </h3>
        <p class="text-muted-foreground">
          ML-basierte Szenarien für bessere Geschäftsentscheidungen
        </p>
      </div>

      <div class="bg-card border border-border rounded-lg p-6 text-center">
        <div
          class="w-12 h-12 bg-chart-3/10 rounded-lg flex items-center justify-center mx-auto mb-4"
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
              d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
            ></path>
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-card-foreground mb-2">
          Multi-Tenant
        </h3>
        <p class="text-muted-foreground">
          Sichere Datenabgrenzung und Rollen-basierte Zugriffskontrolle
        </p>
      </div>
    </div>
  </div>
{:else}
  <!-- Dashboard for Authenticated Users -->
  <div class="space-y-6">
    <!-- Welcome Header -->
    <div
      class="flex flex-col space-y-2
               sm:flex-row sm:items-center sm:justify-between sm:space-y-0"
    >
      <div>
        <div class="flex items-center gap-3 mb-2">
          <h1 class="text-2xl font-bold text-foreground">
            Willkommen zurück{userInfo ? `, ${userInfo.name}` : ""}
          </h1>
          {#if data?.user}
            <RoleBadge role={data.user.role} />
          {/if}
        </div>
        <p class="text-muted-foreground">
          {#if isSystemRole}
            System-weite Übersicht aller Tenants und Benutzer
          {:else if isTenantAdminRole}
            Tenant-Management und E-Commerce Analytics für {data?.user
              ?.tenant_id || "Ihr Tenant"}
          {:else}
            Hier ist eine Übersicht Ihrer E-Commerce Analytics
          {/if}
        </p>
      </div>
      <div class="text-sm text-muted-foreground text-right">
        <div>
          {new Date().toLocaleDateString("de-DE", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </div>
        {#if data?.user?.tenant_id && !isSystemRole}
          <div class="text-xs opacity-70 mt-1">
            Tenant: {data.user.tenant_id}
          </div>
        {/if}
      </div>
    </div>

    <!-- KPI Cards Grid -->
    <div
      class="grid gap-6
               sm:grid-cols-2
               lg:grid-cols-4"
    >
      {#each kpiData as kpi}
        <KPICard
          title={kpi.title}
          value={kpi.value}
          change={kpi.change || null}
          icon={kpi.icon}
          color={kpi.color}
        />
      {/each}
    </div>

    <!-- Main Dashboard Grid -->
    <div
      class="grid gap-6
               lg:grid-cols-3"
    >
      <!-- Quick Actions -->
      <div class="lg:col-span-1">
        <QuickActions user={data?.user} />
      </div>

      <!-- Recent Activity für non-owners oder SaaS Overview für Owner -->
      <div class="lg:col-span-2">
        {#if isOwnerRole && ownerSaasData}
          <!-- Owner SaaS Overview -->
          <div class="space-y-6">
            <!-- Plan Distribution -->
            {#if ownerSaasData.metrics?.plan_distribution}
              <div class="bg-card border border-border rounded-lg p-6">
                <h3 class="text-lg font-semibold text-foreground mb-4">
                  Plan-Verteilung
                </h3>
                <div class="space-y-3">
                  {#each ownerSaasData.metrics.plan_distribution as plan}
                    {@const percentage =
                      ownerSaasData.metrics.current_metrics.mrr_cents > 0
                        ? (plan.total_mrr_cents /
                            ownerSaasData.metrics.current_metrics.mrr_cents) *
                          100
                        : 0}
                    <div class="flex items-center justify-between">
                      <div class="flex items-center gap-3">
                        <div
                          class="w-4 h-4 rounded {plan.plan_name ===
                          'Enterprise'
                            ? 'bg-purple-500'
                            : plan.plan_name === 'Professional'
                              ? 'bg-blue-500'
                              : 'bg-green-500'}"
                        ></div>
                        <span class="font-medium text-foreground"
                          >{plan.plan_name}</span
                        >
                      </div>
                      <div class="text-right">
                        <div class="font-medium text-foreground">
                          €{(plan.total_mrr_cents / 100).toLocaleString(
                            "de-DE",
                            {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            },
                          )}
                        </div>
                        <div class="text-sm text-muted-foreground">
                          {percentage.toFixed(1)}%
                        </div>
                      </div>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div
                        class="h-2 rounded-full {plan.plan_name === 'Enterprise'
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
            {/if}

            <!-- Revenue Trend Overview -->
            {#if ownerSaasData.revenue?.monthly_trend}
              <div class="bg-card border border-border rounded-lg p-6">
                <h3 class="text-lg font-semibold text-foreground mb-4">
                  Revenue Trend (Letzte 6 Monate)
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
                          >Paying Tenants</th
                        >
                      </tr>
                    </thead>
                    <tbody>
                      {#each ownerSaasData.revenue.monthly_trend.slice(-6) as month}
                        <tr class="border-b border-border hover:bg-muted/50">
                          <td class="py-3 px-4 font-medium text-foreground"
                            >{month.month}</td
                          >
                          <td class="py-3 px-4 text-foreground">
                            €{(month.paid_revenue / 100).toLocaleString(
                              "de-DE",
                              {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2,
                              },
                            )}
                          </td>
                          <td class="py-3 px-4 text-foreground"
                            >{month.paying_tenants}</td
                          >
                        </tr>
                      {/each}
                    </tbody>
                  </table>
                </div>
              </div>
            {/if}
          </div>
        {:else}
          <RecentActivity />
        {/if}
      </div>
    </div>
  </div>
{/if}
