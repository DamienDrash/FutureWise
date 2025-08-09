// TypeScript Typdefinitionen für FutureWise

export interface User {
    id: string;
    email: string;
    display_name?: string;
    role: UserRole;
    tenant_id: string;
    created_at?: string;
    updated_at?: string;
}

export type UserRole =
    | 'owner'
    | 'system_manager'
    | 'tenant_admin'
    | 'tenant_user'
    | 'manager'
    | 'analyst'  // Legacy
    | 'viewer';  // Legacy

export interface Tenant {
    id: string;
    name: string;
    status: TenantStatus;
    created_at: string;
    updated_at: string;
}

export type TenantStatus = 'active' | 'trial' | 'suspended';

export interface Scenario {
    id: string;
    name: string;
    description?: string;
    tenant_id: string;
    created_at: string;
    updated_at: string;
}

export interface KPIData {
    date: string;
    value: number;
    metric_name: string;
    tenant_id: string;
}

export interface ImportEvent {
    id: string;
    tenant_id: string;
    filename: string;
    status: string;
    records_imported: number;
    created_at: string;
}

export interface AuthStore {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
}

// Chart color types
export type ChartColor =
    | 'primary'
    | 'secondary'
    | 'chart-1'
    | 'chart-2'
    | 'chart-3'
    | 'chart-4'
    | 'chart-5';

// Role color mappings
export const roleColors: Record<UserRole, string> = {
    owner: 'bg-red-100 text-red-800',
    system_manager: 'bg-purple-100 text-purple-800',
    tenant_admin: 'bg-blue-100 text-blue-800',
    tenant_user: 'bg-green-100 text-green-800',
    manager: 'bg-yellow-100 text-yellow-800',
    analyst: 'bg-gray-100 text-gray-800',
    viewer: 'bg-gray-100 text-gray-800'
};

// Role labels
export const roleLabels: Record<UserRole, string> = {
    owner: 'Owner',
    system_manager: 'System Manager',
    tenant_admin: 'Tenant Admin',
    tenant_user: 'Tenant User',
    manager: 'Manager',
    analyst: 'Analyst', // Legacy
    viewer: 'Viewer' // Legacy
};

// Tenant status colors
export const tenantStatusColors: Record<TenantStatus, string> = {
    active: 'bg-green-100 text-green-800',
    trial: 'bg-yellow-100 text-yellow-800',
    suspended: 'bg-red-100 text-red-800'
};

// Chart colors
export const chartColors: Record<ChartColor, string> = {
    primary: 'hsl(220, 70%, 50%)',
    secondary: 'hsl(160, 60%, 45%)',
    'chart-1': 'hsl(220, 70%, 50%)',
    'chart-2': 'hsl(160, 60%, 45%)',
    'chart-3': 'hsl(30, 80%, 55%)',
    'chart-4': 'hsl(280, 65%, 60%)',
    'chart-5': 'hsl(340, 75%, 55%)'
};
