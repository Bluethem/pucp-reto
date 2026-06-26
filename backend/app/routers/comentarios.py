"""Router del módulo Comentarios."""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import envelope
from app.models.usuario import Usuario
from app.schemas.comentario import ComentarioRequest, ComentarioResponse
from app.services import comentario_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/v1/comentarios", tags=["Comentarios"])


@router.get("")
def listar(
    recurso_tipo: str | None = None,
    recurso_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    comentarios = comentario_service.listar_comentarios(db, recurso_tipo, recurso_id, skip, limit)
    return envelope([ComentarioResponse.model_validate(c).model_dump() for c in comentarios])


@router.post("", status_code=status.HTTP_201_CREATED)
def crear(
    payload: ComentarioRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    comentario = comentario_service.crear_comentario(
        db, usuario, payload.recurso_tipo, payload.recurso_id, payload.contenido, payload.padre_id
    )
    return envelope(ComentarioResponse.model_validate(comentario).model_dump())


@router.delete("/{comentario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    comentario_id: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    comentario_service.eliminar_comentario(db, usuario, comentario_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{comentario_id}/reportar")
def reportar(
    comentario_id: str,
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(get_current_user),
):
    comentario = comentario_service.reportar_comentario(db, comentario_id)
    return envelope(ComentarioResponse.model_validate(comentario).model_dump())
