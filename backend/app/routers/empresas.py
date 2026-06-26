"""Router del módulo Empresas/Contratistas."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import envelope
from app.schemas.empresa import ContratistaDetailResponse, ContratistaResponse
from app.schemas.obra import ObraResponse
from app.services import contratista_service

router = APIRouter(prefix="/api/v1/empresas", tags=["Empresas"])


@router.get("")
def listar(
    ruc: str | None = None,
    razon_social: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    contratistas = contratista_service.listar_contratistas(db, ruc, razon_social, skip, limit)
    return envelope([ContratistaResponse.model_validate(c).model_dump() for c in contratistas])


@router.get("/{contratista_id}")
def detalle(contratista_id: str, db: Session = Depends(get_db)):
    contratista = contratista_service.obtener_contratista(db, contratista_id)
    if contratista is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Empresa no encontrada")
    total = contratista_service.contar_obras(db, contratista_id)
    data = ContratistaDetailResponse(
        **ContratistaResponse.model_validate(contratista).model_dump(),
        total_obras=total,
    )
    return envelope(data.model_dump())


@router.get("/{contratista_id}/obras")
def obras(contratista_id: str, db: Session = Depends(get_db)):
    contratista = contratista_service.obtener_contratista(db, contratista_id)
    if contratista is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Empresa no encontrada")
    obras = contratista_service.obras_de_contratista(db, contratista_id)
    return envelope([ObraResponse.model_validate(o).model_dump() for o in obras])
