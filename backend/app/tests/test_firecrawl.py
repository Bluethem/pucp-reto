"""Tests del FirecrawlDataSource (descarga de PDFs desde INFOBRAS).

Verifica:
- Parseo de HTML de INFOBRAS para encontrar PDFs
- Pipeline completo Firecrawl → Gemini (mocks)
- Manejo de errores (sin API key, PDF no encontrado)
"""

from unittest.mock import patch, MagicMock

import pytest

from app.datasource.firecrawl import _FirecrawlApp, FirecrawlDataSource, FirecrawlError


# --- Mock de página INFOBRAS ---

HTML_CON_PDF = """
<html>
<body>
  <h1>Ficha de Obra</h1>
  <a href="/expedientes/obra-001.pdf">Expediente Técnico</a>
  <a href="/expedientes/obra-001-planos.pdf">Planos</a>
</body>
</html>
"""

HTML_SIN_PDF = """
<html>
<body>
  <h1>Ficha de Obra</h1>
  <p>No hay expediente disponible</p>
</body>
</html>
"""

PARTIDAS_MOCK = [
    {"insumo": "Cemento", "unidad": "bolsa", "cantidad": "500", "precio_unitario": "28.50"},
    {"insumo": "Acero", "unidad": "kg", "cantidad": "2000", "precio_unitario": "4.80"},
]


class TestFirecrawlBuscarPDF:

    def test_sin_api_key_no_disponible(self):
        ds = FirecrawlDataSource(api_key="")
        assert ds.disponible() is False

    def test_con_api_key_disponible(self):
        ds = FirecrawlDataSource(api_key="fake-key")
        assert ds.disponible() is True

    def test_buscar_url_pdf_sin_api_key_lanza_error(self):
        ds = FirecrawlDataSource(api_key="")
        with pytest.raises(FirecrawlError, match="FIRECRAWL_API_KEY no configurada"):
            ds.buscar_url_pdf("OBRA-001")

    def test_buscar_url_pdf_encuentra_enlace(self):
        mock_app = MagicMock()
        mock_app.scrape_url.return_value = {"html": HTML_CON_PDF}

        with patch("app.datasource.firecrawl._FirecrawlApp", return_value=mock_app):
            ds = FirecrawlDataSource(api_key="fake-key")
            url = ds.buscar_url_pdf("OBRA-001")

        assert url is not None
        assert url.endswith(".pdf")
        assert "expedientes/obra-001.pdf" in url

    def test_buscar_url_pdf_sin_enlace_lanza_error(self):
        mock_app = MagicMock()
        mock_app.scrape_url.return_value = {"html": HTML_SIN_PDF}

        with patch("app.datasource.firecrawl._FirecrawlApp", return_value=mock_app):
            ds = FirecrawlDataSource(api_key="fake-key")
            with pytest.raises(FirecrawlError, match="No se encontró PDF"):
                ds.buscar_url_pdf("OBRA-001")

    def test_buscar_url_pdf_convierte_ruta_relativa(self):
        mock_app = MagicMock()
        mock_app.scrape_url.return_value = {"html": HTML_CON_PDF}

        with patch("app.datasource.firecrawl._FirecrawlApp", return_value=mock_app):
            ds = FirecrawlDataSource(api_key="fake-key")
            url = ds.buscar_url_pdf("OBRA-001")

        assert url.startswith("https://")


class TestFirecrawlDescargarPDF:

    def test_descargar_pdf_retorna_bytes(self):
        mock_app = MagicMock()
        mock_app.scrape_url.return_value = {"raw": b"%PDF-1.4 mock content"}

        with patch("app.datasource.firecrawl._FirecrawlApp", return_value=mock_app):
            ds = FirecrawlDataSource(api_key="fake-key")
            pdf_bytes = ds.descargar_pdf("https://example.com/test.pdf")

        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b"%PDF")

    def test_descargar_pdf_error_red(self):
        mock_app = MagicMock()
        mock_app.scrape_url.side_effect = Exception("Connection timeout")

        with patch("app.datasource.firecrawl._FirecrawlApp", return_value=mock_app):
            ds = FirecrawlDataSource(api_key="fake-key")
            with pytest.raises(FirecrawlError, match="Error descargando"):
                ds.descargar_pdf("https://example.com/test.pdf")

    def test_descargar_pdf_sin_api_key(self):
        ds = FirecrawlDataSource(api_key="")
        with pytest.raises(FirecrawlError, match="FIRECRAWL_API_KEY no configurada"):
            ds.descargar_pdf("https://example.com/test.pdf")


class TestFirecrawlPipelineCompleto:

    def test_extraer_partidas_pipeline_completo(self):
        """Flujo completo: buscar PDF → descargar → Gemini extraer."""
        mock_firecrawl = MagicMock()
        mock_firecrawl.scrape_url.side_effect = [
            {"html": HTML_CON_PDF},
            {"raw": b"%PDF-1.4"},
        ]

        with (
            patch("app.datasource.firecrawl._FirecrawlApp", return_value=mock_firecrawl),
            patch.object(FirecrawlDataSource, "disponible", return_value=True),
            patch("app.core.config.settings.gemini_api_key", "fake-gemini-key"),
            patch("app.datasource.gemini.GeminiDataSource.extraer_partidas",
                  return_value=PARTIDAS_MOCK),
        ):
            ds = FirecrawlDataSource(api_key="fake-firecrawl-key")
            partidas = ds.extraer_partidas_de_obra("OBRA-001")

        assert len(partidas) == 2
        assert partidas[0]["insumo"] == "Cemento"
        assert partidas[1]["precio_unitario"] == "4.80"

    def test_extraer_partidas_sin_gemini_key(self):
        ds = FirecrawlDataSource(api_key="fake-key")
        with (
            patch("app.core.config.settings.gemini_api_key", ""),
        ):
            with pytest.raises(FirecrawlError, match="GEMINI_API_KEY no configurada"):
                ds.extraer_partidas_de_obra("OBRA-001")

    def test_extraer_partidas_sin_pdf_en_infobras(self):
        mock_app = MagicMock()
        mock_app.scrape_url.return_value = {"html": HTML_SIN_PDF}

        with (
            patch("app.datasource.firecrawl._FirecrawlApp", return_value=mock_app),
            patch("app.core.config.settings.gemini_api_key", "fake-key"),
        ):
            ds = FirecrawlDataSource(api_key="fake-key")
            with pytest.raises(FirecrawlError, match="No se encontró PDF"):
                ds.extraer_partidas_de_obra("OBRA-001")
