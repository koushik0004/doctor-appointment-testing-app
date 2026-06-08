"""Create booking foundation tables.

Revision ID: 20260608_0001
Revises: None
Create Date: 2026-06-08 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260608_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("phone", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("email", name="uq_patients_email"),
    )

    op.create_table(
        "doctor_availability",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("doctor_id", sa.Integer(), sa.ForeignKey("doctors.id"), nullable=False),
        sa.Column("available_date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Text(), nullable=False),
        sa.Column("end_time", sa.Text(), nullable=False),
        sa.Column("appointment_type", sa.Text(), nullable=False),
        sa.Column("is_booked", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "appointment_type IN ('IN_PERSON', 'TELEMEDICINE')",
            name="ck_doctor_availability_appointment_type",
        ),
    )
    op.create_index("ix_doctor_availability_doctor_id", "doctor_availability", ["doctor_id"])
    op.create_index(
        "ix_doctor_availability_available_date",
        "doctor_availability",
        ["available_date"],
    )
    op.create_index(
        "ix_doctor_availability_is_booked",
        "doctor_availability",
        ["is_booked"],
    )

    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("confirmation_code", sa.Text(), nullable=False),
        sa.Column("doctor_id", sa.Integer(), sa.ForeignKey("doctors.id"), nullable=False),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column(
            "availability_id",
            sa.Integer(),
            sa.ForeignKey("doctor_availability.id"),
            nullable=True,
        ),
        sa.Column("appointment_date", sa.Date(), nullable=False),
        sa.Column("appointment_time", sa.Text(), nullable=False),
        sa.Column("appointment_type", sa.Text(), nullable=False),
        sa.Column("health_description", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "appointment_type IN ('IN_PERSON', 'TELEMEDICINE')",
            name="ck_appointments_appointment_type",
        ),
        sa.CheckConstraint(
            "status IN ('PENDING', 'CONFIRMED', 'CANCELLED')",
            name="ck_appointments_status",
        ),
        sa.UniqueConstraint("confirmation_code", name="uq_appointments_confirmation_code"),
        sa.UniqueConstraint("availability_id", name="uq_appointments_availability_id"),
    )
    op.create_index("ix_appointments_doctor_id", "appointments", ["doctor_id"])
    op.create_index("ix_appointments_patient_id", "appointments", ["patient_id"])
    op.create_index("ix_appointments_appointment_date", "appointments", ["appointment_date"])
    op.create_index("ix_appointments_status", "appointments", ["status"])
    op.create_index(
        "ix_appointments_doctor_date_time",
        "appointments",
        ["doctor_id", "appointment_date", "appointment_time"],
    )


def downgrade() -> None:
    op.drop_index("ix_appointments_doctor_date_time", table_name="appointments")
    op.drop_index("ix_appointments_status", table_name="appointments")
    op.drop_index("ix_appointments_appointment_date", table_name="appointments")
    op.drop_index("ix_appointments_patient_id", table_name="appointments")
    op.drop_index("ix_appointments_doctor_id", table_name="appointments")
    op.drop_table("appointments")

    op.drop_index("ix_doctor_availability_is_booked", table_name="doctor_availability")
    op.drop_index("ix_doctor_availability_available_date", table_name="doctor_availability")
    op.drop_index("ix_doctor_availability_doctor_id", table_name="doctor_availability")
    op.drop_table("doctor_availability")

    op.drop_table("patients")
