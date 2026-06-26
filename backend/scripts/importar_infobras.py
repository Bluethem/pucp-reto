"""Importa el dataset de INFOBRAS (DataSet-Obras-Publicas.xlsx) a la BD.

Tiene ~191k obras con datos reales: presupuesto, estado, entidad, contratista, etc.
Usa parsing XML streaming para manejar el archivo de 726MB.
"""

import sys
import zipfile
import xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, "/app")

from app.core.database import SessionLocal
from app.models.contratista import Contratista
from app.models.entidad import Entidad
from app.models.obra import Obra

RUTA = Path("/app/data/DataSet-Obras-Publicas 26-06-2026.xlsx").resolve()

COL_MAP = {}  # nombre_columna → índice

ESTADOS_MAP = {
    "EN EJECUCIÓN": "ejecucion",
    "CONCLUIDO": "concluido",
    "PARALIZADO": "paralizado",
    "POR EJECUTAR": "planeado",
}


def parse_valor(cell_str: str) -> str:
    """Extrae el valor texto de una celda XML."""
    if not cell_str:
        return ""
    import re
    m = re.search(r"<x:v>(.*?)</x:v>", cell_str)
    return m.group(1) if m else ""


def seed(limite: int = 5000):
    """Importa hasta `limite` obras desde el dataset."""
    db = SessionLocal()
    try:
        print(f"Abriendo {RUTA.name} ({RUTA.stat().st_size / 1024 / 1024:.0f} MB)...")

        with zipfile.ZipFile(RUTA) as z:
            with z.open("xl/worksheets/sheet1.xml") as f:
                context = ET.iterparse(f, events=("end",))
                cache_entidades = {}
                cache_contratistas = {}
                creadas = 0
                row_idx = 0
                header_done = False

                for _, elem in context:
                    if elem.tag.endswith("row"):
                        cells = []
                        for c in elem:
                            v = c.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v")
                            cells.append(v.text if v is not None else "")

                        row_idx += 1

                        # Row 4 = header
                        if row_idx == 4:
                            COL_MAP.clear()
                            for i, val in enumerate(cells):
                                COL_MAP[val.strip()] = i
                            print(f"Columnas mapeadas: {len(COL_MAP)}")
                            print(f"Col 'Código INFOBRAS': idx {COL_MAP.get('Código INFOBRAS', '?')}")
                            header_done = True
                            continue

                        if not header_done or row_idx < 5:
                            continue

                        # Extraer columnas relevantes
                        def col(nombre):
                            idx = COL_MAP.get(nombre)
                            return cells[idx] if idx is not None and idx < len(cells) else ""

                        codigo_infobras = col("Código INFOBRAS")
                        nombre_obra = col("Nombre de obra")
                        if not codigo_infobras or not nombre_obra:
                            continue

                        entidad_nombre = col("Entidad Pública")
                        contratista_nombre = col("Nombre o razón social de la empresa o consorcio")
                        ruc = col("RUC (Ejecución)")
                        departamento = col("Departamento")
                        provincia = col("Provincia")
                        distrito = col("Distrito")

                        monto_str = col("Costo de obra según Expediente técnico") or col("Monto Viable/Aprobado") or "0"
                        monto = Decimal(monto_str.replace(",", "")) if monto_str.replace(",", "").replace(".", "").isdigit() else None

                        estado_raw = col("Estado de ejecución").upper().strip()
                        estado = ESTADOS_MAP.get(estado_raw, "ejecucion")

                        # Entidad
                        entidad_id = None
                        if entidad_nombre and entidad_nombre not in cache_entidades:
                            ent = db.query(Entidad).filter(Entidad.nombre == entidad_nombre).first()
                            if not ent:
                                ent = Entidad(
                                    nombre=entidad_nombre,
                                    tipo="municipalidad_distrital",
                                    departamento=departamento,
                                    provincia=provincia,
                                    distrito=distrito,
                                )
                                db.add(ent)
                                db.flush()
                            cache_entidades[entidad_nombre] = ent.id
                            entidad_id = ent.id
                        elif entidad_nombre:
                            entidad_id = cache_entidades[entidad_nombre]

                        # Contratista (merge para evitar duplicados)
                        contratista_id = None
                        if contratista_nombre and contratista_nombre not in cache_contratistas:
                            con = db.query(Contratista).filter(Contratista.razon_social == contratista_nombre).first()
                            if not con:
                                ruc_clean = (ruc.replace("-", "").strip()[:8] if ruc else f"INF{abs(hash(contratista_nombre)) % 10**7}")
                                con = Contratista(ruc=f"{ruc_clean}{abs(hash(contratista_nombre)) % 1000:03d}"[:11], razon_social=contratista_nombre)
                                db.add(con)
                                db.flush()
                            cache_contratistas[contratista_nombre] = con.id
                            contratista_id = con.id
                        elif contratista_nombre:
                            contratista_id = cache_contratistas[contratista_nombre]

                        # Insertar obra
                        tipo_obra = "edificacion"
                        if departamento:
                            tipo_obra = "edificacion"

                        db.add(Obra(
                            codigo_infobras=codigo_infobras[:100],
                            titulo=nombre_obra[:500],
                            tipo_obra=tipo_obra,
                            estado=estado,
                            presupuesto_total=monto,
                            departamento=departamento,
                            provincia=provincia,
                            distrito=distrito,
                            modo_analisis="fallback_m2",
                            entidad_id=entidad_id,
                            contratista_id=contratista_id,
                        ))
                        creadas += 1

                        if creadas % 200 == 0:
                            db.commit()
                            print(f"  → {creadas} obras...", end="\r")

                        if creadas >= limite:
                            break

                        elem.clear()

                db.commit()
                print(f"\n✅ Importación INFOBRAS completada:")
                print(f"  - {creadas} obras ({len(cache_entidades)} entidades, {len(cache_contratistas)} contratistas)")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limite", type=int, default=5000, help="Máx obras a importar")
    args = parser.parse_args()
    seed(limite=args.limite)
