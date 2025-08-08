# Import Scripts

Varianten:
- API (JSON): `scripts/import/api_import.py`
- CSV: `scripts/import/csv_import.sh`
- XLS: `scripts/import/generate_xls_and_import.py`
- Webhook: `scripts/import/webhook_import.sh`

Template:
- CSV-Header: siehe `data/import/template_kpi_daily.csv`
- Pflichtspalten: date, sessions, orders, revenue_cents, conversion_rate, inventory_units
- Optionale Spalten: channel, currency, tax_rate, revenue_cents_gross, revenue_cents_net

Hinweise:
- Defaults pro Tenant: `tenant_settings` (currency, tax_rate, channel)
- net/gross werden bei Bedarf berechnet
