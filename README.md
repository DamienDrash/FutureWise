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

Alternativ lokal (nur wenn Python-Dependencies installiert sind):
```
export DATABASE_URL=postgresql://futurewise:futurewise@localhost:5432/futurewise
python scripts/seed/seed.py
```

Hinweis: Keine Fake-, Sample- oder Mock-Daten. UI und API lesen immer aus der DB.

## Git Workflow

- main: stabil
- dev: Integration
- feature/<name>: Feature-Entwicklung; Merge in dev nach Nutzer-Freigabe

## Useful

- `make up` / `make down`
- `make logs`
- `make seed`

## Tech Stack

- Backend: FastAPI (Python 3.11), SQLAlchemy, PostgreSQL
- Frontend: Svelte (Vite)
- Infra: Docker Compose
