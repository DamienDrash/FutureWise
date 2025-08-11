<script lang="ts">
    import {
        isSystemManager,
        isTenantAdmin,
        hasMinRole,
    } from "$lib/stores/auth";

    export let user = null;

    // Get API base URL from environment
    const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

    // Dynamic actions based on user role
    $: actions = getActionsForUser(user);

    function getActionsForUser(user: any) {
        if (!user) {
            return [
                {
                    title: "Pricing ansehen",
                    description: "Preispläne und Features",
                    href: "/pricing",
                    icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1",
                    color: "bg-chart-1/10 text-chart-1",
                },
                {
                    title: "Registrieren",
                    description: "Kostenloses Konto erstellen",
                    href: "/register",
                    icon: "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z",
                    color: "bg-chart-2/10 text-chart-2",
                },
            ];
        }

        // System Manager actions
        if (isSystemManager(user.role)) {
            return [
                {
                    title: "System Management",
                    description: "System-weite Verwaltung",
                    href: "/system",
                    icon: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z",
                    color: "bg-chart-1/10 text-chart-1",
                },
                {
                    title: "Alle Tenants",
                    description: "Tenant-Übersicht verwalten",
                    href: "/tenants",
                    icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4",
                    color: "bg-chart-2/10 text-chart-2",
                },
                {
                    title: "System Reports",
                    description: "Umfassende Berichte generieren",
                    href: "/reports",
                    icon: "M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
                    color: "bg-chart-3/10 text-chart-3",
                },
                {
                    title: "API Documentation",
                    description: "System-API Dokumentation",
                    href: `${API_BASE}/docs`,
                    icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
                    color: "bg-chart-4/10 text-chart-4",
                    external: true,
                },
            ];
        }

        // Tenant Admin actions
        if (isTenantAdmin(user.role)) {
            return [
                {
                    title: "Import Daten",
                    description: "Neue KPI-Daten hochladen",
                    href: "/imports",
                    icon: "M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10",
                    color: "bg-chart-1/10 text-chart-1",
                },
                {
                    title: "Neues Szenario",
                    description: "Scenario-Analyse erstellen",
                    href: "/scenarios",
                    icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
                    color: "bg-chart-2/10 text-chart-2",
                },
                {
                    title: "Tenant Management",
                    description: "Benutzer und Rollen verwalten",
                    href: "/management",
                    icon: "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z",
                    color: "bg-chart-3/10 text-chart-3",
                },
                {
                    title: "API Integration",
                    description: "Tenant-API nutzen",
                    href: `${API_BASE}/docs`,
                    icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
                    color: "bg-chart-4/10 text-chart-4",
                    external: true,
                },
            ];
        }

        // Regular tenant user actions
        return [
            {
                title: "Import Daten",
                description: "Neue KPI-Daten hochladen",
                href: "/imports",
                icon: "M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10",
                color: "bg-chart-1/10 text-chart-1",
            },
            {
                title: "Neues Szenario",
                description: "Scenario-Analyse erstellen",
                href: "/scenarios",
                icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
                color: "bg-chart-2/10 text-chart-2",
            },
            {
                title: "Pricing Plans",
                description: "Upgrade-Optionen ansehen",
                href: "/pricing",
                icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1",
                color: "bg-chart-3/10 text-chart-3",
            },
            {
                title: "API Documentation",
                description: "Integration & Entwicklung",
                href: "http://localhost:8000/docs",
                icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
                color: "bg-chart-4/10 text-chart-4",
                external: true,
            },
        ];
    }
</script>

<div class="bg-card border border-border rounded-lg p-6 shadow-sm">
    <h3 class="text-lg font-semibold text-card-foreground mb-4">
        Quick Actions
    </h3>

    <div
        class="grid gap-4
             sm:grid-cols-2
             lg:grid-cols-1
             xl:grid-cols-2"
    >
        {#each actions as action}
            <a
                href={action.href}
                target={action.external ? "_blank" : undefined}
                rel={action.external ? "noopener noreferrer" : undefined}
                class="flex items-start space-x-3 p-4 rounded-lg border border-border
                 hover:bg-muted/50
                 transition-colors group"
            >
                <div
                    class="flex-shrink-0 w-10 h-10 rounded-lg {action.color} flex items-center justify-center"
                >
                    <svg
                        class="w-5 h-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d={action.icon}
                        ></path>
                    </svg>
                </div>
                <div class="flex-1 min-w-0">
                    <p
                        class="text-sm font-medium text-card-foreground group-hover:text-primary"
                    >
                        {action.title}
                    </p>
                    <p class="text-xs text-muted-foreground mt-1">
                        {action.description}
                    </p>
                </div>
                {#if action.external}
                    <svg
                        class="w-4 h-4 text-muted-foreground"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                        ></path>
                    </svg>
                {/if}
            </a>
        {/each}
    </div>
</div>
