from __future__ import annotations

import enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.product import Product


class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class InteractionType(str, enum.Enum):
    VIEW = "VIEW"
    CLICK = "CLICK"
    WISHLIST_ADD = "WISHLIST_ADD"
    WISHLIST_REMOVE = "WISHLIST_REMOVE"


class SearchType(str, enum.Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    MULTIMODAL = "MULTIMODAL"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), default=UserRole.USER, nullable=False)

    wishlist_entries: Mapped[list[Wishlist]] = relationship(back_populates="user", cascade="all, delete-orphan")
    interactions: Mapped[list[InteractionHistory]] = relationship(back_populates="user", cascade="all, delete-orphan")
    searches: Mapped[list[SearchHistory]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Wishlist(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "wishlists"
    __table_args__ = (UniqueConstraint("user_id", "product_id", name="uq_wishlist_user_product"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)

    user: Mapped[User] = relationship(back_populates="wishlist_entries")
    product: Mapped[Product] = relationship(back_populates="wishlist_entries")


class InteractionHistory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "interaction_history"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_type: Mapped[InteractionType] = mapped_column(Enum(InteractionType, name="interaction_type"), nullable=False)

    user: Mapped[User] = relationship(back_populates="interactions")
    product: Mapped[Product] = relationship(back_populates="interactions")


class SearchHistory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "search_history"

    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    search_type: Mapped[SearchType] = mapped_column(Enum(SearchType, name="search_type"), nullable=False)
    text_query: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    user: Mapped[User | None] = relationship(back_populates="searches")
