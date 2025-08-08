#!/usr/bin/env python3
import os
import io
import pandas as pd
import requests

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")
TENANT_ID = os.environ.get("TENANT_ID", "alpha")
CSV_FILE = os.environ.get("CSV_FILE", "data/import/alpha_kpi_daily.csv")

# CSV laden
df = pd.read_csv(CSV_FILE)

# XLSX in Memory erzeugen
buf = io.BytesIO()
df.to_excel(buf, index=False)
buf.seek(0)

files = {"file": ("alpha_kpi_daily.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
data = {"tenant_id": TENANT_ID}
resp = requests.post(f"{API_BASE}/imports/xls", files=files, data=data)
print(resp.status_code, resp.text)
