<script lang="ts">
  import { onMount } from "svelte";
  import KPICard from "$lib/components/KPICard.svelte";
  import QuickActions from "$lib/components/QuickActions.svelte";
  import RecentActivity from "$lib/components/RecentActivity.svelte";
  import RoleGuard from "$lib/components/RoleGuard.svelte";
  import RoleBadge from "$lib/components/RoleBadge.svelte";
  import {
    isSystemManager,
    isTenantAdmin,
    getUserDisplayInfo,
  } from "$lib/stores/auth";

  export let data;

  let token = "";

  onMount(() => {
    if (typeof localStorage !== "undefined") {
      token = localStorage.getItem("fw_token") || "";
    }
  });

  $: userInfo = getUserDisplayInfo(data?.user);
  $: isSystemRole = data?.user && isSystemManager(data.user.role);
  $: isTenantAdminRole = data?.user && isTenantAdmin(data.user.role);

  // Dynamic KPI data based on user role
  $: kpiData = isSystemRole
    ? [
        {
          title: "Total Tenants",
          value: "12",
          change: 20.0,
          icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4",
          color: "chart-1",
        },
        {
          title: "System Users",
          value: "847",
          change: 12.3,
          icon: "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z",
          color: "chart-2",
        },
        {
          title: "System Revenue",
          value: "€124.8k",
          change: 18.5,
          icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1",
          color: "chart-3",
        },
        {
          title: "Active Scenarios",
          value: "234",
          change: 8.7,
          icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
          color: "chart-4",
        },
      ]
    : [
        {
          title: "Total Revenue",
          value: "€2.4M",
          change: 12.5,
          icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1",
          color: "chart-1",
        },
        {
          title: "Active Scenarios",
          value: "24",
          change: 8.2,
          icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
          color: "chart-2",
        },
        {
          title: "Data Points",
          value: "45.2k",
          change: 15.8,
          icon: "M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
          color: "chart-3",
        },
        {
          title: "Conversion Rate",
          value: "3.24%",
          change: -2.1,
          icon: "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6",
          color: "chart-4",
        },
      ];
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

      <!-- Recent Activity -->
      <div class="lg:col-span-2">
        <RecentActivity />
      </div>
    </div>

    <!-- Charts Section Placeholder -->
    <div class="bg-card border border-border rounded-lg p-6">
      <h3 class="text-lg font-semibold text-card-foreground mb-4">
        Analytics Overview
      </h3>
      <div class="h-64 bg-muted rounded-lg flex items-center justify-center">
        <p class="text-muted-foreground">Charts werden hier implementiert</p>
      </div>
    </div>
  </div>
{/if}
