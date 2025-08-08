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
async def login(response: Response, email: str = Form(...), password: str = Form(...), tenant_id: str = Form(...)):
    ensure_tables()
    engine = get_sqlalchemy_engine()
    with engine.connect() as conn:
        row = conn.execute(text("SELECT u.user_id, u.password_hash, COALESCE(ut.role,'viewer') FROM users u LEFT JOIN user_tenants ut ON ut.user_id=u.user_id AND ut.tenant_id=:t WHERE email=:e"), {"e": email, "t": tenant_id}).first()
        if not row or not pwd.verify(password, row[1]):
            raise HTTPException(status_code=401, detail="invalid credentials")
        token = create_token({"sub": str(row[0]), "tenant_id": tenant_id, "role": row[2]})
        csrf = issue_csrf_token()
        # HttpOnly cookie for token, Non-HttpOnly for CSRF echo
        response.set_cookie("access_token", token, httponly=True, secure=SECURE_COOKIE, samesite="lax", domain=COOKIE_DOMAIN, path="/")
        response.set_cookie("csrf_token", csrf, httponly=False, secure=SECURE_COOKIE, samesite="lax", domain=COOKIE_DOMAIN, path="/")
        return {"status": "ok"}


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
        return data
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")
