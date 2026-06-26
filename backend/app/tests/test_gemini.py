"""Tests del GeminiDataSource (extracción de partidas desde PDFs).

Verifica:
- Parseo de respuestas JSON válidas (con y sin markdown)
- Manejo de respuestas inválidas
- Comportamiento sin API key configurada
"""

import json
from unittest.mock import patch, MagicMock

import pytest

from app.datasource.gemini import GeminiDataSource, GeminiExtractionError


# --- Respuestas simuladas de Gemini ---

RESPUESTA_VALIDA = json.dumps([
    {"insumo": "Cemento Portland Tipo I", "unidad": "bolsa", "cantidad": "500", "precio_unitario": "28.50"},
    {"insumo": "Acero corrugado 1/2\"", "unidad": "kg", "cantidad": "2000", "precio_unitario": "4.80"},
    {"insumo": "Arena gruesa", "unidad": "m3", "cantidad": "50", "precio_unitario": "55.00"},
    {"insumo": "Piedra chancada", "unidad": "m3", "cantidad": "40", "precio_unitario": "62.00"},
    {"insumo": "Madera tornillo", "unidad": "p2", "cantidad": "300", "precio_unitario": "8.90"},
])

RESPUESTA_CON_MARKDOWN = f"""```json
{RESPUESTA_VALIDA}
```"""

RESPUESTA_INVALIDA = "No pude extraer la tabla del PDF."

RESPUESTA_VACIA = "[]"

PDF_MOCK = b"%PDF-1.4 mock pdf content for testing"


class TestGeminiParsing:

    def test_parsear_respuesta_valida(self):
        """JSON plano sin markdown debe parsearse correctamente."""
        datos = GeminiDataSource._parsear_respuesta(RESPUESTA_VALIDA)
        assert isinstance(datos, list)
        assert len(datos) == 5
        assert datos[0]["insumo"] == "Cemento Portland Tipo I"
        assert datos[0]["precio_unitario"] == "28.50"

    def test_parsear_respuesta_con_markdown(self):
        """JSON envuelto en ```json ... ``` debe parsearse."""
        datos = GeminiDataSource._parsear_respuesta(RESPUESTA_CON_MARKDOWN)
        assert isinstance(datos, list)
        assert len(datos) == 5

    def test_parsear_respuesta_vacia(self):
        """Array vacío es válido."""
        datos = GeminiDataSource._parsear_respuesta(RESPUESTA_VACIA)
        assert datos == []

    def test_parsear_respuesta_invalida_lanza_error(self):
        """Texto que no es JSON debe lanzar GeminiExtractionError."""
        with pytest.raises(GeminiExtractionError):
            GeminiDataSource._parsear_respuesta(RESPUESTA_INVALIDA)

    def test_parsear_lista_con_campos_esperados(self):
        """Cada partida debe tener los campos: insumo, unidad, cantidad, precio_unitario."""
        datos = GeminiDataSource._parsear_respuesta(RESPUESTA_VALIDA)
        for partida in datos:
            assert "insumo" in partida
            assert "unidad" in partida
            assert "cantidad" in partida
            assert "precio_unitario" in partida


class TestGeminiDisponibilidad:

    def test_sin_api_key_no_disponible(self):
        """Sin API key, disponible() debe retornar False."""
        ds = GeminiDataSource(api_key="")
        assert ds.disponible() is False

    def test_con_api_key_disponible(self):
        """Con API key, disponible() debe retornar True."""
        ds = GeminiDataSource(api_key="fake-key-12345")
        assert ds.disponible() is True

    def test_extraer_sin_api_key_lanza_error(self):
        """Llamar extraer_partidas sin API key debe lanzar GeminiExtractionError."""
        ds = GeminiDataSource(api_key="")
        with pytest.raises(GeminiExtractionError, match="GEMINI_API_KEY no configurada"):
            ds.extraer_partidas(PDF_MOCK)


class TestGeminiExtraccion:

    @patch("google.generativeai.GenerativeModel")
    def test_extraccion_exitosa(self, mock_model):
        """Extracción exitosa debe retornar lista de partidas."""
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value.text = RESPUESTA_VALIDA
        mock_model.return_value = mock_instance

        ds = GeminiDataSource(api_key="fake-key")
        resultado = ds.extraer_partidas(PDF_MOCK)

        assert isinstance(resultado, list)
        assert len(resultado) == 5
        assert resultado[0]["insumo"] == "Cemento Portland Tipo I"

    @patch("google.generativeai.GenerativeModel")
    def test_extraccion_maneja_error_api(self, mock_model):
        """Error de API debe lanzar GeminiExtractionError."""
        mock_instance = MagicMock()
        mock_instance.generate_content.side_effect = Exception("API timeout")
        mock_model.return_value = mock_instance

        ds = GeminiDataSource(api_key="fake-key")
        with pytest.raises(GeminiExtractionError):
            ds.extraer_partidas(PDF_MOCK)

    @patch("google.generativeai.GenerativeModel")
    def test_prompt_incluye_instrucciones(self, mock_model):
        """El prompt debe incluir las claves exactas esperadas."""
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value.text = RESPUESTA_VALIDA
        mock_model.return_value = mock_instance

        ds = GeminiDataSource(api_key="fake-key")
        ds.extraer_partidas(PDF_MOCK)

        args, _ = mock_instance.generate_content.call_args
        prompt_text = args[0][0] if isinstance(args[0], list) else str(args[0])
        assert "insumo" in prompt_text
        assert "unidad" in prompt_text
        assert "cantidad" in prompt_text
        assert "precio_unitario" in prompt_text
        assert "JSON" in prompt_text

    @patch("google.generativeai.GenerativeModel")
    def test_extraccion_con_markdown_en_respuesta(self, mock_model):
        """Respuesta con markdown debe parsearse igual que JSON plano."""
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value.text = RESPUESTA_CON_MARKDOWN
        mock_model.return_value = mock_instance

        ds = GeminiDataSource(api_key="fake-key")
        resultado = ds.extraer_partidas(PDF_MOCK)

        assert len(resultado) == 5
