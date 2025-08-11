<script lang="ts">
    import type { ChartColor } from "$lib/types";

    export let title: string;
    export let value: string | number;
    export let change: number | null = null;
    export let icon: string;
    export let color: ChartColor = "primary";

    // Map color prop to CSS classes
    const colorClasses: Record<ChartColor, string> = {
        primary: "bg-primary/10 text-primary",
        secondary: "bg-secondary/10 text-secondary",
        "chart-1": "bg-chart-1/10 text-chart-1",
        "chart-2": "bg-chart-2/10 text-chart-2",
        "chart-3": "bg-chart-3/10 text-chart-3",
        "chart-4": "bg-chart-4/10 text-chart-4",
        "chart-5": "bg-chart-5/10 text-chart-5",
    };

    $: bgClass = colorClasses[color]?.split(" ")[0] || "bg-primary/10";
    $: textClass = colorClasses[color]?.split(" ")[1] || "text-primary";
</script>

<div
    class="bg-card border border-border rounded-lg p-6 shadow-sm
           hover:shadow-md
           transition-shadow"
>
    <div class="flex items-center justify-between">
        <div class="flex-1">
            <p class="text-muted-foreground text-sm font-medium">
                {title}
            </p>
            <p class="text-2xl font-bold text-card-foreground mt-2">
                {value}
            </p>
            {#if change !== null}
                <div class="flex items-center mt-2">
                    {#if change > 0}
                        <svg
                            class="w-4 h-4 text-green-500 mr-1"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                            ></path>
                        </svg>
                        <span class="text-green-500 text-sm font-medium"
                            >+{change}%</span
                        >
                    {:else if change < 0}
                        <svg
                            class="w-4 h-4 text-red-500 mr-1"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="2"
                                d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"
                            ></path>
                        </svg>
                        <span class="text-red-500 text-sm font-medium"
                            >{change}%</span
                        >
                    {:else}
                        <span class="text-muted-foreground text-sm">0%</span>
                    {/if}
                </div>
            {/if}
        </div>
        <div class="ml-4">
            <div
                class="w-12 h-12 {bgClass} rounded-lg flex items-center justify-center"
            >
                <svg
                    class="w-6 h-6 {textClass}"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d={icon}
                    ></path>
                </svg>
            </div>
        </div>
    </div>
</div>
