"""add docente titular to grado

Revision ID: b8c3d4e5f6a7
Revises: a7f2c9d8e4b1
Create Date: 2026-06-09 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b8c3d4e5f6a7"
down_revision: str | None = "a7f2c9d8e4b1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "grado",
        sa.Column("docente_titular_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_grado_docente_titular_id_docente",
        "grado",
        "docente",
        ["docente_titular_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_grado_docente_titular_id_docente",
        "grado",
        type_="foreignkey",
    )
    op.drop_column("grado", "docente_titular_id")
