#!/usr/bin/env sh
API_BASE=${API_BASE:-http://localhost:8000}
TENANT_ID=${TENANT_ID:-alpha}
FILE=${1:-data/import/alpha_kpi_daily.csv}

curl -s -X POST "${API_BASE}/imports/csv" \
  -F tenant_id="${TENANT_ID}" \
  -F file=@"${FILE}" | cat
