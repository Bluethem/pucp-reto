"""Router del módulo Obras."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import envelope
from app.core.utils import nivel_riesgo
from app.datasource.firecrawl import FirecrawlDataSource
from app.models.obra import Obra
from app.models.partida import PartidaObra
from app.schemas.obra import ObraDetailResponse, ObraExtraerRequest, ObraExtraerResponse, ObraResponse
from app.services import obra_service
from app.services.scoring_service import ScoringService

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


@router.post("/extraer", status_code=status.HTTP_201_CREATED)
def extraer(payload: ObraExtraerRequest, db: Session = Depends(get_db)):
    """Pipeline completo: Firecrawl descarga PDF → Gemini extrae partidas → Scoring."""
    firecrawl = FirecrawlDataSource()
    if not firecrawl.disponible():
        raise HTTPException(400, "FIRECRAWL_API_KEY no configurada")

    # 1. Extraer partidas del PDF via Firecrawl + Gemini
    partidas_data = firecrawl.extraer_partidas_de_obra(payload.codigo_infobras)

    # 2. Crear obra en BD
    obra = Obra(
        codigo_infobras=payload.codigo_infobras,
        titulo=payload.titulo or f"Obra {payload.codigo_infobras}",
        tipo_obra="edificacion",
        estado="ejecucion",
        departamento=payload.departamento,
        modo_analisis="partidas",
        fecha_extraccion=datetime.utcnow(),
    )
    db.add(obra)
    db.flush()

    # 3. Guardar partidas
    for p in partidas_data:
        db.add(PartidaObra(
            obra_id=obra.id,
            insumo=p.get("insumo", ""),
            unidad=p.get("unidad", ""),
            cantidad=float(p["cantidad"]) if p.get("cantidad") else None,
            precio_declarado=float(p["precio_unitario"]) if p.get("precio_unitario") else None,
        ))
    db.commit()

    # 4. Calcular score
    resultado = ScoringService(db).calcular_score(obra.id)

    # 5. Response
    obra_resp = ObraResponse.model_validate(obra).model_dump()
    return envelope({
        "obra": obra_resp,
        "score": resultado.to_dict(),
        "partidas": [{
            "insumo": p.get("insumo"),
            "unidad": p.get("unidad"),
            "cantidad": p.get("cantidad"),
            "precio_unitario": p.get("precio_unitario"),
        } for p in partidas_data],
    })
