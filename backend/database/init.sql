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
