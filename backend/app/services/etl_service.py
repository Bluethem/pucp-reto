"""Servicio ETL — orquestación de ingesta de fuentes externas.

Usa APScheduler (ADR-002) para ejecutar pipelines de forma programada:
  - INEI: mensual (precios de referencia)
  - SEACE/OCDS: diaria (metadatos de obra)
  - JNE: semanal (autoridades)
  - Gemini: bajo demanda (partidas de PDF)

Cada pipeline sigue el patrón:
  1. Consultar fuente externa
  2. Transformar al modelo interno
  3. Cargar (upsert) en BD local
  4. Cachear respuesta cruda en log_extraccion
"""

from datetime import datetime
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.log_extraccion import LogExtraccion


class ETLResult:
    def __init__(self, fuente: str, exitoso: bool, registros: int, error: Optional[str] = None):
        self.fuente = fuente
        self.exitoso = exitoso
        self.registros = registros
        self.error = error


class ETLService:
    """Orquestador de pipelines ETL."""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._setup_jobs()

    def _setup_jobs(self):
        self.scheduler.add_job(
            self.sincronizar_inei, "cron", day=1, hour=6, minute=0,
            id="etl_inei", replace_existing=True,
        )
        self.scheduler.add_job(
            self.sincronizar_seace, "interval", hours=24,
            id="etl_seace", replace_existing=True,
        )

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown(wait=False)

    # --- Firecrawl + Gemini (extracción de partidas desde PDF) ---

    def extraer_partidas_obra(self, codigo_infobras: str) -> ETLResult:
        """Pipeline completo: Firecrawl descarga PDF → Gemini extrae partidas."""
        from app.datasource.firecrawl import FirecrawlDataSource

        from app.models.partida import PartidaObra
        from app.models.obra import Obra
        from app.models.log_extraccion import LogExtraccion

        db = SessionLocal()
        try:
            firecrawl = FirecrawlDataSource()
            partidas_data = firecrawl.extraer_partidas_de_obra(codigo_infobras)

            obra = db.query(Obra).filter(
                Obra.codigo_infobras == codigo_infobras
            ).first()

            registros = 0
            for pd in partidas_data:
                partida = PartidaObra(
                    obra_id=obra.id if obra else None,
                    insumo=pd.get("insumo", ""),
                    codigo_inei=pd.get("codigo_inei"),
                    unidad=pd.get("unidad", ""),
                    cantidad=pd.get("cantidad"),
                    precio_declarado=pd.get("precio_unitario"),
                )
                db.add(partida)
                registros += 1

            db.add(LogExtraccion(
                obra_id=obra.id if obra else None,
                fuente="gemini",
                exitoso=True,
                respuesta_cruda={"partidas": len(partidas_data)},
                intentos=1,
            ))
            db.commit()

            return ETLResult("firecrawl_gemini", True, registros)
        except Exception as exc:
            db.rollback()
            return ETLResult("firecrawl_gemini", False, 0, str(exc))
        finally:
            db.close()

    # --- INEI ---

    def sincronizar_inei(self) -> ETLResult:
        """Descarga el .xlsx mensual de INEI y carga los precios en BD."""
        from app.datasource.inei import INEIDataSource

        db = SessionLocal()
        try:
            url_inei = _obtener_url_ultimo_indice()
            if not url_inei:
                return ETLResult("inei", False, 0, "No se pudo obtener URL del índice")

            import httpx
            import tempfile

            resp = httpx.get(url_inei, follow_redirects=True, timeout=60)
            resp.raise_for_status()

            with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
                tmp.write(resp.content)
                tmp.flush()
                now = datetime.utcnow()
                ds = INEIDataSource()
                cargadas = ds.cargar_xlsx(tmp.name, mes=now.month, anio=now.year)

            _registrar_log(db, "inei", True, {"url": url_inei, "filas": cargadas})
            return ETLResult("inei", True, cargadas)
        except Exception as exc:
            _registrar_log(db, "inei", False, {"error": str(exc)})
            return ETLResult("inei", False, 0, str(exc))
        finally:
            db.close()

    # --- SEACE/OCDS ---

    def sincronizar_seace(self, query: str = "obra", limit: int = 500) -> ETLResult:
        """Obtiene obras desde SEACE/OCDS y las upserta en BD."""
        from app.datasource.seace import SEACEDataSource
        from app.models.obra import Obra
        from app.models.contratista import Contratista
        from app.models.entidad import Entidad

        db = SessionLocal()
        try:
            ds = SEACEDataSource()
            obras_api = ds.buscar_obras(query=query, limit=limit)

            registros = 0
            for obra_data in obras_api:
                contratista = None
                if obra_data.get("contratista_ruc"):
                    contratista = db.query(Contratista).filter(
                        Contratista.ruc == obra_data["contratista_ruc"]
                    ).first()
                    if not contratista and obra_data.get("contratista"):
                        contratista = Contratista(
                            ruc=obra_data["contratista_ruc"],
                            razon_social=obra_data["contratista"],
                        )
                        db.add(contratista)
                        db.flush()

                entidad = None
                if obra_data.get("entidad"):
                    entidad = db.query(Entidad).filter(
                        Entidad.nombre == obra_data["entidad"]
                    ).first()
                    if not entidad:
                        entidad = Entidad(
                            nombre=obra_data["entidad"],
                            tipo="municipalidad_distrital",
                        )
                        db.add(entidad)
                        db.flush()

                obra_existente = db.query(Obra).filter(
                    Obra.codigo_infobras == obra_data.get("ocid", "")
                ).first()

                if not obra_existente:
                    obra = Obra(
                        codigo_infobras=obra_data.get("ocid", ""),
                        titulo=obra_data.get("titulo", "Sin título"),
                        tipo_obra=obra_data.get("tipo_obra", "otros"),
                        estado="ejecucion",
                        presupuesto_total=obra_data.get("monto_total"),
                        contratista_id=contratista.id if contratista else None,
                        entidad_id=entidad.id if entidad else None,
                        modo_analisis="fallback_m2",
                    )
                    db.add(obra)
                    registros += 1

            db.commit()
            _registrar_log(db, "seace", True, {"query": query, "obras": len(obras_api)})
            return ETLResult("seace", True, registros)
        except Exception as exc:
            db.rollback()
            _registrar_log(db, "seace", False, {"error": str(exc)})
            return ETLResult("seace", False, 0, str(exc))
        finally:
            db.close()


# --- Helpers ---

def _obtener_url_ultimo_indice() -> Optional[str]:
    """Retorna la URL del último .xlsx de Índices Unificados de Precios del INEI.

    Por ahora retorna una URL conocida. En producción debe scrapear inei.gob.pe
    para obtener la última publicación.
    """
    # TODO: scrapear inei.gob.pe para obtener la URL más reciente
    return None


def _registrar_log(db: Session, fuente: str, exitoso: bool, detalle: dict):
    from app.models.log_extraccion import LogExtraccion

    log = LogExtraccion(
        fuente=fuente,
        exitoso=exitoso,
        respuesta_cruda=detalle,
    )
    db.add(log)
    db.commit()
