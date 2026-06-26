"""Router del módulo Scoring."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import envelope
from app.core.utils import nivel_riesgo
from app.models.obra import Obra
from app.models.usuario import Usuario
from app.services.auth_service import get_current_admin
from app.services.scoring_service import ScoringService

router = APIRouter(prefix="/api/v1/obras", tags=["Scoring"])


def _calcular_y_persistir(db: Session, obra: Obra) -> dict:
    resultado = ScoringService(db).calcular_score(obra.id)
    obra.score_riesgo = resultado.score
    obra.modo_analisis = resultado.modo_analisis
    db.commit()

    d = resultado.to_dict()
    return {
        "obra_id": obra.id,
        "score": d["score"],
        "clasificacion": d["clasificacion"],
        "nivel_riesgo": nivel_riesgo(d["score"]),
        "modo_analisis": d["modo_analisis"],
        "total_partidas": d["total_partidas"],
        "partidas_comparables": d["partidas_comparables"],
        "alertas": d["alertas"],
        "partidas": d["partidas"],
    }


@router.get("/{obra_id}/score")
def obtener_score(obra_id: str, db: Session = Depends(get_db)):
    obra = db.query(Obra).filter(Obra.id == obra_id).first()
    if obra is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Obra no encontrada")
    return envelope(_calcular_y_persistir(db, obra))


@router.post("/{obra_id}/recalcular")
def recalcular_score(
    obra_id: str,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(get_current_admin),
):
    obra = db.query(Obra).filter(Obra.id == obra_id).first()
    if obra is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Obra no encontrada")
    return envelope(_calcular_y_persistir(db, obra))
