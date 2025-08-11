<script lang="ts">
    import { page } from "$app/stores";
    import { onMount } from "svelte";
    import {
        hasMinRole,
        isSystemManager,
        isTenantAdmin,
        isOwner,
    } from "$lib/stores/auth";
    import RoleBadge from "./RoleBadge.svelte";
    import type { User } from "$lib/types";

    export let user: User | null = null;

    let currentPath = "";

    onMount(() => {
        return page.subscribe((p) => {
            currentPath = p.url.pathname;
        });
    });

    // Dynamic navigation based on user role
    $: navigationItems = [
        // Dashboard immer zuerst
        {
            title: "Dashboard",
            href: "/",
            icon: "M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z",
            showFor: "all",
        },

        // Owner Management Section (höchste Priorität)
        {
            title: "Tenant Management",
            href: "/owner/tenants",
            icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4",
            requiresAuth: true,
            minRole: "owner",
            maxRole: "owner",
        },
        {
            title: "User Management",
            href: "/owner/users",
            icon: "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z",
            requiresAuth: true,
            minRole: "owner",
            maxRole: "owner",
        },
        {
            title: "Revenue Analytics",
            href: "/owner/revenue",
            icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1",
            requiresAuth: true,
            minRole: "owner",
            maxRole: "owner",
        },
        {
            title: "Audit Log",
            href: "/owner/audit",
            icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
            requiresAuth: true,
            minRole: "owner",
            maxRole: "owner",
        },

        // Tenant Admin functionality
        {
            title: "Tenant Management",
            href: "/management",
            icon: "M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z",
            requiresAuth: true,
            minRole: "tenant_admin",
            hideForSystemRoles: true,
        },

        // Operative Funktionen (für alle außer Owner)
        {
            title: "Imports",
            href: "/imports",
            icon: "M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10",
            requiresAuth: true,
            minRole: "tenant_user",
            maxRole: "system_manager", // Nicht für Owner
        },
        {
            title: "Szenarien",
            href: "/scenarios",
            icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
            requiresAuth: true,
            minRole: "tenant_user",
            maxRole: "system_manager", // Nicht für Owner
        },

        // Utility Funktionen (unten)
        {
            title: "Activity",
            href: "/activity",
            icon: "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z",
            requiresAuth: true,
            minRole: "tenant_user",
        },
        {
            title: "Settings",
            href: "/settings",
            icon: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z",
            requiresAuth: true,
            minRole: "tenant_user",
        },

        // Public pages (only show when not authenticated)
        {
            title: "Pricing",
            href: "/pricing",
            icon: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1",
            showFor: "unauthenticated",
        },
    ];

    function isActive(href: string): boolean {
        return currentPath === href;
    }

    function shouldShowItem(item: any): boolean {
        // Show for all users if explicitly marked
        if (item.showFor === "all") return true;

        // Show only for unauthenticated users
        if (item.showFor === "unauthenticated") return !user;

        // Require authentication
        if (item.requiresAuth && !user) return false;

        // Check minimum role requirement
        if (item.minRole && user && !hasMinRole(user.role, item.minRole))
            return false;

        // Check maximum role requirement (exclude higher roles)
        if (
            item.maxRole &&
            user &&
            hasMinRole(user.role, "owner") &&
            item.maxRole !== "owner"
        )
            return false;

        // Hide tenant admin features for system-level roles
        if (item.hideForSystemRoles && user && isSystemManager(user.role))
            return false;

        return true;
    }
</script>

<aside
    class="bg-sidebar border-r border-sidebar-border h-full flex flex-col w-80 p-0
             lg:flex
             md:w-72
             sm:w-64"
>
    <!-- Sidebar Header -->
    <div class="p-6 border-b border-sidebar-border">
        <h2 class="text-sidebar-foreground font-bold text-xl tracking-tight">
            FutureWise
        </h2>
        <p class="text-sidebar-foreground/70 text-sm mt-1">
            E-Commerce Analytics
        </p>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 p-4 space-y-2">
        {#each navigationItems as item}
            {#if shouldShowItem(item)}
                <a
                    href={item.href}
                    class="flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors
                 {isActive(item.href)
                        ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                        : 'text-sidebar-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground'}"
                >
                    <svg
                        class="w-5 h-5 flex-shrink-0"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d={item.icon}
                        >
                        </path>
                    </svg>
                    <span>{item.title}</span>
                </a>
            {/if}
        {/each}
    </nav>

    <!-- User Info at Bottom -->
    {#if user}
        <div class="p-4 border-t border-sidebar-border">
            <div class="flex items-center space-x-3 px-3 py-2">
                <div
                    class="w-8 h-8 bg-sidebar-primary rounded-full flex items-center justify-center"
                >
                    <span
                        class="text-sidebar-primary-foreground text-sm font-medium"
                    >
                        {user.email?.charAt(0).toUpperCase() || "U"}
                    </span>
                </div>
                <div class="flex-1 min-w-0">
                    <p
                        class="text-sidebar-foreground text-sm font-medium truncate"
                    >
                        {user.email || "User"}
                    </p>
                    <div class="flex items-center gap-2 mt-1">
                        <RoleBadge role={user.role || "viewer"} />
                        {#if user.tenant_id && !isSystemManager(user.role)}
                            <span
                                class="text-sidebar-foreground/70 text-xs truncate"
                            >
                                {user.tenant_id}
                            </span>
                        {/if}
                    </div>
                </div>
            </div>
        </div>
    {/if}
</aside>
