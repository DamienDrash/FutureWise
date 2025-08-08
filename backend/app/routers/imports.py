from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from sqlalchemy import text
from ..services.db import get_sqlalchemy_engine
import io
import csv
import re
from datetime import date

router = APIRouter()

RE_CHANNEL = re.compile(r"^(general|seo|sem|email|social|affiliate|marketplace|direct|other)$", re.I)
RE_CURRENCY = re.compile(r"^[A-Z]{3}$")

BASE_COLUMNS = [
    "date",  # YYYY-MM-DD
    "sessions",
    "orders",
    "revenue_cents",
    "conversion_rate",
    "inventory_units",
]

OPTIONAL_COLUMNS = [
    "channel",
    "currency",
    "tax_rate",
    "revenue_cents_gross",
    "revenue_cents_net",
]

EXPECTED_COLUMNS = BASE_COLUMNS  # for CSV minimal check


def _coerce_and_validate_row(tenant_id: str, r: dict) -> dict:
    # Defaults
    channel = (r.get("channel") or "general").lower()
    currency = (r.get("currency") or "EUR").upper()
    try:
        tax_rate = float(r.get("tax_rate", 0.19) or 0.19)
    except Exception:
        raise HTTPException(status_code=400, detail="tax_rate must be a number between 0 and 1")

    if not RE_CHANNEL.match(channel):
        raise HTTPException(status_code=400, detail=f"invalid channel: {channel}")
    if not RE_CURRENCY.match(currency):
        raise HTTPException(status_code=400, detail=f"invalid currency (ISO 4217): {currency}")
    if not (0.0 <= tax_rate <= 1.0):
        raise HTTPException(status_code=400, detail=f"invalid tax_rate: {tax_rate}")

    # Coerce base fields
    payload = {
        "tenant_id": tenant_id,
        "date": r["date"],
        "sessions": int(r.get("sessions", 0) or 0),
        "orders": int(r.get("orders", 0) or 0),
        "revenue_cents": int(r.get("revenue_cents", 0) or 0),
        "conversion_rate": float(r.get("conversion_rate", 0.0) or 0.0),
        "inventory_units": int(r.get("inventory_units", 0) or 0),
        "channel": channel,
        "currency": currency,
        "tax_rate": tax_rate,
    }

    # Net/Gross mapping
    rc = int(r.get("revenue_cents", 0) or 0)
    gross = r.get("revenue_cents_gross")
    net = r.get("revenue_cents_net")

    gross_val = None if gross is None or gross == "" else int(gross)
    net_val = None if net is None or net == "" else int(net)

    if gross_val is None and net_val is None:
        # map legacy revenue_cents to gross by default
        gross_val = rc
    if gross_val is None and net_val is not None:
        gross_val = round(net_val * (1.0 + tax_rate))
    if net_val is None and gross_val is not None:
        net_val = round(gross_val / (1.0 + tax_rate))

    payload["revenue_cents_gross"] = int(gross_val or 0)
    payload["revenue_cents_net"] = int(net_val or 0)

    return payload


def _upsert_many(tenant_id: str, rows: list[dict]):
    engine = get_sqlalchemy_engine()
    with engine.begin() as conn:
        # ensure tenant exists
        tenant_exists = conn.execute(
            text("SELECT 1 FROM tenants WHERE tenant_id = :tid"), {"tid": tenant_id}
        ).first()
        if not tenant_exists:
            raise HTTPException(status_code=400, detail=f"Unknown tenant_id: {tenant_id}")

        for r in rows:
            try:
                payload = _coerce_and_validate_row(tenant_id, r)
            except HTTPException:
                raise
            except Exception as exc:
                raise HTTPException(status_code=400, detail=f"Invalid row values: {exc}")

            conn.execute(
                text(
                    """
                    INSERT INTO kpi_daily (
                      tenant_id, date, sessions, orders, revenue_cents, conversion_rate, inventory_units,
                      channel, currency, tax_rate, revenue_cents_gross, revenue_cents_net
                    ) VALUES (
                      :tenant_id, :date, :sessions, :orders, :revenue_cents, :conversion_rate, :inventory_units,
                      :channel, :currency, :tax_rate, :revenue_cents_gross, :revenue_cents_net
                    )
                    ON CONFLICT (tenant_id, date)
                    DO UPDATE SET
                      sessions = EXCLUDED.sessions,
                      orders = EXCLUDED.orders,
                      revenue_cents = EXCLUDED.revenue_cents,
                      conversion_rate = EXCLUDED.conversion_rate,
                      inventory_units = EXCLUDED.inventory_units,
                      channel = EXCLUDED.channel,
                      currency = EXCLUDED.currency,
                      tax_rate = EXCLUDED.tax_rate,
                      revenue_cents_gross = EXCLUDED.revenue_cents_gross,
                      revenue_cents_net = EXCLUDED.revenue_cents_net
                    """
                ),
                payload,
            )


@router.post("/api")
def import_via_api(tenant_id: str = Form(...), payload: str = Form(...)):
    import json as _json
    try:
        rows = _json.loads(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {exc}")
    if not isinstance(rows, list):
        raise HTTPException(status_code=400, detail="payload must be a JSON array of rows")
    _upsert_many(tenant_id, rows)
    return {"status": "ok", "inserted": len(rows)}


@router.post("/csv")
async def import_via_csv(tenant_id: str = Form(...), file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="file must be .csv")

    content = await file.read()
    text_stream = io.StringIO(content.decode("utf-8"))
    reader = csv.DictReader(text_stream)

    missing = [c for c in EXPECTED_COLUMNS if c not in reader.fieldnames]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")

    rows = [row for row in reader]
    _upsert_many(tenant_id, rows)
    return {"status": "ok", "inserted": len(rows)}


@router.post("/xls")
async def import_via_xls(tenant_id: str = Form(...), file: UploadFile = File(...)):
    fn = file.filename.lower()
    if not (fn.endswith(".xlsx") or fn.endswith(".xls")):
        raise HTTPException(status_code=400, detail="file must be .xlsx or .xls")
    content = await file.read()

    import pandas as pd

    try:
        df = pd.read_excel(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Excel parse error: {exc}")

    for col in BASE_COLUMNS:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Missing column: {col}")

    rows = df[list(set(BASE_COLUMNS + OPTIONAL_COLUMNS) & set(df.columns))].astype(object).to_dict(orient="records")
    _upsert_many(tenant_id, rows)
    return {"status": "ok", "inserted": len(rows)}


@router.post("/webhook")
async def import_via_webhook(tenant_id: str = Form(...), payload: str = Form(...)):
    import json as _json
    try:
        rows = _json.loads(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {exc}")
    if not isinstance(rows, list):
        raise HTTPException(status_code=400, detail="payload must be a JSON array of rows")
    _upsert_many(tenant_id, rows)
    return {"status": "ok", "inserted": len(rows)}


@router.get("/summary")
async def import_summary(
    tenant_id: str = Query(...),
    date_from: date = Query(...),
    date_to: date = Query(...),
):
    engine = get_sqlalchemy_engine()
    with engine.connect() as conn:
        res = conn.execute(
            text(
                """
                SELECT 
                  COUNT(*) AS num_days,
                  SUM(sessions) AS sessions_sum,
                  SUM(orders) AS orders_sum,
                  SUM(revenue_cents_gross) AS revenue_gross_sum,
                  SUM(revenue_cents_net) AS revenue_net_sum
                FROM kpi_daily
                WHERE tenant_id = :tid AND date BETWEEN :df AND :dt
                """
            ),
            {"tid": tenant_id, "df": date_from, "dt": date_to},
        ).mappings().first()
        return {"tenant_id": tenant_id, "range": {"from": str(date_from), "to": str(date_to)}, "summary": dict(res) if res else {}}
