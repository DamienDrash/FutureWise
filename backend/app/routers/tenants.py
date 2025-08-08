from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from ..services.db import get_sqlalchemy_engine

router = APIRouter()


@router.get("")
def list_tenants():
    engine = get_sqlalchemy_engine()
    try:
        with engine.connect() as conn:
            # Minimaler Tabellen-Check; falls Tabelle noch nicht existiert, leere Liste zurück
            result = conn.execute(
                text(
                    """
                    SELECT tenant_id, name
                    FROM tenants
                    ORDER BY name ASC
                    """
                )
            )
            tenants = [
                {"tenant_id": row[0], "name": row[1]} for row in result.fetchall()
            ]
            return {"items": tenants}
    except Exception as exc:
        # Keine Mock-Daten; im Fehlerfall aussagekräftiger Fehler
        raise HTTPException(status_code=500, detail=f"DB error: {exc}")
