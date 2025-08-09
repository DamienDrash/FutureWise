# Tech Stack

## Context
Global tech stack defaults for Agent OS projects, overridable in project-specific `.agent-os/product/tech-stack.md`.

---

## Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI (REST + WebSocket APIs)
- **Architecture:** Microservices in separate Docker containers
- **Config Management:** `.env` files for secrets, YAML files for service configurations, loaded via Docker Compose
- **Task Queue / Messaging:** Celery with Redis *(Opt-in, not included in slimline project start)*
- **Authentication Standard:** JWT
- **Logging Standard:** Centralized structured logging in JSON format
- **Testing Framework:** pytest

---

## Frontend
- **Language:** TypeScript
- **Framework:** Svelte (SvelteKit optional for SSR)
- **Styling:** TailwindCSS
- **UI Components:**
  - Headless UI for behavior
  - DaisyUI for visual styling
- **Icons:**
  - Heroicons as the standard icon set
  - Lucide as an additional library
- **Build Tool:** Vite

---

## Database & Data Layer
- **Primary Database:** PostgreSQL 15+
- **Vector Support:** pgvector extension *(enabled only if required)*
- **ORM:** SQLAlchemy 2.x (core kept slim, schema-decoupled)
- **Schema Layer:** Pydantic v2 only when `FEATURE_SCHEMA_LAYER=true`, exclusively at API input/output boundaries
- **Migrations:** Alembic
- **ETL:** dbt *(if required)*

---

## Infrastructure & Deployment
- **Containerization:** Docker (for both Dev and Prod)
- **Orchestration (Default):** Docker Compose
- **Scale-up Path:** Transition to k3s/Kubernetes when cluster size, service count, or SLAs demand
- **Secrets Management (Prod):**
  - HashiCorp Vault (default for on-premise/hybrid setups)
  - AWS Secrets Manager only if the stack runs fully on AWS
- **Storage Provider:**
  - MinIO (default) – S3-compatible, lightweight, and free
  - AWS S3 optional via `FEATURE_S3=true`
- **CDN (Optional):** CloudFront

---

## CI/CD
- **Platform:** GitHub Actions
- **Triggers:** Merge into `main` or `staging`
- **Build:** Docker Build & Push to container registry
- **Tests & Code Quality:**
  - pytest
  - Black
  - isort
  - flake8
  - mypy
- **Deployment:** Automated to staging and production

---

## Monitoring & Observability
- **Metrics:**
  - Prometheus + Grafana as the default stack for both Prod and Dev
  - Enabled in Dev only if `_ENABLE_METRICS=true`
- **Logging:**
  - Loki + Promtail + Grafana by default
  - ELK stack only for compliance/SIEM/full-text search requirements
- **Tracing:**
  - OpenTelemetry tracing enabled in production deployments
  - In Dev/Staging, controlled via `ENABLE_OTEL=false`

---

**Note:** Optional features are controlled via environment flags.  
These allow a minimal, slimline project start while keeping advanced capabilities available when needed.
