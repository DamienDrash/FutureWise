from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from sqlalchemy import text
from ..services.db import get_sqlalchemy_engine
import io
import csv

router = APIRouter()

EXPECTED_COLUMNS = [
    "date",  # YYYY-MM-DD
    "sessions",
    "orders",
    "revenue_cents",
    "conversion_rate",
    "inventory_units",
]


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
            # Basic coercion and validation
            try:
                payload = {
                    "tenant_id": tenant_id,
                    "date": r["date"],
                    "sessions": int(r.get("sessions", 0) or 0),
                    "orders": int(r.get("orders", 0) or 0),
                    "revenue_cents": int(r.get("revenue_cents", 0) or 0),
                    "conversion_rate": float(r.get("conversion_rate", 0.0) or 0.0),
                    "inventory_units": int(r.get("inventory_units", 0) or 0),
                }
            except Exception as exc:
                raise HTTPException(status_code=400, detail=f"Invalid row values: {exc}")

            conn.execute(
                text(
                    """
                    INSERT INTO kpi_daily (
                      tenant_id, date, sessions, orders, revenue_cents, conversion_rate, inventory_units
                    ) VALUES (
                      :tenant_id, :date, :sessions, :orders, :revenue_cents, :conversion_rate, :inventory_units
                    )
                    ON CONFLICT (tenant_id, date)
                    DO UPDATE SET
                      sessions = EXCLUDED.sessions,
                      orders = EXCLUDED.orders,
                      revenue_cents = EXCLUDED.revenue_cents,
                      conversion_rate = EXCLUDED.conversion_rate,
                      inventory_units = EXCLUDED.inventory_units
                    """
                ),
                payload,
            )


@router.post("/api")
def import_via_api(tenant_id: str = Form(...), payload: str = Form(...)):
    # payload erwartet JSON-String
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

    # Lazy import to keep base import fast
    import pandas as pd

    try:
        df = pd.read_excel(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Excel parse error: {exc}")

    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Missing column: {col}")

    rows = df[EXPECTED_COLUMNS].astype(object).to_dict(orient="records")
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
