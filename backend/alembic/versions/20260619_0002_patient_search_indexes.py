"""Add indexes for appointment search fields.

Revision ID: 20260619_0002
Revises: 20260608_0001
Create Date: 2026-06-19 00:00:00
"""

from alembic import op


revision = "20260619_0002"
down_revision = "20260608_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_patients_full_name", "patients", ["full_name"])
    op.create_index("ix_patients_phone", "patients", ["phone"])


def downgrade() -> None:
    op.drop_index("ix_patients_phone", table_name="patients")
    op.drop_index("ix_patients_full_name", table_name="patients")
