
"""Add external catalog ID and canonical text to products."""

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision = "20261009_04"
down_revision = "20261009_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Store the product ID from the source dataset.
    op.add_column(
        "products",
        sa.Column(
            "external_id",
            sa.String(length=64),
            nullable=True,
        ),
    )

    # Store the normalized text used to generate text embeddings.
    op.add_column(
        "products",
        sa.Column(
            "canonical_text",
            sa.Text(),
            nullable=True,
        ),
    )

    # Ensure that non-NULL external IDs are unique.
    op.create_index(
        "uq_products_external_id",
        "products",
        ["external_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "uq_products_external_id",
        table_name="products",
    )

    op.drop_column("products", "canonical_text")
    op.drop_column("products", "external_id")