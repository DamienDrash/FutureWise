#!/usr/bin/env sh
API_BASE=${API_BASE:-http://localhost:8000}
TENANT_ID=${TENANT_ID:-alpha}
FILE=${1:-data/import/alpha_kpi_daily.csv}
COOKIES=$(mktemp)

# Optional: Login, wenn LOGIN_EMAIL und LOGIN_PASSWORD gesetzt sind
if [ -n "$LOGIN_EMAIL" ] && [ -n "$LOGIN_PASSWORD" ]; then
  echo "=> Login für ${LOGIN_EMAIL} (Tenant ${TENANT_ID})"
  curl -s -c "$COOKIES" -b "$COOKIES" -X POST "${API_BASE}/auth/login" \
    -F email="$LOGIN_EMAIL" \
    -F password="$LOGIN_PASSWORD" \
    -F tenant_id="$TENANT_ID" | cat
  echo
fi

echo "=> CSV Upload: ${FILE}"
curl -s -c "$COOKIES" -b "$COOKIES" -X POST "${API_BASE}/imports/csv" \
  -F tenant_id="${TENANT_ID}" \
  -F file=@"${FILE}" | cat
echo

rm -f "$COOKIES"
