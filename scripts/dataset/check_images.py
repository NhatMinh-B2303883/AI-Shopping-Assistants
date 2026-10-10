from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
from PIL import Image, UnidentifiedImageError


# ============================================================
# Paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PRODUCT_CSV = (
    PROJECT_ROOT
    / "data"
    / "product"
    / "products.csv"
)

PRODUCT_DIR = (
    PROJECT_ROOT
    / "data"
    / "product"
)


# ============================================================
# Configuration
# ============================================================

MIN_WIDTH = 60
MIN_HEIGHT = 80


# ============================================================
# Helpers
# ============================================================

def calculate_md5(path: Path) -> str:
    """Calculate MD5 hash for exact duplicate detection."""
    hash_md5 = hashlib.md5()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def main() -> None:
    print("=" * 72)
    print("AI Shopping Assistant - Image Quality Audit")
    print("=" * 72)

    if not PRODUCT_CSV.exists():
        raise FileNotFoundError(
            f"products.csv not found:\n{PRODUCT_CSV}"
        )

    df = pd.read_csv(PRODUCT_CSV)

    print(f"\nProducts in CSV: {len(df):,}")

    missing = []
    corrupt = []
    too_small = []
    valid = []

    mode_counter = Counter()
    format_counter = Counter()
    size_counter = Counter()

    hash_to_products: defaultdict[str, list[str]] = defaultdict(list)

    # ========================================================
    # Check images
    # ========================================================

    print("\nChecking images...")

    for _, row in df.iterrows():
        product_id = str(row["product_id"])
        image_path_value = str(row["image_path"])

        image_path = PRODUCT_DIR / image_path_value

        # ----------------------------------------------------
        # File exists?
        # ----------------------------------------------------

        if not image_path.exists():
            missing.append(product_id)
            continue

        # ----------------------------------------------------
        # Open image
        # ----------------------------------------------------

        try:
            with Image.open(image_path) as image:
                image.verify()

            # Open again because verify() invalidates the object.
            with Image.open(image_path) as image:
                width, height = image.size
                image_format = image.format
                image_mode = image.mode

        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
        ):
            corrupt.append(product_id)
            continue

        # ----------------------------------------------------
        # Dimensions
        # ----------------------------------------------------

        if width < MIN_WIDTH or height < MIN_HEIGHT:
            too_small.append(
                {
                    "product_id": product_id,
                    "width": width,
                    "height": height,
                }
            )
            continue

        # ----------------------------------------------------
        # Valid
        # ----------------------------------------------------

        valid.append(product_id)

        mode_counter[image_mode] += 1
        format_counter[str(image_format)] += 1

        size_counter[f"{width}x{height}"] += 1

        # ----------------------------------------------------
        # Exact duplicate detection
        # ----------------------------------------------------

        image_hash = calculate_md5(image_path)
        hash_to_products[image_hash].append(product_id)

    # ========================================================
    # Duplicate summary
    # ========================================================

    duplicate_groups = {
        image_hash: product_ids
        for image_hash, product_ids in hash_to_products.items()
        if len(product_ids) > 1
    }

    duplicate_product_count = sum(
        len(product_ids)
        for product_ids in duplicate_groups.values()
    )

    # ========================================================
    # Output
    # ========================================================

    print("\n=== SUMMARY ===")

    print(f"Total products      : {len(df):,}")
    print(f"Valid images        : {len(valid):,}")
    print(f"Missing images      : {len(missing):,}")
    print(f"Corrupt images      : {len(corrupt):,}")
    print(f"Too-small images    : {len(too_small):,}")
    print(
        f"Exact duplicate products: "
        f"{duplicate_product_count:,}"
    )
    print(
        f"Duplicate groups    : "
        f"{len(duplicate_groups):,}"
    )

    # ========================================================
    # Image formats
    # ========================================================

    print("\n=== IMAGE FORMAT ===")

    for fmt, count in format_counter.most_common():
        print(f"{fmt:10} {count:6,}")

    # ========================================================
    # Image modes
    # ========================================================

    print("\n=== IMAGE MODE ===")

    for mode, count in mode_counter.most_common():
        print(f"{mode:10} {count:6,}")

    # ========================================================
    # Most common dimensions
    # ========================================================

    print("\n=== MOST COMMON IMAGE DIMENSIONS ===")

    for size, count in size_counter.most_common(20):
        print(f"{size:15} {count:6,}")

    # ========================================================
    # Missing images
    # ========================================================

    if missing:
        print("\n=== MISSING IMAGE SAMPLE ===")

        for product_id in missing[:20]:
            print(product_id)

    # ========================================================
    # Corrupt images
    # ========================================================

    if corrupt:
        print("\n=== CORRUPT IMAGE SAMPLE ===")

        for product_id in corrupt[:20]:
            print(product_id)

    # ========================================================
    # Too-small images
    # ========================================================

    if too_small:
        print("\n=== TOO SMALL IMAGE SAMPLE ===")

        for item in too_small[:20]:
            print(
                f'{item["product_id"]}: '
                f'{item["width"]}x{item["height"]}'
            )

    # ========================================================
    # Duplicate sample
    # ========================================================

    if duplicate_groups:
        print("\n=== DUPLICATE GROUP SAMPLE ===")

        shown = 0

        for image_hash, product_ids in duplicate_groups.items():
            print(
                f"{image_hash[:12]}... -> "
                f"{product_ids[:10]}"
            )

            shown += 1

            if shown >= 20:
                break

    # ========================================================
    # Save reports
    # ========================================================

    report_dir = PRODUCT_DIR / "quality_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    if missing:
        pd.DataFrame(
            {"product_id": missing}
        ).to_csv(
            report_dir / "missing_images.csv",
            index=False,
            encoding="utf-8-sig",
        )

    if corrupt:
        pd.DataFrame(
            {"product_id": corrupt}
        ).to_csv(
            report_dir / "corrupt_images.csv",
            index=False,
            encoding="utf-8-sig",
        )

    if too_small:
        pd.DataFrame(too_small).to_csv(
            report_dir / "too_small_images.csv",
            index=False,
            encoding="utf-8-sig",
        )

    duplicate_rows = []

    for image_hash, product_ids in duplicate_groups.items():
        for product_id in product_ids:
            duplicate_rows.append(
                {
                    "image_hash": image_hash,
                    "product_id": product_id,
                }
            )

    if duplicate_rows:
        pd.DataFrame(duplicate_rows).to_csv(
            report_dir / "duplicate_images.csv",
            index=False,
            encoding="utf-8-sig",
        )

    print("\n=== REPORT FILES ===")
    print(f"Report directory: {report_dir}")

    print("\nDone.")
    print("=" * 72)


if __name__ == "__main__":
    main()