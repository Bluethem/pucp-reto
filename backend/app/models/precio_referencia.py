import uuid
from sqlalchemy import Column, String, Enum, Numeric, SmallInteger

from app.core.database import Base


class PrecioReferencia(Base):
    __tablename__ = "precios_referencia"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    codigo_inei = Column(String(50), index=True, nullable=False)
    insumo = Column(String(300), nullable=False)
    unidad = Column(String(50))
    precio = Column(Numeric(12, 2), nullable=False)
    departamento = Column(String(100))
    mes = Column(SmallInteger)
    anio = Column(SmallInteger)
    fuente = Column(
        Enum("inei", "mvivienda", name="fuente_precio_enum"),
        nullable=False,
    )
