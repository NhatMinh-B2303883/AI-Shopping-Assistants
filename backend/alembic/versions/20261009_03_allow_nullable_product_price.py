"""Allow products to have a missing price."""

from alembic import op
import sqlalchemy as sa


revision = "20261009_03"
down_revision = "20261007_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "products",
        "price",
        existing_type=sa.Numeric(precision=12, scale=2),
        nullable=True,
    )


def downgrade() -> None:
    connection = op.get_bind()

    null_count = connection.execute(
        sa.text(
            "SELECT COUNT(*) FROM products WHERE price IS NULL"
        )
    ).scalar_one()

    if null_count > 0:
        raise RuntimeError(
            "Cannot restore NOT NULL on products.price: "
            f"{null_count} product(s) have a NULL price. "
            "Assign valid prices before downgrading."
        )

    op.alter_column(
        "products",
        "price",
        existing_type=sa.Numeric(precision=12, scale=2),
        nullable=False,
    )