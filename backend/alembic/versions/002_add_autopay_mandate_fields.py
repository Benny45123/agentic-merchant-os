"""add autopay mandate fields

Revision ID: 002_add_autopay_mandate_fields
Revises: 001_initial_schema
Create Date: 2026-08-31 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002_add_autopay_mandate_fields"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_cols = {c["name"] for c in inspector.get_columns("mandates")}

    if "autopay_enabled" not in existing_cols:
        op.add_column("mandates", sa.Column("autopay_enabled", sa.Boolean(), server_default=sa.text("0"), nullable=False))
    if "autopay_token" not in existing_cols:
        op.add_column("mandates", sa.Column("autopay_token", sa.String(length=255), nullable=True))
    if "customer_id" not in existing_cols:
        op.add_column("mandates", sa.Column("customer_id", sa.String(length=255), nullable=True))
    if "max_amount_per_charge" not in existing_cols:
        op.add_column("mandates", sa.Column("max_amount_per_charge", sa.Integer(), server_default=sa.text("1000000"), nullable=False))
    if "recurring_auth_status" not in existing_cols:
        op.add_column("mandates", sa.Column("recurring_auth_status", sa.String(length=50), server_default=sa.text("'NONE'"), nullable=False))
    if "autopay_bank_name" not in existing_cols:
        op.add_column("mandates", sa.Column("autopay_bank_name", sa.String(length=100), nullable=True))
    if "autopay_vpa" not in existing_cols:
        op.add_column("mandates", sa.Column("autopay_vpa", sa.String(length=255), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_cols = {c["name"] for c in inspector.get_columns("mandates")}

    if "autopay_vpa" in existing_cols:
        op.drop_column("mandates", "autopay_vpa")
    if "autopay_bank_name" in existing_cols:
        op.drop_column("mandates", "autopay_bank_name")
    if "recurring_auth_status" in existing_cols:
        op.drop_column("mandates", "recurring_auth_status")
    if "max_amount_per_charge" in existing_cols:
        op.drop_column("mandates", "max_amount_per_charge")
    if "customer_id" in existing_cols:
        op.drop_column("mandates", "customer_id")
    if "autopay_token" in existing_cols:
        op.drop_column("mandates", "autopay_token")
    if "autopay_enabled" in existing_cols:
        op.drop_column("mandates", "autopay_enabled")


