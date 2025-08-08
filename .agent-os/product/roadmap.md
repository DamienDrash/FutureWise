# Product Roadmap

## Phase 1: MVP

**Goal:** Validate end-to-end flow from data import to visual scenario comparison for single-tenant pilots
**Success Criteria:** Import data in <1 day; create baseline + 2 scenarios; decision meeting using the app

### Features

- [x] Data import (API, CSV, XLS, Webhook) with schema validation `M`
- [x] Baseline calculation (KPI aggregation + backfill) `S`
- [x] Adjustable indicators (elasticity, promo uplift, seasonality) `M`
- [x] Visual forecasting (charts, KPIs, intervals, compare) `M`
- [x] Scenario storage & versioning (save, clone, tag) `S`
- [ ] Authentication & basic RBAC `S`
- [x] Seeding script for two demo tenants (continually extended) `S`
- [x] Import logging (events + error details) `S`
- [x] UI: File upload (CSV/XLS) mit Validierung und Preview `M`
- [x] API Docs (OpenAPI) für Import/Scenario-Endpunkte `S`

### Dependencies

- PostgreSQL, FastAPI service, SvelteKit app, Docker Compose

## Phase 2: SaaS Foundation

**Goal:** From prototype to sellable SaaS (multi-tenant, auth, roles, billing, marketing)
**Success Criteria:** Users can sign-up/login, manage tenants, assign roles; pricing page; subscription metadata stored; public marketing site live

### Features

- [x] Public Site: Landing, Pricing Seiten `S`
- [x] Basic Auth UI & Layout: Login/Register, Sidebar, Management `S`
- [x] Route Guards: Client + Server (SvelteKit hooks) `S`
- [x] Backend RBAC Guards (hierarchisch) `M`
- [~] Cookies (HttpOnly) + CSRF (Basis integriert; ausrollen auf alle Mutations) `M`
- [ ] Email (Transaktional): Einladungen, Passwort-Reset `M`
- [x] Subscriptions: Stripe Checkout (Session) `M`
- [ ] Billing Webhooks/Plan Gates (Limits, UI Badge) `M`
- [ ] Admin Console: Übersicht über Tenants, Nutzungsmetriken, Limits `M`
- [ ] Legal/Compliance: Impressum, Datenschutz, ToS `S`

## Phase 3: Differentiators

**Goal:** Improve accuracy, governance, and collaboration
**Success Criteria:** +10-20% forecast error reduction; auditable decisions; multi-user workflows

### Features

- [ ] ML model selection & backtesting with metrics (MAPE, WAPE) `M`
- [ ] Confidence intervals & uncertainty visualization `S`
- [ ] Audit trail (assumptions, changes, approvals) `S`
- [ ] Sharing & review/approval workflow `M`
- [ ] Tenant isolation & advanced RBAC `M`
- [ ] API & Webhooks for automation `S`

## Phase 4: Scale & Enterprise

**Goal:** Scale to many tenants; enhance performance, reliability, and ecosystem integrations
**Success Criteria:** 50+ tenants; p95 < 300ms for key APIs; near-zero manual ops

### Features

- [ ] Incremental data loads & connectors library `M`
- [ ] Caching and async pipelines for heavy simulations `M`
- [ ] Multi-region readiness & backups `L`
- [ ] SSO (SAML/OIDC) and audit exports `M`
- [ ] Integration apps (e.g., Shopify, BigCommerce, GA4, Ads) `L`
- [ ] Observability (tracing, metrics, logs) `S`
