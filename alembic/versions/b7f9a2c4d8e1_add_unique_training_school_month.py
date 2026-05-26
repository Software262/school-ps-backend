"""add unique constraint for training school monthly records

Revision ID: b7f9a2c4d8e1
Revises: 60a8206120d4
Create Date: 2026-05-23 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


revision: str = "b7f9a2c4d8e1"
down_revision: Union[str, Sequence[str], None] = "60a8206120d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE detalleescuelaformacion SET mes = lower(trim(mes))")
    op.create_unique_constraint(
        "uq_detalle_escuela_estudiante_programa_mes",
        "detalleescuelaformacion",
        ["complementario_id", "estudiante_id", "mes"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_detalle_escuela_estudiante_programa_mes",
        "detalleescuelaformacion",
        type_="unique",
    )
