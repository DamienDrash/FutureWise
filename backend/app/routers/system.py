from fastapi import APIRouter, Depends
from sqlalchemy import text
from ..services.db import get_sqlalchemy_engine
from ..services.security import AuthContext, require_role

router = APIRouter()


@router.get("/stats")
async def system_stats(ctx: AuthContext = Depends(require_role("system_manager"))):
    """
    Get system-wide statistics for system managers and owners.
    Returns aggregated KPIs across all tenants.
    """
    engine = get_sqlalchemy_engine()
    with engine.connect() as conn:
        # Count total tenants
        tenant_count = conn.execute(text("SELECT COUNT(*) FROM tenants")).scalar()
        
        # Count total users
        user_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
        
        # Get system-wide revenue (sum across all tenants)
        revenue_result = conn.execute(text("""
            SELECT 
                COALESCE(SUM(revenue_cents_gross), 0) as total_revenue,
                COUNT(*) as total_records
            FROM kpi_daily 
            WHERE date >= NOW() - INTERVAL '30 days'
        """)).first()
        
        # Count active scenarios across all tenants
        scenario_count = conn.execute(text("SELECT COUNT(*) FROM scenarios")).scalar()
        
        return {
            "total_tenants": tenant_count,
            "total_users": user_count,
            "system_revenue": revenue_result[0] if revenue_result else 0,
            "active_scenarios": scenario_count,
            "total_data_points": revenue_result[1] if revenue_result else 0
        }
