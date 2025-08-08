#!/usr/bin/env python3
import os
import json
import requests

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")
TENANT_ID = os.environ.get("TENANT_ID", "alpha")

rows = [
    {"date": "2025-08-03", "sessions": 900, "orders": 40, "revenue_cents": 1000000, "conversion_rate": 0.044, "inventory_units": 480},
    {"date": "2025-08-04", "sessions": 950, "orders": 42, "revenue_cents": 1050000, "conversion_rate": 0.044, "inventory_units": 475},
]

resp = requests.post(
    f"{API_BASE}/imports/api",
    data={"tenant_id": TENANT_ID, "payload": json.dumps(rows)},
)
print(resp.status_code, resp.text)
