"""Lógica de negocio de Entidades (municipios) y Autoridades."""

from sqlalchemy.orm import Session

from app.models.autoridad import Autoridad
from app.models.entidad import Entidad
from app.models.obra import Obra


def listar_entidades(
    db: Session,
    departamento: str | None = None,
    tipo: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Entidad]:
    query = db.query(Entidad)
    if departamento:
        query = query.filter(Entidad.departamento == departamento)
    if tipo:
        query = query.filter(Entidad.tipo == tipo)
    return query.offset(skip).limit(limit).all()


def obtener_entidad(db: Session, entidad_id: str) -> Entidad | None:
    return db.query(Entidad).filter(Entidad.id == entidad_id).first()


def obras_de_entidad(db: Session, entidad_id: str) -> list[Obra]:
    return db.query(Obra).filter(Obra.entidad_id == entidad_id).all()


def listar_autoridades(
    db: Session,
    entidad_id: str | None = None,
    cargo: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Autoridad]:
    query = db.query(Autoridad)
    if entidad_id:
        query = query.filter(Autoridad.entidad_id == entidad_id)
    if cargo:
        query = query.filter(Autoridad.cargo == cargo)
    return query.offset(skip).limit(limit).all()


def obtener_autoridad(db: Session, autoridad_id: str) -> Autoridad | None:
    return db.query(Autoridad).filter(Autoridad.id == autoridad_id).first()


def obras_de_autoridad(db: Session, autoridad: Autoridad) -> list[Obra]:
    """Obras a cargo de la autoridad = obras de su entidad."""
    if not autoridad.entidad_id:
        return []
    return db.query(Obra).filter(Obra.entidad_id == autoridad.entidad_id).all()
