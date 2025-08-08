from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from ..services.db import get_sqlalchemy_engine

router = APIRouter()


@router.get("")
def list_tenants():
    engine = get_sqlalchemy_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT tenant_id, name
                    FROM tenants
                    ORDER BY name ASC
                    """
                )
            )
            tenants = [
                {"tenant_id": row[0], "name": row[1]} for row in result.fetchall()
            ]
            return {"items": tenants}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"DB error: {exc}")


@router.get("/{tenant_id}/settings")
def get_tenant_settings(tenant_id: str):
    engine = get_sqlalchemy_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT default_currency, default_tax_rate, default_channel
                FROM tenant_settings WHERE tenant_id=:tid
                """
            ),
            {"tid": tenant_id},
        ).first()
        if not row:
            return {
                "tenant_id": tenant_id,
                "default_currency": "EUR",
                "default_tax_rate": 0.19,
                "default_channel": "general",
            }
        return {
            "tenant_id": tenant_id,
            "default_currency": row[0],
            "default_tax_rate": float(row[1]),
            "default_channel": row[2],
        }


@router.put("/{tenant_id}/settings")
def upsert_tenant_settings(tenant_id: str, default_currency: str = "EUR", default_tax_rate: float = 0.19, default_channel: str = "general"):
    engine = get_sqlalchemy_engine()
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO tenant_settings(tenant_id, default_currency, default_tax_rate, default_channel)
                VALUES (:tid, :cur, :tax, :ch)
                ON CONFLICT (tenant_id) DO UPDATE SET
                  default_currency = EXCLUDED.default_currency,
                  default_tax_rate = EXCLUDED.default_tax_rate,
                  default_channel = EXCLUDED.default_channel,
                  updated_at = NOW()
                """
            ),
            {"tid": tenant_id, "cur": default_currency, "tax": default_tax_rate, "ch": default_channel},
        )
        return {"status": "ok"}
