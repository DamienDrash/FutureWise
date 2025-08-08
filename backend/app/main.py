from fastapi import FastAPI
from .routers import health, tenants

app = FastAPI(title="FutureWise API", version="0.1.0")

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(tenants.router, prefix="/tenants", tags=["tenants"])


@app.get("/")
def root():
    return {"name": "FutureWise API", "version": app.version}
