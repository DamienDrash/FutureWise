<script lang="ts">
    import { onMount } from "svelte";
    import { authStore } from "$lib/stores/auth";
    import RoleGuard from "$lib/components/RoleGuard.svelte";
    import type { User } from "$lib/types";

    const API = import.meta.env.VITE_API_BASE || "http://localhost:8000";

    let users: any[] = [];
    let loading = true;
    let error = "";
    let searchTerm = "";

    // User management state
    let showCreateUser = false;
    let showEditUser = false;
    let editingUser: any = null;
    let newUser = {
        email: "",
        display_name: "",
        password: "",
        tenant_ids: [],
        roles: [],
    };

    $: user = $authStore?.user as User | null;
    $: filteredUsers = users.filter(
        (user) =>
            user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (user.display_name &&
                user.display_name
                    .toLowerCase()
                    .includes(searchTerm.toLowerCase())) ||
            user.tenant_ids.some((id: string) =>
                id.toLowerCase().includes(searchTerm.toLowerCase()),
            ),
    );

    onMount(async () => {
        await loadUsers();
    });

    async function loadUsers() {
        loading = true;
        error = "";

        try {
            const res = await fetch(`${API}/owner/users`, {
                credentials: "include",
            });

            if (res.ok) {
                const data = await res.json();
                users = data.users;
            } else {
                error = "Failed to load users";
            }
        } catch (err) {
            error = "Failed to load users: " + err;
            console.error("Users error:", err);
        } finally {
            loading = false;
        }
    }

    async function createUser() {
        if (!newUser.email || !newUser.password) {
            alert("Email und Passwort sind erforderlich");
            return;
        }

        try {
            const res = await fetch(`${API}/owner/users`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify(newUser),
            });

            if (res.ok) {
                newUser = {
                    email: "",
                    display_name: "",
                    password: "",
                    tenant_ids: [],
                    roles: [],
                };
                showCreateUser = false;
                await loadUsers();
            } else {
                const errorData = await res.json();
                alert("Fehler: " + errorData.detail);
            }
        } catch (err) {
            alert("Fehler beim Erstellen: " + err);
        }
    }

    async function updateUser() {
        if (!editingUser || !editingUser.email) {
            alert("Ungültige User-Daten");
            return;
        }

        try {
            const res = await fetch(
                `${API}/owner/users/${editingUser.user_id}`,
                {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    credentials: "include",
                    body: JSON.stringify(editingUser),
                },
            );

            if (res.ok) {
                editingUser = null;
                showEditUser = false;
                await loadUsers();
            } else {
                const errorData = await res.json();
                alert("Fehler: " + errorData.detail);
            }
        } catch (err) {
            alert("Fehler beim Aktualisieren: " + err);
        }
    }

    async function deleteUser(userId: number, email: string) {
        if (
            !confirm(
                `User ${email} wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.`,
            )
        ) {
            return;
        }

        try {
            const res = await fetch(`${API}/owner/users/${userId}`, {
                method: "DELETE",
                credentials: "include",
            });

            if (res.ok) {
                await loadUsers();
            } else {
                const errorData = await res.json();
                alert("Fehler beim Löschen: " + errorData.detail);
            }
        } catch (err) {
            alert("Fehler beim Löschen: " + err);
        }
    }

    function editUser(user: any) {
        editingUser = { ...user };
        showEditUser = true;
    }

    function formatDate(dateStr: string): string {
        return new Date(dateStr).toLocaleDateString("de-DE");
    }

    function getRoleBadgeColor(role: string): string {
        switch (role) {
            case "owner":
                return "bg-purple-100 text-purple-800";
            case "system_manager":
                return "bg-blue-100 text-blue-800";
            case "tenant_admin":
                return "bg-green-100 text-green-800";
            case "manager":
                return "bg-yellow-100 text-yellow-800";
            case "tenant_user":
                return "bg-gray-100 text-gray-800";
            case "analyst":
                return "bg-indigo-100 text-indigo-800";
            case "viewer":
                return "bg-slate-100 text-slate-800";
            default:
                return "bg-gray-100 text-gray-800";
        }
    }

    function formatRoleName(role: string): string {
        const roleNames: { [key: string]: string } = {
            owner: "Owner",
            system_manager: "System Manager",
            tenant_admin: "Tenant Admin",
            manager: "Manager",
            tenant_user: "Tenant User",
            analyst: "Analyst",
            viewer: "Viewer",
        };
        return roleNames[role] || role;
    }

    function getActivityStatus(
        lastLogin: string | null,
        loginCount: number,
    ): string {
        if (!lastLogin) return "Nie eingeloggt";

        const lastLoginDate = new Date(lastLogin);
        const daysSinceLastLogin = Math.floor(
            (Date.now() - lastLoginDate.getTime()) / (1000 * 60 * 60 * 24),
        );

        if (daysSinceLastLogin === 0) return "Heute aktiv";
        if (daysSinceLastLogin === 1) return "Gestern aktiv";
        if (daysSinceLastLogin <= 7)
            return `Vor ${daysSinceLastLogin} Tagen aktiv`;
        if (daysSinceLastLogin <= 30) return "In letzten 30 Tagen aktiv";
        return "Längere Zeit inaktiv";
    }

    function getActivityStatusColor(lastLogin: string | null): string {
        if (!lastLogin) return "bg-gray-100 text-gray-800";

        const daysSinceLastLogin = Math.floor(
            (Date.now() - new Date(lastLogin).getTime()) /
                (1000 * 60 * 60 * 24),
        );

        if (daysSinceLastLogin <= 1) return "bg-green-100 text-green-800";
        if (daysSinceLastLogin <= 7) return "bg-yellow-100 text-yellow-800";
        if (daysSinceLastLogin <= 30) return "bg-orange-100 text-orange-800";
        return "bg-red-100 text-red-800";
    }
</script>

<RoleGuard minRole="owner">
    <div class="space-y-6">
        <!-- Header -->
        <div class="border-b border-border pb-6">
            <h1 class="text-3xl font-bold text-foreground">User Management</h1>
            <p class="text-muted-foreground mt-2">
                Übersicht aller Users, Rollen und Aktivitäten across all Tenants
            </p>
        </div>

        {#if loading}
            <div class="flex items-center justify-center h-64">
                <div class="text-muted-foreground">Lade Users...</div>
            </div>
        {:else if error}
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <h3 class="text-red-800 font-medium">Fehler beim Laden</h3>
                <p class="text-red-600 text-sm mt-1">{error}</p>
            </div>
        {:else}
            <!-- Stats Cards -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div class="bg-card border border-border rounded-lg p-6">
                    <div class="flex items-center justify-between">
                        <div>
                            <p
                                class="text-sm font-medium text-muted-foreground"
                            >
                                Total Users
                            </p>
                            <p class="text-2xl font-bold text-foreground">
                                {users.length}
                            </p>
                        </div>
                        <div
                            class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center"
                        >
                            <svg
                                class="w-4 h-4 text-blue-600"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                            >
                                <path
                                    d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z"
                                />
                            </svg>
                        </div>
                    </div>
                </div>

                <div class="bg-card border border-border rounded-lg p-6">
                    <div class="flex items-center justify-between">
                        <div>
                            <p
                                class="text-sm font-medium text-muted-foreground"
                            >
                                Active (30d)
                            </p>
                            <p class="text-2xl font-bold text-foreground">
                                {users.filter((u) => u.login_count_30d > 0)
                                    .length}
                            </p>
                        </div>
                        <div
                            class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center"
                        >
                            <svg
                                class="w-4 h-4 text-green-600"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                            >
                                <path
                                    fill-rule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                    clip-rule="evenodd"
                                />
                            </svg>
                        </div>
                    </div>
                </div>

                <div class="bg-card border border-border rounded-lg p-6">
                    <div class="flex items-center justify-between">
                        <div>
                            <p
                                class="text-sm font-medium text-muted-foreground"
                            >
                                Multi-Tenant
                            </p>
                            <p class="text-2xl font-bold text-foreground">
                                {users.filter((u) => u.tenant_count > 1).length}
                            </p>
                        </div>
                        <div
                            class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center"
                        >
                            <svg
                                class="w-4 h-4 text-purple-600"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                            >
                                <path
                                    d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM9 7a1 1 0 012 0v1a1 1 0 11-2 0V7zM13 15.5a4 4 0 01-8 0v-1a2 2 0 012-2h4a2 2 0 012 2v1z"
                                />
                            </svg>
                        </div>
                    </div>
                </div>

                <div class="bg-card border border-border rounded-lg p-6">
                    <div class="flex items-center justify-between">
                        <div>
                            <p
                                class="text-sm font-medium text-muted-foreground"
                            >
                                Never Logged In
                            </p>
                            <p class="text-2xl font-bold text-foreground">
                                {users.filter((u) => !u.last_login).length}
                            </p>
                        </div>
                        <div
                            class="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center"
                        >
                            <svg
                                class="w-4 h-4 text-red-600"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                            >
                                <path
                                    fill-rule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                                    clip-rule="evenodd"
                                />
                            </svg>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Search and Actions -->
            <div class="flex justify-between items-center">
                <div class="flex-1 max-w-md">
                    <input
                        type="text"
                        placeholder="Search users by email, name, or tenant..."
                        bind:value={searchTerm}
                        class="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground"
                    />
                </div>
                <div class="flex items-center gap-4">
                    <div class="text-sm text-muted-foreground">
                        {filteredUsers.length} of {users.length} users
                    </div>
                    <button
                        on:click={() => (showCreateUser = true)}
                        class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors"
                    >
                        Neuen User erstellen
                    </button>
                </div>
            </div>

            <!-- Create User Form -->
            {#if showCreateUser}
                <div class="bg-muted border border-border rounded-lg p-6">
                    <h3 class="font-medium text-foreground mb-4">Neuer User</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label
                                for="user_email"
                                class="block text-sm font-medium text-foreground mb-1"
                            >
                                Email *
                            </label>
                            <input
                                id="user_email"
                                type="email"
                                bind:value={newUser.email}
                                placeholder="user@example.com"
                                class="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground"
                            />
                        </div>
                        <div>
                            <label
                                for="user_display_name"
                                class="block text-sm font-medium text-foreground mb-1"
                            >
                                Display Name
                            </label>
                            <input
                                id="user_display_name"
                                bind:value={newUser.display_name}
                                placeholder="Max Mustermann"
                                class="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground"
                            />
                        </div>
                        <div>
                            <label
                                for="user_password"
                                class="block text-sm font-medium text-foreground mb-1"
                            >
                                Passwort *
                            </label>
                            <input
                                id="user_password"
                                type="password"
                                bind:value={newUser.password}
                                placeholder="••••••••"
                                class="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground"
                            />
                        </div>
                    </div>
                    <div class="flex gap-2 mt-4">
                        <button
                            on:click={createUser}
                            class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90"
                        >
                            Erstellen
                        </button>
                        <button
                            on:click={() => (showCreateUser = false)}
                            class="bg-secondary text-secondary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-secondary/90"
                        >
                            Abbrechen
                        </button>
                    </div>
                </div>
            {/if}

            <!-- Edit User Form -->
            {#if showEditUser && editingUser}
                <div class="bg-muted border border-border rounded-lg p-6">
                    <h3 class="font-medium text-foreground mb-4">
                        User bearbeiten
                    </h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label
                                for="edit_user_email"
                                class="block text-sm font-medium text-foreground mb-1"
                            >
                                Email
                            </label>
                            <input
                                id="edit_user_email"
                                type="email"
                                bind:value={editingUser.email}
                                class="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground"
                            />
                        </div>
                        <div>
                            <label
                                for="edit_user_display_name"
                                class="block text-sm font-medium text-foreground mb-1"
                            >
                                Display Name
                            </label>
                            <input
                                id="edit_user_display_name"
                                bind:value={editingUser.display_name}
                                class="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground"
                            />
                        </div>
                    </div>
                    <div class="flex gap-2 mt-4">
                        <button
                            on:click={updateUser}
                            class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-primary/90"
                        >
                            Speichern
                        </button>
                        <button
                            on:click={() => {
                                showEditUser = false;
                                editingUser = null;
                            }}
                            class="bg-secondary text-secondary-foreground px-4 py-2 rounded-md text-sm font-medium hover:bg-secondary/90"
                        >
                            Abbrechen
                        </button>
                    </div>
                </div>
            {/if}

            <!-- Users Table -->
            <div class="bg-card border border-border rounded-lg p-6">
                <div class="overflow-x-auto">
                    <table class="w-full border-collapse">
                        <thead>
                            <tr class="border-b border-border">
                                <th
                                    class="text-left py-3 px-4 font-medium text-foreground"
                                >
                                    User
                                </th>
                                <th
                                    class="text-left py-3 px-4 font-medium text-foreground"
                                >
                                    Tenants & Rollen
                                </th>
                                <th
                                    class="text-left py-3 px-4 font-medium text-foreground"
                                >
                                    Registriert
                                </th>
                                <th
                                    class="text-left py-3 px-4 font-medium text-foreground"
                                >
                                    Letzter Login
                                </th>
                                <th
                                    class="text-left py-3 px-4 font-medium text-foreground"
                                >
                                    Aktivität (30d)
                                </th>
                                <th
                                    class="text-left py-3 px-4 font-medium text-foreground"
                                >
                                    Status
                                </th>
                                <th
                                    class="text-left py-3 px-4 font-medium text-foreground"
                                >
                                    Aktionen
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each filteredUsers as user}
                                <tr
                                    class="border-b border-border hover:bg-muted/50"
                                >
                                    <td class="py-3 px-4">
                                        <div>
                                            <div
                                                class="font-medium text-foreground"
                                            >
                                                {user.display_name ||
                                                    user.email.split("@")[0]}
                                            </div>
                                            <div
                                                class="text-sm text-muted-foreground"
                                            >
                                                {user.email}
                                            </div>
                                        </div>
                                    </td>
                                    <td class="py-3 px-4">
                                        <div class="space-y-1">
                                            {#each user.tenant_ids as tenantId, i}
                                                <div
                                                    class="flex items-center gap-2 text-sm"
                                                >
                                                    <span
                                                        class="text-muted-foreground"
                                                        >{tenantId}</span
                                                    >
                                                    <span
                                                        class="text-xs {getRoleBadgeColor(
                                                            user.roles[i] ||
                                                                'viewer',
                                                        )} px-2 py-1 rounded"
                                                    >
                                                        {formatRoleName(
                                                            user.roles[i] ||
                                                                "viewer",
                                                        )}
                                                    </span>
                                                </div>
                                            {/each}
                                        </div>
                                    </td>
                                    <td
                                        class="py-3 px-4 text-sm text-muted-foreground"
                                    >
                                        {user.created_at
                                            ? formatDate(user.created_at)
                                            : "-"}
                                    </td>
                                    <td
                                        class="py-3 px-4 text-sm text-muted-foreground"
                                    >
                                        {user.last_login
                                            ? formatDate(user.last_login)
                                            : "Nie"}
                                    </td>
                                    <td
                                        class="py-3 px-4 text-sm text-muted-foreground"
                                    >
                                        {user.login_count_30d} Logins
                                    </td>
                                    <td class="py-3 px-4">
                                        <span
                                            class="text-xs {getActivityStatusColor(
                                                user.last_login,
                                            )} px-2 py-1 rounded"
                                        >
                                            {getActivityStatus(
                                                user.last_login,
                                                user.login_count_30d,
                                            )}
                                        </span>
                                    </td>
                                    <td class="py-3 px-4">
                                        <div class="flex gap-2">
                                            <button
                                                on:click={() => editUser(user)}
                                                class="text-blue-600 hover:text-blue-800 text-sm font-medium"
                                            >
                                                Bearbeiten
                                            </button>
                                            <button
                                                on:click={() =>
                                                    deleteUser(
                                                        user.user_id,
                                                        user.email,
                                                    )}
                                                class="text-red-600 hover:text-red-800 text-sm font-medium"
                                            >
                                                Löschen
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            </div>
        {/if}
    </div>
</RoleGuard>
