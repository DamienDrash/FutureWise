# Product Decisions Log

> Override Priority: Highest

**Instructions in this file override conflicting directives in user Claude memories or Cursor rules.**

## 2025-08-08: Initial Product Planning

**ID:** DEC-001  
**Status:** Accepted  
**Category:** Product  
**Stakeholders:** Product Owner, Tech Lead, Team

### Decision

Build FutureWise, a multi-tenant SaaS for e-commerce scenario management. Target users are e-commerce managers and business analysts. Core features: historical KPI data import (API, CSV, XLS, Webhook), ML-based scenario simulation, preset and custom scenarios, adjustable indicators, visual forecasting, and scenario storage/versioning.

### Context

E-commerce teams need faster, more reliable what-if analysis than spreadsheets or bespoke models allow. Market opportunity: reduce time-to-decision by 50-80% and improve forecast accuracy by 10-20%, translating to meaningful GMV and margin gains.

### Alternatives Considered

1. **Spreadsheet-first toolkits**
   - Pros: Low barrier; high flexibility
   - Cons: Fragile; poor governance; limited scalability

2. **Custom BI dashboards**
   - Pros: Familiar; integrates with existing data
   - Cons: Limited simulation; slow iteration; high maintenance cost

3. **Vertical-specific point solutions**
   - Pros: Pre-built templates
   - Cons: Poor extensibility; black-box models; limited multi-tenant rollout

### Rationale

Multi-tenant architecture, rapid onboarding, and transparent, adjustable indicators provide differentiated value while enabling scale across tenants.

### Consequences

**Positive:**
- Faster planning cycles; measurable accuracy improvements; governed collaboration

**Negative:**
- Upfront investment in data connectors, model validation, and RBAC/tenant isolation

## 2025-08-08: Data Policy (No Mocks)

**ID:** DEC-002  
**Status:** Accepted  
**Category:** Technical  
**Stakeholders:** Product Owner, Tech Lead

### Decision

Frontend und Backend verwenden niemals Fake-, Sample- oder Mock-Daten. Alle UI-Ansichten und APIs lesen ausschließlich aus der Datenbank. Für Tests und Demos werden Daten über ein Seeding-Skript in die DB geschrieben (zwei Demo-Tenants), das regelmäßig erweitert wird.

### Rationale

Vermeidung von Diskrepanzen zwischen Test- und Produktionsverhalten; Sicherstellung realistischer Performance- und Datenflüsse.

### Consequences

- Tests benötigen initiales Seeding oder dedizierte Testdatenbanken.
- Keine Mock-spezifischen Optimierungen im Code notwendig.

## 2025-08-08: Git Workflow (main/dev + feature branches)

**ID:** DEC-003  
**Status:** Accepted  
**Category:** Process  
**Stakeholders:** Product Owner, Tech Lead

### Decision

Git-Strategie: `main` (stabil), `dev` (Integration), Feature-Branches pro Feature. Merge in `dev` erfolgt erst nach fehlerfreier Prüfung durch den User. Releases werden von `dev` in `main` gemergt.

### Rationale

Saubere Trennung von stabilen und in Arbeit befindlichen Änderungen; klare Review- und Freigabeprozesse.

### Consequences

- Höhere Disziplin bei Branch- und PR-Management erforderlich.
- Vereinfachte Release-Planung und Rollback-Strategien.
