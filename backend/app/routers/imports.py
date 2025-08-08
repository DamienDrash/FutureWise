from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from sqlalchemy import text
from ..services.db import get_sqlalchemy_engine
import io
import csv
import re
from datetime import date
import json as _json

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


def _get_tenant_defaults(conn, tenant_id: str) -> dict:
    row = conn.execute(
        text(
            """
            SELECT default_currency, default_tax_rate, default_channel
            FROM tenant_settings WHERE tenant_id = :tid
            """
        ),
        {"tid": tenant_id},
    ).first()
    return {
        "default_currency": (row[0] if row else "EUR"),
        "default_tax_rate": (float(row[1]) if row else 0.19),
        "default_channel": (row[2] if row else "general"),
    }


def _coerce_and_validate_row(tenant_id: str, r: dict, defaults: dict) -> dict:
    channel = (r.get("channel") or defaults["default_channel"]).lower()
    currency = (r.get("currency") or defaults["default_currency"]).upper()
    try:
        tax_rate = float(r.get("tax_rate", defaults["default_tax_rate"]) or defaults["default_tax_rate"])
    except Exception:
        raise HTTPException(status_code=400, detail="tax_rate must be a number between 0 and 1")

    if not RE_CHANNEL.match(channel):
        raise HTTPException(status_code=400, detail=f"invalid channel: {channel}")
    if not RE_CURRENCY.match(currency):
        raise HTTPException(status_code=400, detail=f"invalid currency (ISO 4217): {currency}")
    if not (0.0 <= tax_rate <= 1.0):
        raise HTTPException(status_code=400, detail=f"invalid tax_rate: {tax_rate}")

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

    rc = int(r.get("revenue_cents", 0) or 0)
    gross = r.get("revenue_cents_gross")
    net = r.get("revenue_cents_net")
    gross_val = None if gross is None or gross == "" else int(gross)
    net_val = None if net is None or net == "" else int(net)

    if gross_val is None and net_val is None:
        gross_val = rc
    if gross_val is None and net_val is not None:
        gross_val = round(net_val * (1.0 + tax_rate))
    if net_val is None and gross_val is not None:
        net_val = round(gross_val / (1.0 + tax_rate))

    payload["revenue_cents_gross"] = int(gross_val or 0)
    payload["revenue_cents_net"] = int(net_val or 0)
    return payload


def _begin_event(conn, tenant_id: str, source: str, filename: str | None) -> int:
    event_id = conn.execute(
        text(
            """
            INSERT INTO import_events(tenant_id, source, filename, inserted_count, error_count, status)
            VALUES (:tid, :src, :fn, 0, 0, 'success') RETURNING event_id
            """
        ),
        {"tid": tenant_id, "src": source, "fn": filename},
    ).scalar()
    return int(event_id)


def _finish_event(conn, event_id: int, inserted: int, errors: int):
    status = "success" if errors == 0 else ("partial" if inserted > 0 else "failed")
    conn.execute(
        text("UPDATE import_events SET inserted_count=:i, error_count=:e, status=:s WHERE event_id=:id"),
        {"i": inserted, "e": errors, "s": status, "id": event_id},
    )


def _record_error(conn, event_id: int, idx: int, err: str, raw: dict):
    conn.execute(
        text(
            """
            INSERT INTO import_event_errors(event_id, row_index, error, raw_row)
            VALUES (:eid, :idx, :err, CAST(:raw AS JSONB))
            """
        ),
        {"eid": event_id, "idx": idx, "err": err, "raw": _json.dumps(raw)},
    )


def _upsert_many(source: str, tenant_id: str, rows: list[dict], filename: str | None = None) -> dict:
    engine = get_sqlalchemy_engine()
    with engine.begin() as conn:
        tenant_exists = conn.execute(
            text("SELECT 1 FROM tenants WHERE tenant_id = :tid"), {"tid": tenant_id}
        ).first()
        if not tenant_exists:
            raise HTTPException(status_code=400, detail=f"Unknown tenant_id: {tenant_id}")

        defaults = _get_tenant_defaults(conn, tenant_id)
        event_id = _begin_event(conn, tenant_id, source, filename)

        inserted = 0
        errors = 0
        for idx, r in enumerate(rows):
            try:
                payload = _coerce_and_validate_row(tenant_id, r, defaults)
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
                inserted += 1
            except HTTPException as he:
                errors += 1
                _record_error(conn, event_id, idx, he.detail, r)
            except Exception as exc:
                errors += 1
                _record_error(conn, event_id, idx, str(exc), r)

        _finish_event(conn, event_id, inserted, errors)
        return {"event_id": event_id, "inserted": inserted, "errors": errors}


@router.post("/api")
def import_via_api(tenant_id: str = Form(...), payload: str = Form(...)):
    try:
        rows = _json.loads(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {exc}")
    if not isinstance(rows, list):
        raise HTTPException(status_code=400, detail="payload must be a JSON array of rows")
    result = _upsert_many("api", tenant_id, rows)
    return {"status": "ok", **result}


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
    result = _upsert_many("csv", tenant_id, rows, filename=file.filename)
    return {"status": "ok", **result}


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

    cols = list(set(BASE_COLUMNS + OPTIONAL_COLUMNS) & set(df.columns))
    rows = df[cols].astype(object).to_dict(orient="records")
    result = _upsert_many("xls", tenant_id, rows, filename=file.filename)
    return {"status": "ok", **result}


@router.post("/webhook")
async def import_via_webhook(tenant_id: str = Form(...), payload: str = Form(...)):
    try:
        rows = _json.loads(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {exc}")
    if not isinstance(rows, list):
        raise HTTPException(status_code=400, detail="payload must be a JSON array of rows")
    result = _upsert_many("webhook", tenant_id, rows)
    return {"status": "ok", **result}


@router.get("/events")
async def list_import_events(tenant_id: str = Query(...), limit: int = Query(20, ge=1, le=100)):
    engine = get_sqlalchemy_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT event_id, source, filename, inserted_count, error_count, status, created_at
                FROM import_events
                WHERE tenant_id = :tid
                ORDER BY created_at DESC
                LIMIT :lim
                """
            ),
            {"tid": tenant_id, "lim": limit},
        ).mappings().all()
        return {"items": [dict(r) for r in rows]}


@router.get("/events/{event_id}/errors")
async def get_import_event_errors(event_id: int):
    engine = get_sqlalchemy_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT row_index, error, raw_row
                FROM import_event_errors WHERE event_id = :eid ORDER BY id ASC
                """
            ),
            {"eid": event_id},
        ).mappings().all()
        return {"items": [dict(r) for r in rows]}


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
                  COALESCE(SUM(sessions),0) AS sessions_sum,
                  COALESCE(SUM(orders),0) AS orders_sum,
                  COALESCE(SUM(revenue_cents_gross),0) AS revenue_gross_sum,
                  COALESCE(SUM(revenue_cents_net),0) AS revenue_net_sum
                FROM kpi_daily
                WHERE tenant_id = :tid AND date BETWEEN :df AND :dt
                """
            ),
            {"tid": tenant_id, "df": date_from, "dt": date_to},
        ).mappings().first()
        return {"tenant_id": tenant_id, "range": {"from": str(date_from), "to": str(date_to)}, "summary": dict(res) if res else {}}
