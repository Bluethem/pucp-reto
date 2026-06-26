"""Lógica de negocio del módulo Obras: filtros, geo-queries y resumen."""

from geoalchemy2 import Geometry
from sqlalchemy import cast, func, or_
from sqlalchemy.orm import Session

from app.models.obra import Obra
from app.models.contratista import Contratista
from app.models.entidad import Entidad

NIVELES = {"verde": (0, 40), "amarillo": (41, 60), "rojo": (61, 100)}


def _enriquecer(obra: Obra) -> Obra:
    """Carga nombres de entidad y contratista en atributos virtuales."""
    if obra.entidad:
        obra.entidad_nombre = obra.entidad.nombre
    if obra.contratista:
        obra.contratista_nombre = obra.contratista.razon_social
    return obra


def listar_obras(
    db: Session,
    departamento: str | None = None,
    tipo_obra: str | None = None,
    estado: str | None = None,
    nivel: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Obra]:
    query = db.query(Obra).options(
        __import__("sqlalchemy").orm.joinedload(Obra.entidad),
        __import__("sqlalchemy").orm.joinedload(Obra.contratista),
    )
    if departamento:
        query = query.filter(Obra.departamento == departamento)
    if tipo_obra:
        query = query.filter(Obra.tipo_obra == tipo_obra)
    if estado:
        query = query.filter(Obra.estado == estado)
    if nivel and nivel in NIVELES:
        bajo, alto = NIVELES[nivel]
        query = query.filter(Obra.score_riesgo >= bajo, Obra.score_riesgo <= alto)
    obras = query.offset(skip).limit(limit).all()
    for o in obras:
        _enriquecer(o)
    return obras


def obtener_obra(db: Session, obra_id: str) -> Obra | None:
    obra = db.query(Obra).options(
        __import__("sqlalchemy").orm.joinedload(Obra.entidad),
        __import__("sqlalchemy").orm.joinedload(Obra.contratista),
    ).filter(Obra.id == obra_id).first()
    if obra:
        _enriquecer(obra)
    return obra


def obras_geolocalizadas(
    db: Session,
    ne_lat: float | None = None,
    ne_lng: float | None = None,
    sw_lat: float | None = None,
    sw_lng: float | None = None,
) -> list[dict]:
    geom = cast(Obra.ubicacion, Geometry)
    query = db.query(
        Obra.id,
        Obra.titulo,
        Obra.tipo_obra,
        Obra.estado,
        Obra.score_riesgo,
        func.ST_Y(geom).label("lat"),
        func.ST_X(geom).label("lon"),
    ).filter(Obra.ubicacion.isnot(None))

    if None not in (ne_lat, ne_lng, sw_lat, sw_lng):
        envelope = func.ST_MakeEnvelope(sw_lng, sw_lat, ne_lng, ne_lat, 4326)
        query = query.filter(func.ST_Intersects(geom, envelope))

    return [
        {
            "id": row.id,
            "titulo": row.titulo,
            "tipo_obra": row.tipo_obra,
            "estado": row.estado,
            "score_riesgo": row.score_riesgo,
            "lat": row.lat,
            "lon": row.lon,
        }
        for row in query.all()
    ]


def resumen_obras(
    db: Session,
    departamento: str | None = None,
    tipo_obra: str | None = None,
    estado: str | None = None,
) -> dict:
    query = db.query(Obra.score_riesgo)
    if departamento:
        query = query.filter(Obra.departamento == departamento)
    if tipo_obra:
        query = query.filter(Obra.tipo_obra == tipo_obra)
    if estado:
        query = query.filter(Obra.estado == estado)

    conteo = {"verde": 0, "amarillo": 0, "rojo": 0, "sin_score": 0}
    total = 0
    for (score,) in query.all():
        total += 1
        if score is None:
            conteo["sin_score"] += 1
        elif score <= 40:
            conteo["verde"] += 1
        elif score <= 60:
            conteo["amarillo"] += 1
        else:
            conteo["rojo"] += 1
    return {"total": total, "por_nivel": conteo}


def buscar_obras(db: Session, q: str, limit: int = 50) -> list[Obra]:
    patron = f"%{q}%"
    return (
        db.query(Obra)
        .filter(
            or_(
                Obra.titulo.ilike(patron),
                Obra.codigo_infobras.ilike(patron),
                Obra.departamento.ilike(patron),
            )
        )
        .limit(limit)
        .all()
    )
