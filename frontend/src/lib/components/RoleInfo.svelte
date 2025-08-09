<script lang="ts">
    import { ROLE_DESCRIPTIONS } from "$lib/demo-users";
    import RoleBadge from "./RoleBadge.svelte";
    import type { User, UserRole } from "$lib/types";
    import { roleLabels } from "$lib/types";

    export let user: User | null = null;
    export let showDescription = true;
</script>

{#if user}
    <div class="bg-muted/30 border border-border rounded-lg p-4">
        <div class="flex items-center gap-3 mb-2">
            <span class="text-sm font-medium text-foreground"
                >Aktuelle Rolle:</span
            >
            <RoleBadge role={user.role} />
        </div>

        {#if showDescription}
            <p class="text-xs text-muted-foreground">
                {roleLabels[user.role as UserRole] || user.role}
            </p>
        {/if}
    </div>
{/if}
