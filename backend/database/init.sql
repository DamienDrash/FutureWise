-- Initiales Schema für FutureWise
CREATE TABLE IF NOT EXISTS tenants (
  tenant_id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS kpi_daily (
  tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  date DATE NOT NULL,
  sessions INTEGER NOT NULL DEFAULT 0,
  orders INTEGER NOT NULL DEFAULT 0,
  revenue_cents BIGINT NOT NULL DEFAULT 0,
  conversion_rate DOUBLE PRECISION NOT NULL DEFAULT 0,
  inventory_units INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  PRIMARY KEY (tenant_id, date)
);

-- Zusatzspalten (idempotent)
ALTER TABLE kpi_daily ADD COLUMN IF NOT EXISTS channel TEXT NOT NULL DEFAULT 'general';
ALTER TABLE kpi_daily ADD COLUMN IF NOT EXISTS currency TEXT NOT NULL DEFAULT 'EUR';
ALTER TABLE kpi_daily ADD COLUMN IF NOT EXISTS tax_rate DOUBLE PRECISION NOT NULL DEFAULT 0.19; -- 19%
ALTER TABLE kpi_daily ADD COLUMN IF NOT EXISTS revenue_cents_gross BIGINT;
ALTER TABLE kpi_daily ADD COLUMN IF NOT EXISTS revenue_cents_net BIGINT;

CREATE INDEX IF NOT EXISTS idx_kpi_daily_tenant_date ON kpi_daily(tenant_id, date);

-- Tenant Settings
CREATE TABLE IF NOT EXISTS tenant_settings (
  tenant_id TEXT PRIMARY KEY REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  default_currency TEXT NOT NULL DEFAULT 'EUR',
  default_tax_rate DOUBLE PRECISION NOT NULL DEFAULT 0.19,
  default_channel TEXT NOT NULL DEFAULT 'general',
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Import Logging
CREATE TABLE IF NOT EXISTS import_events (
  event_id BIGSERIAL PRIMARY KEY,
  tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  source TEXT NOT NULL, -- api,csv,xls,webhook
  filename TEXT,
  inserted_count INTEGER NOT NULL DEFAULT 0,
  error_count INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'success', -- success,partial,failed
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_import_events_tenant_created ON import_events(tenant_id, created_at DESC);

CREATE TABLE IF NOT EXISTS import_event_errors (
  id BIGSERIAL PRIMARY KEY,
  event_id BIGINT NOT NULL REFERENCES import_events(event_id) ON DELETE CASCADE,
  row_index INTEGER,
  error TEXT NOT NULL,
  raw_row JSONB
);
CREATE INDEX IF NOT EXISTS idx_import_errors_event ON import_event_errors(event_id);
