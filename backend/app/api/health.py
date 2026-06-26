"""Endpoints de salud del sistema.

Sirven para verificar que el backend arrancó y que sus dependencias
(base de datos) responden. Base para el tablero de estado (RF-ADM-06).
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Liveness: el servicio está en pie."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
    }


@router.get("/health/db")
def health_db(db: Session = Depends(get_db)) -> dict:
    """Readiness: la base de datos responde."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "up"}
    except Exception as exc:  # noqa: BLE001 — se reporta el detalle al operador
        return {"status": "error", "database": "down", "detail": str(exc)}
