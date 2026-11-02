"""Add legal acceptance types and user acceptance records.

Revision ID: 0007
Revises: 0006
"""
import uuid

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None

TOS_ID = uuid.UUID("00000000-0000-0000-0000-000000000007")


def upgrade() -> None:
    op.create_table(
        "legal_acception",
        sa.Column("legal_acception", sa.String(length=100), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_on", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("last_modified_on", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_modified_by", sa.Uuid(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("legal_acception"),
    )
    op.create_table(
        "legal_acceptions",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("legal_acception_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_on", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("last_modified_on", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_modified_by", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["legal_acception_id"], ["legal_acception.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "legal_acception_id"),
    )
    legal_acception = sa.table(
        "legal_acception",
        sa.column("id", sa.Uuid()),
        sa.column("legal_acception", sa.String()),
    )
    op.bulk_insert(
        legal_acception,
        [{"id": TOS_ID, "legal_acception": "ToS"}],
    )


def downgrade() -> None:
    op.drop_table("legal_acceptions")
    op.drop_table("legal_acception")
