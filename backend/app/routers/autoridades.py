"""Router del módulo Autoridades (solo datos públicos del JNE)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import envelope
from app.schemas.autoridad import AutoridadResponse
from app.schemas.obra import ObraResponse
from app.services import entidad_service

router = APIRouter(prefix="/api/v1/autoridades", tags=["Autoridades"])

DESCARGO = (
    "Información pública del JNE con fines de transparencia cívica; "
    "no implica determinación ni sospecha de culpabilidad de la persona."
)


@router.get("")
def listar(
    entidad_id: str | None = None,
    cargo: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    autoridades = entidad_service.listar_autoridades(db, entidad_id, cargo, skip, limit)
    return envelope([AutoridadResponse.model_validate(a).model_dump() for a in autoridades])


@router.get("/{autoridad_id}")
def detalle(autoridad_id: str, db: Session = Depends(get_db)):
    autoridad = entidad_service.obtener_autoridad(db, autoridad_id)
    if autoridad is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Autoridad no encontrada")
    obras = entidad_service.obras_de_autoridad(db, autoridad)
    data = {
        **AutoridadResponse.model_validate(autoridad).model_dump(),
        "obras": [ObraResponse.model_validate(o).model_dump() for o in obras],
        "descargo": DESCARGO,
    }
    return envelope(data)
