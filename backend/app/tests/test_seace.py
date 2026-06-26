"""Tests del SEACE/OCDS DataSource.

Usa respuestas mock de la API OCDS para verificar:
- Parseo de registros a obras simplificadas
- Inferencia de tipo de obra desde el título
- Manejo de errores de conexión y HTTP
"""

from unittest.mock import patch

import httpx
import pytest
from respx import MockRouter

from app.datasource.seace import SEACEDataSource, SEACEError, _inferir_tipo_obra


# --- Test de inferencia de tipo de obra ---

class TestInferirTipoObra:

    def test_edificacion_por_palabra_clave(self):
        assert _inferir_tipo_obra("Construcción de local municipal") == "edificacion"

    def test_carretera_por_palabra_clave(self):
        assert _inferir_tipo_obra("Rehabilitación de carretera vecinal") == "carretera"

    def test_agua_saneamiento(self):
        assert _inferir_tipo_obra("Mejoramiento del sistema de agua potable") == "agua_saneamiento"

    def test_educacion(self):
        assert _inferir_tipo_obra("Construcción de colegio inicial") == "educacion"

    def test_salud(self):
        assert _inferir_tipo_obra("Mejoramiento del hospital regional") == "salud"

    def test_otros_si_no_hay_match(self):
        assert _inferir_tipo_obra("Adquisición de computadoras") == "otros"

    def test_case_insensitive(self):
        assert _inferir_tipo_obra("CARRETERA Longitudinal") == "carretera"


# --- Mock de respuesta OCDS ---

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

    def test_parsear_sin_entidad_devuelve_none(self):
        data = {
            "records": [
                {
                    "ocid": "test",
                    "releases": [
                        {
                            "ocid": "test",
                            "tender": {},
                            "buyer": {},
                            "awards": [],
                        }
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


class TestSEACEHTTP:

    def test_buscar_con_exito(self, respx_mock):
        respx_mock.get("https://contratacionesabiertas.oece.gob.pe/api/ocds/records").respond(
            200, json=RESPUESTA_BUSQUEDA,
        )
        ds = SEACEDataSource()
        resultado = ds.buscar_obras(query="Lima")
        assert len(resultado) == 1

    def test_buscar_error_404(self, respx_mock):
        respx_mock.get("https://contratacionesabiertas.oece.gob.pe/api/ocds/records").respond(404)
        ds = SEACEDataSource()
        with pytest.raises(SEACEError) as exc:
            ds.buscar_obras()
        assert "404" in str(exc.value)

    def test_buscar_error_conexion(self, respx_mock):
        respx_mock.get("https://contratacionesabiertas.oece.gob.pe/api/ocds/records").mock(
            side_effect=httpx.RequestError("Connection refused"),
        )
        ds = SEACEDataSource()
        with pytest.raises(SEACEError) as exc:
            ds.buscar_obras()
        assert "Error de conexión" in str(exc.value)

    def test_obtener_por_ocid_exitoso(self, respx_mock):
        respx_mock.get("https://contratacionesabiertas.oece.gob.pe/api/ocds/record/test-ocid").respond(
            200, json=RESPUESTA_BUSQUEDA["records"][0],
        )
        ds = SEACEDataSource()
        resultado = ds.obtener_obra_por_ocid("test-ocid")
        assert resultado is not None
        assert resultado["ocid"] == "ocds-123-obra-001"

    def test_obtener_por_ocid_no_encontrado(self, respx_mock):
        respx_mock.get("https://contratacionesabiertas.oece.gob.pe/api/ocds/record/inexistente").respond(404)
        ds = SEACEDataSource()
        resultado = ds.obtener_obra_por_ocid("inexistente")
        assert resultado is None
