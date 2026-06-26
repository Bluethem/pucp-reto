"""Conexión a la base de datos PostgreSQL + PostGIS (ADR-006).

Expone el engine de SQLAlchemy, la fábrica de sesiones, la Base declarativa
para los modelos ORM y la dependencia `get_db` para inyectar sesiones en los
endpoints de FastAPI.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # valida la conexión antes de usarla (resiliencia)
    echo=settings.debug,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


class Base(DeclarativeBase):
    """Base declarativa para todos los modelos ORM de Glass."""


def get_db() -> Generator[Session, None, None]:
    """Dependencia de FastAPI: provee una sesión de BD y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
