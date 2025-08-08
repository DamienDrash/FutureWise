import os
from sqlalchemy import create_engine


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        # Kein Fallback auf Mock/Memory erlaubt
        raise RuntimeError("DATABASE_URL ist nicht gesetzt")
    return url


def get_sqlalchemy_engine():
    return create_engine(get_database_url(), pool_pre_ping=True)
