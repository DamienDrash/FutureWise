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
