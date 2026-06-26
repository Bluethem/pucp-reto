"""Extrae partidas del expediente técnico PDF usando Gemini.

Lee docs/5669010-expediente-tecnico-obra-rio-viejo-flores-parte1.pdf,
extrae las partidas y calcula el score contra precios INEI.
"""

import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, "/app")

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.obra import Obra
from app.models.partida import PartidaObra
from app.services.scoring_service import ScoringService

RUTA_PDF = Path("/app/data/5669010-expediente-tecnico-obra-rio-viejo-flores-parte1.pdf").resolve()

PROMPT_PARTIDAS = (
    "Extrae la tabla de partidas del siguiente expediente técnico. "
    "Devuelve EXCLUSIVAMENTE un array JSON de objetos con las claves exactas: "
    '"insumo", "unidad", "cantidad", "precio_unitario". '
    "No incluyas texto adicional ni explicaciones. "
    "Usa punto como separador decimal. Incluye todas las filas de la tabla."
)


def seed():
    if not settings.gemini_api_key:
        print("GEMINI_API_KEY no configurada. Saltando.")
        return

    db = SessionLocal()
    try:
        print("Leyendo PDF del expediente técnico...")
        with open(RUTA_PDF, "rb") as f:
            pdf_bytes = f.read()

        print("Enviando a Gemini para extraer partidas...")
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        respuesta = model.generate_content(
            [PROMPT_PARTIDAS, {"mime_type": "application/pdf", "data": pdf_bytes}]
        )

        import json
        texto = respuesta.text.strip()
        if texto.startswith("```"):
            texto = texto.strip("`").strip()
            if texto.startswith("json"):
                texto = texto[4:].strip()
        partidas_data = json.loads(texto)

        if not isinstance(partidas_data, list):
            print(f"Respuesta inesperada: {type(partidas_data)}")
            return

        print(f"Gemini extrajo {len(partidas_data)} partidas")
        for p in partidas_data[:3]:
            print(f"  - {p.get('insumo')}: {p.get('precio_unitario')} x {p.get('cantidad')}")

        # Crear obra con las partidas extraídas
        obra = Obra(
            codigo_infobras="EXP-5669010",
            titulo="Expediente: Río Viejo Flores - Parte 1",
            tipo_obra="edificacion",
            estado="ejecucion",
            modo_analisis="partidas",
        )
        db.add(obra)
        db.flush()

        for p in partidas_data:
            db.add(PartidaObra(
                obra_id=obra.id,
                insumo=p.get("insumo", ""),
                unidad=p.get("unidad", ""),
                cantidad=Decimal(str(p["cantidad"])) if p.get("cantidad") else None,
                precio_declarado=Decimal(str(p["precio_unitario"])) if p.get("precio_unitario") else None,
            ))
        db.commit()

        # Calcular score
        resultado = ScoringService(db).calcular_score(obra.id)

        print(f"\n✅ Score calculado para expediente real:")
        print(f"  Score: {resultado.score}/100 ({resultado.clasificacion})")
        print(f"  Modo: {resultado.modo_analisis}")
        print(f"  Partidas: {resultado.to_dict().get('total_partidas', 0)} total, "
              f"{resultado.to_dict().get('partidas_comparables', 0)} comparables, "
              f"{resultado.to_dict().get('alertas', 0)} alertas")

        # Imprimir partidas con ratios
        for partida in resultado.partidas:
            d = partida.to_dict()
            print(f"  {d['insumo']}: {d['precio_declarado']} vs ref {d['precio_referencia']} → ratio {d['ratio']}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
