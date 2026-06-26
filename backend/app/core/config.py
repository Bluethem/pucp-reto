"""Configuración de la aplicación resuelta en tiempo de ejecución (ADR-009).

Todas las credenciales y URLs se leen de variables de entorno (patrón 12-factor).
Para desarrollo local se cargan desde un archivo `.env`. Ver `.env.example`.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    app_name: str = "Glass API"
    environment: str = "development"
    debug: bool = True

    # --- CORS ---
    frontend_url: str = "http://localhost:3000"

    # --- Base de datos (PostgreSQL + PostGIS, ADR-006) ---
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/glass"

    # --- Caché (Redis, ADR-007) ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Gemini API (ADR-001) ---
    gemini_api_key: str = ""

    # --- Fuentes externas (ADR-002) ---
    seace_ocds_base_url: str = "https://contratacionesabiertas.oece.gob.pe"
    infobras_base_url: str = "https://appbp.contraloria.gob.pe/BuscadorCGR/Infobras"

    # --- Autenticación (RNF-08) ---
    jwt_secret_key: str = "cambia-esto-por-un-secreto-largo-y-aleatorio"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_url.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Devuelve la instancia única de configuración (cacheada)."""
    return Settings()


settings = get_settings()
