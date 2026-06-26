"""Formato de respuesta uniforme: {"data": ..., "error": ...}."""

from typing import Any


def envelope(data: Any = None, error: Any = None) -> dict:
    """Envuelve cualquier payload en el contrato estándar de la API."""
    return {"data": data, "error": error}
