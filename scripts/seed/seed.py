#!/usr/bin/env python3
import os
import sys
from textwrap import dedent
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import random


def get_database_url() -> str:
    return os.environ.get("DATABASE_URL", "")


def ensure_prerequisites(database_url: str) -> None:
    if not database_url:
        print(
            dedent(
                """
                DATABASE_URL ist nicht gesetzt. Bitte setzen und erneut ausführen.
                Beispiel: export DATABASE_URL=postgresql://futurewise:futurewise@localhost:5432/futurewise
                """
            ).strip()
        )
        sys.exit(0)


def run_migrations_if_any(engine) -> None:
    """Apply SaaS schema extensions"""
    with engine.begin() as conn:
        # Create SaaS tables directly
        try:
            # Subscription plans
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS subscription_plans (
                    plan_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    price_cents BIGINT NOT NULL,
                    currency TEXT NOT NULL DEFAULT 'EUR',
                    max_users INTEGER,
                    max_data_points INTEGER,
                    max_scenarios INTEGER,
                    features JSONB NOT NULL DEFAULT '{}',
                    is_active BOOLEAN NOT NULL DEFAULT true,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                )
            """))
            
            # Insert default plans
            conn.execute(text("""
                INSERT INTO subscription_plans (plan_id, name, description, price_cents, max_users, max_data_points, max_scenarios, features)
                VALUES 
                    ('starter', 'Starter', 'Basic analytics for small businesses', 2900, 5, 100, 3, '["basic_analytics", "csv_import"]'),
                    ('professional', 'Professional', 'Advanced analytics for growing businesses', 9900, 25, 1000, 20, '["basic_analytics", "csv_import", "api_import", "advanced_charts"]'),
                    ('enterprise', 'Enterprise', 'Full analytics suite for large organizations', 29900, 100, 10000, 100, '["basic_analytics", "csv_import", "api_import", "advanced_charts", "custom_integrations", "white_label"]')
                ON CONFLICT (plan_id) DO NOTHING
            """))
            
            # Tenant subscriptions
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS tenant_subscriptions (
                    subscription_id BIGSERIAL PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
                    plan_id TEXT NOT NULL REFERENCES subscription_plans(plan_id),
                    status TEXT NOT NULL DEFAULT 'active',
                    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    ends_at TIMESTAMP WITH TIME ZONE,
                    trial_ends_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                )
            """))
            
            # Invoices
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS invoices (
                    invoice_id BIGSERIAL PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
                    subscription_id BIGINT REFERENCES tenant_subscriptions(subscription_id),
                    invoice_number TEXT UNIQUE NOT NULL,
                    amount_cents BIGINT NOT NULL,
                    tax_cents BIGINT NOT NULL DEFAULT 0,
                    currency TEXT NOT NULL DEFAULT 'EUR',
                    status TEXT NOT NULL DEFAULT 'pending',
                    billing_period_start DATE NOT NULL,
                    billing_period_end DATE NOT NULL,
                    due_date DATE NOT NULL,
                    paid_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                )
            """))
            
            # Usage events
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS usage_events (
                    event_id BIGSERIAL PRIMARY KEY,
                    tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
                    user_id BIGINT REFERENCES users(user_id),
                    event_type TEXT NOT NULL,
                    event_data JSONB,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                )
            """))
            
            # Monthly usage
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS monthly_usage (
                    tenant_id TEXT NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
                    year_month TEXT NOT NULL,
                    total_logins INTEGER NOT NULL DEFAULT 0,
                    total_data_imports INTEGER NOT NULL DEFAULT 0,
                    total_scenarios_run INTEGER NOT NULL DEFAULT 0,
                    total_api_calls INTEGER NOT NULL DEFAULT 0,
                    total_data_points INTEGER NOT NULL DEFAULT 0,
                    active_users INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    PRIMARY KEY (tenant_id, year_month)
                )
            """))
            
            # Audit events table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    audit_id BIGSERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
                    action_type TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    details JSONB,
                    ip_address INET,
                    user_agent TEXT,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                )
            """))
            
            # Index for audit events
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_audit_events_created_at ON audit_events(created_at DESC)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_audit_events_user_id ON audit_events(user_id)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_audit_events_entity ON audit_events(entity_type, entity_id)
            """))
            
            print("SaaS schema created successfully")
            
        except Exception as e:
            print(f"Schema creation failed: {e}")
            pass


def seed_tenants(engine) -> None:
    with engine.begin() as conn:
        # Use existing table structure from init.sql
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS tenants (
                  tenant_id TEXT PRIMARY KEY,
                  name TEXT NOT NULL UNIQUE
                );
                """
            )
        )
        
        # Extended tenant data - use existing structure
        tenants_data = [
            ("alpha", "Alpha Corporation"),
            ("beta", "Beta Industries"),
            ("gamma", "Gamma Solutions"),
            ("delta", "Delta Enterprises"),
            ("epsilon", "Epsilon Tech")
        ]
        
        for tenant_id, name in tenants_data:
            conn.execute(text("DELETE FROM tenants WHERE tenant_id = :tid OR name = :name"), {"tid": tenant_id, "name": name})
            conn.execute(
                text("INSERT INTO tenants (tenant_id, name) VALUES (:tid, :name)"),
                {"tid": tenant_id, "name": name},
            )
        # Defaults
        conn.execute(
            text(
                """
                INSERT INTO tenant_settings(tenant_id, default_currency, default_tax_rate, default_channel)
                VALUES ('alpha', 'EUR', 0.19, 'general')
                ON CONFLICT (tenant_id) DO UPDATE SET updated_at = NOW();
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT INTO tenant_settings(tenant_id, default_currency, default_tax_rate, default_channel)
                VALUES ('beta', 'USD', 0.07, 'marketplace')
                ON CONFLICT (tenant_id) DO UPDATE SET updated_at = NOW();
                """
            )
        )

        # Seed Users & Roles
        # Minimal auth tables (idempotent) to ensure inserts work even if init.sql has not yet created them
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS users (
              user_id BIGSERIAL PRIMARY KEY,
              email TEXT UNIQUE NOT NULL,
              password_hash TEXT NOT NULL,
              display_name TEXT,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        ))
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS user_tenants (
              user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
              tenant_id TEXT REFERENCES tenants(tenant_id) ON DELETE CASCADE,
              role TEXT NOT NULL DEFAULT 'viewer',
              PRIMARY KEY (user_id, tenant_id)
            );
            """
        ))

        # Helper to upsert a user and assign a role to a tenant
        def upsert_user(email: str, password_hash: str, display: str, tenant: str, role: str):
            row = conn.execute(text("SELECT user_id FROM users WHERE email=:e"), {"e": email}).first()
            if row:
                uid = row[0]
            else:
                uid = conn.execute(text("INSERT INTO users(email,password_hash,display_name) VALUES (:e,:p,:d) RETURNING user_id"), {"e": email, "p": password_hash, "d": display}).scalar()
            conn.execute(text("INSERT INTO user_tenants(user_id,tenant_id,role) VALUES (:u,:t,:r) ON CONFLICT (user_id,tenant_id) DO UPDATE SET role=:r"), {"u": uid, "t": tenant, "r": role})

        # Password hashes (bcrypt) for demo: password = "secret"
        from passlib.context import CryptContext
        pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
        h = pwd.hash("secret")

        # First, ensure 'system' tenant exists for system-level roles
        conn.execute(
            text("INSERT INTO tenants (tenant_id, name) VALUES ('system', 'System') ON CONFLICT (tenant_id) DO NOTHING")
        )
        
        # Global/Owner - assign to all tenants with owner role, but primarily to 'system'
        upsert_user("owner@futurewise.local", h, "Owner", "system", "owner")
        upsert_user("owner@futurewise.local", h, "Owner", "alpha", "owner")
        upsert_user("owner@futurewise.local", h, "Owner", "beta", "owner")
        
        # System Manager (platform-level)
        upsert_user("sysman@futurewise.local", h, "System Manager", "system", "system_manager")
        upsert_user("sysman@futurewise.local", h, "System Manager", "alpha", "system_manager")
        upsert_user("sysman@futurewise.local", h, "System Manager", "beta", "system_manager")
        # Tenant Admins
        upsert_user("alpha.admin@futurewise.local", h, "Alpha Admin", "alpha", "tenant_admin")
        upsert_user("beta.admin@futurewise.local", h, "Beta Admin", "beta", "tenant_admin")
        # Tenant Users
        upsert_user("alpha.user@futurewise.local", h, "Alpha User", "alpha", "tenant_user")
        upsert_user("beta.user@futurewise.local", h, "Beta User", "beta", "tenant_user")
        upsert_user("gamma.user@futurewise.local", h, "Gamma User", "gamma", "tenant_user")
        upsert_user("delta.admin@futurewise.local", h, "Delta Admin", "delta", "tenant_admin")
        upsert_user("epsilon.user@futurewise.local", h, "Epsilon User", "epsilon", "tenant_user")


def seed_kpi_data(engine) -> None:
    """Seed realistic KPI data for testing using existing kpi_daily table"""
    with engine.begin() as conn:
        # Use existing kpi_daily table structure
        # Clear existing data
        conn.execute(text("DELETE FROM kpi_daily"))
        
        # Generate data for the last 30 days
        import random
        from datetime import date, timedelta
        
        base_data = {
            'alpha': {'revenue_base': 50000, 'orders_base': 200, 'customers_base': 150},
            'beta': {'revenue_base': 35000, 'orders_base': 140, 'customers_base': 100},
            'gamma': {'revenue_base': 15000, 'orders_base': 60, 'customers_base': 45},
            'delta': {'revenue_base': 75000, 'orders_base': 300, 'customers_base': 200},
            'epsilon': {'revenue_base': 25000, 'orders_base': 100, 'customers_base': 70}
        }
        
        for tenant_id, base in base_data.items():
            for i in range(30):
                current_date = date.today() - timedelta(days=i)
                
                # Add some randomness to make it realistic
                revenue = base['revenue_base'] * (1 + random.uniform(-0.3, 0.4))
                orders = int(base['orders_base'] * (1 + random.uniform(-0.2, 0.3)))
                sessions = int(base['customers_base'] * random.uniform(1.5, 3.5))
                conversion_rate = orders / sessions if sessions > 0 else 0
                revenue_cents = int(revenue * 100)  # Convert to cents
                inventory_units = random.randint(1000, 5000)
                
                # Calculate gross and net revenue (assuming 19% tax rate)
                tax_rate = 0.19
                revenue_cents_gross = revenue_cents
                revenue_cents_net = int(revenue_cents / (1.0 + tax_rate))
                
                conn.execute(text(
                    """
                    INSERT INTO kpi_daily (
                        tenant_id, date, sessions, orders, revenue_cents, conversion_rate, inventory_units,
                        channel, currency, tax_rate, revenue_cents_gross, revenue_cents_net
                    ) VALUES (
                        :tenant_id, :date, :sessions, :orders, :revenue_cents, :conversion_rate, :inventory_units,
                        :channel, :currency, :tax_rate, :revenue_cents_gross, :revenue_cents_net
                    )
                    ON CONFLICT (tenant_id, date) DO NOTHING
                    """
                ), {
                    'tenant_id': tenant_id,
                    'date': current_date,
                    'sessions': sessions,
                    'orders': orders,
                    'revenue_cents': revenue_cents,
                    'conversion_rate': round(conversion_rate, 4),
                    'inventory_units': inventory_units,
                    'channel': 'general',
                    'currency': 'EUR',
                    'tax_rate': tax_rate,
                    'revenue_cents_gross': revenue_cents_gross,
                    'revenue_cents_net': revenue_cents_net
                })


def seed_scenarios(engine) -> None:
    """Seed sample scenarios"""
    with engine.begin() as conn:
        # Ensure scenarios table exists
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS scenarios (
                scenario_id BIGSERIAL PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                name TEXT NOT NULL,
                kind TEXT DEFAULT 'forecast',
                params JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        ))
        
        # Clear existing scenarios
        conn.execute(text("DELETE FROM scenarios"))
        
        scenarios_data = [
            ("alpha", "Q4 2024 Revenue Forecast", "forecast", '{"growth_rate": 0.15, "seasonality": "high"}'),
            ("alpha", "Black Friday Impact Analysis", "what-if", '{"event": "black_friday", "uplift": 0.40}'),
            ("alpha", "New Product Launch", "optimization", '{"product": "premium_line", "target_margin": 0.35}'),
            ("beta", "Market Expansion Scenario", "forecast", '{"new_markets": ["DE", "FR"], "investment": 50000}'),
            ("beta", "Price Optimization", "optimization", '{"price_elasticity": -1.2, "target_volume": 1000}'),
            ("gamma", "Growth Strategy", "forecast", '{"marketing_budget": 15000, "expected_cac": 25}'),
            ("delta", "Supply Chain Optimization", "optimization", '{"lead_time_reduction": 0.2, "cost_savings": 0.1}'),
            ("epsilon", "Customer Retention", "what-if", '{"retention_improvement": 0.15, "ltv_impact": 0.25}')
        ]
        
        for tenant_id, name, kind, params in scenarios_data:
            conn.execute(text(
                """
                INSERT INTO scenarios (tenant_id, name, kind, params)
                VALUES (:tenant_id, :name, :kind, CAST(:params AS jsonb))
                """
            ), {
                'tenant_id': tenant_id,
                'name': name,
                'kind': kind,
                'params': params
            })


def seed_import_events(engine) -> None:
    """Seed sample import events using existing table structure"""
    with engine.begin() as conn:
        # Use existing import_events table structure
        # Clear existing events
        conn.execute(text("DELETE FROM import_events"))
        
        # Generate import events for the last 7 days
        from datetime import datetime, timedelta
        import random
        
        filenames = [
            "daily_sales_data.csv",
            "customer_metrics.xlsx", 
            "product_performance.csv",
            "marketing_data.json",
            "inventory_update.csv",
            "transaction_log.csv"
        ]
        
        for tenant_id in ['alpha', 'beta', 'gamma', 'delta', 'epsilon']:
            for i in range(7):
                # Some days might have multiple imports
                num_imports = random.randint(1, 3)
                for j in range(num_imports):
                    import_date = datetime.now() - timedelta(days=i, hours=random.randint(0, 23))
                    filename = random.choice(filenames)
                    source = random.choice(['csv', 'api', 'xls', 'webhook'])
                    inserted_count = random.randint(100, 5000)
                    
                    conn.execute(text(
                        """
                        INSERT INTO import_events (tenant_id, source, filename, inserted_count, created_at)
                        VALUES (:tenant_id, :source, :filename, :inserted_count, :created_at)
                        """
                    ), {
                        'tenant_id': tenant_id,
                        'source': source,
                        'filename': filename,
                        'inserted_count': inserted_count,
                        'created_at': import_date
                    })


def seed_saas_data(engine) -> None:
    """Seed SaaS-specific data: subscriptions, billing, usage"""
    with engine.begin() as conn:
        # Create tenant subscriptions with different plans
        subscriptions = [
            ("alpha", "professional", "active", datetime.now() - timedelta(days=90)),
            ("beta", "starter", "active", datetime.now() - timedelta(days=45)),
            ("gamma", "enterprise", "active", datetime.now() - timedelta(days=120)),
            ("delta", "starter", "active", datetime.now() - timedelta(days=30)),
            ("epsilon", "professional", "active", datetime.now() - timedelta(days=60)),
        ]
        
        for tenant_id, plan_id, status, started_at in subscriptions:
            conn.execute(text("""
                INSERT INTO tenant_subscriptions (tenant_id, plan_id, status, started_at)
                VALUES (:tenant_id, :plan_id, :status, :started_at)
                ON CONFLICT DO NOTHING
            """), {
                "tenant_id": tenant_id,
                "plan_id": plan_id, 
                "status": status,
                "started_at": started_at
            })
        
        # Generate realistic invoices for the last 6 months
        plans_pricing = {"starter": 2900, "professional": 9900, "enterprise": 29900}
        
        for tenant_id, plan_id, status, started_at in subscriptions:
            price_cents = plans_pricing[plan_id]
            
            # Generate monthly invoices since subscription start
            current_date = started_at.replace(day=1)  # Start of month
            while current_date < datetime.now():
                invoice_number = f"INV-{current_date.strftime('%Y%m')}-{tenant_id.upper()}"
                billing_end = (current_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                due_date = current_date + timedelta(days=30)
                
                # 90% of invoices are paid
                is_paid = random.random() < 0.9
                paid_at = current_date + timedelta(days=random.randint(5, 25)) if is_paid else None
                status_invoice = "paid" if is_paid else "pending"
                
                conn.execute(text("""
                    INSERT INTO invoices (
                        tenant_id, invoice_number, amount_cents, tax_cents, 
                        billing_period_start, billing_period_end, due_date, 
                        status, paid_at, created_at
                    ) VALUES (
                        :tenant_id, :invoice_number, :amount_cents, :tax_cents,
                        :billing_start, :billing_end, :due_date,
                        :status, :paid_at, :created_at
                    ) ON CONFLICT (invoice_number) DO NOTHING
                """), {
                    "tenant_id": tenant_id,
                    "invoice_number": invoice_number,
                    "amount_cents": price_cents,
                    "tax_cents": int(price_cents * 0.19),  # 19% tax
                    "billing_start": current_date,
                    "billing_end": billing_end,
                    "due_date": due_date,
                    "status": status_invoice,
                    "paid_at": paid_at,
                    "created_at": current_date
                })
                
                current_date = (current_date + timedelta(days=32)).replace(day=1)
        
        # Seed some sample audit events
        sample_audit_events = [
            (1, "CREATE", "tenant", "alpha", '{"name": "Alpha Corp", "created_by": 1}'),
            (1, "CREATE", "tenant", "beta", '{"name": "Beta Ltd", "created_by": 1}'),
            (2, "UPDATE", "user", "3", '{"changes": {"display_name": {"old": "John", "new": "John Doe"}}, "updated_by": 2}'),
            (1, "CREATE", "subscription", "1", '{"tenant_id": "alpha", "plan_id": "professional", "created_by": 1}'),
            (1, "DELETE", "user", "999", '{"email": "test@example.com", "deleted_by": 1}'),
        ]
        
        for user_id, action_type, entity_type, entity_id, details in sample_audit_events:
            conn.execute(text("""
                INSERT INTO audit_events (user_id, action_type, entity_type, entity_id, details)
                VALUES (:user_id, :action_type, :entity_type, :entity_id, :details)
                ON CONFLICT DO NOTHING
            """), {
                "user_id": user_id,
                "action_type": action_type,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "details": details
            })


def main() -> None:
    database_url = get_database_url()
    ensure_prerequisites(database_url)

    engine = create_engine(database_url, pool_pre_ping=True)
    print("Verbunden mit:", database_url)

    run_migrations_if_any(engine)
    
    print("Seeding Tenants und Users...")
    seed_tenants(engine)
    
    print("Seeding KPI-Daten...")
    seed_kpi_data(engine)
    
    print("Seeding Szenarien...")
    seed_scenarios(engine)
    
    print("Seeding Import-Events...")
    seed_import_events(engine)
    
    print("Seeding SaaS-Daten...")
    seed_saas_data(engine)
    
    print("Seeding abgeschlossen. Realistische SaaS-Testdaten wurden geladen.")


if __name__ == "__main__":
    main()
