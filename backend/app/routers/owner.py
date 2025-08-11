from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from typing import List, Dict, Any
from ..services.db import get_sqlalchemy_engine
from ..services.security import AuthContext, require_role

router = APIRouter()


@router.get("/saas-metrics")
async def get_saas_metrics(ctx: AuthContext = Depends(require_role("owner"))):
    """
    Get high-level SaaS metrics for the owner dashboard.
    Returns MRR, ARR, tenant count, churn, etc.
    """
    engine = get_sqlalchemy_engine()
    with engine.connect() as conn:
        # Current month metrics
        current_metrics = conn.execute(text("""
            SELECT 
                COUNT(DISTINCT t.tenant_id) as total_tenants,
                COUNT(DISTINCT CASE WHEN ts.status = 'active' THEN t.tenant_id END) as active_tenants,
                SUM(CASE WHEN ts.status = 'active' THEN sp.price_cents ELSE 0 END) as mrr_cents,
                SUM(CASE WHEN ts.status = 'active' THEN sp.price_cents * 12 ELSE 0 END) as arr_cents,
                COUNT(DISTINCT ut.user_id) as total_users,
                SUM(CASE WHEN i.status = 'paid' AND i.created_at >= DATE_TRUNC('month', NOW()) THEN i.amount_cents ELSE 0 END) as monthly_revenue,
                COUNT(DISTINCT CASE WHEN i.status = 'pending' THEN i.tenant_id END) as pending_invoices
            FROM tenants t
            LEFT JOIN tenant_subscriptions ts ON t.tenant_id = ts.tenant_id AND ts.status = 'active'
            LEFT JOIN subscription_plans sp ON ts.plan_id = sp.plan_id
            LEFT JOIN user_tenants ut ON t.tenant_id = ut.tenant_id
            LEFT JOIN invoices i ON t.tenant_id = i.tenant_id
        """)).first()
        
        # Growth metrics (last 3 months)
        growth_metrics = conn.execute(text("""
            SELECT 
                DATE_TRUNC('month', ts.created_at) as month,
                COUNT(DISTINCT ts.tenant_id) as new_tenants,
                SUM(sp.price_cents) as new_mrr_cents
            FROM tenant_subscriptions ts
            JOIN subscription_plans sp ON ts.plan_id = sp.plan_id
            WHERE ts.created_at >= DATE_TRUNC('month', NOW()) - INTERVAL '3 months'
            GROUP BY DATE_TRUNC('month', ts.created_at)
            ORDER BY month DESC
        """)).fetchall()
        
        # Plan distribution
        plan_distribution = conn.execute(text("""
            SELECT 
                sp.name as plan_name,
                sp.price_cents,
                COUNT(ts.tenant_id) as tenant_count,
                SUM(sp.price_cents) as total_mrr_cents
            FROM subscription_plans sp
            LEFT JOIN tenant_subscriptions ts ON sp.plan_id = ts.plan_id AND ts.status = 'active'
            GROUP BY sp.plan_id, sp.name, sp.price_cents
            ORDER BY sp.price_cents DESC
        """)).fetchall()
        
        return {
            "current_metrics": {
                "total_tenants": current_metrics[0] if current_metrics else 0,
                "active_tenants": current_metrics[1] if current_metrics else 0,
                "mrr_cents": current_metrics[2] if current_metrics else 0,
                "arr_cents": current_metrics[3] if current_metrics else 0,
                "total_users": current_metrics[4] if current_metrics else 0,
                "monthly_revenue": current_metrics[5] if current_metrics else 0,
                "pending_invoices": current_metrics[6] if current_metrics else 0
            },
            "growth": [
                {
                    "month": row[0].strftime("%Y-%m"),
                    "new_tenants": row[1],
                    "new_mrr_cents": row[2]
                } for row in growth_metrics
            ],
            "plan_distribution": [
                {
                    "plan_name": row[0],
                    "price_cents": row[1],
                    "tenant_count": row[2],
                    "total_mrr_cents": row[3] or 0
                } for row in plan_distribution
            ]
        }


@router.get("/tenants")
async def get_all_tenants(ctx: AuthContext = Depends(require_role("owner"))):
    """
    Get all tenants with their subscription and usage information.
    """
    engine = get_sqlalchemy_engine()
    with engine.connect() as conn:
        tenants = conn.execute(text("""
            SELECT 
                t.tenant_id,
                t.name,
                ts.status as subscription_status,
                sp.name as plan_name,
                sp.price_cents,
                ts.started_at as subscription_started,
                ts.trial_ends_at,
                COUNT(DISTINCT ut.user_id) as user_count,
                COUNT(DISTINCT s.scenario_id) as scenario_count,
                COALESCE(mu.total_logins, 0) as monthly_logins,
                COALESCE(mu.total_data_imports, 0) as monthly_imports,
                COALESCE(SUM(CASE WHEN i.status = 'paid' AND i.created_at >= DATE_TRUNC('month', NOW()) THEN i.amount_cents END), 0) as monthly_revenue
            FROM tenants t
            LEFT JOIN tenant_subscriptions ts ON t.tenant_id = ts.tenant_id AND ts.status = 'active'
            LEFT JOIN subscription_plans sp ON ts.plan_id = sp.plan_id
            LEFT JOIN user_tenants ut ON t.tenant_id = ut.tenant_id
            LEFT JOIN scenarios s ON t.tenant_id = s.tenant_id
            LEFT JOIN monthly_usage mu ON t.tenant_id = mu.tenant_id AND mu.year_month = TO_CHAR(NOW(), 'YYYY-MM')
            LEFT JOIN invoices i ON t.tenant_id = i.tenant_id
            GROUP BY t.tenant_id, t.name, ts.status, sp.name, sp.price_cents, ts.started_at, ts.trial_ends_at, mu.total_logins, mu.total_data_imports
            ORDER BY subscription_started DESC NULLS LAST
        """)).fetchall()
        
        return {
            "tenants": [
                {
                    "tenant_id": row[0],
                    "name": row[1],
                    "subscription_status": row[2],
                    "plan_name": row[3],
                    "price_cents": row[4],
                    "subscription_started": row[5].isoformat() if row[5] else None,
                    "trial_ends_at": row[6].isoformat() if row[6] else None,
                    "user_count": row[7],
                    "scenario_count": row[8],
                    "monthly_logins": row[9],
                    "monthly_imports": row[10],
                    "monthly_revenue": row[11]
                } for row in tenants
            ]
        }


@router.get("/users")
async def get_all_users(ctx: AuthContext = Depends(require_role("owner"))):
    """
    Get all users across all tenants with their roles and activity.
    """
    engine = get_sqlalchemy_engine()
    with engine.connect() as conn:
        users = conn.execute(text("""
            SELECT 
                u.user_id,
                u.email,
                u.display_name,
                u.created_at,
                STRING_AGG(DISTINCT ut.tenant_id, ', ') as tenant_ids,
                STRING_AGG(DISTINCT ut.role, ', ') as roles,
                COUNT(DISTINCT ut.tenant_id) as tenant_count,
                COALESCE(ue.last_login, NULL) as last_login,
                COALESCE(ue.login_count, 0) as login_count_30d
            FROM users u
            LEFT JOIN user_tenants ut ON u.user_id = ut.user_id
            LEFT JOIN (
                SELECT 
                    user_id,
                    MAX(created_at) as last_login,
                    COUNT(*) as login_count
                FROM usage_events 
                WHERE event_type = 'login' AND created_at >= NOW() - INTERVAL '30 days'
                GROUP BY user_id
            ) ue ON u.user_id = ue.user_id
            GROUP BY u.user_id, u.email, u.display_name, u.created_at, ue.last_login, ue.login_count
            ORDER BY u.created_at DESC
        """)).fetchall()
        
        return {
            "users": [
                {
                    "user_id": row[0],
                    "email": row[1],
                    "display_name": row[2],
                    "created_at": row[3].isoformat() if row[3] else None,
                    "tenant_ids": row[4].split(', ') if row[4] else [],
                    "roles": row[5].split(', ') if row[5] else [],
                    "tenant_count": row[6],
                    "last_login": row[7].isoformat() if row[7] else None,
                    "login_count_30d": row[8]
                } for row in users
            ]
        }


@router.get("/revenue")
async def get_revenue_metrics(ctx: AuthContext = Depends(require_role("owner"))):
    """
    Get detailed revenue metrics and forecasting.
    """
    engine = get_sqlalchemy_engine()
    with engine.connect() as conn:
        # Monthly revenue trend (last 12 months)
        monthly_revenue = conn.execute(text("""
            SELECT 
                TO_CHAR(i.created_at, 'YYYY-MM') as month,
                SUM(CASE WHEN i.status = 'paid' THEN i.amount_cents ELSE 0 END) as paid_revenue,
                SUM(CASE WHEN i.status = 'pending' THEN i.amount_cents ELSE 0 END) as pending_revenue,
                COUNT(DISTINCT i.tenant_id) as paying_tenants
            FROM invoices i
            WHERE i.created_at >= DATE_TRUNC('month', NOW()) - INTERVAL '12 months'
            GROUP BY TO_CHAR(i.created_at, 'YYYY-MM')
            ORDER BY month DESC
        """)).fetchall()
        
        # Revenue by plan
        revenue_by_plan = conn.execute(text("""
            SELECT 
                sp.name as plan_name,
                SUM(CASE WHEN i.status = 'paid' THEN i.amount_cents ELSE 0 END) as total_revenue,
                COUNT(DISTINCT i.tenant_id) as tenant_count,
                AVG(i.amount_cents) as avg_invoice_amount
            FROM invoices i
            JOIN tenant_subscriptions ts ON i.tenant_id = ts.tenant_id
            JOIN subscription_plans sp ON ts.plan_id = sp.plan_id
            WHERE i.created_at >= DATE_TRUNC('month', NOW()) - INTERVAL '6 months'
            GROUP BY sp.name
            ORDER BY total_revenue DESC
        """)).fetchall()
        
        return {
            "monthly_trend": [
                {
                    "month": row[0],
                    "paid_revenue": row[1],
                    "pending_revenue": row[2],
                    "paying_tenants": row[3]
                } for row in monthly_revenue
            ],
            "revenue_by_plan": [
                {
                    "plan_name": row[0],
                    "total_revenue": row[1],
                    "tenant_count": row[2],
                    "avg_invoice_amount": float(row[3]) if row[3] else 0
                } for row in revenue_by_plan
            ]
        }


@router.post("/tenants")
async def create_tenant(
    tenant_data: Dict[str, Any],
    ctx: AuthContext = Depends(require_role("owner"))
):
    """
    Create a new tenant with subscription.
    """
    engine = get_sqlalchemy_engine()
    with engine.begin() as conn:
        tenant_id = tenant_data.get("tenant_id")
        name = tenant_data.get("name")
        plan_id = tenant_data.get("plan_id", "starter")
        
        if not tenant_id or not name:
            raise HTTPException(status_code=400, detail="tenant_id and name are required")
        
        # Create tenant
        conn.execute(text("""
            INSERT INTO tenants (tenant_id, name)
            VALUES (:tenant_id, :name)
        """), {"tenant_id": tenant_id, "name": name})
        
        # Create subscription
        conn.execute(text("""
            INSERT INTO tenant_subscriptions (tenant_id, plan_id, status)
            VALUES (:tenant_id, :plan_id, 'active')
        """), {"tenant_id": tenant_id, "plan_id": plan_id})
        
        return {"status": "created", "tenant_id": tenant_id}


@router.put("/tenants/{tenant_id}")
async def update_tenant(
    tenant_id: str,
    tenant_data: Dict[str, Any],
    ctx: AuthContext = Depends(require_role("owner"))
):
    """
    Update tenant information and subscription.
    """
    engine = get_sqlalchemy_engine()
    with engine.begin() as conn:
        # Update tenant name if provided
        if "name" in tenant_data:
            conn.execute(text("""
                UPDATE tenants SET name = :name WHERE tenant_id = :tenant_id
            """), {"name": tenant_data["name"], "tenant_id": tenant_id})
        
        # Update subscription if plan_id provided
        if "plan_id" in tenant_data:
            conn.execute(text("""
                UPDATE tenant_subscriptions 
                SET plan_id = :plan_id, updated_at = NOW()
                WHERE tenant_id = :tenant_id AND status = 'active'
            """), {"plan_id": tenant_data["plan_id"], "tenant_id": tenant_id})
        
        return {"status": "updated", "tenant_id": tenant_id}


@router.delete("/tenants/{tenant_id}")
async def delete_tenant(
    tenant_id: str,
    ctx: AuthContext = Depends(require_role("owner"))
):
    """
    Delete a tenant and all associated data.
    """
    engine = get_sqlalchemy_engine()
    with engine.begin() as conn:
        # Check if tenant exists
        result = conn.execute(text("""
            SELECT COUNT(*) FROM tenants WHERE tenant_id = :tenant_id
        """), {"tenant_id": tenant_id}).scalar()
        
        if not result:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # Delete tenant (CASCADE will handle related data)
        conn.execute(text("""
            DELETE FROM tenants WHERE tenant_id = :tenant_id
        """), {"tenant_id": tenant_id})
        
        return {"status": "deleted", "tenant_id": tenant_id}


def log_audit_event(conn, user_id: int, action_type: str, entity_type: str, entity_id: str, details: dict = None):
    """Helper function to log audit events"""
    conn.execute(text("""
        INSERT INTO audit_events (user_id, action_type, entity_type, entity_id, details)
        VALUES (:user_id, :action_type, :entity_type, :entity_id, :details)
    """), {
        "user_id": user_id,
        "action_type": action_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "details": json.dumps(details) if details else None
    })


@router.post("/users")
async def create_user(
    user_data: Dict[str, Any],
    ctx: AuthContext = Depends(require_role("owner"))
):
    """
    Create a new user.
    """
    from ..services.security import pwd
    import json
    
    engine = get_sqlalchemy_engine()
    with engine.begin() as conn:
        email = user_data.get("email")
        display_name = user_data.get("display_name")
        password = user_data.get("password")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="email and password are required")
        
        # Check if user already exists
        existing = conn.execute(text("""
            SELECT COUNT(*) FROM users WHERE email = :email
        """), {"email": email}).scalar()
        
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Hash password
        password_hash = pwd.hash(password)
        
        # Create user
        result = conn.execute(text("""
            INSERT INTO users (email, display_name, password_hash)
            VALUES (:email, :display_name, :password_hash)
            RETURNING user_id
        """), {
            "email": email,
            "display_name": display_name,
            "password_hash": password_hash
        })
        
        user_id = result.scalar()
        
        # Log audit event
        log_audit_event(conn, ctx.user_id, "CREATE", "user", str(user_id), {
            "email": email,
            "display_name": display_name,
            "created_by": ctx.user_id
        })
        
        return {"status": "created", "user_id": user_id}


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: Dict[str, Any],
    ctx: AuthContext = Depends(require_role("owner"))
):
    """
    Update user information.
    """
    import json
    
    engine = get_sqlalchemy_engine()
    with engine.begin() as conn:
        # Check if user exists and get current values
        result = conn.execute(text("""
            SELECT email, display_name FROM users WHERE user_id = :user_id
        """), {"user_id": user_id}).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        old_email = result.email
        old_display_name = result.display_name
        
        # Update user
        update_fields = []
        params = {"user_id": user_id}
        changes = {}
        
        if "email" in user_data:
            update_fields.append("email = :email")
            params["email"] = user_data["email"]
            changes["email"] = {"old": old_email, "new": user_data["email"]}
            
        if "display_name" in user_data:
            update_fields.append("display_name = :display_name")  
            params["display_name"] = user_data["display_name"]
            changes["display_name"] = {"old": old_display_name, "new": user_data["display_name"]}
        
        if update_fields:
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = :user_id"
            conn.execute(text(query), params)
            
            # Log audit event
            log_audit_event(conn, ctx.user_id, "UPDATE", "user", str(user_id), {
                "changes": changes,
                "updated_by": ctx.user_id
            })
        
        return {"status": "updated", "user_id": user_id}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    ctx: AuthContext = Depends(require_role("owner"))
):
    """
    Delete a user and all associated data.
    """
    import json
    
    engine = get_sqlalchemy_engine()
    with engine.begin() as conn:
        # Check if user exists and get user info for audit
        result = conn.execute(text("""
            SELECT email, display_name FROM users WHERE user_id = :user_id
        """), {"user_id": user_id}).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_email = result.email
        user_display_name = result.display_name
        
        # Log audit event before deletion
        log_audit_event(conn, ctx.user_id, "DELETE", "user", str(user_id), {
            "email": user_email,
            "display_name": user_display_name,
            "deleted_by": ctx.user_id
        })
        
        # Delete user (CASCADE will handle related data)
        conn.execute(text("""
            DELETE FROM users WHERE user_id = :user_id
        """), {"user_id": user_id})
        
        return {"status": "deleted", "user_id": user_id}


@router.get("/audit-log")
async def get_audit_log(
    ctx: AuthContext = Depends(require_role("owner")),
    limit: int = 50,
    offset: int = 0
):
    """
    Get audit log for all system activities.
    """
    engine = get_sqlalchemy_engine()
    with engine.connect() as conn:
        # Get audit entries
        result = conn.execute(text("""
            SELECT 
                ae.audit_id,
                ae.action_type,
                ae.entity_type,
                ae.entity_id,
                ae.user_id,
                u.email as user_email,
                u.display_name as user_name,
                ae.details,
                ae.created_at
            FROM audit_events ae
            LEFT JOIN users u ON ae.user_id = u.user_id
            ORDER BY ae.created_at DESC
            LIMIT :limit OFFSET :offset
        """), {"limit": limit, "offset": offset})
        
        audit_entries = []
        for row in result:
            audit_entries.append({
                "audit_id": row.audit_id,
                "action_type": row.action_type,
                "entity_type": row.entity_type,
                "entity_id": row.entity_id,
                "user_id": row.user_id,
                "user_email": row.user_email,
                "user_name": row.user_name,
                "details": row.details,
                "created_at": row.created_at.isoformat() if row.created_at else None
            })
        
        return {"audit_entries": audit_entries}
