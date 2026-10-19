"""add_coordinates_not_found_to_ort

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-19 14:38:56.805862
"""
from alembic import op
import sqlalchemy as sa


revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ort",
        sa.Column(
            "coordinates_not_found",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    op.drop_column("ort", "coordinates_not_found")
