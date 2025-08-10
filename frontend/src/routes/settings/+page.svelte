<script lang="ts">
    import { onMount } from "svelte";
    import RoleGuard from "$lib/components/RoleGuard.svelte";
    import { authStore } from "$lib/stores/auth";

    const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

    let displayName = "";
    let currentPassword = "";
    let newPassword = "";
    let confirmPassword = "";
    let isLoading = false;
    let message = "";
    let messageType = "success";

    $: user = $authStore.user;

    onMount(() => {
        if (user) {
            displayName = user.display_name || "";
        }
    });

    async function updateProfile() {
        if (!displayName.trim()) {
            message = "Display name is required";
            messageType = "error";
            return;
        }

        isLoading = true;
        message = "";

        try {
            const formData = new FormData();
            formData.append("display_name", displayName.trim());

            const res = await fetch(`${API_BASE}/auth/profile`, {
                method: "PUT",
                body: formData,
                credentials: "include",
            });

            if (res.ok) {
                message = "Profile updated successfully";
                messageType = "success";

                // Update the auth store
                if (user) {
                    authStore.set({
                        ...$authStore,
                        user: { ...user, display_name: displayName.trim() },
                    });
                }
            } else {
                const data = await res.json();
                message = data.detail || "Failed to update profile";
                messageType = "error";
            }
        } catch (error) {
            message = "Failed to update profile";
            messageType = "error";
        } finally {
            isLoading = false;
        }
    }

    async function changePassword() {
        if (!currentPassword || !newPassword || !confirmPassword) {
            message = "All password fields are required";
            messageType = "error";
            return;
        }

        if (newPassword !== confirmPassword) {
            message = "New passwords do not match";
            messageType = "error";
            return;
        }

        if (newPassword.length < 6) {
            message = "New password must be at least 6 characters";
            messageType = "error";
            return;
        }

        isLoading = true;
        message = "";

        try {
            const formData = new FormData();
            formData.append("current_password", currentPassword);
            formData.append("new_password", newPassword);

            const res = await fetch(`${API_BASE}/auth/change-password`, {
                method: "PUT",
                body: formData,
                credentials: "include",
            });

            if (res.ok) {
                message = "Password changed successfully";
                messageType = "success";
                currentPassword = "";
                newPassword = "";
                confirmPassword = "";
            } else {
                const data = await res.json();
                message = data.detail || "Failed to change password";
                messageType = "error";
            }
        } catch (error) {
            message = "Failed to change password";
            messageType = "error";
        } finally {
            isLoading = false;
        }
    }
</script>

<RoleGuard requiredRole="tenant_user">
    <div class="max-w-4xl mx-auto p-6">
        <div class="mb-8">
            <h1 class="text-2xl font-bold text-foreground mb-2">
                User Settings
            </h1>
            <p class="text-muted-foreground">
                Manage your account settings and preferences
            </p>
        </div>

        {#if message}
            <div
                class="mb-6 p-4 rounded-lg {messageType === 'success'
                    ? 'bg-green-50 border border-green-200 text-green-800'
                    : 'bg-red-50 border border-red-200 text-red-800'}"
            >
                {message}
            </div>
        {/if}

        <div class="grid gap-8 lg:grid-cols-2">
            <!-- Profile Settings -->
            <div class="bg-card border border-border rounded-lg p-6">
                <h2 class="text-lg font-semibold text-foreground mb-4">
                    Profile Information
                </h2>

                <form
                    on:submit|preventDefault={updateProfile}
                    class="space-y-4"
                >
                    <div>
                        <label
                            for="email"
                            class="block text-sm font-medium text-foreground mb-2"
                        >
                            Email Address
                        </label>
                        <input
                            type="email"
                            id="email"
                            value={user?.email || ""}
                            disabled
                            class="w-full px-3 py-2 border border-border rounded-md bg-muted text-muted-foreground cursor-not-allowed"
                        />
                        <p class="text-xs text-muted-foreground mt-1">
                            Email cannot be changed
                        </p>
                    </div>

                    <div>
                        <label
                            for="display_name"
                            class="block text-sm font-medium text-foreground mb-2"
                        >
                            Display Name
                        </label>
                        <input
                            type="text"
                            id="display_name"
                            bind:value={displayName}
                            class="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                            placeholder="Enter your display name"
                        />
                    </div>

                    <div>
                        <label
                            for="user_role"
                            class="block text-sm font-medium text-foreground mb-2"
                        >
                            Role
                        </label>
                        <div
                            id="user_role"
                            class="px-3 py-2 border border-border rounded-md bg-muted text-muted-foreground"
                        >
                            {user?.role || "Unknown"}
                        </div>
                        <p class="text-xs text-muted-foreground mt-1">
                            Role is managed by administrators
                        </p>
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        class="w-full bg-primary text-primary-foreground py-2 px-4 rounded-md hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
                    >
                        {isLoading ? "Updating..." : "Update Profile"}
                    </button>
                </form>
            </div>

            <!-- Password Change -->
            <div class="bg-card border border-border rounded-lg p-6">
                <h2 class="text-lg font-semibold text-foreground mb-4">
                    Change Password
                </h2>

                <form
                    on:submit|preventDefault={changePassword}
                    class="space-y-4"
                >
                    <div>
                        <label
                            for="current_password"
                            class="block text-sm font-medium text-foreground mb-2"
                        >
                            Current Password
                        </label>
                        <input
                            type="password"
                            id="current_password"
                            bind:value={currentPassword}
                            class="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                            placeholder="Enter current password"
                        />
                    </div>

                    <div>
                        <label
                            for="new_password"
                            class="block text-sm font-medium text-foreground mb-2"
                        >
                            New Password
                        </label>
                        <input
                            type="password"
                            id="new_password"
                            bind:value={newPassword}
                            class="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                            placeholder="Enter new password"
                        />
                    </div>

                    <div>
                        <label
                            for="confirm_password"
                            class="block text-sm font-medium text-foreground mb-2"
                        >
                            Confirm New Password
                        </label>
                        <input
                            type="password"
                            id="confirm_password"
                            bind:value={confirmPassword}
                            class="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                            placeholder="Confirm new password"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        class="w-full bg-primary text-primary-foreground py-2 px-4 rounded-md hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
                    >
                        {isLoading ? "Changing..." : "Change Password"}
                    </button>
                </form>
            </div>
        </div>

        <!-- Account Information -->
        <div class="mt-8 bg-card border border-border rounded-lg p-6">
            <h2 class="text-lg font-semibold text-foreground mb-4">
                Account Information
            </h2>

            <div class="grid gap-4 md:grid-cols-2">
                <div>
                    <div class="text-sm font-medium text-foreground mb-1">
                        Tenant
                    </div>
                    <div class="text-sm text-muted-foreground">
                        {user?.tenant_id || "Not assigned"}
                    </div>
                </div>

                <div>
                    <div class="text-sm font-medium text-foreground mb-1">
                        User ID
                    </div>
                    <div class="text-sm text-muted-foreground">
                        {user?.user_id || "Unknown"}
                    </div>
                </div>
            </div>
        </div>
    </div>
</RoleGuard>
