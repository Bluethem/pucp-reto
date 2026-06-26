"""initial migration

Revision ID: 001
Revises:
Create Date: 2026-06-26
"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contratistas",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("ruc", sa.String(11), unique=True, nullable=False),
        sa.Column("razon_social", sa.String(300), nullable=False),
        sa.Column("representante_legal", sa.String(200)),
        sa.Column("estado_sunat", sa.String(50)),
        sa.Column("score_confiabilidad", sa.SmallInteger),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "entidades",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("nombre", sa.String(300), nullable=False),
        sa.Column(
            "tipo",
            sa.Enum(
                "municipalidad_distrital", "municipalidad_provincial",
                "gobierno_regional", "ministerio", "otro",
                name="tipo_entidad_enum",
            ),
            nullable=False,
        ),
        sa.Column("departamento", sa.String(100)),
        sa.Column("provincia", sa.String(100)),
        sa.Column("distrito", sa.String(100)),
        sa.Column("ubigeo", sa.String(6)),
    )
    op.create_table(
        "precios_referencia",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("codigo_inei", sa.String(50), index=True, nullable=False),
        sa.Column("insumo", sa.String(300), nullable=False),
        sa.Column("unidad", sa.String(50)),
        sa.Column("precio", sa.Numeric(12, 2), nullable=False),
        sa.Column("departamento", sa.String(100)),
        sa.Column("mes", sa.SmallInteger),
        sa.Column("anio", sa.SmallInteger),
        sa.Column(
            "fuente",
            sa.Enum("inei", "mvivienda", name="fuente_precio_enum"),
            nullable=False,
        ),
    )
    op.create_table(
        "usuarios",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("alias", sa.String(100)),
        sa.Column(
            "rol",
            sa.Enum("anonimo", "registrado", "administrador", name="rol_usuario_enum"),
            nullable=False,
            server_default="registrado",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "obras",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("codigo_infobras", sa.String(100), unique=True, nullable=False),
        sa.Column("titulo", sa.String(500), nullable=False),
        sa.Column(
            "tipo_obra",
            sa.Enum(
                "edificacion", "carretera", "agua_saneamiento",
                "educacion", "salud", "otros",
                name="tipo_obra_enum",
            ),
            nullable=False,
        ),
        sa.Column(
            "estado",
            sa.Enum(
                "planeado", "ejecucion", "concluido", "paralizado",
                name="estado_obra_enum",
            ),
            nullable=False,
        ),
        sa.Column("presupuesto_total", sa.Numeric(15, 2)),
        sa.Column("metrado_total", sa.Numeric(10, 2)),
        sa.Column("ubicacion", geoalchemy2.Geography(geometry_type="POINT", srid=4326)),
        sa.Column("departamento", sa.String(100)),
        sa.Column("provincia", sa.String(100)),
        sa.Column("distrito", sa.String(100)),
        sa.Column("score_riesgo", sa.SmallInteger),
        sa.Column(
            "modo_analisis",
            sa.Enum("partidas", "fallback_m2", name="modo_analisis_enum"),
        ),
        sa.Column("fecha_extraccion", sa.DateTime(timezone=True)),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("entidad_id", sa.String(36), sa.ForeignKey("entidades.id")),
        sa.Column("contratista_id", sa.String(36), sa.ForeignKey("contratistas.id")),
    )
    op.create_index("idx_obras_ubicacion", "obras", ["ubicacion"], postgresql_using="gist")
    op.create_index("idx_obras_score", "obras", ["score_riesgo"])
    op.create_index("idx_obras_departamento", "obras", ["departamento"])
    op.create_index("idx_obras_entidad", "obras", ["entidad_id"])
    op.create_index("idx_obras_contratista", "obras", ["contratista_id"])
    op.create_table(
        "autoridades",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("entidad_id", sa.String(36), sa.ForeignKey("entidades.id"), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column(
            "cargo",
            sa.Enum(
                "alcalde", "regidor", "gobernador", "consejero", "otro",
                name="cargo_autoridad_enum",
            ),
            nullable=False,
        ),
        sa.Column("partido", sa.String(200)),
        sa.Column("periodo_inicio", sa.Date),
        sa.Column("periodo_fin", sa.Date),
        sa.Column("foto_url", sa.String(500)),
        sa.Column("fuente_actualizacion", sa.String(100)),
    )
    op.create_table(
        "comentarios",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("usuario_id", sa.String(36), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column(
            "recurso_tipo",
            sa.Enum("obra", "empresa", "municipio", "autoridad", name="recurso_tipo_enum"),
            nullable=False,
        ),
        sa.Column("recurso_id", sa.String(36), nullable=False),
        sa.Column("contenido", sa.Text, nullable=False),
        sa.Column("padre_id", sa.String(36), sa.ForeignKey("comentarios.id")),
        sa.Column("reportado", sa.Boolean, server_default="false"),
        sa.Column("oculto", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "log_extraccion",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("obra_id", sa.String(36), sa.ForeignKey("obras.id"), nullable=False),
        sa.Column(
            "fuente",
            sa.Enum("gemini", "inei", "seace", "sunat", "jne", name="fuente_log_enum"),
            nullable=False,
        ),
        sa.Column("respuesta_cruda", sa.JSON),
        sa.Column("exitoso", sa.Boolean),
        sa.Column("intentos", sa.SmallInteger, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "partidas_obra",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("obra_id", sa.String(36), sa.ForeignKey("obras.id"), nullable=False),
        sa.Column("insumo", sa.String(300), nullable=False),
        sa.Column("codigo_inei", sa.String(50)),
        sa.Column("unidad", sa.String(50)),
        sa.Column("cantidad", sa.Numeric(12, 2)),
        sa.Column("precio_declarado", sa.Numeric(12, 2)),
        sa.Column("precio_referencia_inei", sa.Numeric(12, 2)),
        sa.Column("ratio", sa.Numeric(5, 2)),
        sa.Column("version_tabla_inei", sa.String(20)),
    )
    op.create_table(
        "suscripciones",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("usuario_id", sa.String(36), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column(
            "recurso_tipo",
            sa.Enum(
                "obra", "empresa", "municipio", "autoridad",
                name="suscripcion_recurso_tipo_enum",
            ),
            nullable=False,
        ),
        sa.Column("recurso_id", sa.String(36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("usuario_id", "recurso_tipo", "recurso_id", name="uq_suscripcion"),
    )


def downgrade() -> None:
    op.drop_table("suscripciones")
    op.drop_table("partidas_obra")
    op.drop_table("log_extraccion")
    op.drop_table("comentarios")
    op.drop_table("autoridades")
    op.drop_table("obras")
    op.drop_table("precios_referencia")
    op.drop_table("entidades")
    op.drop_table("usuarios")
    op.drop_table("contratistas")

    op.execute("DROP TYPE IF EXISTS tipo_entidad_enum")
    op.execute("DROP TYPE IF EXISTS tipo_obra_enum")
    op.execute("DROP TYPE IF EXISTS estado_obra_enum")
    op.execute("DROP TYPE IF EXISTS modo_analisis_enum")
    op.execute("DROP TYPE IF EXISTS cargo_autoridad_enum")
    op.execute("DROP TYPE IF EXISTS recurso_tipo_enum")
    op.execute("DROP TYPE IF EXISTS fuente_log_enum")
    op.execute("DROP TYPE IF EXISTS fuente_precio_enum")
    op.execute("DROP TYPE IF EXISTS rol_usuario_enum")
    op.execute("DROP TYPE IF EXISTS suscripcion_recurso_tipo_enum")
