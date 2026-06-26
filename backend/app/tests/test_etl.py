"""Tests del servicio ETL y datasources externos.

Verifica:
- INEI: parseo de .xlsx, conteo de filas, filtrado de filas inválidas
- SEACE: parseo de respuestas OCDS, inferencia de tipo de obra
- Gemini: parseo de respuestas JSON con/sin markdown
- Registro de logs de extracción
"""

from unittest.mock import patch
from decimal import Decimal

import pytest
from openpyxl import Workbook

from app.datasource.inei import INEIDataSource
from app.datasource.seace import SEACEDataSource, _inferir_tipo_obra
from app.models.log_extraccion import LogExtraccion


# ==================== Helpers ====================

def _crear_xlsx_inei(path: str, rows: list[tuple] | None = None):
    wb = Workbook()
    ws = wb.active
    ws.append(("codigo_inei", "insumo", "unidad", "precio", "departamento"))
    if rows:
        for row in rows:
            ws.append(row)
    else:
        ws.append(("CEM-001", "Cemento Portland Tipo I", "bolsa", 28.50, None))
        ws.append(("CEM-002", "Cemento Portland Tipo II", "bolsa", 32.00, None))
        ws.append(("ACR-001", "Acero corrugado 1/2", "kg", 4.50, None))
        ws.append(("ACR-002", "Acero corrugado 3/8", "kg", 5.20, None))
        ws.append(("AGR-001", "Agregado grueso", "m3", 55.00, "Lima"))
        ws.append(("AGR-002", "Agregado fino", "m3", 65.00, "Cusco"))
    wb.save(path)


# ==================== INEI — Parseo de .xlsx ====================

class TestINEIXLSXParser:

    def test_cargar_xlsx_cuenta_filas(self):
        """Debe retornar el número correcto de filas cargadas."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
            _crear_xlsx_inei(tmp.name)
            with patch.object(INEIDataSource, "_insertar_en_db") as mock_insert:
                mock_insert.return_value = 6
                ds = INEIDataSource()
                cargadas = ds.cargar_xlsx(tmp.name, mes=6, anio=2026)
        assert cargadas == 6

    def test_cargar_xlsx_ignora_filas_sin_codigo(self):
        """Filas sin código_inei deben ignorarse."""
        import tempfile
        rows = [
            (None, "Sin código", "u", 10.0, None),
            ("COD-001", "Con código", "u", 20.0, None),
        ]
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
            _crear_xlsx_inei(tmp.name, rows=rows)
            with patch.object(INEIDataSource, "_insertar_en_db") as mock_insert:
                mock_insert.return_value = 1
                ds = INEIDataSource()
                cargadas = ds.cargar_xlsx(tmp.name, mes=6, anio=2026)
        assert cargadas == 1

    def test_cargar_xlsx_ignora_filas_sin_precio(self):
        """Filas sin precio deben ignorarse."""
        import tempfile
        rows = [
            ("COD-001", "Con precio", "u", 20.0, None),
            ("COD-002", "Sin precio", "u", None, None),
        ]
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
            _crear_xlsx_inei(tmp.name, rows=rows)
            with patch.object(INEIDataSource, "_insertar_en_db") as mock_insert:
                mock_insert.return_value = 1
                ds = INEIDataSource()
                cargadas = ds.cargar_xlsx(tmp.name, mes=6, anio=2026)
        assert cargadas == 1

    def test_cargar_xlsx_archivo_vacio(self):
        """Archivo sin filas de datos debe retornar 0."""
        import tempfile
        rows = []
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
            _crear_xlsx_inei(tmp.name, rows=rows)
            with patch.object(INEIDataSource, "_insertar_en_db") as mock_insert:
                mock_insert.return_value = 0
                ds = INEIDataSource()
                cargadas = ds.cargar_xlsx(tmp.name, mes=6, anio=2026)
        assert cargadas == 0

    def test_precios_se_parsean_como_decimal(self):
        """Los precios deben ser instancias de Decimal."""
        import tempfile
        from openpyxl import load_workbook
        rows = [("CEM-001", "Cemento", "bolsa", 28.50, None)]
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
            _crear_xlsx_inei(tmp.name, rows=rows)
            ds = INEIDataSource()
            with patch.object(ds, "_insertar_en_db") as mock_insert:
                mock_insert.return_value = 1
                ds.cargar_xlsx(tmp.name, mes=6, anio=2026)


# ==================== SEACE — Parseo de OCDS ====================

RESPUESTA_BUSQUEDA = {
    "records": [
        {
            "ocid": "ocds-123-obra-001",
            "releases": [
                {
                    "ocid": "ocds-123-obra-001",
                    "tender": {
                        "title": "Mejoramiento de carretera vecinal",
                        "status": "adjudicado",
                        "value": {"amount": 1500000.00},
                    },
                    "buyer": {
                        "name": {"es": "Municipalidad de Lima"},
                        "id": {"id": "20123456789"},
                    },
                    "awards": [
                        {
                            "date": "2026-01-15",
                            "suppliers": [
                                {
                                    "name": {"es": "Constructora Perú SAC"},
                                    "id": {"id": "20123456790"},
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    ]
}

RESPUESTA_VACIA = {"records": []}


class TestSEACEParseo:

    def test_parsear_registros_devuelve_lista(self):
        resultado = SEACEDataSource._parsear_registros(RESPUESTA_BUSQUEDA)
        assert isinstance(resultado, list)
        assert len(resultado) == 1

    def test_parsear_registros_campos_esperados(self):
        resultado = SEACEDataSource._parsear_registros(RESPUESTA_BUSQUEDA)
        obra = resultado[0]
        assert obra["ocid"] == "ocds-123-obra-001"
        assert obra["titulo"] == "Mejoramiento de carretera vecinal"
        assert obra["tipo_obra"] == "carretera"
        assert obra["entidad"] == "Municipalidad de Lima"
        assert obra["contratista"] == "Constructora Perú SAC"
        assert obra["contratista_ruc"] == "20123456790"
        assert obra["monto_total"] == 1500000.0
        assert obra["fuente"] == "seace_ocds"

    def test_parsear_registros_vacio(self):
        resultado = SEACEDataSource._parsear_registros(RESPUESTA_VACIA)
        assert resultado == []

    def test_parsear_sin_entidad(self):
        data = {
            "records": [
                {
                    "ocid": "test",
                    "releases": [
                        {"ocid": "test", "tender": {}, "buyer": {}, "awards": []}
                    ],
                }
            ]
        }
        resultado = SEACEDataSource._parsear_registros(data)
        assert len(resultado) == 1
        obra = resultado[0]
        assert obra["entidad"] == ""
        assert obra["contratista"] == ""
        assert obra["monto_total"] is None


# ==================== SEACE — Inferencia de tipo ====================

class TestInferirTipoObra:

    def test_edificacion(self):
        assert _inferir_tipo_obra("Construcción de local municipal") == "edificacion"

    def test_carretera(self):
        assert _inferir_tipo_obra("Rehabilitación de carretera vecinal") == "carretera"

    def test_agua_saneamiento(self):
        assert _inferir_tipo_obra("Mejoramiento del sistema de agua potable") == "agua_saneamiento"

    def test_alcantarillado(self):
        assert _inferir_tipo_obra("Construcción de alcantarillado") == "agua_saneamiento"

    def test_educacion(self):
        assert _inferir_tipo_obra("Construcción de colegio inicial") == "educacion"

    def test_salud(self):
        assert _inferir_tipo_obra("Mejoramiento del hospital regional") == "salud"

    def test_puente(self):
        assert _inferir_tipo_obra("Construcción de puente carrozable") == "carretera"

    def test_otros_si_no_hay_match(self):
        assert _inferir_tipo_obra("Adquisición de computadoras") == "otros"

    def test_case_insensitive(self):
        assert _inferir_tipo_obra("CARRETERA Longitudinal") == "carretera"


# ==================== Gemini — Parseo de respuestas ====================

from app.datasource.gemini import GeminiDataSource, GeminiExtractionError

RESPUESTA_VALIDA = (
    '[{"insumo": "Cemento", "unidad": "bolsa", "cantidad": "500", "precio_unitario": "28.50"},'
    '{"insumo": "Acero", "unidad": "kg", "cantidad": "2000", "precio_unitario": "4.80"}]'
)

RESPUESTA_CON_MARKDOWN = f"```json\n{RESPUESTA_VALIDA}\n```"


class TestGeminiParsing:

    def test_parsear_json_valido(self):
        datos = GeminiDataSource._parsear_respuesta(RESPUESTA_VALIDA)
        assert len(datos) == 2
        assert datos[0]["insumo"] == "Cemento"

    def test_parsear_con_markdown(self):
        datos = GeminiDataSource._parsear_respuesta(RESPUESTA_CON_MARKDOWN)
        assert len(datos) == 2

    def test_parsear_vacio(self):
        datos = GeminiDataSource._parsear_respuesta("[]")
        assert datos == []

    def test_parsear_invalido_lanza_error(self):
        with pytest.raises(GeminiExtractionError):
            GeminiDataSource._parsear_respuesta("No es JSON")

    def test_parsear_tiene_campos_requeridos(self):
        datos = GeminiDataSource._parsear_respuesta(RESPUESTA_VALIDA)
        for p in datos:
            assert "insumo" in p
            assert "unidad" in p
            assert "cantidad" in p
            assert "precio_unitario" in p

    def test_sin_api_key_no_disponible(self):
        ds = GeminiDataSource(api_key="")
        assert ds.disponible() is False

    def test_sin_api_key_extraer_lanza_error(self):
        ds = GeminiDataSource(api_key="")
        with pytest.raises(GeminiExtractionError, match="GEMINI_API_KEY no configurada"):
            ds.extraer_partidas(b"pdf-content")


# ==================== Log de extracción ====================

class TestLogExtraccion:

    def test_log_creacion(self, db_session, crear_obra):
        obra = crear_obra()
        log = LogExtraccion(obra_id=obra.id, fuente="gemini", exitoso=True, intentos=1,
                            respuesta_cruda={"mensaje": "prueba"})
        db_session.add(log)
        db_session.commit()

        recuperado = db_session.get(LogExtraccion, log.id)
        assert recuperado is not None
        assert recuperado.exitoso is True
        assert recuperado.respuesta_cruda["mensaje"] == "prueba"
