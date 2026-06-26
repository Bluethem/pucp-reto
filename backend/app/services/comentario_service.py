"""Lógica de negocio del módulo Comentarios."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.comentario import Comentario
from app.models.usuario import Usuario


def listar_comentarios(
    db: Session,
    recurso_tipo: str | None = None,
    recurso_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Comentario]:
    query = db.query(Comentario).filter(Comentario.oculto.is_(False))
    if recurso_tipo:
        query = query.filter(Comentario.recurso_tipo == recurso_tipo)
    if recurso_id:
        query = query.filter(Comentario.recurso_id == recurso_id)
    return query.order_by(Comentario.created_at.desc()).offset(skip).limit(limit).all()


def crear_comentario(
    db: Session,
    usuario: Usuario,
    recurso_tipo: str,
    recurso_id: str,
    contenido: str,
    padre_id: str | None = None,
) -> Comentario:
    comentario = Comentario(
        usuario_id=usuario.id,
        recurso_tipo=recurso_tipo,
        recurso_id=recurso_id,
        contenido=contenido,
        padre_id=padre_id,
    )
    db.add(comentario)
    db.commit()
    db.refresh(comentario)
    return comentario


def eliminar_comentario(db: Session, usuario: Usuario, comentario_id: str) -> None:
    comentario = db.query(Comentario).filter(Comentario.id == comentario_id).first()
    if comentario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Comentario no encontrado")
    if comentario.usuario_id != usuario.id and usuario.rol != "administrador":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "No puedes eliminar este comentario")
    db.delete(comentario)
    db.commit()


def reportar_comentario(db: Session, comentario_id: str) -> Comentario:
    comentario = db.query(Comentario).filter(Comentario.id == comentario_id).first()
    if comentario is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Comentario no encontrado")
    comentario.reportado = True
    db.commit()
    db.refresh(comentario)
    return comentario
