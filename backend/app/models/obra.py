import uuid
from sqlalchemy import Column, String, ForeignKey, Enum, Numeric, SmallInteger, DateTime
from geoalchemy2 import Geography
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Obra(Base):
    __tablename__ = "obras"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    codigo_infobras = Column(String(100), unique=True, nullable=False)
    titulo = Column(String(500), nullable=False)
    tipo_obra = Column(
        Enum("edificacion", "carretera", "agua_saneamiento", "educacion", "salud", "otros",
             name="tipo_obra_enum"),
        nullable=False,
    )
    estado = Column(
        Enum("planeado", "ejecucion", "concluido", "paralizado", name="estado_obra_enum"),
        nullable=False,
    )
    presupuesto_total = Column(Numeric(15, 2))
    metrado_total = Column(Numeric(10, 2))
    ubicacion = Column(Geography(geometry_type="POINT", srid=4326))
    departamento = Column(String(100))
    provincia = Column(String(100))
    distrito = Column(String(100))
    score_riesgo = Column(SmallInteger)
    modo_analisis = Column(
        Enum("partidas", "fallback_m2", name="modo_analisis_enum"),
    )
    fecha_extraccion = Column(DateTime(timezone=True))
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    entidad_id = Column(String(36), ForeignKey("entidades.id"))
    contratista_id = Column(String(36), ForeignKey("contratistas.id"))

    entidad = relationship("Entidad", back_populates="obras")
    contratista = relationship("Contratista", back_populates="obras")
    partidas = relationship("PartidaObra", back_populates="obra", cascade="all, delete-orphan")
    logs = relationship("LogExtraccion", back_populates="obra", cascade="all, delete-orphan")
