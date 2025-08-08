from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy import text
from ..services.db import get_sqlalchemy_engine
from ..services.security import require_role, AuthContext
import uuid

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


@router.post("/create")
def create_tenant(name: str = Form(...), ctx: AuthContext = Depends(require_role("manager"))):
    engine = get_sqlalchemy_engine()
    tenant_id = name.lower().replace(" ", "-")
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO tenants(tenant_id, name) VALUES (:t,:n) ON CONFLICT (tenant_id) DO NOTHING"), {"t": tenant_id, "n": name})
        # grant current manager ownership
        conn.execute(text("INSERT INTO user_tenants(user_id, tenant_id, role) VALUES (:u,:t,'manager') ON CONFLICT (user_id,tenant_id) DO UPDATE SET role='manager'"), {"u": ctx.user_id, "t": tenant_id})
    return {"status": "ok", "tenant_id": tenant_id}


@router.post("/{tenant_id}/invite")
def invite_user(tenant_id: str, email: str = Form(...), role: str = Form("viewer"), ctx: AuthContext = Depends(require_role("manager"))):
    if ctx.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="wrong tenant")
    token = uuid.uuid4().hex
    engine = get_sqlalchemy_engine()
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO invitations(token, tenant_id, email, role) VALUES (:tok,:t,:e,:r)"), {"tok": token, "t": tenant_id, "e": email, "r": role})
    return {"invite_token": token}


@router.post("/invite/accept")
def accept_invite(token: str = Form(...), user_id: int = Form(...)):
    engine = get_sqlalchemy_engine()
    with engine.begin() as conn:
        inv = conn.execute(text("SELECT tenant_id, role FROM invitations WHERE token=:tok AND accepted_at IS NULL"), {"tok": token}).first()
        if not inv:
            raise HTTPException(status_code=400, detail="invalid invite")
        conn.execute(text("UPDATE invitations SET accepted_at=NOW() WHERE token=:tok"), {"tok": token})
        conn.execute(text("INSERT INTO user_tenants(user_id, tenant_id, role) VALUES (:u,:t,:r) ON CONFLICT (user_id,tenant_id) DO UPDATE SET role=EXCLUDED.role"), {"u": user_id, "t": inv[0], "r": inv[1]})
    return {"status": "ok"}


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
def upsert_tenant_settings(tenant_id: str, default_currency: str = "EUR", default_tax_rate: float = 0.19, default_channel: str = "general", ctx: AuthContext = Depends(require_role("manager"))):
    if ctx.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="wrong tenant")
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
