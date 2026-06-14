from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nama = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    transaksi = relationship("Transaksi", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    nota = relationship("Nota", back_populates="user", cascade="all, delete-orphan")
    insights = relationship("AIInsight", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("AIMemory", back_populates="user", cascade="all, delete-orphan")


class Kategori(Base):
    __tablename__ = "kategori"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nama = Column(String(255), nullable=False)
    warna_hex = Column(String(7), nullable=True)
    icon = Column(String(255), nullable=True)
    tipe = Column(String(50), nullable=True)  # "pemasukan" | "pengeluaran"

    transaksi = relationship("Transaksi", back_populates="kategori")
    budgets = relationship("Budget", back_populates="kategori")


class Nota(Base):
    __tablename__ = "nota"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    path_foto = Column(String(255), nullable=True)
    ocr_raw_text = Column(Text, nullable=True)
    ocr_status = Column(String(50), nullable=True)
    tanggal_scan = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="nota")
    transaksi = relationship("Transaksi", back_populates="nota", foreign_keys="Transaksi.nota_id")


class Transaksi(Base):
    __tablename__ = "transaksi"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nota_id = Column(Integer, ForeignKey("nota.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    kategori_id = Column(Integer, ForeignKey("kategori.id", ondelete="RESTRICT"), nullable=False)
    nominal = Column(Numeric(15, 2), nullable=False)
    kategori = Column(String(255), nullable=True)
    merchant = Column(String(255), nullable=True)
    tanggal_transaksi = Column(Date, nullable=False, index=True)
    deskripsi = Column(Text, nullable=True)
    metode_bayar = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="transaksi")
    kategori_obj = relationship("Kategori", back_populates="transaksi")
    nota = relationship("Nota", back_populates="transaksi", foreign_keys=[nota_id])
    items = relationship("ItemTransaksi", back_populates="transaksi", cascade="all, delete-orphan")
    klasifikasi_logs = relationship(
        "KlasifikasiLog", back_populates="transaksi", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_transaksi_user_tanggal", "user_id", "tanggal_transaksi"),
    )


class ItemTransaksi(Base):
    __tablename__ = "item_transaksi"
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaksi_id = Column(
        Integer, ForeignKey("transaksi.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nama_item = Column(String(255), nullable=False)
    qty = Column(Integer, nullable=False, default=1)
    harga_satuan = Column(Numeric(15, 2), nullable=False)
    kategori = Column(String(255), nullable=True)

    transaksi = relationship("Transaksi", back_populates="items")


class Budget(Base):
    __tablename__ = "budget"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    kategori_id = Column(Integer, ForeignKey("kategori.id", ondelete="CASCADE"), nullable=False)
    nominal_budget = Column(Numeric(15, 2), nullable=False)
    tahun = Column(Integer, nullable=False)
    bulan = Column(Integer, nullable=False)

    user = relationship("User", back_populates="budgets")
    kategori = relationship("Kategori", back_populates="budgets")

    __table_args__ = (
        Index("ix_budget_user_periode", "user_id", "tahun", "bulan"),
    )


class KlasifikasiLog(Base):
    __tablename__ = "klasifikasi_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaksi_id = Column(
        Integer, ForeignKey("transaksi.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kategori_prediksi_id = Column(
        Integer, ForeignKey("kategori.id", ondelete="RESTRICT"), nullable=False
    )
    confidence_score = Column(Float, nullable=False)
    metode = Column(String(100), nullable=True)
    status_review = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    transaksi = relationship("Transaksi", back_populates="klasifikasi_logs")
    kategori_prediksi = relationship("Kategori")
    training_data = relationship(
        "TrainingData", back_populates="klasifikasi_log", cascade="all, delete-orphan"
    )


class TrainingData(Base):
    __tablename__ = "training_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    klasifikasi_log_id = Column(
        Integer, ForeignKey("klasifikasi_log.id", ondelete="CASCADE"), nullable=True, index=True
    )
    teks_input = Column(Text, nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    klasifikasi_log = relationship("KlasifikasiLog", back_populates="training_data")


class AIInsight(Base):
    __tablename__ = "ai_insight"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    judul = Column(String(160), nullable=False)
    konten = Column(Text, nullable=False)
    tipe = Column(String(40), default="general")
    sudah_dibaca = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="insights")


class AIMemory(Base):
    __tablename__ = "ai_memory"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topik = Column(String(80), nullable=False)
    ringkasan = Column(Text, nullable=False)
    fakta = Column(JSON, nullable=True)
    versi = Column(Integer, default=1, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    user = relationship("User", back_populates="memories")

    __table_args__ = (
        Index("ix_memory_user_topik", "user_id", "topik", unique=True),
    )
