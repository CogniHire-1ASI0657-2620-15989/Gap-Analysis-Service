"""add gap analysis engine

Revision ID: 20260929_03
Revises: 20260929_02
Create Date: 2026-09-29
"""
from alembic import op
import sqlalchemy as sa


revision = "20260929_03"
down_revision = "20260929_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("gap_reports", sa.Column("analysis_engine", sa.String(length=100), nullable=False, server_default="rule_based"))
    op.alter_column("gap_reports", "analysis_engine", server_default=None)


def downgrade() -> None:
    op.drop_column("gap_reports", "analysis_engine")
