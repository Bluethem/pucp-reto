"""Utilidades transversales del dominio."""

from uuid import uuid4


def gen_uuid() -> str:
    """Genera un UUID v4 como string (IDs de toda la app)."""
    return str(uuid4())


def nivel_riesgo(score: int | float | None) -> str | None:
    """Clasifica un score 0-100 en el semáforo (RF-G-02).

    verde (0-40) · amarillo (41-60) · rojo (61-100).
    """
    if score is None:
        return None
    if score <= 40:
        return "verde"
    if score <= 60:
        return "amarillo"
    return "rojo"
