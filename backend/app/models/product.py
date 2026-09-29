from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.user import InteractionHistory, Wishlist


class Product(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[UUID | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    color: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    category: Mapped[Category | None] = relationship(back_populates="products")
    images: Mapped[list[ProductImage]] = relationship(back_populates="product", cascade="all, delete-orphan")
    embeddings: Mapped[list[ProductEmbedding]] = relationship(back_populates="product", cascade="all, delete-orphan")
    wishlist_entries: Mapped[list[Wishlist]] = relationship(back_populates="product", cascade="all, delete-orphan")
    interactions: Mapped[list[InteractionHistory]] = relationship(back_populates="product", cascade="all, delete-orphan")


class ProductImage(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "product_images"

    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    product: Mapped[Product] = relationship(back_populates="images")


class ProductEmbedding(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "product_embeddings"

    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(512), nullable=False)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)

    product: Mapped[Product] = relationship(back_populates="embeddings")
