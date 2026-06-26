"""Lógica de negocio del módulo Admin (backoffice)."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.comentario import Comentario
from app.models.log_extraccion import LogExtraccion
from app.models.usuario import Usuario

FUENTES = ["inei", "seace", "sunat", "jne", "gemini"]


def salud_fuentes(db: Session) -> list[dict]:
    """Estado de cada fuente externa, derivado del último log de extracción."""
    estados = []
    for fuente in FUENTES:
        ultimo = (
            db.query(LogExtraccion)
            .filter(LogExtraccion.fuente == fuente)
            .order_by(LogExtraccion.created_at.desc())
            .first()
        )
        if ultimo is None:
            estado = "desconocido"
            ultima = None
        else:
            estado = "up" if ultimo.exitoso else "down"
            ultima = ultimo.created_at
        estados.append({"nombre": fuente, "estado": estado, "ultima_actualizacion": ultima})
    return estados


def comentarios_reportados(db: Session) -> list[Comentario]:
    return (
        db.query(Comentario)
        .filter(Comentario.reportado.is_(True))
        .order_by(Comentario.created_at.desc())
        .all()
    )


def moderar_comentario(db: Session, comentario_id: str, accion: str) -> Comentario:
    comentario = db.query(Comentario).filter(Comentario.id == comentario_id).first()
    if comentario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Comentario no encontrado")
    if accion == "ocultar":
        comentario.oculto = True
    elif accion == "restaurar":
        comentario.oculto = False
        comentario.reportado = False
    else:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Acción inválida")
    db.commit()
    db.refresh(comentario)
    return comentario


def listar_usuarios(db: Session, skip: int = 0, limit: int = 100) -> list[Usuario]:
    return db.query(Usuario).offset(skip).limit(limit).all()
