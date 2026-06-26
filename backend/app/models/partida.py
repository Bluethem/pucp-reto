import uuid
from sqlalchemy import Column, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from app.core.database import Base


class PartidaObra(Base):
    __tablename__ = "partidas_obra"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    obra_id = Column(String(36), ForeignKey("obras.id"), nullable=False)
    insumo = Column(String(300), nullable=False)
    codigo_inei = Column(String(50))
    unidad = Column(String(50))
    cantidad = Column(Numeric(12, 2))
    precio_declarado = Column(Numeric(12, 2))
    precio_referencia_inei = Column(Numeric(12, 2))
    ratio = Column(Numeric(5, 2))
    version_tabla_inei = Column(String(20))

    obra = relationship("Obra", back_populates="partidas")
