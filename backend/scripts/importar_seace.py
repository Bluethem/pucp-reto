"""Importa el dump OCDS del SEACE a la BD.

Lee data/2026-06_seace_v3.json y crea registros de obras, contratistas y entidades.
Procesa en lotes para mejor performance.
"""

import json
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, "/app")

from sqlalchemy import text

from app.core.database import SessionLocal, engine
from app.models.contratista import Contratista
from app.models.entidad import Entidad
from app.models.obra import Obra

RUTA_JSON = Path("/app/data/2026-06_seace_v3.json").resolve()

TIPOS = {
    "carretera": "carretera", "puente": "carretera", "pista": "carretera",
    "agua": "agua_saneamiento", "alcantarillado": "agua_saneamiento", "saneamiento": "agua_saneamiento",
    "hospital": "salud", "salud": "salud", "colegio": "educacion", "educacion": "educacion",
    "local": "edificacion", "edificacion": "edificacion", "construccion": "edificacion",
    "mejoramiento": "edificacion", "rehabilitacion": "edificacion",
}


def inferir_tipo(titulo: str, desc: str = "") -> str:
    texto = (titulo + " " + desc).lower()
    for kw, tipo in TIPOS.items():
        if kw in texto:
            return tipo
    return "otros"


def seed():
    # Limpiar BD primero
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM partidas_obra"))
        conn.execute(text("DELETE FROM log_extraccion"))
        conn.execute(text("DELETE FROM comentarios"))
        conn.execute(text("DELETE FROM suscripciones"))
        conn.execute(text("DELETE FROM obras"))
        conn.execute(text("DELETE FROM autoridades"))
        conn.execute(text("DELETE FROM contratistas"))
        conn.execute(text("DELETE FROM entidades"))

    db = SessionLocal()
    try:
        with open(RUTA_JSON) as f:
            data = json.load(f)

        registros = data.get("records", [])
        print(f"SEACE: {len(registros)} registros")

        entidades_dict = {}
        contratistas_dict = {}
        obras_list = []
        creadas = 0

        for record in registros:
            cr = record.get("compiledRelease", record)
            ocid = cr.get("ocid", "")

            buyer = cr.get("buyer", {})
            buyer_name = buyer.get("name", "") if isinstance(buyer, dict) else str(buyer)

            tender = cr.get("tender", {})
            titulo = tender.get("title", "") or tender.get("description", "") or ocid
            descripcion = tender.get("description", "")
            monto = tender.get("value", {}).get("amount")

            awards = cr.get("awards", [])
            supplier_name = ""
            if awards:
                suppliers = awards[0].get("suppliers", [])
                if suppliers:
                    s = suppliers[0]
                    supplier_name = s.get("name", {}).get("es", "") if isinstance(s.get("name"), dict) else str(s.get("name", ""))

            # Entidades
            if buyer_name and buyer_name not in entidades_dict:
                ent = db.query(Entidad).filter(Entidad.nombre == buyer_name).first()
                if not ent:
                    ent = Entidad(nombre=buyer_name, tipo="municipalidad_distrital")
                    db.add(ent)
                    db.flush()
                entidades_dict[buyer_name] = ent.id

            # Contratistas
            if supplier_name and supplier_name not in contratistas_dict:
                con = db.query(Contratista).filter(Contratista.razon_social == supplier_name).first()
                if not con:
                    con = Contratista(
                        ruc=f"S{abs(hash(supplier_name)) % 10**9}",
                        razon_social=supplier_name,
                    )
                    db.add(con)
                    db.flush()
                contratistas_dict[supplier_name] = con.id

            obras_list.append(Obra(
                codigo_infobras=ocid[:100],
                titulo=(titulo or "Sin título")[:500],
                tipo_obra=inferir_tipo(titulo, descripcion),
                estado="ejecucion",
                presupuesto_total=Decimal(str(monto)) if monto else None,
                modo_analisis="fallback_m2",
                entidad_id=entidades_dict.get(buyer_name),
                contratista_id=contratistas_dict.get(supplier_name),
            ))
            creadas += 1

            if creadas % 500 == 0:
                db.commit()
                print(f"  → {creadas}/{len(registros)}...")

        # Insert por lotes
        for i in range(0, len(obras_list), 200):
            db.add_all(obras_list[i:i+200])
            db.commit()
            print(f"  → lote {i//200 + 1} guardado ({min(i+200, creadas)}/{creadas})")

        print(f"\n✅ Importación SEACE completada:")
        print(f"  - {creadas} obras")
        print(f"  - {len(entidades_dict)} entidades")
        print(f"  - {len(contratistas_dict)} contratistas")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
