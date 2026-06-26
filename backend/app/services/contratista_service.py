"""Lógica de negocio del módulo Empresas/Contratistas."""

from sqlalchemy.orm import Session

from app.models.contratista import Contratista
from app.models.obra import Obra


def listar_contratistas(
    db: Session,
    ruc: str | None = None,
    razon_social: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Contratista]:
    query = db.query(Contratista)
    if ruc:
        query = query.filter(Contratista.ruc == ruc)
    if razon_social:
        query = query.filter(Contratista.razon_social.ilike(f"%{razon_social}%"))
    return query.offset(skip).limit(limit).all()


def obtener_contratista(db: Session, contratista_id: str) -> Contratista | None:
    return db.query(Contratista).filter(Contratista.id == contratista_id).first()


def obras_de_contratista(db: Session, contratista_id: str) -> list[Obra]:
    return db.query(Obra).filter(Obra.contratista_id == contratista_id).all()


def contar_obras(db: Session, contratista_id: str) -> int:
    return db.query(Obra).filter(Obra.contratista_id == contratista_id).count()
