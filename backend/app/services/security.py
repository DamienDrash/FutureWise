from fastapi import Header, HTTPException, Depends
from jose import jwt
from typing import Optional
import os

ALGO = os.getenv("JWT_ALGO", "HS256")
SECRET = os.getenv("JWT_SECRET", "dev-change-me")

ROLE_LEVEL = {
    "viewer": 1,
    "analyst": 2,
    "manager": 3,
}

class AuthContext:
    def __init__(self, user_id: str, tenant_id: str, role: str):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.role = role


def decode_token(authorization: Optional[str] = Header(None)) -> AuthContext:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        data = jwt.decode(token, SECRET, algorithms=[ALGO])
        return AuthContext(user_id=data.get("sub"), tenant_id=data.get("tenant_id"), role=data.get("role", "viewer"))
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")


def require_role(min_role: str):
    def dependency(ctx: AuthContext = Depends(decode_token)) -> AuthContext:
        have = ROLE_LEVEL.get(ctx.role, 0)
        need = ROLE_LEVEL.get(min_role, 999)
        if have < need:
            raise HTTPException(status_code=403, detail="insufficient role")
        return ctx
    return dependency
