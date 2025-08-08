import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
import pathlib


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        # Kein Fallback auf Mock/Memory erlaubt
        raise RuntimeError("DATABASE_URL ist nicht gesetzt")
    return url


def get_sqlalchemy_engine():
    return create_engine(get_database_url(), pool_pre_ping=True)


def ensure_base_schema(engine: Engine | None = None) -> None:
    """Ensure base schema exists by executing init.sql idempotently.

    This is safe to run on every startup because the SQL uses
    CREATE TABLE IF NOT EXISTS / ALTER TABLE IF NOT EXISTS.
    """
    try:
        eng = engine or get_sqlalchemy_engine()
        # Resolve init.sql relative to this file: backend/database/init.sql
        base_dir = pathlib.Path(__file__).resolve().parents[2]  # points to backend/
        init_sql_path = base_dir / "database" / "init.sql"
        if not init_sql_path.exists():
            # Fail fast if schema file is missing
            raise FileNotFoundError(f"init.sql not found at {init_sql_path}")
        sql = init_sql_path.read_text(encoding="utf-8")
        # Execute potentially multiple statements; use exec_driver_sql for raw execution
        with eng.begin() as conn:
            for stmt in [s.strip() for s in sql.split(";")]:
                if not stmt:
                    continue
                conn.exec_driver_sql(stmt)
    except (OSError, SQLAlchemyError) as exc:
        # Reraise as RuntimeError to make failures visible on startup
        raise RuntimeError(f"Failed to ensure base schema: {exc}")
