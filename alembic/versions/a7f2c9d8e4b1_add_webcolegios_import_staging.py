"""add webcolegios import staging

Revision ID: a7f2c9d8e4b1
Revises: 9d7f73fd0fd2
Create Date: 2026-06-07 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a7f2c9d8e4b1"
down_revision: str | None = "9d7f73fd0fd2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "webcolegios_staging_student",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("nombre", sa.String(length=150), nullable=True),
        sa.Column("documento", sa.String(length=100), nullable=True),
        sa.Column("grado_nombre", sa.String(length=100), nullable=True),
        sa.Column("curso", sa.String(length=50), nullable=True),
        sa.Column("sede", sa.String(length=100), nullable=True),
        sa.Column("jornada", sa.String(length=100), nullable=True),
        sa.Column("titular_nombre", sa.String(length=150), nullable=True),
        sa.Column("acudiente_nombre", sa.String(length=100), nullable=True),
        sa.Column("acudiente_telefono", sa.String(length=50), nullable=True),
        sa.Column("acudiente_correo", sa.String(length=150), nullable=True),
        sa.Column("raw_data", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_webcolegios_staging_student_documento",
        "webcolegios_staging_student",
        ["documento"],
        unique=False,
    )

    op.create_table(
        "webcolegios_staging_teacher",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("nombre", sa.String(length=150), nullable=True),
        sa.Column("documento", sa.String(length=100), nullable=True),
        sa.Column("asignatura", sa.String(length=100), nullable=True),
        sa.Column("grado_titular", sa.String(length=100), nullable=True),
        sa.Column("curso_titular", sa.String(length=50), nullable=True),
        sa.Column("sede", sa.String(length=100), nullable=True),
        sa.Column("jornada", sa.String(length=100), nullable=True),
        sa.Column("raw_data", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_webcolegios_staging_teacher_documento",
        "webcolegios_staging_teacher",
        ["documento"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_webcolegios_staging_teacher_documento",
        table_name="webcolegios_staging_teacher",
    )
    op.drop_table("webcolegios_staging_teacher")
    op.drop_index(
        "ix_webcolegios_staging_student_documento",
        table_name="webcolegios_staging_student",
    )
    op.drop_table("webcolegios_staging_student")
