"""Create initial product, user, and activity schema."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision = "20260920_01"
down_revision = None
branch_labels = None
depends_on = None

user_role = postgresql.ENUM("USER", "ADMIN", name="user_role", create_type=False)
interaction_type = postgresql.ENUM("VIEW", "CLICK", "WISHLIST_ADD", "WISHLIST_REMOVE", name="interaction_type", create_type=False)
search_type = postgresql.ENUM("TEXT", "IMAGE", "MULTIMODAL", name="search_type", create_type=False)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    user_role.create(op.get_bind(), checkfirst=True)
    interaction_type.create(op.get_bind(), checkfirst=True)
    search_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="USER"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table(
        "categories",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("parent_id", sa.UUID(), sa.ForeignKey("categories.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("name", name="uq_categories_name"),
    )
    op.create_table(
        "products",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("category_id", sa.UUID(), sa.ForeignKey("categories.id", ondelete="SET NULL")),
        sa.Column("gender", sa.String(length=30)),
        sa.Column("color", sa.String(length=50)),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_products_name", "products", ["name"])
    op.create_index("ix_products_gender", "products", ["gender"])
    op.create_index("ix_products_color", "products", ["color"])
    op.create_table(
        "product_images",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("product_id", sa.UUID(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("image_url", sa.String(length=2048), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_product_images_product_id", "product_images", ["product_id"])
    op.create_index("uq_product_images_one_primary", "product_images", ["product_id"], unique=True, postgresql_where=sa.text("is_primary"))
    op.create_table(
        "product_embeddings",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("product_id", sa.UUID(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("embedding", Vector(512), nullable=False),
        sa.Column("model_name", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_product_embeddings_product_id", "product_embeddings", ["product_id"])
    op.create_table(
        "wishlists",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.UUID(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", "product_id", name="uq_wishlist_user_product"),
    )
    op.create_index("ix_wishlists_user_id", "wishlists", ["user_id"])
    op.create_index("ix_wishlists_product_id", "wishlists", ["product_id"])
    op.create_table(
        "interaction_history",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.UUID(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("interaction_type", interaction_type, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_interaction_history_user_id", "interaction_history", ["user_id"])
    op.create_index("ix_interaction_history_product_id", "interaction_history", ["product_id"])
    op.create_table(
        "search_history",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("search_type", search_type, nullable=False),
        sa.Column("text_query", sa.Text()),
        sa.Column("image_url", sa.String(length=2048)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_search_history_user_id", "search_history", ["user_id"])


def downgrade() -> None:
    op.drop_table("search_history")
    op.drop_table("interaction_history")
    op.drop_table("wishlists")
    op.drop_table("product_embeddings")
    op.drop_table("product_images")
    op.drop_table("products")
    op.drop_table("categories")
    op.drop_table("users")
    search_type.drop(op.get_bind(), checkfirst=True)
    interaction_type.drop(op.get_bind(), checkfirst=True)
    user_role.drop(op.get_bind(), checkfirst=True)
