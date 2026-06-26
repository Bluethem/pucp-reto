"""Script de seed: carga obras y precios de referencia de prueba.

Idempotente: solo carga datos si la tabla obras está vacía.
Útil para tener datos inmediatamente después del deploy, sin depender
de Firecrawl + Gemini (que requieren API keys y conexión externa).

Uso:
    python scripts/seed_infobras.py

Requiere DATABASE_URL configurada en .env o variable de entorno.
"""

import sys
import uuid
from decimal import Decimal

sys.path.insert(0, "/app")

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.contratista import Contratista
from app.models.entidad import Entidad
from app.models.obra import Obra
from app.models.precio_referencia import PrecioReferencia

# --- Datos de prueba ---

ENTIDADES = [
    {"nombre": "Municipalidad Distrital de Miraflores", "tipo": "municipalidad_distrital", "departamento": "Lima", "provincia": "Lima", "distrito": "Miraflores"},
    {"nombre": "Municipalidad Provincial del Cusco", "tipo": "municipalidad_provincial", "departamento": "Cusco", "provincia": "Cusco", "distrito": "Cusco"},
    {"nombre": "Gobierno Regional de Loreto", "tipo": "gobierno_regional", "departamento": "Loreto", "provincia": "Maynas", "distrito": "Iquitos"},
]

CONTRATISTAS = [
    {"ruc": "20123456789", "razon_social": "Constructora Los Andes SAC", "representante_legal": "Carlos Pérez", "estado_sunat": "ACTIVO", "score_confiabilidad": 75},
    {"ruc": "20987654321", "razon_social": "Grupo Inmobiliario del Sur EIRL", "representante_legal": "María López", "estado_sunat": "ACTIVO", "score_confiabilidad": 45},
    {"ruc": "20777777777", "razon_social": "Consorcio Vial Amazónico SAC", "representante_legal": "Juan Ríos", "estado_sunat": "ACTIVO", "score_confiabilidad": 30},
]

OBRAS = [
    {"codigo_infobras": "INF-2024-001", "titulo": "Mejoramiento de pistas y veredas en Miraflores", "tipo_obra": "edificacion", "estado": "ejecucion",
     "presupuesto_total": 2500000, "metrado_total": 850, "departamento": "Lima", "score_riesgo": 35, "modo_analisis": "fallback_m2", "entidad_idx": 0, "contratista_idx": 0},
    {"codigo_infobras": "INF-2024-002", "titulo": "Construcción de local municipal en Cusco", "tipo_obra": "edificacion", "estado": "concluido",
     "presupuesto_total": 1800000, "metrado_total": 620, "departamento": "Cusco", "score_riesgo": 55, "modo_analisis": "fallback_m2", "entidad_idx": 1, "contratista_idx": 1},
    {"codigo_infobras": "INF-2024-003", "titulo": "Carretera Iquitos-Nauta", "tipo_obra": "carretera", "estado": "ejecucion",
     "presupuesto_total": 15000000, "metrado_total": 45000, "departamento": "Loreto", "score_riesgo": 72, "modo_analisis": "fallback_m2", "entidad_idx": 2, "contratista_idx": 2},
]

PRECIOS = [
    {"codigo_inei": "CEM-001", "insumo": "Cemento Portland Tipo I", "unidad": "bolsa", "precio": 28.50, "departamento": None, "mes": 6, "anio": 2026, "fuente": "inei"},
    {"codigo_inei": "CEM-002", "insumo": "Cemento Portland Tipo II", "unidad": "bolsa", "precio": 32.00, "departamento": None, "mes": 6, "anio": 2026, "fuente": "inei"},
    {"codigo_inei": "ACR-001", "insumo": "Acero corrugado 1/2", "unidad": "kg", "precio": 4.50, "departamento": None, "mes": 6, "anio": 2026, "fuente": "inei"},
    {"codigo_inei": "AGR-001", "insumo": "Agregado grueso", "unidad": "m3", "precio": 55.00, "departamento": "Lima", "mes": 6, "anio": 2026, "fuente": "inei"},
    {"codigo_inei": "AGR-002", "insumo": "Agregado fino (arena)", "unidad": "m3", "precio": 45.00, "departamento": None, "mes": 6, "anio": 2026, "fuente": "inei"},
    {"codigo_inei": "MAD-001", "insumo": "Madera tornillo", "unidad": "p2", "precio": 8.50, "departamento": "Loreto", "mes": 6, "anio": 2026, "fuente": "inei"},
    {"codigo_inei": "M2-EDIF", "insumo": "edificacion costo m2 referencia", "unidad": "m2", "precio": 2800, "departamento": "Lima", "mes": 1, "anio": 2026, "fuente": "mvivienda"},
    {"codigo_inei": "M2-EDIF", "insumo": "edificacion costo m2 referencia", "unidad": "m2", "precio": 3200, "departamento": "Cusco", "mes": 1, "anio": 2026, "fuente": "mvivienda"},
    {"codigo_inei": "M2-EDIF", "insumo": "edificacion costo m2 referencia", "unidad": "m2", "precio": 3100, "departamento": "Loreto", "mes": 1, "anio": 2026, "fuente": "mvivienda"},
    {"codigo_inei": "M2-CARR", "insumo": "carretera costo m2 referencia", "unidad": "m2", "precio": 1200, "departamento": "Loreto", "mes": 1, "anio": 2026, "fuente": "mvivienda"},
]


def seed():
    db = SessionLocal()
    try:
        obra_count = db.query(Obra).count()
        if obra_count > 0:
            print(f"BD ya tiene {obra_count} obras — saltando seed")
            return

        entidades = []
        for data in ENTIDADES:
            ent = Entidad(**data)
            db.add(ent)
            entidades.append(ent)
        db.commit()

        contratistas = []
        for data in CONTRATISTAS:
            con = Contratista(**data)
            db.add(con)
            contratistas.append(con)
        db.commit()

        for data in OBRAS:
            obra = Obra(
                codigo_infobras=data["codigo_infobras"],
                titulo=data["titulo"],
                tipo_obra=data["tipo_obra"],
                estado=data["estado"],
                presupuesto_total=Decimal(str(data["presupuesto_total"])),
                metrado_total=Decimal(str(data["metrado_total"])),
                departamento=data["departamento"],
                score_riesgo=data["score_riesgo"],
                modo_analisis=data["modo_analisis"],
                entidad_id=entidades[data["entidad_idx"]].id,
                contratista_id=contratistas[data["contratista_idx"]].id,
            )
            db.add(obra)
        db.commit()

        for data in PRECIOS:
            db.add(PrecioReferencia(
                codigo_inei=data["codigo_inei"],
                insumo=data["insumo"],
                unidad=data["unidad"],
                precio=Decimal(str(data["precio"])),
                departamento=data["departamento"],
                mes=data["mes"],
                anio=data["anio"],
                fuente=data["fuente"],
            ))
        db.commit()

        print(f"Seed completado:")
        print(f"  - {len(ENTIDADES)} entidades")
        print(f"  - {len(CONTRATISTAS)} contratistas")
        print(f"  - {len(OBRAS)} obras")
        print(f"  - {len(PRECIOS)} precios de referencia")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
