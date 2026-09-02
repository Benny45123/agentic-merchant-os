"""add google ap2 mandate fields

Revision ID: 003_add_google_ap2_mandate_fields
Revises: 002_add_autopay_mandate_fields
Create Date: 2026-09-02 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "003_add_google_ap2_mandate_fields"
down_revision: Union[str, None] = "002_add_autopay_mandate_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_cols = {c["name"] for c in inspector.get_columns("mandates")}

    if "open_mandate_jwt" not in existing_cols:
        op.add_column("mandates", sa.Column("open_mandate_jwt", sa.Text(), nullable=True))
    if "user_public_key_pem" not in existing_cols:
        op.add_column("mandates", sa.Column("user_public_key_pem", sa.Text(), nullable=True))
    if "agent_public_key_pem" not in existing_cols:
        op.add_column("mandates", sa.Column("agent_public_key_pem", sa.Text(), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_cols = {c["name"] for c in inspector.get_columns("mandates")}

    if "agent_public_key_pem" in existing_cols:
        op.drop_column("mandates", "agent_public_key_pem")
    if "user_public_key_pem" in existing_cols:
        op.drop_column("mandates", "user_public_key_pem")
    if "open_mandate_jwt" in existing_cols:
        op.drop_column("mandates", "open_mandate_jwt")
