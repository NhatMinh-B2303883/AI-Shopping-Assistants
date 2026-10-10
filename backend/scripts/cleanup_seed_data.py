"""Safely remove legacy demo products created by backend/scripts/seed.py.

Default behavior is dry-run. Pass --apply to commit deletions.

This script:
- Deletes only the exact sample product names defined in the old seed.py.
- Removes obsolete leaf categories (Sneakers, Running Shoes, Hoodie) only when
  they have no remaining products and no child categories.
- Keeps shared/root categories (Shoes, Clothing, Sandals, T-Shirt, Jacket).
- Reports the two demo users created by seed.py but never deletes users.
"""

from __future__ import annotations

import argparse

from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models.category import Category
from app.models.product import Product
from app.models.user import User


SEED_PRODUCT_NAMES = [
    "Urban Runner X1",
    "Street Classic Pro",
    "Neon Kick 2.0",
    "Canvas Low Top",
    "Monochrome Edge",
    "AeroStride 500",
    "FlexRun Lite",
    "TrailBlazer Pro",
    "SpeedForm Elite",
    "Summer Slide Basic",
    "Sport Sandal Active",
    "Essential Tee White",
    "Graphic Print Tee",
    "Cropped Pastel Tee",
    "Oversized Drop Shoulder",
    "Striped Nautical Tee",
    "Classic Pullover Hoodie",
    "Zip-Up Tech Fleece",
    "Pastel Oversized Hoodie",
    "Windbreaker Lightweight",
    "Bomber Satin Jacket",
    "Denim Trucker Jacket",
    "Puffer Crop Jacket",
]

SEED_USER_EMAILS = [
    "an.nguyen@example.com",
    "bich.tran@example.com",
]

OBSOLETE_CATEGORY_NAMES = [
    "Sneakers",
    "Running Shoes",
    "Hoodie",
]


def count_products_for_category(db, category_id, excluding_ids=()) -> int:
    stmt = (
        select(func.count())
        .select_from(Product)
        .where(Product.category_id == category_id)
    )
    if excluding_ids:
        stmt = stmt.where(Product.id.not_in(list(excluding_ids)))
    return int(db.scalar(stmt) or 0)


def count_child_categories(db, category_id) -> int:
    stmt = (
        select(func.count())
        .select_from(Category)
        .where(Category.parent_id == category_id)
    )
    return int(db.scalar(stmt) or 0)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preview or remove products from the legacy sample seed."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit deletions. Without this flag the script only previews changes.",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        products = list(
            db.scalars(
                select(Product).where(Product.name.in_(SEED_PRODUCT_NAMES))
            ).all()
        )
        product_ids = {product.id for product in products}

        print("=" * 72)
        print("Legacy seed cleanup")
        print(f"Mode: {'APPLY (will commit)' if args.apply else 'DRY RUN (no changes committed)'}")
        print("=" * 72)
        print(f"Matched legacy sample products: {len(products)} / {len(SEED_PRODUCT_NAMES)}")

        for product in products:
            # These counts make linked data visible before deleting the product.
            image_count = len(product.images)
            embedding_count = len(product.embeddings)
            wishlist_count = len(product.wishlist_entries)
            interaction_count = len(product.interactions)
            print(
                f"  - {product.name} | images={image_count}, "
                f"embeddings={embedding_count}, wishlists={wishlist_count}, "
                f"interactions={interaction_count}"
            )

        demo_users = list(
            db.scalars(
                select(User).where(User.email.in_(SEED_USER_EMAILS))
            ).all()
        )
        print(f"\nLegacy demo accounts found: {len(demo_users)} (preserved)")
        for user in demo_users:
            print(f"  - {user.email}")

        categories = list(
            db.scalars(
                select(Category).where(
                    Category.name.in_(OBSOLETE_CATEGORY_NAMES)
                )
            ).all()
        )
        print("\nObsolete categories:")
        safe_category_ids = []
        for category in categories:
            other_product_count = count_products_for_category(
                db,
                category.id,
                excluding_ids=product_ids,
            )
            child_count = count_child_categories(db, category.id)
            can_delete = other_product_count == 0 and child_count == 0
            print(
                f"  - {category.name}: products outside this cleanup="
                f"{other_product_count}, child_categories={child_count}, "
                f"{'eligible for deletion' if can_delete else 'KEEP (still referenced)'}"
            )
            if can_delete:
                safe_category_ids.append(category.id)

        if not args.apply:
            db.rollback()
            print("\nDRY RUN finished. Database was not changed.")
            print("Review the matched products above before running with --apply.")
            return

        # ORM cascade rules on Product remove its dependent images, embeddings,
        # wishlist entries, and interaction records as configured by the models.
        for product in products:
            db.delete(product)
        db.flush()

        deleted_categories = 0
        for category_id in safe_category_ids:
            category = db.get(Category, category_id)
            if category is None:
                continue

            # Recheck after product deletion to guard against stale assumptions.
            remaining_products = count_products_for_category(db, category.id)
            remaining_children = count_child_categories(db, category.id)
            if remaining_products == 0 and remaining_children == 0:
                db.delete(category)
                deleted_categories += 1

        db.commit()
        print("\nCleanup committed.")
        print(f"Products deleted: {len(products)}")
        print(f"Obsolete categories deleted: {deleted_categories}")
        print("Demo user accounts were preserved.")
    except Exception:
        db.rollback()
        print("\nCleanup failed; transaction rolled back.")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
