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

Setze `DATABASE_URL` und starte das Skript:

```
export DATABASE_URL=postgresql://futurewise:futurewise@localhost:5432/futurewise
python scripts/seed/seed.py
```

Hinweis: Keine Fake-, Sample- oder Mock-Daten. UI und API lesen immer aus der DB.

## Git Workflow

- main: stabil
- dev: Integration
- feature/<name>: Feature-Entwicklung; Merge in dev nach Nutzer-Freigabe

## Tech Stack

- Backend: FastAPI (Python 3.11), SQLAlchemy, PostgreSQL
- Frontend: Svelte (Vite)
- Infra: Docker Compose
