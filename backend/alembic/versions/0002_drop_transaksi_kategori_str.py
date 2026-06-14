"""drop redundant transaksi.kategori string column

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-14
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("transaksi", "kategori")


def downgrade():
    op.add_column(
        "transaksi",
        sa.Column("kategori", sa.String(255), nullable=True),
    )
