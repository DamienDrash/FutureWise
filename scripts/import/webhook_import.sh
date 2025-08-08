#!/usr/bin/env sh
API_BASE=${API_BASE:-http://localhost:8000}
TENANT_ID=${TENANT_ID:-alpha}

PAYLOAD='[{"date":"2025-08-05","sessions":1100,"orders":55,"revenue_cents":1375000,"conversion_rate":0.05,"inventory_units":470}]'

curl -s -X POST "${API_BASE}/imports/webhook" \
  -F tenant_id="${TENANT_ID}" \
  -F payload="${PAYLOAD}" | cat
