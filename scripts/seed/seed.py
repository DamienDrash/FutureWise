#!/usr/bin/env python3
import os
import sys
from textwrap import dedent


def get_database_url() -> str:
    return os.environ.get("DATABASE_URL", "")


def ensure_prerequisites(database_url: str) -> None:
    if not database_url:
        print(
            dedent(
                """
                DATABASE_URL ist nicht gesetzt. Bitte setzen und erneut ausführen.
                Beispiel: export DATABASE_URL=postgresql://user:pass@localhost:5432/futurewise
                """
            ).strip()
        )
        sys.exit(0)


def seed_tenant_alpha() -> None:
    # Platzhalter: Wird implementiert, sobald das DB-Schema feststeht
    print("Seede Demo-Tenant 'alpha' ... (wird mit Schema implementiert)")


def seed_tenant_beta() -> None:
    # Platzhalter: Wird implementiert, sobald das DB-Schema feststeht
    print("Seede Demo-Tenant 'beta' ... (wird mit Schema implementiert)")


def main() -> None:
    database_url = get_database_url()
    ensure_prerequisites(database_url)

    print("Verbunden mit:", database_url)
    print("Starte Seeding...")

    seed_tenant_alpha()
    seed_tenant_beta()

    print("Seeding abgeschlossen.")


if __name__ == "__main__":
    main()
