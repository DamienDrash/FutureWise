from fastapi import APIRouter, HTTPException, Request, Form
import os
import stripe
from sqlalchemy import text
from ..services.db import get_sqlalchemy_engine

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


@router.post("/checkout")
async def create_checkout(tenant_id: str = Form(...)):
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="stripe not configured")
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": os.getenv("STRIPE_PRICE_ID", ""), "quantity": 1}],
        success_url=f"{FRONTEND_URL}/?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{FRONTEND_URL}/pricing",
        metadata={"tenant_id": tenant_id},
    )
    return {"id": session.id, "url": session.url}


@router.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("Stripe-Signature")
    try:
        evt = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if evt["type"] in ("checkout.session.completed", "customer.subscription.updated", "customer.subscription.deleted"):
        data = evt["data"]["object"]
        tenant_id = (data.get("metadata", {}) or {}).get("tenant_id")
        status = data.get("status") or data.get("subscription") or "unknown"
        engine = get_sqlalchemy_engine()
        with engine.begin() as conn:
            conn.execute(text("CREATE TABLE IF NOT EXISTS subscriptions (tenant_id TEXT PRIMARY KEY, status TEXT, updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW())"))
            conn.execute(text("INSERT INTO subscriptions(tenant_id,status) VALUES (:t,:s) ON CONFLICT (tenant_id) DO UPDATE SET status=:s, updated_at=NOW()"), {"t": tenant_id, "s": str(status)})
    return {"received": True}
