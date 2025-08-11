<script lang="ts">
    export let role: string;

    const roleStyles = {
        owner: "bg-destructive text-destructive-foreground",
        system_manager: "bg-chart-4 text-white",
        tenant_admin: "bg-primary text-primary-foreground",
        tenant_user: "bg-secondary text-secondary-foreground",
        manager: "bg-primary text-primary-foreground", // Legacy
        analyst: "bg-chart-2 text-white", // Legacy
        viewer: "bg-muted text-muted-foreground", // Legacy
    };

    const roleLabels = {
        owner: "Owner",
        system_manager: "System Manager",
        tenant_admin: "Tenant Admin",
        tenant_user: "User",
        manager: "Manager",
        analyst: "Analyst",
        viewer: "Viewer",
    };

    $: styleClass =
        roleStyles[role as keyof typeof roleStyles] ||
        "bg-muted text-muted-foreground";
    $: label = roleLabels[role as keyof typeof roleLabels] || role;
</script>

<span class="px-2 py-1 rounded-full text-xs font-medium {styleClass}">
    {label}
</span>
