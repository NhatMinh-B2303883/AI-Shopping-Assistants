from pathlib import Path
import csv
import hashlib
import json
import shutil
from collections import defaultdict
from datetime import datetime

from PIL import Image


# ============================================================
# PATH CONFIG
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_CSV = (
    PROJECT_ROOT
    / "data"
    / "product"
    / "products.csv"
)

INPUT_IMAGE_DIR = (
    PROJECT_ROOT
    / "data"
    / "product"
    / "images"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "product"
    / "deduplicated"
)

OUTPUT_CSV = OUTPUT_DIR / "products.csv"
OUTPUT_IMAGE_DIR = OUTPUT_DIR / "images"
REPORT_DIR = OUTPUT_DIR / "reports"

DUPLICATE_REPORT = REPORT_DIR / "duplicate_groups.csv"
REMOVED_REPORT = REPORT_DIR / "removed_products.csv"
SUMMARY_REPORT = REPORT_DIR / "dedup_report.json"


# ============================================================
# RULES
# ============================================================

MIN_WIDTH = 60
MIN_HEIGHT = 80

# Only these dimensions are rejected by the current audit rule.
# This removes the two 60x60 images.
REJECT_IF_SMALLER_THAN = (MIN_WIDTH, MIN_HEIGHT)


# ============================================================
# UTILITIES
# ============================================================

def calculate_md5(file_path: Path, chunk_size: int = 1024 * 1024):
    """
    Calculate MD5 hash of a file.

    MD5 is used here only for exact duplicate detection.
    It is not being used for security.
    """

    md5 = hashlib.md5()

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)

            if not chunk:
                break

            md5.update(chunk)

    return md5.hexdigest()


def find_image(product_id: str):
    """
    Find product image using common image extensions.
    """

    extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    ]

    for ext in extensions:

        image_path = INPUT_IMAGE_DIR / f"{product_id}{ext}"

        if image_path.exists():
            return image_path

    return None


def get_image_size(image_path: Path):
    """
    Return (width, height) or None if image cannot be read.
    """

    try:
        with Image.open(image_path) as img:
            return img.size

    except Exception:
        return None


def is_too_small(width: int, height: int):
    """
    Check whether image is below the accepted minimum.
    """

    return (
        width < REJECT_IF_SMALLER_THAN[0]
        or height < REJECT_IF_SMALLER_THAN[1]
    )


def choose_keeper(group):
    """
    Select the product to keep from an exact duplicate group.

    Deterministic rule:
    1. Prefer product with the smallest numeric source_id if possible.
    2. Otherwise sort by product_id.

    This prevents the result from changing between runs.
    """

    def sort_key(product):

        source_id = product.get("source_id", "").strip()

        try:
            source_number = int(source_id)
        except (ValueError, TypeError):
            source_number = 10**18

        product_id = product.get("product_id", "").strip()

        return (
            source_number,
            product_id,
        )

    return sorted(group, key=sort_key)[0]


# ============================================================
# LOAD CSV
# ============================================================

def load_products():

    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            f"Không tìm thấy products.csv:\n{INPUT_CSV}"
        )

    with open(
        INPUT_CSV,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        fieldnames = reader.fieldnames

        if not fieldnames:
            raise ValueError(
                "products.csv không có header."
            )

        products = list(reader)

    if not products:
        raise ValueError(
            "products.csv không có dữ liệu."
        )

    return products, fieldnames


# ============================================================
# CREATE OUTPUT DIRECTORIES
# ============================================================

def prepare_output_directories():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_IMAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# MAIN DEDUPLICATION
# ============================================================

def main():

    print("=" * 70)
    print("DEDUPLICATE PRODUCT DATASET")
    print("=" * 70)

    print(f"Project root : {PROJECT_ROOT}")
    print(f"Input CSV    : {INPUT_CSV}")
    print(f"Input images : {INPUT_IMAGE_DIR}")
    print(f"Output dir   : {OUTPUT_DIR}")

    # --------------------------------------------------------
    # Check paths
    # --------------------------------------------------------

    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            f"\nKhông tìm thấy:\n{INPUT_CSV}"
        )

    if not INPUT_IMAGE_DIR.exists():
        raise FileNotFoundError(
            f"\nKhông tìm thấy:\n{INPUT_IMAGE_DIR}"
        )

    prepare_output_directories()

    # --------------------------------------------------------
    # Load products
    # --------------------------------------------------------

    products, fieldnames = load_products()

    total_products = len(products)

    print(
        f"\nProducts loaded: "
        f"{total_products:,}"
    )

    # --------------------------------------------------------
    # Step 1: Validate image files
    # --------------------------------------------------------

    print("\nChecking images...")

    missing_images = []
    corrupt_images = []
    too_small_products = []

    valid_products = []

    for index, product in enumerate(products, start=1):

        product_id = product.get(
            "product_id",
            ""
        ).strip()

        if not product_id:
            print(
                f"WARNING: row {index} "
                "không có product_id."
            )
            continue

        image_path = find_image(product_id)

        # ----------------------------------------------------
        # Missing image
        # ----------------------------------------------------

        if image_path is None:

            missing_images.append(product)

            continue

        # ----------------------------------------------------
        # Read image
        # ----------------------------------------------------

        size = get_image_size(image_path)

        if size is None:

            corrupt_images.append(product)

            continue

        width, height = size

        # ----------------------------------------------------
        # Too small
        # ----------------------------------------------------

        if is_too_small(width, height):

            too_small_products.append({
                "product": product,
                "image_path": image_path,
                "width": width,
                "height": height,
            })

            continue

        # ----------------------------------------------------
        # Valid
        # ----------------------------------------------------

        valid_products.append({
            "product": product,
            "image_path": image_path,
            "width": width,
            "height": height,
        })

    print(
        f"Valid images       : "
        f"{len(valid_products):,}"
    )

    print(
        f"Missing images     : "
        f"{len(missing_images):,}"
    )

    print(
        f"Corrupt images     : "
        f"{len(corrupt_images):,}"
    )

    print(
        f"Too-small images   : "
        f"{len(too_small_products):,}"
    )

    # --------------------------------------------------------
    # Step 2: Calculate MD5 hashes
    # --------------------------------------------------------

    print("\nCalculating image hashes...")

    hash_groups = defaultdict(list)

    for item in valid_products:

        product = item["product"]
        image_path = item["image_path"]

        product_id = product["product_id"]

        try:
            image_hash = calculate_md5(image_path)

        except Exception as e:

            print(
                f"Hash error: "
                f"{product_id} -> {e}"
            )

            corrupt_images.append(product)

            continue

        item["md5"] = image_hash

        hash_groups[image_hash].append(item)

    # --------------------------------------------------------
    # Step 3: Identify duplicate groups
    # --------------------------------------------------------

    duplicate_groups = []

    duplicate_removed = []

    for image_hash, group in hash_groups.items():

        if len(group) <= 1:
            continue

        products_in_group = [
            item["product"]
            for item in group
        ]

        keeper = choose_keeper(
            products_in_group
        )

        keeper_id = keeper.get(
            "product_id",
            ""
        )

        removed = [
            product
            for product in products_in_group
            if product.get("product_id") != keeper_id
        ]

        duplicate_groups.append({
            "md5": image_hash,
            "count": len(group),
            "keeper_product_id": keeper_id,
            "product_ids": [
                product.get("product_id", "")
                for product in products_in_group
            ],
        })

        duplicate_removed.extend(removed)

    # --------------------------------------------------------
    # Step 4: Build final products
    # --------------------------------------------------------

    duplicate_removed_ids = {
        product.get("product_id", "")
        for product in duplicate_removed
    }

    too_small_ids = {
        item["product"].get("product_id", "")
        for item in too_small_products
    }

    missing_ids = {
        product.get("product_id", "")
        for product in missing_images
    }

    corrupt_ids = {
        product.get("product_id", "")
        for product in corrupt_images
    }

    removed_ids = (
        duplicate_removed_ids
        | too_small_ids
        | missing_ids
        | corrupt_ids
    )

    final_products = [
        product
        for product in products
        if product.get("product_id", "") not in removed_ids
    ]

    # --------------------------------------------------------
    # Step 5: Copy image files
    # --------------------------------------------------------

    print("\nCopying final images...")

    copied_count = 0

    for item in valid_products:

        product = item["product"]

        product_id = product.get(
            "product_id",
            ""
        ).strip()

        # Skip duplicate products
        if product_id in duplicate_removed_ids:
            continue

        # Skip products that were otherwise removed
        if product_id in removed_ids:
            continue

        source_path = item["image_path"]

        extension = source_path.suffix.lower()

        destination_path = (
            OUTPUT_IMAGE_DIR
            / f"{product_id}{extension}"
        )

        shutil.copy2(
            source_path,
            destination_path
        )

        copied_count += 1

    print(
        f"Images copied: "
        f"{copied_count:,}"
    )

    # --------------------------------------------------------
    # Step 6: Update image_path
    # --------------------------------------------------------

    for product in final_products:

        product_id = product.get(
            "product_id",
            ""
        ).strip()

        # Search actual copied extension
        image_path = None

        for extension in [
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        ]:

            candidate = (
                OUTPUT_IMAGE_DIR
                / f"{product_id}{extension}"
            )

            if candidate.exists():

                image_path = candidate

                break

        if image_path is not None:

            product["image_path"] = (
                f"images/{image_path.name}"
            )

    # --------------------------------------------------------
    # Step 7: Write products.csv
    # --------------------------------------------------------

    print("\nWriting deduplicated products.csv...")

    with open(
        OUTPUT_CSV,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for product in final_products:

            writer.writerow(product)

    # --------------------------------------------------------
    # Step 8: Write duplicate report
    # --------------------------------------------------------

    print(
        "Writing duplicate_groups.csv..."
    )

    with open(
        DUPLICATE_REPORT,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "md5",
            "count",
            "keeper_product_id",
            "duplicate_product_ids",
        ])

        for group in duplicate_groups:

            writer.writerow([
                group["md5"],
                group["count"],
                group["keeper_product_id"],
                ";".join(
                    group["product_ids"]
                ),
            ])

    # --------------------------------------------------------
    # Step 9: Write removed products report
    # --------------------------------------------------------

    print(
        "Writing removed_products.csv..."
    )

    removed_fieldnames = (
        fieldnames
        + [
            "remove_reason",
            "width",
            "height",
        ]
    )

    with open(
        REMOVED_REPORT,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=removed_fieldnames
        )

        writer.writeheader()

        # ----------------------------------------------------
        # Too-small
        # ----------------------------------------------------

        for item in too_small_products:

            row = dict(item["product"])

            row["remove_reason"] = (
                "too_small"
            )

            row["width"] = item["width"]
            row["height"] = item["height"]

            writer.writerow(row)

        # ----------------------------------------------------
        # Missing
        # ----------------------------------------------------

        for product in missing_images:

            row = dict(product)

            row["remove_reason"] = (
                "missing_image"
            )

            row["width"] = ""
            row["height"] = ""

            writer.writerow(row)

        # ----------------------------------------------------
        # Corrupt
        # ----------------------------------------------------

        for product in corrupt_images:

            row = dict(product)

            row["remove_reason"] = (
                "corrupt_image"
            )

            row["width"] = ""
            row["height"] = ""

            writer.writerow(row)

        # ----------------------------------------------------
        # Duplicates
        # ----------------------------------------------------

        for product in duplicate_removed:

            row = dict(product)

            row["remove_reason"] = (
                "exact_duplicate"
            )

            row["width"] = ""
            row["height"] = ""

            writer.writerow(row)

    # --------------------------------------------------------
    # Step 10: Summary report
    # --------------------------------------------------------

    summary = {
        "created_at": datetime.now().isoformat(),

        "input": {
            "total_products": total_products,
        },

        "validation": {
            "valid_images": len(valid_products),
            "missing_images": len(missing_images),
            "corrupt_images": len(corrupt_images),
            "too_small_images": len(
                too_small_products
            ),
        },

        "duplicates": {
            "duplicate_groups": len(
                duplicate_groups
            ),
            "duplicate_products_removed": len(
                duplicate_removed
            ),
        },

        "output": {
            "final_products": len(
                final_products
            ),
            "images_copied": copied_count,
        },

        "rules": {
            "min_width": MIN_WIDTH,
            "min_height": MIN_HEIGHT,
            "duplicate_detection": "MD5",
            "keeper_rule": (
                "smallest source_id, "
                "otherwise product_id"
            ),
        },

        "paths": {
            "products_csv": str(
                OUTPUT_CSV
            ),
            "images": str(
                OUTPUT_IMAGE_DIR
            ),
            "reports": str(
                REPORT_DIR
            ),
        },
    }

    print(
        "Writing dedup_report.json..."
    )

    with open(
        SUMMARY_REPORT,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            summary,
            f,
            indent=4,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("DEDUPLICATION COMPLETE")
    print("=" * 70)

    print(
        f"Input products          : "
        f"{total_products:,}"
    )

    print(
        f"Duplicate groups        : "
        f"{len(duplicate_groups):,}"
    )

    print(
        f"Duplicate products out  : "
        f"{len(duplicate_removed):,}"
    )

    print(
        f"Too-small products out  : "
        f"{len(too_small_products):,}"
    )

    print(
        f"Missing products out    : "
        f"{len(missing_images):,}"
    )

    print(
        f"Corrupt products out    : "
        f"{len(corrupt_images):,}"
    )

    print(
        f"Final products           : "
        f"{len(final_products):,}"
    )

    print(
        f"Final images             : "
        f"{copied_count:,}"
    )

    print("\nOutput:")
    print(f"  {OUTPUT_CSV}")
    print(f"  {OUTPUT_IMAGE_DIR}")
    print(f"  {REPORT_DIR}")

    print("=" * 70)


if __name__ == "__main__":
    main()