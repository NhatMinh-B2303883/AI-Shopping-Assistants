from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.user import InteractionHistory, Wishlist


class Product(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "products"

    __table_args__ = (
        Index(
            "uq_products_external_id",
            "external_id",
            unique=True,
        ),
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    gender: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        index=True,
    )

    color: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    external_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    canonical_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    category: Mapped[Category | None] = relationship(
        back_populates="products"
    )

    images: Mapped[list[ProductImage]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )

    embeddings: Mapped[list[ProductEmbedding]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )

    wishlist_entries: Mapped[list[Wishlist]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )

    interactions: Mapped[list[InteractionHistory]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )


class ProductImage(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "product_images"

    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    image_url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    product: Mapped[Product] = relationship(
        back_populates="images"
    )

    # One image can have one/more embeddings
    # (e.g. different model versions later).
    embeddings: Mapped[list[ProductEmbedding]] = relationship(
        back_populates="image",
        cascade="all, delete-orphan",
    )


class ProductEmbedding(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "product_embeddings"

    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # NULL for text embedding.
    # NOT NULL for image embedding.
    product_image_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("product_images.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # "text" or "image"
    embedding_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # SigLIP 2 Base output dimension = 768
    embedding: Mapped[list[float]] = mapped_column(
        Vector(768),
        nullable=False,
    )

    # Example:
    # google/siglip2-base-patch16-256
    model_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    product: Mapped[Product] = relationship(
        back_populates="embeddings"
    )

    image: Mapped[ProductImage | None] = relationship(
        back_populates="embeddings"
    )

    __table_args__ = (
        CheckConstraint(
            """
            (
                embedding_type = 'text'
                AND product_image_id IS NULL
            )
            OR
            (
                embedding_type = 'image'
                AND product_image_id IS NOT NULL
            )
            """,
            name="ck_product_embedding_type",
        ),

        # A product can have only one text embedding
        # for a given model.
        Index(
            "uq_product_text_embedding_per_model",
            "product_id",
            "model_name",
            unique=True,
            postgresql_where=(
                embedding_type == "text"
            ),
        ),

        # A specific image has only one embedding
        # for a given model.
        Index(
            "uq_product_image_embedding_per_model",
            "product_image_id",
            "model_name",
            unique=True,
            postgresql_where=(
                embedding_type == "image"
            ),
        ),
    )