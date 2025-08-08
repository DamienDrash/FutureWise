# Seeding

Dieses Verzeichnis enthält das Seeding-Skript für zwei Demo-Tenants (`alpha`, `beta`).

Voraussetzungen:
- PostgreSQL erreichbar per `DATABASE_URL` (z. B. postgresql+psycopg://user:pass@localhost:5432/futurewise)
- Datenbankschema migriert

Ausführen (im Container empfohlen):
```
make seed
```

Hinweise:
- Keine Mock-/Fake-Daten im Code. Das Frontend/Backend liest immer aus der DB.
- Dieses Skript wird regelmäßig erweitert (neue Tabellen, KPIs, Beispiele).
