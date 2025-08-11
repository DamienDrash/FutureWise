-- SaaS Owner Schema Extensions für FutureWise
-- Subscription Management
CREATE TABLE IF NOT EXISTS subscription_plans (
    plan_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price_cents BIGINT NOT NULL, -- Monthly price in cents
    currency TEXT NOT NULL DEFAULT 'EUR',
    max_users INTEGER,
    max_data_points INTEGER, -- Daily KPI data points allowed
    max_scenarios INTEGER,
    features JSONB NOT NULL DEFAULT '{}', -- JSON array of feature flags
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Insert default plans
INSERT INTO
    subscription_plans (
        plan_id,
        name,
        description,
        price_cents,
        max_users,
        max_data_points,
        max_scenarios,
        features
    )
VALUES (
        'starter',
        'Starter',
        'Basic analytics for small businesses',
        2900,
        5,
        100,
        3,
        '["basic_analytics", "csv_import"]'
    ),
    (
        'professional',
        'Professional',
        'Advanced analytics for growing businesses',
        9900,
        25,
        1000,
        20,
        '["basic_analytics", "csv_import", "api_import", "advanced_charts"]'
    ),
    (
        'enterprise',
        'Enterprise',
        'Full analytics suite for large organizations',
        29900,
        100,
        10000,
        100,
        '["basic_analytics", "csv_import", "api_import", "advanced_charts", "custom_integrations", "white_label"]'
    )
ON CONFLICT (plan_id) DO NOTHING;

-- Tenant Subscriptions
CREATE TABLE IF NOT EXISTS tenant_subscriptions (
    subscription_id BIGSERIAL PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants (tenant_id) ON DELETE CASCADE,
    plan_id TEXT NOT NULL REFERENCES subscription_plans (plan_id),
    status TEXT NOT NULL DEFAULT 'active', -- active, suspended, cancelled
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    ends_at TIMESTAMP WITH TIME ZONE,
    trial_ends_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tenant_subscriptions_tenant ON tenant_subscriptions (tenant_id);

CREATE INDEX IF NOT EXISTS idx_tenant_subscriptions_status ON tenant_subscriptions (status);

-- Billing & Invoices
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id BIGSERIAL PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants (tenant_id) ON DELETE CASCADE,
    subscription_id BIGINT REFERENCES tenant_subscriptions (subscription_id),
    invoice_number TEXT UNIQUE NOT NULL,
    amount_cents BIGINT NOT NULL,
    tax_cents BIGINT NOT NULL DEFAULT 0,
    currency TEXT NOT NULL DEFAULT 'EUR',
    status TEXT NOT NULL DEFAULT 'pending', -- pending, paid, failed, cancelled
    billing_period_start DATE NOT NULL,
    billing_period_end DATE NOT NULL,
    due_date DATE NOT NULL,
    paid_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_invoices_tenant ON invoices (tenant_id);

CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices (status);

CREATE INDEX IF NOT EXISTS idx_invoices_due_date ON invoices (due_date);

-- Usage Tracking für SaaS Metriken
CREATE TABLE IF NOT EXISTS usage_events (
    event_id BIGSERIAL PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants (tenant_id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users (user_id),
    event_type TEXT NOT NULL, -- login, data_import, scenario_run, api_call
    event_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_usage_events_tenant_date ON usage_events (tenant_id, created_at);

CREATE INDEX IF NOT EXISTS idx_usage_events_type ON usage_events (event_type);

-- Monthly Usage Aggregates (für Performance)
CREATE TABLE IF NOT EXISTS monthly_usage (
    tenant_id TEXT NOT NULL REFERENCES tenants (tenant_id) ON DELETE CASCADE,
    year_month TEXT NOT NULL, -- 'YYYY-MM' format
    total_logins INTEGER NOT NULL DEFAULT 0,
    total_data_imports INTEGER NOT NULL DEFAULT 0,
    total_scenarios_run INTEGER NOT NULL DEFAULT 0,
    total_api_calls INTEGER NOT NULL DEFAULT 0,
    total_data_points INTEGER NOT NULL DEFAULT 0,
    active_users INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (tenant_id, year_month)
);

-- SaaS Owner KPIs
CREATE OR REPLACE VIEW saas_metrics AS
SELECT
    DATE_TRUNC('month', ts.created_at) as month,
    COUNT(DISTINCT ts.tenant_id) as total_tenants,
    COUNT(
        DISTINCT CASE
            WHEN ts.status = 'active' THEN ts.tenant_id
        END
    ) as active_tenants,
    SUM(
        CASE
            WHEN ts.status = 'active' THEN sp.price_cents
            ELSE 0
        END
    ) as mrr_cents,
    SUM(
        CASE
            WHEN ts.status = 'active' THEN sp.price_cents * 12
            ELSE 0
        END
    ) as arr_cents,
    AVG(sp.price_cents) as avg_price_cents,
    COUNT(DISTINCT ut.user_id) as total_users
FROM
    tenant_subscriptions ts
    JOIN subscription_plans sp ON ts.plan_id = sp.plan_id
    LEFT JOIN user_tenants ut ON ts.tenant_id = ut.tenant_id
GROUP BY
    DATE_TRUNC('month', ts.created_at)
ORDER BY month DESC;

-- Erweiterte Tenant-Info mit Subscription-Daten
CREATE OR REPLACE VIEW tenant_overview AS
SELECT
    t.tenant_id,
    t.name,
    ts.status as subscription_status,
    sp.name as plan_name,
    sp.price_cents,
    ts.started_at as subscription_started,
    ts.trial_ends_at,
    COUNT(DISTINCT ut.user_id) as user_count,
    COUNT(DISTINCT s.scenario_id) as scenario_count,
    mu.total_data_points as monthly_data_points,
    mu.total_logins as monthly_logins
FROM
    tenants t
    LEFT JOIN tenant_subscriptions ts ON t.tenant_id = ts.tenant_id
    AND ts.status = 'active'
    LEFT JOIN subscription_plans sp ON ts.plan_id = sp.plan_id
    LEFT JOIN user_tenants ut ON t.tenant_id = ut.tenant_id
    LEFT JOIN scenarios s ON t.tenant_id = s.tenant_id
    LEFT JOIN monthly_usage mu ON t.tenant_id = mu.tenant_id
    AND mu.year_month = TO_CHAR(NOW(), 'YYYY-MM')
GROUP BY
    t.tenant_id,
    t.name,
    ts.status,
    sp.name,
    sp.price_cents,
    ts.started_at,
    ts.trial_ends_at,
    mu.total_data_points,
    mu.total_logins;