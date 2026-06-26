"""Router del módulo Municipios/Entidades."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import envelope
from app.schemas.autoridad import AutoridadResponse
from app.schemas.municipio import EntidadDetailResponse, EntidadResponse
from app.schemas.obra import ObraResponse
from app.services import entidad_service

router = APIRouter(prefix="/api/v1/municipios", tags=["Municipios"])


@router.get("")
def listar(
    departamento: str | None = None,
    tipo: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    entidades = entidad_service.listar_entidades(db, departamento, tipo, skip, limit)
    return envelope([EntidadResponse.model_validate(e).model_dump() for e in entidades])


@router.get("/{entidad_id}")
def detalle(entidad_id: str, db: Session = Depends(get_db)):
    entidad = entidad_service.obtener_entidad(db, entidad_id)
    if entidad is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Entidad no encontrada")
    data = EntidadDetailResponse(
        **EntidadResponse.model_validate(entidad).model_dump(),
        autoridades=[AutoridadResponse.model_validate(a) for a in entidad.autoridades],
    )
    return envelope(data.model_dump())


@router.get("/{entidad_id}/obras")
def obras(entidad_id: str, db: Session = Depends(get_db)):
    entidad = entidad_service.obtener_entidad(db, entidad_id)
    if entidad is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Entidad no encontrada")
    obras = entidad_service.obras_de_entidad(db, entidad_id)
    return envelope([ObraResponse.model_validate(o).model_dump() for o in obras])
