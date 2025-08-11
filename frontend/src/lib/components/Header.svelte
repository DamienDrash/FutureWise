<script lang="ts">
    import { onMount } from "svelte";
    import type { User } from "$lib/types";

    export let user: User | null = null;
    export let onLogout = () => {};
    export let onToggleSidebar = () => {};

    let darkMode = false;

    onMount(() => {
        // Check for saved theme preference or default to light mode
        const saved = localStorage.getItem("theme");
        if (saved === "dark") {
            darkMode = true;
            document.documentElement.classList.add("dark");
        } else {
            darkMode = false;
            document.documentElement.classList.remove("dark");
        }
    });

    function toggleDarkMode() {
        darkMode = !darkMode;
        if (darkMode) {
            document.documentElement.classList.add("dark");
            localStorage.setItem("theme", "dark");
        } else {
            document.documentElement.classList.remove("dark");
            localStorage.setItem("theme", "light");
        }
    }
</script>

<header
    class="bg-background border-b border-border h-16 flex items-center justify-between px-4
               lg:px-6"
>
    <!-- Mobile Menu Button -->
    <button
        class="lg:hidden p-2 rounded-md hover:bg-muted"
        on:click={onToggleSidebar}
        aria-label="Toggle navigation menu"
    >
        <svg
            class="w-6 h-6 text-foreground"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
        >
            <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
            >
            </path>
        </svg>
    </button>

    <!-- Page Title or Search -->
    <div class="flex-1 lg:ml-0 ml-4">
        <h1 class="text-lg font-semibold text-foreground">Dashboard</h1>
    </div>

    <!-- Header Actions -->
    <div class="flex items-center space-x-2">
        <!-- Dark Mode Toggle -->
        <button
            class="p-2 rounded-md hover:bg-muted transition-colors"
            on:click={toggleDarkMode}
            aria-label="Toggle dark mode"
        >
            {#if darkMode}
                <!-- Sun Icon -->
                <svg
                    class="w-5 h-5 text-foreground"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
                    >
                    </path>
                </svg>
            {:else}
                <!-- Moon Icon -->
                <svg
                    class="w-5 h-5 text-foreground"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
                    >
                    </path>
                </svg>
            {/if}
        </button>

        {#if user}
            <!-- User Menu -->
            <div class="flex items-center space-x-3">
                <span class="text-sm text-muted-foreground hidden sm:block">
                    {user.email || user.display_name || "User"}
                </span>
                <button
                    class="px-4 py-2 text-sm font-medium text-foreground bg-background border border-border rounded-md
                 hover:bg-muted
                 focus:outline-none focus:ring-2 focus:ring-ring"
                    on:click={onLogout}
                >
                    Logout
                </button>
            </div>
        {:else}
            <!-- Auth Buttons -->
            <div class="flex items-center space-x-2">
                <a
                    href="/login"
                    class="px-4 py-2 text-sm font-medium text-foreground bg-background border border-border rounded-md
                 hover:bg-muted
                 focus:outline-none focus:ring-2 focus:ring-ring"
                >
                    Login
                </a>
                <a
                    href="/register"
                    class="px-4 py-2 text-sm font-medium text-primary-foreground bg-primary rounded-md
                 hover:bg-primary/90
                 focus:outline-none focus:ring-2 focus:ring-ring"
                >
                    Register
                </a>
            </div>
        {/if}
    </div>
</header>
