<script lang="ts">
    import { authStore, hasMinRole } from "$lib/stores/auth";
    import type { User, UserRole } from "$lib/types";

    export let requiredRole: UserRole = "viewer";
    export let fallback: string = "";
    export let user: User | null = null;

    $: userRole =
        user?.role || ($authStore as any)?.user?.role || ("viewer" as UserRole);
    $: hasPermission = hasMinRole(userRole, requiredRole);
</script>

{#if hasPermission}
    <slot />
{:else}
    <div
        class="text-muted-foreground text-sm p-4 text-center bg-muted/30 rounded-lg"
    >
        {fallback ||
            `Zugriff verweigert: ${requiredRole} Berechtigung erforderlich`}
    </div>
{/if}
