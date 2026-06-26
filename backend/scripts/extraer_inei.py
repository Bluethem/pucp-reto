"""Extrae precios de referencia del PDF INEI usando Gemini.

Lee docs/4025211-r-j-n-149-2026-inei-indices-mes-de-mayo-2026.pdf
y carga los precios en la tabla precios_referencia.
"""

import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, "/app")

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.precio_referencia import PrecioReferencia

RUTA_PDF = Path("/app/data/4025211-r-j-n-149-2026-inei-indices-mes-de-mayo-2026.pdf").resolve()

PROMPT_PRECIOS = (
    "Extrae la tabla de precios de referencia de construcción del siguiente documento INEI. "
    "Devuelve EXCLUSIVAMENTE un array JSON de objetos con las claves exactas: "
    '"codigo_inei", "insumo", "unidad", "precio". '
    "No incluyas texto adicional ni explicaciones. "
    "Usa punto como separador decimal."
)


def seed():
    if not settings.gemini_api_key:
        print("GEMINI_API_KEY no configurada. Saltando extracción INEI.")
        return

    db = SessionLocal()
    try:
        # Forzar extracción incluso si hay precios previos
        db.query(PrecioReferencia).filter(PrecioReferencia.fuente == "inei").delete()
        db.commit()

        print("Leyendo PDF INEI...")
        with open(RUTA_PDF, "rb") as f:
            pdf_bytes = f.read()

        print("Enviando a Gemini para extraer precios...")
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        respuesta = model.generate_content(
            [PROMPT_PRECIOS, {"mime_type": "application/pdf", "data": pdf_bytes}]
        )

        import json
        texto = respuesta.text.strip()
        if texto.startswith("```"):
            texto = texto.strip("`").strip()
            if texto.startswith("json"):
                texto = texto[4:].strip()
        datos = json.loads(texto)

        if not isinstance(datos, list):
            print(f"Respuesta inesperada de Gemini: {type(datos)}")
            return

        cargadas = 0
        for item in datos:
            codigo = item.get("codigo_inei")
            insumo = item.get("insumo", "")
            unidad = item.get("unidad", "")
            precio = item.get("precio")
            if not codigo or precio is None:
                continue
            db.add(PrecioReferencia(
                codigo_inei=str(codigo),
                insumo=str(insumo),
                unidad=str(unidad),
                precio=Decimal(str(precio)),
                departamento=None,
                mes=5,
                anio=2026,
                fuente="inei",
            ))
            cargadas += 1

        db.commit()
        print(f"\nExtracción INEI completada:")
        print(f"  - {cargadas} precios cargados")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
