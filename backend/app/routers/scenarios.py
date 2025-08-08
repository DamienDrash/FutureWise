from fastapi import APIRouter, HTTPException, Form
from sqlalchemy import text
from ..services.db import get_sqlalchemy_engine
from datetime import date, timedelta
import json as _json

router = APIRouter()


@router.get("")
async def list_scenarios(tenant_id: str):
    engine = get_sqlalchemy_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT scenario_id, name, kind, params, created_at
                FROM scenarios
                WHERE tenant_id = :tid
                ORDER BY created_at DESC
                LIMIT 50
                """
            ),
            {"tid": tenant_id},
        ).mappings().all()
        return {"items": [dict(r) for r in rows]}


@router.post("")
async def create_scenario(tenant_id: str, name: str, kind: str = "custom", params: str = "{}"):
    engine = get_sqlalchemy_engine()
    try:
        params_obj = _json.loads(params)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"invalid params JSON: {exc}")

    with engine.begin() as conn:
        sid = conn.execute(
            text(
                """
                INSERT INTO scenarios(tenant_id, name, kind, params)
                VALUES (:tid, :name, :kind, CAST(:params AS JSONB))
                RETURNING scenario_id
                """
            ),
            {"tid": tenant_id, "name": name, "kind": kind, "params": _json.dumps(params_obj)},
        ).scalar()
        return {"status": "ok", "scenario_id": int(sid)}


@router.post("/simulate")
async def simulate_scenario(
    tenant_id: str = Form(...),
    scenario_id: int | None = Form(None),
    params: str | None = Form(None),
    date_from: str = Form(...),
    date_to: str = Form(...),
):
    engine = get_sqlalchemy_engine()
    with engine.begin() as conn:
        # Load params
        scenario_params = {}
        if scenario_id is not None:
            row = conn.execute(
                text("SELECT params FROM scenarios WHERE scenario_id=:sid AND tenant_id=:tid"),
                {"sid": scenario_id, "tid": tenant_id},
            ).first()
            if not row:
                raise HTTPException(status_code=404, detail="scenario not found")
            scenario_params = row[0]
        elif params is not None:
            try:
                scenario_params = _json.loads(params)
            except Exception as exc:
                raise HTTPException(status_code=400, detail=f"invalid params JSON: {exc}")
        else:
            raise HTTPException(status_code=400, detail="provide scenario_id or params")

        # Range
        if not date_from or not date_to:
            raise HTTPException(status_code=400, detail="date_from and date_to are required (YYYY-MM-DD)")
        dfrom = date.fromisoformat(date_from)
        dto = date.fromisoformat(date_to)

        # Baseline: use kpi_daily
        baseline = conn.execute(
            text(
                """
                SELECT date, sessions, orders, revenue_cents_gross, revenue_cents_net
                FROM kpi_daily WHERE tenant_id=:tid AND date BETWEEN :df AND :dt
                ORDER BY date ASC
                """
            ),
            {"tid": tenant_id, "df": dfrom, "dt": dto},
        ).mappings().all()

        # Simple modifiers from params
        price_elasticity = float(scenario_params.get("price_elasticity", -1.2))
        price_change_pct = float(scenario_params.get("price_change_pct", 0.0))  # +0.05 => +5%
        promo_uplift_orders = float(scenario_params.get("promo_uplift_orders", 0.0))  # +0.1 => +10%
        traffic_change_pct = float(scenario_params.get("traffic_change_pct", 0.0))  # sessions

        results = []
        for r in baseline:
            sessions = int(round(r["sessions"] * (1.0 + traffic_change_pct)))
            # price impact on orders via elasticity
            orders_base = r["orders"]
            orders_adj = orders_base * (1.0 + promo_uplift_orders) * (1.0 + price_elasticity * price_change_pct)
            orders = max(0, int(round(orders_adj)))
            # assume revenue scales with orders proportionally
            rev_gross_per_order = (r["revenue_cents_gross"] / r["orders"]) if r["orders"] else 0
            rev_net_per_order = (r["revenue_cents_net"] / r["orders"]) if r["orders"] else 0
            revenue_gross = int(round(rev_gross_per_order * orders))
            revenue_net = int(round(rev_net_per_order * orders))

            results.append({
                "date": str(r["date"]),
                "sessions": sessions,
                "orders": orders,
                "revenue_cents_gross": revenue_gross,
                "revenue_cents_net": revenue_net,
            })

        # store results (overwrite)
        sid = scenario_id
        if sid is None:
            sid = conn.execute(
                text(
                    """
                    INSERT INTO scenarios(tenant_id, name, kind, params)
                    VALUES (:tid, :name, 'custom', CAST(:params AS JSONB))
                    RETURNING scenario_id
                    """
                ),
                {"tid": tenant_id, "name": scenario_params.get("name", "Ad-hoc"), "params": _json.dumps(scenario_params)},
            ).scalar()
        conn.execute(text("DELETE FROM scenario_results_daily WHERE scenario_id=:sid"), {"sid": sid})
        for row in results:
            conn.execute(
                text(
                    """
                    INSERT INTO scenario_results_daily(scenario_id, tenant_id, date, sessions, orders, revenue_cents_gross, revenue_cents_net)
                    VALUES (:sid, :tid, :date, :sessions, :orders, :rg, :rn)
                    """
                ),
                {"sid": sid, "tid": tenant_id, "date": row["date"], "sessions": row["sessions"], "orders": row["orders"], "rg": row["revenue_cents_gross"], "rn": row["revenue_cents_net"]},
            )

        return {"status": "ok", "scenario_id": int(sid), "count": len(results)}
