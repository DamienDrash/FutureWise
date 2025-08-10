from fastapi import APIRouter, HTTPException, Depends, Form, Response, Request
from sqlalchemy import text
from ..services.db import get_sqlalchemy_engine
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
import os
from ..services.security import issue_csrf_token

router = APIRouter()

SECRET = os.getenv("JWT_SECRET", "dev-change-me")
ALGO = os.getenv("JWT_ALGO", "HS256")
ACCESS_MINUTES = int(os.getenv("JWT_ACCESS_MIN", "720"))
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECURE_COOKIE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", None)


def ensure_tables():
    engine = get_sqlalchemy_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
              user_id BIGSERIAL PRIMARY KEY,
              email TEXT UNIQUE NOT NULL,
              password_hash TEXT NOT NULL,
              display_name TEXT,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_tenants (
              user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
              tenant_id TEXT REFERENCES tenants(tenant_id) ON DELETE CASCADE,
              role TEXT NOT NULL DEFAULT 'viewer',
              PRIMARY KEY (user_id, tenant_id)
            );
        """))


def create_token(payload: dict) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=ACCESS_MINUTES)
    to_encode = {"iat": int(now.timestamp()), "exp": int(exp.timestamp()), **payload}
    return jwt.encode(to_encode, SECRET, algorithm=ALGO)


@router.post("/register")
async def register(email: str = Form(...), password: str = Form(...), display_name: str = Form(""), tenant_id: str = Form(...), role: str = Form("manager")):
    ensure_tables()
    engine = get_sqlalchemy_engine()
    with engine.begin() as conn:
        t = conn.execute(text("SELECT 1 FROM tenants WHERE tenant_id=:t"), {"t": tenant_id}).first()
        if not t:
            raise HTTPException(status_code=400, detail="tenant does not exist")
        h = pwd.hash(password)
        try:
            uid = conn.execute(text("INSERT INTO users(email, password_hash, display_name) VALUES (:e,:p,:d) RETURNING user_id"), {"e": email, "p": h, "d": display_name}).scalar()
        except Exception:
            raise HTTPException(status_code=400, detail="email already registered")
        conn.execute(text("INSERT INTO user_tenants(user_id, tenant_id, role) VALUES (:u,:t,:r) ON CONFLICT (user_id,tenant_id) DO UPDATE SET role=EXCLUDED.role"), {"u": uid, "t": tenant_id, "r": role})
    return {"status": "ok"}


@router.post("/login")
async def login(response: Response, email: str = Form(...), password: str = Form(...), tenant_id: str | None = Form(None)):
    ensure_tables()
    engine = get_sqlalchemy_engine()
    with engine.connect() as conn:
        user = conn.execute(text("SELECT user_id, password_hash FROM users WHERE email=:e"), {"e": email}).first()
        if not user or not pwd.verify(password, user[1]):
            raise HTTPException(status_code=401, detail="invalid credentials")

        # Determine tenant + role
        selected_tenant = None
        selected_role = None
        if tenant_id:
            r = conn.execute(text("SELECT role FROM user_tenants WHERE user_id=:u AND tenant_id=:t"), {"u": user[0], "t": tenant_id}).first()
            if not r:
                raise HTTPException(status_code=403, detail="no access to tenant")
            selected_tenant = tenant_id
            selected_role = r[0]
        else:
            # pick highest-privilege assignment deterministically
            row = conn.execute(text(
                """
                SELECT tenant_id, role
                FROM user_tenants
                WHERE user_id=:u
                ORDER BY CASE role
                    WHEN 'owner' THEN 100
                    WHEN 'system_manager' THEN 90
                    WHEN 'tenant_admin' THEN 80
                    WHEN 'manager' THEN 70
                    WHEN 'analyst' THEN 60
                    WHEN 'tenant_user' THEN 50
                    WHEN 'viewer' THEN 40
                    ELSE 0 END DESC, tenant_id ASC
                LIMIT 1
                """
            ), {"u": user[0]}).first()
            if not row:
                raise HTTPException(status_code=403, detail="user has no tenant assignment")
            selected_tenant = row[0]
            selected_role = row[1]

        token = create_token({"sub": str(user[0]), "tenant_id": selected_tenant, "role": selected_role})
        csrf = issue_csrf_token()
        response.set_cookie("access_token", token, httponly=True, secure=SECURE_COOKIE, samesite="lax", domain=COOKIE_DOMAIN, path="/")
        response.set_cookie("csrf_token", csrf, httponly=False, secure=SECURE_COOKIE, samesite="lax", domain=COOKIE_DOMAIN, path="/")
        return {"status": "ok", "tenant_id": selected_tenant, "role": selected_role}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("csrf_token", path="/")
    return {"status": "ok"}


@router.get("/me")
async def me(request: Request):
    tok = request.cookies.get("access_token")
    if not tok:
        raise HTTPException(status_code=401, detail="not logged in")
    try:
        data = jwt.decode(tok, SECRET, algorithms=[ALGO])
        user_id = data.get("sub")
        tenant_id = data.get("tenant_id")
        role = data.get("role", "viewer")
        
        # Get additional user info from database
        engine = get_sqlalchemy_engine()
        with engine.connect() as conn:
            user_row = conn.execute(text("SELECT email, display_name FROM users WHERE user_id = :uid"), {"uid": user_id}).first()
            if user_row:
                return {
                    "user_id": user_id, 
                    "email": user_row[0],
                    "display_name": user_row[1],
                    "tenant_id": tenant_id, 
                    "role": role
                }
            else:
                raise HTTPException(status_code=404, detail="user not found")
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")
