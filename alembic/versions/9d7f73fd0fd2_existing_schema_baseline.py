"""existing schema baseline

Revision ID: 9d7f73fd0fd2
Revises:
Create Date: 2026-06-07 00:00:00.000000

"""

from collections.abc import Sequence

revision: str = "9d7f73fd0fd2"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
