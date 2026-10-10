"""Rebuild product_embeddings table to match updated ProductEmbedding model.

Changes from initial schema:
- Vector dimension: 512 -> 768  (SigLIP 2 Base output)
- New column: embedding_type VARCHAR(20) NOT NULL  ("text" or "image")
- New column: product_image_id UUID NULL FK -> product_images.id CASCADE
- New CHECK constraint: embedding_type/product_image_id consistency
- New partial unique index: one text embedding per product+model
- New partial unique index: one image embedding per product_image+model
"""

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = "20261007_02"
down_revision = "20260920_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the old table and recreate with updated schema.
    # (No real embedding data exists yet at this stage of the project.)
    op.drop_index("ix_product_embeddings_product_id", table_name="product_embeddings")
    op.drop_table("product_embeddings")

    op.create_table(
        "product_embeddings",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("product_id", sa.UUID(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        # NULL  → text embedding  (belongs to the product as a whole)
        # NOT NULL → image embedding (belongs to a specific ProductImage)
        sa.Column("product_image_id", sa.UUID(), sa.ForeignKey("product_images.id", ondelete="CASCADE"), nullable=True),
        # "text" or "image"
        sa.Column("embedding_type", sa.String(20), nullable=False),
        # SigLIP 2 Base (google/siglip2-base-patch16-256) output dim = 768
        sa.Column("embedding", Vector(768), nullable=False),
        sa.Column("model_name", sa.String(120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(
            """
            (embedding_type = 'text'  AND product_image_id IS NULL)
            OR
            (embedding_type = 'image' AND product_image_id IS NOT NULL)
            """,
            name="ck_product_embedding_type",
        ),
    )

    op.create_index("ix_product_embeddings_product_id", "product_embeddings", ["product_id"])
    op.create_index("ix_product_embeddings_image_id", "product_embeddings", ["product_image_id"])

    # One text embedding per product per model
    op.create_index(
        "uq_product_text_embedding_per_model",
        "product_embeddings",
        ["product_id", "model_name"],
        unique=True,
        postgresql_where=sa.text("embedding_type = 'text'"),
    )

    # One image embedding per product_image per model
    op.create_index(
        "uq_product_image_embedding_per_model",
        "product_embeddings",
        ["product_image_id", "model_name"],
        unique=True,
        postgresql_where=sa.text("embedding_type = 'image'"),
    )


def downgrade() -> None:
    op.drop_index("uq_product_image_embedding_per_model", table_name="product_embeddings")
    op.drop_index("uq_product_text_embedding_per_model", table_name="product_embeddings")
    op.drop_index("ix_product_embeddings_image_id", table_name="product_embeddings")
    op.drop_index("ix_product_embeddings_product_id", table_name="product_embeddings")
    op.drop_table("product_embeddings")

    # Restore original Vector(512) table (no data loss risk — never had real embeddings)
    op.create_table(
        "product_embeddings",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("product_id", sa.UUID(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("embedding", Vector(512), nullable=False),
        sa.Column("model_name", sa.String(120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_product_embeddings_product_id", "product_embeddings", ["product_id"])
