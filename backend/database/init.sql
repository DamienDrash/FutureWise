-- Initiales Schema für FutureWise
CREATE TABLE IF NOT EXISTS tenants (
  tenant_id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);
