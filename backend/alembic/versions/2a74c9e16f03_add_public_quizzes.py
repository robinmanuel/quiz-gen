"""Add public quiz sharing.

Revision ID: 2a74c9e16f03
Revises: 6b8f2a1c9d34
Create Date: 2026-10-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2a74c9e16f03"
down_revision: Union[str, None] = "6b8f2a1c9d34"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "quizzes",
        sa.Column("is_public", sa.Boolean(), server_default=sa.false(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("quizzes", "is_public")
