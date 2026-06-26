import uuid
from sqlalchemy import Column, String, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship

from app.core.database import Base


class Autoridad(Base):
    __tablename__ = "autoridades"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entidad_id = Column(String(36), ForeignKey("entidades.id"), nullable=False)
    nombre = Column(String(200), nullable=False)
    cargo = Column(
        Enum("alcalde", "regidor", "gobernador", "consejero", "otro", name="cargo_autoridad_enum"),
        nullable=False,
    )
    partido = Column(String(200))
    periodo_inicio = Column(Date)
    periodo_fin = Column(Date)
    foto_url = Column(String(500))
    fuente_actualizacion = Column(String(100))

    entidad = relationship("Entidad", back_populates="autoridades")
