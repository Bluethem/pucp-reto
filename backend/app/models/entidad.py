import uuid
from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base


class Entidad(Base):
    __tablename__ = "entidades"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(300), nullable=False)
    tipo = Column(
        Enum("municipalidad_distrital", "municipalidad_provincial", "gobierno_regional",
             "ministerio", "otro", name="tipo_entidad_enum"),
        nullable=False,
    )
    departamento = Column(String(100))
    provincia = Column(String(100))
    distrito = Column(String(100))
    ubigeo = Column(String(6))

    obras = relationship("Obra", back_populates="entidad")
    autoridades = relationship("Autoridad", back_populates="entidad", cascade="all, delete-orphan")
