# Technical Stack

- **application_framework:** FastAPI (Python 3.11+)
- **database_system:** PostgreSQL 15+
- **javascript_framework:** SvelteKit (TypeScript, Vite)
- **import_strategy:** node
- **css_framework:** Tailwind CSS v3 + PostCSS
- **ui_component_library:** Headless UI (behavior) + DaisyUI (styling)
- **fonts_provider:** Google Fonts
- **icon_library:** Heroicons (primary) + Lucide (additional)
- **application_hosting:** Docker Compose (default); path to k8s when needed
- **database_hosting:** Docker Compose (default dev); managed PostgreSQL optional in prod
- **asset_hosting:** MinIO (S3-compatible) by default; AWS S3 optional via FEATURE_S3=true
- **deployment_solution:** GitHub Actions (Docker build & push; deploy to staging/prod)
- **code_repository_url:** https://github.com/DamienDrash/FutureWise.git

## Data Policy
- Frontend und Backend verwenden niemals Fake-, Sample- oder Mock-Daten.
- Alle UI-Ansichten und APIs lesen stets aus der Datenbank.
- Für Tests und Demos werden Daten ausschließlich per Seeding in die Datenbank geschrieben (keine Mock-APIs, keine In-Memory-Fakes).
