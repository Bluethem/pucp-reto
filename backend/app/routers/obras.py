"""Router del módulo Obras."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import envelope
from app.core.utils import nivel_riesgo
from app.schemas.obra import ObraDetailResponse, ObraResponse
from app.services import obra_service

router = APIRouter(prefix="/api/v1/obras", tags=["Obras"])


@router.get("")
def listar(
    departamento: str | None = None,
    tipo_obra: str | None = None,
    estado: str | None = None,
    nivel: str | None = None,
    skip: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
):
    obras = obra_service.listar_obras(db, departamento, tipo_obra, estado, nivel, skip, limit)
    data = [ObraResponse.model_validate(o).model_dump() for o in obras]
    return envelope(data)


@router.get("/geolocalizadas")
def geolocalizadas(
    ne_lat: float | None = None,
    ne_lng: float | None = None,
    sw_lat: float | None = None,
    sw_lng: float | None = None,
    db: Session = Depends(get_db),
):
    obras = obra_service.obras_geolocalizadas(db, ne_lat, ne_lng, sw_lat, sw_lng)
    for o in obras:
        o["nivel_riesgo"] = nivel_riesgo(o.get("score_riesgo"))
    return envelope(obras)


@router.get("/resumen")
def resumen(
    departamento: str | None = None,
    tipo_obra: str | None = None,
    estado: str | None = None,
    db: Session = Depends(get_db),
):
    return envelope(obra_service.resumen_obras(db, departamento, tipo_obra, estado))


@router.get("/buscar")
def buscar(q: str = Query(min_length=1), db: Session = Depends(get_db)):
    obras = obra_service.buscar_obras(db, q)
    data = [ObraResponse.model_validate(o).model_dump() for o in obras]
    return envelope(data)


@router.get("/{obra_id}")
def detalle(obra_id: str, db: Session = Depends(get_db)):
    obra = obra_service.obtener_obra(db, obra_id)
    if obra is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Obra no encontrada")
    return envelope(ObraDetailResponse.model_validate(obra).model_dump())
