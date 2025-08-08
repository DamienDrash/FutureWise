#!/usr/bin/env python3
import os
import sys
from textwrap import dedent
from sqlalchemy import create_engine, text


def get_database_url() -> str:
    return os.environ.get("DATABASE_URL", "")


def ensure_prerequisites(database_url: str) -> None:
    if not database_url:
        print(
            dedent(
                """
                DATABASE_URL ist nicht gesetzt. Bitte setzen und erneut ausführen.
                Beispiel: export DATABASE_URL=postgresql://futurewise:futurewise@localhost:5432/futurewise
                """
            ).strip()
        )
        sys.exit(0)


def run_migrations_if_any(engine) -> None:
    pass


def seed_tenants(engine) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS tenants (
                  tenant_id TEXT PRIMARY KEY,
                  name TEXT NOT NULL UNIQUE
                );
                """
            )
        )
        for tenant_id, name in [("alpha", "Alpha Demo Tenant"), ("beta", "Beta Demo Tenant")]:
            conn.execute(text("DELETE FROM tenants WHERE tenant_id = :tid OR name = :name"), {"tid": tenant_id, "name": name})
            conn.execute(
                text("INSERT INTO tenants (tenant_id, name) VALUES (:tid, :name)"),
                {"tid": tenant_id, "name": name},
            )
        # Defaults
        conn.execute(
            text(
                """
                INSERT INTO tenant_settings(tenant_id, default_currency, default_tax_rate, default_channel)
                VALUES ('alpha', 'EUR', 0.19, 'general')
                ON CONFLICT (tenant_id) DO UPDATE SET updated_at = NOW();
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT INTO tenant_settings(tenant_id, default_currency, default_tax_rate, default_channel)
                VALUES ('beta', 'USD', 0.07, 'marketplace')
                ON CONFLICT (tenant_id) DO UPDATE SET updated_at = NOW();
                """
            )
        )

        # Seed Users & Roles
        # Minimal auth tables (idempotent) to ensure inserts work even if init.sql has not yet created them
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS users (
              user_id BIGSERIAL PRIMARY KEY,
              email TEXT UNIQUE NOT NULL,
              password_hash TEXT NOT NULL,
              display_name TEXT,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        ))
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS user_tenants (
              user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
              tenant_id TEXT REFERENCES tenants(tenant_id) ON DELETE CASCADE,
              role TEXT NOT NULL DEFAULT 'viewer',
              PRIMARY KEY (user_id, tenant_id)
            );
            """
        ))

        # Helper to upsert a user and assign a role to a tenant
        def upsert_user(email: str, password_hash: str, display: str, tenant: str, role: str):
            row = conn.execute(text("SELECT user_id FROM users WHERE email=:e"), {"e": email}).first()
            if row:
                uid = row[0]
            else:
                uid = conn.execute(text("INSERT INTO users(email,password_hash,display_name) VALUES (:e,:p,:d) RETURNING user_id"), {"e": email, "p": password_hash, "d": display}).scalar()
            conn.execute(text("INSERT INTO user_tenants(user_id,tenant_id,role) VALUES (:u,:t,:r) ON CONFLICT (user_id,tenant_id) DO UPDATE SET role=:r"), {"u": uid, "t": tenant, "r": role})

        # Password hashes (bcrypt) for demo: password = "secret"
        from passlib.context import CryptContext
        pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
        h = pwd.hash("secret")

        # Global/Owner
        upsert_user("owner@futurewise.local", h, "Owner", "alpha", "owner")
        # System Manager (platform-level)
        upsert_user("sysman@futurewise.local", h, "System Manager", "alpha", "system_manager")
        # Tenant Admins
        upsert_user("alpha.admin@futurewise.local", h, "Alpha Admin", "alpha", "tenant_admin")
        upsert_user("beta.admin@futurewise.local", h, "Beta Admin", "beta", "tenant_admin")
        # Tenant Users
        upsert_user("alpha.user@futurewise.local", h, "Alpha User", "alpha", "tenant_user")
        upsert_user("beta.user@futurewise.local", h, "Beta User", "beta", "tenant_user")


def main() -> None:
    database_url = get_database_url()
    ensure_prerequisites(database_url)

    engine = create_engine(database_url, pool_pre_ping=True)
    print("Verbunden mit:", database_url)

    run_migrations_if_any(engine)
    seed_tenants(engine)

    print("Seeding abgeschlossen.")


if __name__ == "__main__":
    main()
