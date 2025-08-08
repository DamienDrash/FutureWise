# FutureWise

Multi-tenant SaaS für E‑Commerce Szenario‑Management.

## Start (Dev)

Voraussetzungen: Docker, Docker Compose

```
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- DB: postgres://futurewise:futurewise@localhost:5432/futurewise

## Seeding

Empfohlen im Backend-Container ausführen (stellt sicher, dass alle Python-Dependencies vorhanden sind):

```
make seed
```

## Import-Flows testen (API / CSV / XLS / Webhook)

- API (JSON):
```
make import-api
```

- CSV (Datei: `data/import/alpha_kpi_daily.csv`):
```
make import-csv
```

- XLS (CSV wird in-memory zu XLSX konvertiert und importiert):
```
make import-xls
```

- Webhook (JSON-Form-Field):
```
make import-webhook
```

Hinweis: Keine Fake-, Sample- oder Mock-Daten zur UI/APIs. Alle Daten werden in die DB geschrieben und von dort gelesen. Die Dateien/Skripte dienen zur initialen Befüllung (Seeding/Import) der Demo-Tenants.

## Git Workflow

- main: stabil
- dev: Integration
- feature/<name>: Feature-Entwicklung; Merge in dev nach Nutzer-Freigabe

## Useful

- `make up` / `make down`
- `make logs`
- `make seed`
- `make import-*`

## Tech Stack

- Backend: FastAPI (Python 3.11), SQLAlchemy, PostgreSQL
- Frontend: Svelte (Vite), TailwindCSS + DaisyUI
- Infra: Docker Compose
