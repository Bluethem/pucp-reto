"""Router del módulo Suscripciones."""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import envelope
from app.models.usuario import Usuario
from app.schemas.suscripcion import SuscripcionRequest, SuscripcionResponse
from app.services import suscripcion_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/v1/suscripciones", tags=["Suscripciones"])


@router.get("")
def listar(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    suscripciones = suscripcion_service.listar_suscripciones(db, usuario)
    return envelope([SuscripcionResponse.model_validate(s).model_dump() for s in suscripciones])


@router.post("", status_code=status.HTTP_201_CREATED)
def crear(
    payload: SuscripcionRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    suscripcion = suscripcion_service.crear_suscripcion(
        db, usuario, payload.recurso_tipo, payload.recurso_id
    )
    return envelope(SuscripcionResponse.model_validate(suscripcion).model_dump())


@router.delete("/{suscripcion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    suscripcion_id: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    suscripcion_service.eliminar_suscripcion(db, usuario, suscripcion_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
