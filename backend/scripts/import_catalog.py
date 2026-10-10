"""Import the finalized 1,000-product catalog into PostgreSQL.

Run inside the backend container:
    docker compose exec backend python scripts/import_catalog.py --dry-run
    docker compose exec backend python scripts/import_catalog.py

The importer is idempotent by Product.external_id. It does not delete products
that are not present in the CSV, and it preserves manually entered description
or price values when the corresponding CSV cell is blank.
"""

from __future__ import annotations

import argparse
import csv
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import SessionLocal
from app.models.category import Category
from app.models.product import Product, ProductImage

DATA_ROOT = Path("/data/products")
CSV_PATH = DATA_ROOT / "products.csv"
IMAGES_ROOT = (DATA_ROOT / "images").resolve()

# Root category -> allowed child categories, matching the finalized dataset.
TAXONOMY: dict[str, tuple[str, ...]] = {
    "Clothing": ("T-Shirt", "Polo", "Sweatshirt", "Jacket"),
    "Shoes": ("Casual Shoes", "Sports Shoes", "Sandals"),
}
ALLOWED_GENDERS = {"Men", "Women", "Unisex"}
REQUIRED_COLUMNS = {
    "product_id",
    "name",
    "category",
    "sub_category",
    "gender",
    "color",
    "image_path",
    "canonical_text",
}


def clean(value: Any) -> str | None:
    """Trim a CSV value and convert an empty cell to None."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def parse_price(value: Any, row_number: int) -> Decimal | None:
    text = clean(value)
    if text is None:
        return None
    try:
        price = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(
            f"CSV row {row_number}: price must be a decimal number, got {text!r}"
        ) from exc
    if not price.is_finite() or price < 0:
        raise ValueError(
            f"CSV row {row_number}: price must be finite and non-negative, got {text!r}"
        )
    return price


def resolve_image_path(value: str | None, row_number: int) -> tuple[Path, str]:
    """Validate the image path and return (absolute path, URL-relative path)."""
    if not value:
        raise ValueError(f"CSV row {row_number}: image_path is empty")

    # CSV paths are POSIX-style (for example: images/FP001163.jpg).
    relative_path = PurePosixPath(value.replace("\\", "/"))
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError(
            f"CSV row {row_number}: unsafe image_path {value!r}"
        )

    absolute_path = (DATA_ROOT / Path(*relative_path.parts)).resolve()
    try:
        url_relative_path = absolute_path.relative_to(IMAGES_ROOT)
    except ValueError as exc:
        raise ValueError(
            f"CSV row {row_number}: image_path must point inside {IMAGES_ROOT}, got {value!r}"
        ) from exc

    if not absolute_path.is_file():
        raise ValueError(
            f"CSV row {row_number}: image file does not exist: {absolute_path}"
        )

    return absolute_path, url_relative_path.as_posix()


def load_and_validate_rows() -> list[dict[str, Any]]:
    if not CSV_PATH.is_file():
        raise FileNotFoundError(
            f"Cannot find {CSV_PATH}. Confirm docker-compose.yml mounts "
            "./data/product/final to /data/products:ro."
        )

    rows: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_images: set[str] = set()

    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        actual_columns = set(reader.fieldnames or [])
        missing_columns = REQUIRED_COLUMNS - actual_columns
        if missing_columns:
            raise ValueError(
                "CSV is missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

        for row_number, raw_row in enumerate(reader, start=2):
            product_id = clean(raw_row.get("product_id"))
            name = clean(raw_row.get("name"))
            category_name = clean(raw_row.get("category"))
            sub_category = clean(raw_row.get("sub_category"))
            gender_raw = clean(raw_row.get("gender"))
            color = clean(raw_row.get("color"))
            canonical_text = clean(raw_row.get("canonical_text"))

            if not product_id:
                raise ValueError(f"CSV row {row_number}: product_id is empty")
            if product_id in seen_ids:
                raise ValueError(
                    f"CSV row {row_number}: duplicate product_id {product_id!r}"
                )
            seen_ids.add(product_id)

            if not name:
                raise ValueError(f"CSV row {row_number}: name is empty")
            if not category_name or category_name not in TAXONOMY:
                raise ValueError(
                    f"CSV row {row_number}: unsupported category {category_name!r}"
                )
            if not sub_category or sub_category not in TAXONOMY[category_name]:
                raise ValueError(
                    f"CSV row {row_number}: sub_category {sub_category!r} "
                    f"does not belong to {category_name!r}"
                )
            if not gender_raw:
                raise ValueError(f"CSV row {row_number}: gender is empty")
            gender = gender_raw.title()
            if gender not in ALLOWED_GENDERS:
                raise ValueError(
                    f"CSV row {row_number}: unsupported gender {gender_raw!r}; "
                    f"expected one of {sorted(ALLOWED_GENDERS)}"
                )
            if not color:
                raise ValueError(f"CSV row {row_number}: color is empty")
            if not canonical_text:
                raise ValueError(f"CSV row {row_number}: canonical_text is empty")

            image_abs_path, image_url_relative_path = resolve_image_path(
                clean(raw_row.get("image_path")), row_number
            )
            if image_abs_path in seen_images:
                raise ValueError(
                    f"CSV row {row_number}: duplicate image path {image_abs_path}"
                )
            seen_images.add(image_abs_path)

            rows.append(
                {
                    "external_id": product_id,
                    "name": name,
                    "description": clean(raw_row.get("description")),
                    "category": category_name,
                    "sub_category": sub_category,
                    "gender": gender,
                    "color": color,
                    "price": parse_price(raw_row.get("price"), row_number),
                    "canonical_text": canonical_text,
                    "image_url": f"/catalog-images/{image_url_relative_path}",
                }
            )

    if not rows:
        raise ValueError(f"No product rows found in {CSV_PATH}")

    return rows


def ensure_categories(db) -> dict[str, Category]:
    """Create missing taxonomy nodes; fail rather than silently re-parent nodes."""
    category_map: dict[str, Category] = {}

    # Create or find roots first so their IDs are available for child nodes.
    for root_name in TAXONOMY:
        root = db.scalar(
            select(Category).where(Category.name == root_name)
        )
        if root is not None and root.parent_id is not None:
            raise ValueError(
                f"Category {root_name!r} already exists as a child category. "
                "Resolve the category hierarchy before importing."
            )
        if root is None:
            root = Category(name=root_name, parent_id=None)
            db.add(root)
            db.flush()
        category_map[root_name] = root

    for root_name, child_names in TAXONOMY.items():
        parent = category_map[root_name]
        for child_name in child_names:
            child = db.scalar(
                select(Category).where(Category.name == child_name)
            )
            if child is not None:
                if child.parent_id != parent.id:
                    raise ValueError(
                        f"Category {child_name!r} exists with a different parent. "
                        "The importer will not change an existing hierarchy automatically."
                    )
            else:
                child = Category(name=child_name, parent_id=parent.id)
                db.add(child)
                db.flush()
            category_map[child_name] = child

    return category_map


def upsert_product(db, row: dict[str, Any], category_map: dict[str, Category]) -> str:
    product = db.scalar(
        select(Product)
        .options(selectinload(Product.images))
        .where(Product.external_id == row["external_id"])
    )

    is_new = product is None
    if is_new:
        product = Product(external_id=row["external_id"])
        db.add(product)

    # Fields owned by the source dataset are refreshed on every import.
    product.name = row["name"]
    product.category_id = category_map[row["sub_category"]].id
    product.gender = row["gender"]
    product.color = row["color"]
    product.canonical_text = row["canonical_text"]

    # Preserve later admin edits when the source CSV has blank cells.
    if row["description"] is not None or is_new:
        product.description = row["description"]
    if row["price"] is not None or is_new:
        product.price = row["price"]

    # Maintain one primary catalog image for the dataset image.
    primary_image = next(
        (image for image in product.images if image.is_primary),
        None,
    )
    if primary_image is None and product.images:
        primary_image = product.images[0]
        primary_image.is_primary = True

    if primary_image is None:
        product.images.append(
            ProductImage(image_url=row["image_url"], is_primary=True)
        )
    else:
        primary_image.image_url = row["image_url"]
        primary_image.is_primary = True
        for image in product.images:
            if image is not primary_image and image.is_primary:
                image.is_primary = False

    return "created" if is_new else "updated"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import products from data/product/final/products.csv"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and simulate the import, then roll back all DB changes.",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        rows = load_and_validate_rows()
        print(f"Validated {len(rows)} product rows and image files from {CSV_PATH}.")

        category_map = ensure_categories(db)
        created = 0
        updated = 0
        for row in rows:
            result = upsert_product(db, row, category_map)
            if result == "created":
                created += 1
            else:
                updated += 1

        # Force pending SQL to execute before reporting success.
        db.flush()

        if args.dry_run:
            db.rollback()
            print("DRY RUN: database changes were rolled back; nothing was committed.")
        else:
            db.commit()
            print("Import committed successfully.")

        print(f"Products created: {created}")
        print(f"Products updated: {updated}")
        print(f"Taxonomy nodes checked: {len(category_map)}")
        return 0

    except Exception as exc:
        db.rollback()
        print(f"IMPORT FAILED; database transaction rolled back: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
