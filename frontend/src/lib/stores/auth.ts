import { writable } from 'svelte/store';
import type { User, AuthStore, UserRole } from '../types';
import { roleLabels } from '../types';

// Auth Store mit korrekten TypeScript Typen
export const authStore = writable<AuthStore>({
    user: null,
    token: null,
    isAuthenticated: false
});

// Helper Funktionen für Auth Store
export const setUser = (user: User, token: string) => {
    authStore.set({
        user,
        token,
        isAuthenticated: true
    });
};

export const clearAuth = () => {
    authStore.set({
        user: null,
        token: null,
        isAuthenticated: false
    });
};

export const updateUser = (updates: Partial<User>) => {
    authStore.update(store => {
        if (store.user) {
            return {
                ...store,
                user: { ...store.user, ...updates }
            };
        }
        return store;
    });
};

// Role hierarchy - höhere Werte = mehr Berechtigung
const roleHierarchy: Record<UserRole, number> = {
    viewer: 1,
    analyst: 2,
    tenant_user: 3,
    manager: 4,
    tenant_admin: 5,
    system_manager: 6,
    owner: 7
};

// Check if user has minimum required role
export const hasMinRole = (userRole: UserRole, minRole: UserRole): boolean => {
    return roleHierarchy[userRole] >= roleHierarchy[minRole];
};

// Role check functions
export const isOwner = (role: UserRole): boolean => role === 'owner';
export const isSystemManager = (role: UserRole): boolean => role === 'system_manager' || isOwner(role);
export const isTenantAdmin = (role: UserRole): boolean => role === 'tenant_admin' || isSystemManager(role);

// Get user display info
export const getUserDisplayInfo = (user: User | null) => {
    if (!user) return null;

    return {
        name: user.display_name || user.email.split('@')[0],
        email: user.email,
        role: roleLabels[user.role] || user.role,
        tenant: user.tenant_id
    };
};