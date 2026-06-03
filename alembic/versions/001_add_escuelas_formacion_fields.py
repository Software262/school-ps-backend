"""add escuelas formacion fields

Revision ID: 001
Revises:
Create Date: 2026-06-01

"""

from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if "detalleescuelaformacion" not in tables:
        # table does not exist yet — sqlmodel will create it from the updated model
        return

    existing_cols = {col["name"] for col in inspector.get_columns("detalleescuelaformacion")}

    if "periodo_id" not in existing_cols:
        op.add_column(
            "detalleescuelaformacion",
            sa.Column("periodo_id", sa.Integer(), nullable=True),
        )
        op.create_foreign_key(
            "fk_detalle_escuela_periodo",
            "detalleescuelaformacion",
            "periodo",
            ["periodo_id"],
            ["id"],
        )
        op.create_index(
            "ix_detalleescuelaformacion_periodo_id",
            "detalleescuelaformacion",
            ["periodo_id"],
        )

    if "usuario_id" not in existing_cols:
        op.add_column(
            "detalleescuelaformacion",
            sa.Column("usuario_id", sa.Integer(), nullable=True),
        )
        op.create_foreign_key(
            "fk_detalle_escuela_usuario",
            "detalleescuelaformacion",
            "usuario",
            ["usuario_id"],
            ["id"],
        )

    if "saldo_pendiente" not in existing_cols:
        op.add_column(
            "detalleescuelaformacion",
            sa.Column("saldo_pendiente", sa.Integer(), nullable=False, server_default="0"),
        )

    if "motivo_retiro" not in existing_cols:
        op.add_column(
            "detalleescuelaformacion",
            sa.Column("motivo_retiro", sa.String(400), nullable=True),
        )

    # ensure estudiante_id index exists
    indexes = {ix["name"] for ix in inspector.get_indexes("detalleescuelaformacion")}
    if "ix_detalleescuelaformacion_estudiante_id" not in indexes:
        op.create_index(
            "ix_detalleescuelaformacion_estudiante_id",
            "detalleescuelaformacion",
            ["estudiante_id"],
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if "detalleescuelaformacion" not in tables:
        return

    existing_cols = {col["name"] for col in inspector.get_columns("detalleescuelaformacion")}

    if "motivo_retiro" in existing_cols:
        op.drop_column("detalleescuelaformacion", "motivo_retiro")
    if "saldo_pendiente" in existing_cols:
        op.drop_column("detalleescuelaformacion", "saldo_pendiente")
    if "usuario_id" in existing_cols:
        op.drop_constraint(
            "fk_detalle_escuela_usuario", "detalleescuelaformacion", type_="foreignkey"
        )
        op.drop_column("detalleescuelaformacion", "usuario_id")
    if "periodo_id" in existing_cols:
        op.drop_index(
            "ix_detalleescuelaformacion_periodo_id",
            table_name="detalleescuelaformacion",
        )
        op.drop_constraint(
            "fk_detalle_escuela_periodo", "detalleescuelaformacion", type_="foreignkey"
        )
        op.drop_column("detalleescuelaformacion", "periodo_id")
