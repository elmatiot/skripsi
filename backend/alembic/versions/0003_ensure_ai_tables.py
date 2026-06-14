"""ensure ai_insight and ai_memory tables exist

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-14

Dibuat karena entrypoint.sh sebelumnya punya fallback `alembic stamp head`
yang menyebabkan migration 0001 ditandai selesai tanpa benar-benar dijalankan.
Migration ini memastikan tabel ai_insight dan ai_memory ada.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # ai_insight
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS ai_insight (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            judul VARCHAR(160) NOT NULL,
            konten TEXT NOT NULL,
            tipe VARCHAR(40) DEFAULT 'general',
            sudah_dibaca BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_ai_insight_user_id ON ai_insight (user_id)"
    ))

    # ai_memory
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS ai_memory (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            topik VARCHAR(80) NOT NULL,
            ringkasan TEXT NOT NULL,
            fakta JSONB,
            versi INTEGER NOT NULL DEFAULT 1,
            updated_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS ix_ai_memory_user_id ON ai_memory (user_id)"
    ))
    conn.execute(sa.text(
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_memory_user_topik ON ai_memory (user_id, topik)"
    ))


def downgrade():
    op.drop_table("ai_memory")
    op.drop_table("ai_insight")
