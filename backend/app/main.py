from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import health, tenants, imports, scenarios, auth, billing

app = FastAPI(title="FutureWise API", version="0.1.0")

# CORS für Dev-Frontend
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
app.include_router(imports.router, prefix="/imports", tags=["imports"])
app.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(billing.router, prefix="/billing", tags=["billing"])


@app.get("/")
def root():
    return {"name": "FutureWise API", "version": app.version}
