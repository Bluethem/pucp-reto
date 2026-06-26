import uuid
from sqlalchemy import Column, String, SmallInteger, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Contratista(Base):
    __tablename__ = "contratistas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ruc = Column(String(11), unique=True, nullable=False)
    razon_social = Column(String(300), nullable=False)
    representante_legal = Column(String(200))
    estado_sunat = Column(String(50))
    score_confiabilidad = Column(SmallInteger)
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    obras = relationship("Obra", back_populates="contratista")
