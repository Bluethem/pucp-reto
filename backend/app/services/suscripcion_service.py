"""Lógica de negocio del módulo Suscripciones."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.suscripcion import Suscripcion
from app.models.usuario import Usuario


def listar_suscripciones(db: Session, usuario: Usuario) -> list[Suscripcion]:
    return db.query(Suscripcion).filter(Suscripcion.usuario_id == usuario.id).all()


def crear_suscripcion(
    db: Session,
    usuario: Usuario,
    recurso_tipo: str,
    recurso_id: str,
) -> Suscripcion:
    existente = (
        db.query(Suscripcion)
        .filter(
            Suscripcion.usuario_id == usuario.id,
            Suscripcion.recurso_tipo == recurso_tipo,
            Suscripcion.recurso_id == recurso_id,
        )
        .first()
    )
    if existente:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya estás suscrito a este recurso")
    suscripcion = Suscripcion(
        usuario_id=usuario.id,
        recurso_tipo=recurso_tipo,
        recurso_id=recurso_id,
    )
    db.add(suscripcion)
    db.commit()
    db.refresh(suscripcion)
    return suscripcion


def eliminar_suscripcion(db: Session, usuario: Usuario, suscripcion_id: str) -> None:
    suscripcion = (
        db.query(Suscripcion)
        .filter(Suscripcion.id == suscripcion_id, Suscripcion.usuario_id == usuario.id)
        .first()
    )
    if suscripcion is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Suscripción no encontrada")
    db.delete(suscripcion)
    db.commit()
