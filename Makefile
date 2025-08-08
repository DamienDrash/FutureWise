SHELL := /bin/bash

.PHONY: up down logs seed rebuild

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

down:
	docker compose down -v
