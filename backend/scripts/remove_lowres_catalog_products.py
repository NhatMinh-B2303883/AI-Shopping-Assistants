"""Safely remove the eight catalog products with low-resolution source images.

Default is DRY RUN. The script refuses to commit if any matched product has
wishlist or interaction history rows, so the user can decide how to handle them.

Run from repository root:
  docker compose exec -e PYTHONPATH=/app:/workspace backend python scripts/remove_lowres_catalog_products.py
  docker compose exec -e PYTHONPATH=/app:/workspace backend python scripts/remove_lowres_catalog_products.py --apply
"""

from __future__ import annotations

import argparse

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import SessionLocal
from app.models.product import Product, ProductEmbedding, ProductImage


LOW_RES_PRODUCT_IDS = {
    "FP002749",
    "FP002751",
    "FP003191",
    "FP003213",
    "FP005397",
    "FP015852",
    "FP015856",
    "FP015864",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview or delete the eight low-resolution catalog products."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit deletions. Without this flag, run a dry-run and rollback.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db = SessionLocal()

    try:
        products = list(
            db.scalars(
                select(Product)
                .where(Product.external_id.in_(LOW_RES_PRODUCT_IDS))
                .options(
                    selectinload(Product.images).selectinload(ProductImage.embeddings),
                    selectinload(Product.embeddings),
                    selectinload(Product.wishlist_entries),
                    selectinload(Product.interactions),
                )
                .order_by(Product.external_id)
            ).unique().all()
        )

        found_ids = {product.external_id for product in products}
        missing_ids = LOW_RES_PRODUCT_IDS - found_ids
        unexpected_ids = found_ids - LOW_RES_PRODUCT_IDS

        print("=" * 72)
        print(f"Mode: {'APPLY — COMMIT DELETIONS' if args.apply else 'DRY RUN — NO CHANGES COMMITTED'}")
        print(f"Target IDs: {len(LOW_RES_PRODUCT_IDS)}")
        print(f"Products found: {len(products)}")
        print(f"Missing IDs: {sorted(missing_ids) if missing_ids else 'none'}")
        print("=" * 72)

        total_text = total_image = total_wishlist = total_interaction = 0
        linked_rows_found = False
        for product in products:
            text_count = sum(1 for e in product.embeddings if e.embedding_type == "text")
            image_count = sum(1 for e in product.embeddings if e.embedding_type == "image")
            # Image embeddings can also be attached through ProductImage.embeddings.
            # Count by ProductEmbedding to avoid double-counting.
            total_text += text_count
            total_image += image_count
            wishlist_count = len(product.wishlist_entries)
            interaction_count = len(product.interactions)
            total_wishlist += wishlist_count
            total_interaction += interaction_count
            if wishlist_count or interaction_count:
                linked_rows_found = True

            print(
                f"{product.external_id} | {product.name} | "
                f"images={len(product.images)} | text_embeddings={text_count} | "
                f"image_embeddings={image_count} | wishlists={wishlist_count} | "
                f"interactions={interaction_count}"
            )

        print("-" * 72)
        print(f"Text embeddings scheduled for removal: {total_text}")
        print(f"Image embeddings scheduled for removal: {total_image}")
        print(f"Wishlist rows linked: {total_wishlist}")
        print(f"Interaction rows linked: {total_interaction}")

        if unexpected_ids:
            raise RuntimeError(f"Unexpected matched IDs: {sorted(unexpected_ids)}")
        if missing_ids:
            raise RuntimeError(
                "Not all eight target products were found. No deletion performed; inspect database."
            )

        if not args.apply:
            db.rollback()
            print("\nDRY RUN complete; database unchanged.")
            print("Review the linked-row counts above before running with --apply.")
            return

        if linked_rows_found:
            raise RuntimeError(
                "Deletion blocked because one or more target products have wishlist or interaction rows. "
                "No changes committed. Decide how those user-related records should be handled first."
            )

        for product in products:
            db.delete(product)
        db.flush()
        db.commit()

        print("\nDeletion committed.")
        print(f"Products deleted: {len(products)}")
        print(f"Text embeddings deleted with targets: {total_text}")
        print(f"Image embeddings deleted with targets: {total_image}")
        print("Remaining catalog products and embeddings were not intentionally modified.")
    except Exception:
        db.rollback()
        print("\nOperation failed; transaction rolled back.")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
