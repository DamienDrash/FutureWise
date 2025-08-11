// Demo login credentials for testing role-based UI
export const DEMO_USERS = {
    owner: {
        email: 'owner@futurewise.local',
        password: 'secret',
        role: 'owner',
        tenant_id: 'system',
        display_name: 'System Owner'
    },
    system_manager: {
        email: 'sysman@futurewise.local',
        password: 'secret',
        role: 'system_manager',
        tenant_id: 'system',
        display_name: 'System Manager'
    },
    alpha_admin: {
        email: 'alpha.admin@futurewise.local',
        password: 'secret',
        role: 'tenant_admin',
        tenant_id: 'alpha',
        display_name: 'Alpha Admin'
    },
    beta_admin: {
        email: 'beta.admin@futurewise.local',
        password: 'secret',
        role: 'tenant_admin',
        tenant_id: 'beta',
        display_name: 'Beta Admin'
    },
    alpha_user: {
        email: 'alpha.user@futurewise.local',
        password: 'secret',
        role: 'tenant_user',
        tenant_id: 'alpha',
        display_name: 'Alpha User'
    },
    beta_user: {
        email: 'beta.user@futurewise.local',
        password: 'secret',
        role: 'tenant_user',
        tenant_id: 'beta',
        display_name: 'Beta User'
    }
};

export const ROLE_DESCRIPTIONS = {
    owner: 'Vollzugriff auf das gesamte System, alle Tenants und Benutzer',
    system_manager: 'System-weite Verwaltung, Tenant-Erstellung und -Übersicht',
    tenant_admin: 'Vollzugriff innerhalb des eigenen Tenants, Benutzerverwaltung',
    tenant_user: 'Standard-Zugriff auf Daten und Szenarien des eigenen Tenants',
    manager: 'Legacy-Rolle mit erweiterten Rechten (entspricht tenant_admin)',
    analyst: 'Legacy-Rolle mit Standard-Rechten (entspricht tenant_user)',
    viewer: 'Legacy-Rolle mit Nur-Lese-Zugriff'
};
