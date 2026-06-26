"""Backfill departamentos for obras based on entity names.

Many SEACE obras have null departamento. This script infers the departamento
from the name of the associated entity (municipality, regional government, etc.)
"""

import sys
import re
sys.path.insert(0, "/app")

from app.core.database import SessionLocal
from app.models.obra import Obra
from app.models.entidad import Entidad

# All 24 Peruvian departments + Callao
DEPARTAMENTOS = [
    "AMAZONAS", "ANCASH", "APURIMAC", "AREQUIPA", "AYACUCHO",
    "CAJAMARCA", "CALLAO", "CUSCO", "HUANCAVELICA", "HUANUCO",
    "ICA", "JUNIN", "LA LIBERTAD", "LAMBAYEQUE", "LIMA",
    "LORETO", "MADRE DE DIOS", "MOQUEGUA", "PASCO", "PIURA",
    "PUNO", "SAN MARTIN", "TACNA", "TUMBES", "UCAYALI",
]

# Provincias conocidas → departamento (solo las más comunes del dataset)
PROVINCIAS_MAP = {
    "LIMA": "LIMA",
    "CALLAO": "CALLAO",
    "AREQUIPA": "AREQUIPA",
    "CUSCO": "CUSCO",
    "TRUJILLO": "LA LIBERTAD",
    "CHICLAYO": "LAMBAYEQUE",
    "PIURA": "PIURA",
    "HUANUCO": "HUANUCO",
    "HUANCAYO": "JUNIN",
    "JUNIN": "JUNIN",
    "ICA": "ICA",
    "PUNO": "PUNO",
    "AYACUCHO": "AYACUCHO",
    "CAJAMARCA": "CAJAMARCA",
    "SAN MARTIN": "SAN MARTIN",
    "LORETO": "LORETO",
    "UCAYALI": "UCAYALI",
    "TACNA": "TACNA",
    "MOQUEGUA": "MOQUEGUA",
    "TUMBES": "TUMBES",
    "PASCO": "PASCO",
    "HUANCAVELICA": "HUANCAVELICA",
    "APURIMAC": "APURIMAC",
    "MADRE DE DIOS": "MADRE DE DIOS",
    "AMAZONAS": "AMAZONAS",
    "ANCASH": "ANCASH",
    "CAYLLOMA": "AREQUIPA",
    "CHINCHEROS": "APURIMAC",
    "CHUMBIVILCAS": "CUSCO",
    "CONDORCANQUI": "AMAZONAS",
    "DATEM DEL MARAÑON": "LORETO",
    "LAURICOCHA": "HUANUCO",
    "LAMPA": "PUNO",
    "CHEPEN": "LA LIBERTAD",
    "VIRU": "LA LIBERTAD",
    "CAÑETE": "LIMA",
    "HUAROCHIRI": "LIMA",
    "YAUYOS": "LIMA",
    "CANTA": "LIMA",
    "HUARAL": "LIMA",
    "BARRANCA": "LIMA",
    "CAJATAMBO": "LIMA",
    "OYON": "LIMA",
    "HUARMEY": "ANCASH",
    "SANTA": "ANCASH",
    "CORONGO": "ANCASH",
    "AIJA": "ANCASH",
    "CARHUAZ": "ANCASH",
    "HUARI": "ANCASH",
    "POMABAMBA": "ANCASH",
    "YUNGAY": "ANCASH",
    "MARISCAL LUZURIAGA": "ANCASH",
    "ASUNCION": "ANCASH",
    "ANTONIO RAYMONDI": "ANCASH",
    "CARLOS FERMIN FITZCARRALD": "ANCASH",
    "HUAYLAS": "ANCASH",
    "PALPA": "ICA",
    "PISCO": "ICA",
    "NAZCA": "ICA",
    "CHINCHA": "ICA",
}


def inferir_departamento(entidad: Entidad) -> str | None:
    """Infiere el departamento desde el nombre de la entidad."""
    nombre = (entidad.nombre or "").upper().strip()
    if not nombre:
        return None

    # 1. Gobierno Regional de <DEPARTAMENTO>
    m = re.search(r"GOBIERNO REGIONAL DE (\w+(?:\s+\w+)?)", nombre)
    if m:
        dep = m.group(1).strip()
        if dep in DEPARTAMENTOS:
            return dep

    # 2. Buscar departamentos directamente en el nombre
    for dep in sorted(DEPARTAMENTOS, key=len, reverse=True):
        if dep in nombre:
            return dep

    # 3. Buscar provincias conocidas
    for prov, dep in PROVINCIAS_MAP.items():
        if prov in nombre:
            return dep

    return None


def seed():
    db = SessionLocal()
    try:
        # 1. Actualizar departamento en entidades que no tienen
        entidades = db.query(Entidad).filter(Entidad.departamento.is_(None)).all()
        print(f"Entidades sin departamento: {len(entidades)}")
        actualizadas_ent = 0
        for ent in entidades:
            dep = inferir_departamento(ent)
            if dep:
                ent.departamento = dep
                actualizadas_ent += 1
        db.commit()
        print(f"  → {actualizadas_ent} entidades actualizadas")

        # 2. Actualizar departamento en obras que tienen entidad pero no departamento
        obras = db.query(Obra).filter(
            Obra.departamento.is_(None),
            Obra.entidad_id.isnot(None),
        ).all()
        print(f"\nObras sin departamento (con entidad): {len(obras)}")
        actualizadas_obra = 0
        for obra in obras:
            entidad = db.query(Entidad).filter(Entidad.id == obra.entidad_id).first()
            if entidad and entidad.departamento:
                obra.departamento = entidad.departamento
                actualizadas_obra += 1
                if actualizadas_obra % 500 == 0:
                    db.commit()
        db.commit()
        print(f"  → {actualizadas_obra} obras actualizadas")

        # 3. Resumen por departamento
        resumen = db.query(Obra.departamento, db.func.count(Obra.id)).group_by(Obra.departamento).all()
        print(f"\nResumen por departamento:")
        for dep, cnt in sorted(resumen, key=lambda x: x[1] if x[0] else 0, reverse=True):
            print(f"  {dep or 'SIN DEPARTAMENTO'}: {cnt}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
