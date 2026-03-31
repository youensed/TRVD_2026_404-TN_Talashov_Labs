from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260328_0001"
down_revision = None
branch_labels = None
depends_on = None


user_role_enum = sa.Enum("PATIENT", "DOCTOR", "ADMIN", "OWNER", name="userrole", native_enum=False)
appointment_status_enum = sa.Enum(
    "SCHEDULED",
    "COMPLETED",
    "CANCELLED",
    "NO_SHOW",
    name="appointmentstatus",
    native_enum=False,
)
payment_status_enum = sa.Enum("PENDING", "PAID", "FAILED", "REFUNDED", name="paymentstatus", native_enum=False)
payment_method_enum = sa.Enum("CARD", "CASH", name="paymentmethod", native_enum=False)
audit_event_enum = sa.Enum(
    "LOGIN_SUCCESS",
    "LOGIN_FAILED",
    "LOGOUT",
    "REFRESH",
    "REMINDER_CREATED",
    name="auditeventtype",
    native_enum=False,
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("role", user_role_enum, nullable=False),
        sa.Column("first_name", sa.String(length=512), nullable=False),
        sa.Column("last_name", sa.String(length=512), nullable=False),
        sa.Column("phone", sa.String(length=512), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "doctor_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("specialty", sa.String(length=120), nullable=False),
        sa.Column("cabinet_number", sa.String(length=30), nullable=False),
        sa.Column("bio", sa.String(length=1000), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "schedule_shifts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("doctor_id", sa.Uuid(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("slot_minutes", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["doctor_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_schedule_shifts_doctor_start_time", "schedule_shifts", ["doctor_id", "start_time"])

    op.create_table(
        "appointments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("doctor_id", sa.Uuid(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", appointment_status_enum, nullable=False, server_default="SCHEDULED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["patient_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["doctor_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_appointments_start_time", "appointments", ["start_time"])
    op.create_index("ix_appointments_doctor_id", "appointments", ["doctor_id"])
    op.create_index(
        "uq_appointments_doctor_active_slot",
        "appointments",
        ["doctor_id", "start_time"],
        unique=True,
        postgresql_where=sa.text("status IN ('SCHEDULED', 'COMPLETED', 'NO_SHOW')"),
    )
    op.create_index(
        "uq_appointments_patient_active_slot",
        "appointments",
        ["patient_id", "start_time"],
        unique=True,
        postgresql_where=sa.text("status IN ('SCHEDULED', 'COMPLETED', 'NO_SHOW')"),
    )

    op.create_table(
        "medical_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("appointment_id", sa.Uuid(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("doctor_id", sa.Uuid(), nullable=False),
        sa.Column("complaints", sa.Text(), nullable=False),
        sa.Column("diagnosis", sa.Text(), nullable=False),
        sa.Column("treatment_plan", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["doctor_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("appointment_id"),
    )
    op.create_index("ix_medical_records_patient_id", "medical_records", ["patient_id"])

    op.create_table(
        "payments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("appointment_id", sa.Uuid(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("status", payment_status_enum, nullable=False, server_default="PENDING"),
        sa.Column("method", payment_method_enum, nullable=False, server_default="CARD"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("appointment_id"),
    )
    op.create_index("ix_payments_created_at", "payments", ["created_at"])

    op.create_table(
        "reminder_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("appointment_id", sa.Uuid(), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reminder_events_appointment_id", "reminder_events", ["appointment_id"], unique=True)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("event_type", audit_event_enum, nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_index("ix_reminder_events_appointment_id", table_name="reminder_events")
    op.drop_table("reminder_events")
    op.drop_index("ix_payments_created_at", table_name="payments")
    op.drop_table("payments")
    op.drop_index("ix_medical_records_patient_id", table_name="medical_records")
    op.drop_table("medical_records")
    op.drop_index("uq_appointments_patient_active_slot", table_name="appointments")
    op.drop_index("uq_appointments_doctor_active_slot", table_name="appointments")
    op.drop_index("ix_appointments_doctor_id", table_name="appointments")
    op.drop_index("ix_appointments_start_time", table_name="appointments")
    op.drop_table("appointments")
    op.drop_index("ix_schedule_shifts_doctor_start_time", table_name="schedule_shifts")
    op.drop_table("schedule_shifts")
    op.drop_table("doctor_profiles")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

