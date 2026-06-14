"""initial schema (skripsi v2)

Revision ID: 0001
Revises:
Create Date: 2026-06-14
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nama", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "kategori",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nama", sa.String(255), nullable=False),
        sa.Column("warna_hex", sa.String(7)),
        sa.Column("icon", sa.String(255)),
        sa.Column("tipe", sa.String(50)),
    )

    op.create_table(
        "nota",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("path_foto", sa.String(255)),
        sa.Column("ocr_raw_text", sa.Text),
        sa.Column("ocr_status", sa.String(50)),
        sa.Column("tanggal_scan", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_nota_user_id", "nota", ["user_id"])

    op.create_table(
        "transaksi",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nota_id", sa.Integer, sa.ForeignKey("nota.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kategori_id", sa.Integer, sa.ForeignKey("kategori.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("nominal", sa.Numeric(15, 2), nullable=False),
        sa.Column("kategori", sa.String(255)),
        sa.Column("merchant", sa.String(255)),
        sa.Column("tanggal_transaksi", sa.Date, nullable=False),
        sa.Column("deskripsi", sa.Text),
        sa.Column("metode_bayar", sa.String(100)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_transaksi_user_id", "transaksi", ["user_id"])
    op.create_index("ix_transaksi_tanggal", "transaksi", ["tanggal_transaksi"])
    op.create_index("ix_transaksi_user_tanggal", "transaksi", ["user_id", "tanggal_transaksi"])

    op.create_table(
        "item_transaksi",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "transaksi_id",
            sa.Integer,
            sa.ForeignKey("transaksi.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("nama_item", sa.String(255), nullable=False),
        sa.Column("qty", sa.Integer, nullable=False, server_default="1"),
        sa.Column("harga_satuan", sa.Numeric(15, 2), nullable=False),
        sa.Column("kategori", sa.String(255)),
    )
    op.create_index("ix_item_transaksi_transaksi_id", "item_transaksi", ["transaksi_id"])

    op.create_table(
        "budget",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "kategori_id", sa.Integer, sa.ForeignKey("kategori.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("nominal_budget", sa.Numeric(15, 2), nullable=False),
        sa.Column("tahun", sa.Integer, nullable=False),
        sa.Column("bulan", sa.Integer, nullable=False),
    )
    op.create_index("ix_budget_user_id", "budget", ["user_id"])
    op.create_index("ix_budget_user_periode", "budget", ["user_id", "tahun", "bulan"])

    op.create_table(
        "klasifikasi_log",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "transaksi_id",
            sa.Integer,
            sa.ForeignKey("transaksi.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "kategori_prediksi_id",
            sa.Integer,
            sa.ForeignKey("kategori.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("confidence_score", sa.Float, nullable=False),
        sa.Column("metode", sa.String(100)),
        sa.Column("status_review", sa.String(50)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_klasifikasi_log_transaksi_id", "klasifikasi_log", ["transaksi_id"])

    op.create_table(
        "training_data",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "klasifikasi_log_id",
            sa.Integer,
            sa.ForeignKey("klasifikasi_log.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("teks_input", sa.Text, nullable=False),
        sa.Column("verified", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_training_data_klasifikasi_log_id", "training_data", ["klasifikasi_log_id"])

    op.create_table(
        "ai_insight",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("judul", sa.String(160), nullable=False),
        sa.Column("konten", sa.Text, nullable=False),
        sa.Column("tipe", sa.String(40), server_default="general"),
        sa.Column("sudah_dibaca", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ai_insight_user_id", "ai_insight", ["user_id"])

    op.create_table(
        "ai_memory",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("topik", sa.String(80), nullable=False),
        sa.Column("ringkasan", sa.Text, nullable=False),
        sa.Column("fakta", sa.JSON),
        sa.Column("versi", sa.Integer, nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ai_memory_user_id", "ai_memory", ["user_id"])
    op.create_index("ix_memory_user_topik", "ai_memory", ["user_id", "topik"], unique=True)

    # Seed kategori dasar
    op.execute(
        """
        INSERT INTO kategori (nama, warna_hex, icon, tipe) VALUES
        ('Gaji', '#10b981', 'wallet', 'pemasukan'),
        ('Bonus', '#22c55e', 'gift', 'pemasukan'),
        ('Investasi', '#0ea5e9', 'trending-up', 'pemasukan'),
        ('Makanan', '#f97316', 'utensils', 'pengeluaran'),
        ('Transportasi', '#3b82f6', 'car', 'pengeluaran'),
        ('Belanja', '#ec4899', 'shopping-bag', 'pengeluaran'),
        ('Hiburan', '#a855f7', 'film', 'pengeluaran'),
        ('Tagihan', '#ef4444', 'file-text', 'pengeluaran'),
        ('Kesehatan', '#14b8a6', 'heart', 'pengeluaran'),
        ('Lainnya', '#6b7280', 'receipt', 'pengeluaran')
        """
    )

    # Seed knowledge base awal untuk RAG (verified=true, tanpa klasifikasi_log)
    op.execute(
        """
        INSERT INTO training_data (klasifikasi_log_id, teks_input, verified) VALUES
        (NULL, 'Format nota Indonesia umumnya berisi Total Belanja, Tunai, Kembali, Kasir, Rp., Harga.', TRUE),
        (NULL, 'Indomaret/Alfamart adalah minimarket fisik, nota biasanya memuat barcode, NPWP, dan PPN.', TRUE),
        (NULL, 'Tokopedia/Shopee adalah e-commerce, biasanya memuat Invoice, Status Pesanan, Ongkos Kirim.', TRUE),
        (NULL, 'Gojek/GoFood/GrabFood adalah layanan online dengan Delivery Fee, Biaya Layanan, Biaya Aplikasi.', TRUE),
        (NULL, 'Nota asli umumnya memiliki kata kunci: Subtotal, Total, Kembalian, PPN, Pajak, Diskon.', TRUE),
        (NULL, 'Kategori Makanan: warung, restoran, kafe, bakery, snack, minuman, kopi.', TRUE),
        (NULL, 'Kategori Transportasi: bensin, parkir, tol, ojek online, taksi, kereta, bus.', TRUE),
        (NULL, 'Kategori Belanja: supermarket, minimarket, baju, peralatan rumah, kosmetik, elektronik.', TRUE),
        (NULL, 'Kategori Hiburan: bioskop, konser, streaming, langganan game, wahana, taman hiburan.', TRUE),
        (NULL, 'Kategori Kesehatan: apotek, dokter, klinik, rumah sakit, BPJS, suplemen, vitamin.', TRUE),
        (NULL, 'Kategori Tagihan: listrik PLN, air PDAM, internet, BPJS, pulsa, paket data, sewa.', TRUE)
        """
    )


def downgrade() -> None:
    for tbl in [
        "ai_memory",
        "ai_insight",
        "training_data",
        "klasifikasi_log",
        "budget",
        "item_transaksi",
        "transaksi",
        "nota",
        "kategori",
        "users",
    ]:
        op.drop_table(tbl)
