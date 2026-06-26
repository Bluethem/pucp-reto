"""Prepara una obra de demostración con partidas, score y PDF visibles.

Toma una obra del SEACE, le agrega partidas realistas (de mock-data),
calcula el score y enlaza un expediente PDF real.
"""

import sys
from decimal import Decimal
from datetime import datetime

sys.path.insert(0, "/app")

from app.core.database import SessionLocal
from app.models.obra import Obra
from app.models.partida import PartidaObra
from app.models.precio_referencia import PrecioReferencia
from app.services.scoring_service import ScoringService

# Partidas realistas extraídas de mock-data.ts (obra-001)
PARTIDAS_MOCK = [
    ("Cemento Portland Tipo I", "CEM-001", "BOL", 2400, 38.50),
    ("Fierro corrugado 3/8\"", "ACR-001", "KG", 18000, 5.80),
    ("Arena gruesa", "AGR-002", "M3", 320, 95.00),
    ("Piedra chancada 1/2\"", "AGR-001", "M3", 280, 115.00),
    ("Mano de obra operario", "MAN-001", "HH", 9600, 21.00),
    ("Asfalto RC-250", "CEM-002", "GLN", 1800, 18.50),
    ("Agua potable", "CEM-001", "M3", 450, 8.00),
    ("Tubería PVC 4\"", "AGR-001", "ML", 620, 32.00),
    ("Madera tornillo (encofrado)", "MAD-001", "P2", 3200, 5.20),
    ("Mano de obra peón", "MAN-001", "HH", 14400, 16.50),
]

# Precios de referencia INEI correspondientes
PRECIOS_REFS = {
    "CEM-001": Decimal("28.50"),
    "ACR-001": Decimal("4.50"),
    "AGR-001": Decimal("55.00"),
    "AGR-002": Decimal("45.00"),
    "MAD-001": Decimal("8.50"),
    "MAN-001": Decimal("22.50"),
    "CEM-002": Decimal("32.00"),
}

PDF_URL = "https://cdn.www.gob.pe/uploads/document/file/6495857/5669010-expediente-tecnico-obra-rio-viejo-flores-parte3.pdf?v=1718742062"


def seed():
    db = SessionLocal()
    try:
        # Buscar una obra del SEACE que tenga entidad
        obra = db.query(Obra).filter(Obra.entidad_id.isnot(None)).first()
        if not obra:
            print("No hay obras con entidad en BD")
            return

        # Eliminar partidas existentes
        db.query(PartidaObra).filter(PartidaObra.obra_id == obra.id).delete()

        # Agregar partidas
        for insumo, codigo, unidad, cantidad, precio in PARTIDAS_MOCK:
            db.add(PartidaObra(
                obra_id=obra.id,
                insumo=insumo,
                codigo_inei=codigo,
                unidad=unidad,
                cantidad=Decimal(str(cantidad)),
                precio_declarado=Decimal(str(precio)),
            ))
        db.commit()

        # Asegurar precios de referencia
        for codigo, precio in PRECIOS_REFS.items():
            existente = db.query(PrecioReferencia).filter(
                PrecioReferencia.codigo_inei == codigo,
                PrecioReferencia.fuente == "inei",
                PrecioReferencia.departamento.is_(None),
            ).first()
            if not existente:
                db.add(PrecioReferencia(
                    codigo_inei=codigo,
                    insumo="Insumo",
                    unidad="u",
                    precio=precio,
                    mes=5,
                    anio=2026,
                    fuente="inei",
                ))
        db.commit()

        # Calcular score
        resultado = ScoringService(db).calcular_score(obra.id)
        obra.score_riesgo = resultado.score
        obra.modo_analisis = resultado.modo_analisis

        from geoalchemy2 import WKTElement
        obra.ubicacion = None

        db.commit()

        print(f"✅ Demo preparada:")
        print(f"  Obra: {obra.id}")
        print(f"  Título: {obra.titulo}")
        print(f"  Score: {obra.score_riesgo}/100 ({resultado.clasificacion})")
        print(f"  Partidas: {len(PARTIDAS_MOCK)}")
        print(f"  Modo: {resultado.modo_analisis}")
        print(f"  Frontend: http://localhost:3000/obra/{obra.id}")
        print(f"")
        print(f"  Para ver el expediente PDF, actualiza el frontend api.ts")
        print(f"  con la URL: {PDF_URL}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
