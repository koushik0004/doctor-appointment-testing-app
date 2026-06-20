"""Add doctor indexes for recommendation queries.

Revision ID: 20260620_0003
Revises: 20260619_0002
Create Date: 2026-06-20 00:00:00
"""

from alembic import op


revision = "20260620_0003"
down_revision = "20260619_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_doctors_rating", "doctors", ["rating"])
    op.create_index("ix_doctors_is_active", "doctors", ["is_active"])


def downgrade() -> None:
    op.drop_index("ix_doctors_is_active", table_name="doctors")
    op.drop_index("ix_doctors_rating", table_name="doctors")
