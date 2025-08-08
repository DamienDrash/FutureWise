from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy import text
from ..services.db import get_sqlalchemy_engine
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt

router = APIRouter()

SECRET = "change-me-in-env"
ALGO = "HS256"
ACCESS_MINUTES = 60 * 12
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Minimal schema tables (idempotent created via init.sql in prod; here runtime-safe)

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
        # ensure tenant exists
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
async def login(email: str = Form(...), password: str = Form(...), tenant_id: str = Form(...)):
    ensure_tables()
    engine = get_sqlalchemy_engine()
    with engine.connect() as conn:
        row = conn.execute(text("SELECT u.user_id, u.password_hash, COALESCE(ut.role,'viewer') FROM users u LEFT JOIN user_tenants ut ON ut.user_id=u.user_id AND ut.tenant_id=:t WHERE email=:e"), {"e": email, "t": tenant_id}).first()
        if not row or not pwd.verify(password, row[1]):
            raise HTTPException(status_code=401, detail="invalid credentials")
        token = create_token({"sub": str(row[0]), "tenant_id": tenant_id, "role": row[2]})
        return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
async def me(token: str):
    try:
        data = jwt.decode(token, SECRET, algorithms=[ALGO])
        return data
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")
