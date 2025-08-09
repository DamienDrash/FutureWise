# Development Best Practices

## Context
Global development guidelines for Agent OS projects.  
These apply to backend (Python), frontend (Svelte/TypeScript), infrastructure (Docker/YAML), CI/CD, and documentation.

---

## Core Principles

### Keep It Simple
- Implement solutions in the fewest lines possible without sacrificing clarity
- Avoid over-engineering; choose straightforward approaches over clever tricks
- Break down complex problems into smaller, testable units

### Optimize for Readability
- Code must be **clear, self-documenting**, and follow the agreed code style
- Use descriptive variable, function, and class names
- Add comments for **"why"**, not **"what"**
- Follow NumPy-style docstrings for all public modules, classes, and functions

### DRY (Don't Repeat Yourself)
- Extract repeated business logic into private functions or utilities
- Extract repeated UI markup into reusable components
- Create shared modules for common operations

### Single Responsibility
- Each file, class, and function should have **one clear responsibility**
- Each microservice should encapsulate a specific business domain

---

## Architecture Guidelines

### Microservices
- Each service must be:
  - **A standalone Docker container**
  - **In its own directory** with dedicated `Dockerfile`, configuration, and source folder
- All services are orchestrated via `docker-compose.yml`
- **Environment variables:** `.env` files for secrets
- **Service configuration:** YAML files for static/non-sensitive settings
- Docker Compose must load `.env` and `.yml` configs and pass them to relevant services

### API Design
- Backend APIs must be built with FastAPI
- Use clear and consistent naming for endpoints and parameters
- Include OpenAPI/Swagger documentation
- All APIs must handle error responses gracefully with standardized error structures

### Data Layer
- PostgreSQL as the default database
- Alembic for migrations
- dbt for ETL when needed
- Use `pgvector` only when vector search is required

---

## Documentation

### Language & Style
- **English only** for all comments, docstrings, and documentation
- NumPy-style docstrings required for all public-facing functions, classes, and modules
- Keep README files up to date for each microservice

### Issue Tracking in Code
- Use comment tags for:
  - `# TODO:` – pending tasks
  - `# FIXME:` – known bugs
  - `# BUG:` – confirmed issues
  - `# NOTE:` – important clarifications
  - `# OPTIMIZE:` – possible performance improvements
  - `# SECURITY:` – potential security concerns
- Include description, date (`YYYY-MM-DD`), and author initials

Example:
```python
# TODO: Implement Redis caching for session data
# Date: 2025-08-02
# Author: DF


---

Quality Assurance

Testing
	•	Backend: pytest with Arrange-Act-Assert structure
	•	Frontend: vitest or playwright depending on scope
	•	Maintain high test coverage for core business logic
	•	Use fixtures for test data

Code Quality
	•	Lint before committing:
	•	Python: black, isort, flake8, mypy
	•	Frontend: ESLint, Prettier
	•	No merge if tests or linting fail

---

Security
	•	No secrets or credentials in source control
	•	Store sensitive data only in .env files or secrets manager (Vault / AWS Secrets Manager)
	•	Sanitize all user inputs
	•	Enforce HTTPS for all API endpoints
	•	Review dependencies regularly for vulnerabilities

---

CI/CD & Deployment
	•	Use GitHub Actions for build, test, and deploy pipelines
	•	Enforce branch protection rules on main and staging
	•	Deployments must be automated and reproducible
	•	Keep Docker images minimal and version-pinned
	•	Use feature flags for optional services

---

Monitoring & Observability
	•	Prometheus + Grafana for metrics (_ENABLE_METRICS=true in Dev)
	•	Loki + Promtail + Grafana for logging by default; ELK only when required
	•	OpenTelemetry for tracing in production; optional in Dev/Staging via ENABLE_OTEL=false

---

Note: These practices are mandatory for all projects unless explicitly overridden in project-specific documentation.

