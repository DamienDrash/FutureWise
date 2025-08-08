SHELL := /bin/bash

.PHONY: up down logs seed rebuild import-api import-csv import-xls import-webhook

up:
	docker compose up -d

rebuild:
	docker compose build --no-cache backend frontend
	docker compose up -d --force-recreate

logs:
	docker compose logs -f --tail=200

seed:
	# Seeding wird im Backend-Container mit installiertem SQLAlchemy ausgeführt
	DockerDBURL=postgresql+psycopg://futurewise:futurewise@db:5432/futurewise; \
	docker compose exec -e DATABASE_URL=$$DockerDBURL backend python3 scripts/seed/seed.py

import-api:
	docker compose exec backend python3 scripts/import/api_import.py

import-csv:
	docker compose exec backend sh -lc 'API_BASE=http://localhost:8000 TENANT_ID=alpha scripts/import/csv_import.sh'

import-xls:
	docker compose exec backend python3 scripts/import/generate_xls_and_import.py

import-webhook:
	docker compose exec backend sh -lc 'API_BASE=http://localhost:8000 TENANT_ID=alpha scripts/import/webhook_import.sh'

down:
	docker compose down -v
