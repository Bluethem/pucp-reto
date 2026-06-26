"""Router del módulo Admin (backoffice, requiere rol administrador)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import envelope
from app.models.usuario import Usuario
from app.schemas.admin import (
    ComentarioReportadoResponse,
    SaludFuentesResponse,
    UsuarioAdminResponse,
)
from app.services import admin_service
from app.services.auth_service import get_current_admin

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.get("/salud-fuentes")
def salud_fuentes(
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(get_current_admin),
):
    data = SaludFuentesResponse(fuentes=admin_service.salud_fuentes(db))
    return envelope(data.model_dump())


@router.get("/comentarios-reportados")
def comentarios_reportados(
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(get_current_admin),
):
    comentarios = admin_service.comentarios_reportados(db)
    return envelope([ComentarioReportadoResponse.model_validate(c).model_dump() for c in comentarios])


@router.post("/comentarios/{comentario_id}/moderar")
def moderar(
    comentario_id: str,
    accion: str = Query(description="ocultar | restaurar"),
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(get_current_admin),
):
    comentario = admin_service.moderar_comentario(db, comentario_id, accion)
    return envelope(ComentarioReportadoResponse.model_validate(comentario).model_dump())


@router.get("/usuarios")
def usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(get_current_admin),
):
    usuarios = admin_service.listar_usuarios(db, skip, limit)
    return envelope([UsuarioAdminResponse.model_validate(u).model_dump() for u in usuarios])
