from pathlib import Path
from collections import Counter, defaultdict
import csv
import hashlib
import json
from datetime import datetime

from PIL import Image


# ============================================================
# PATH CONFIG
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_DIR = PROJECT_ROOT / "data" / "product" / "final"
PRODUCT_CSV = DATASET_DIR / "products.csv"
IMAGE_DIR = DATASET_DIR / "images"
REPORT_DIR = DATASET_DIR / "reports"
REPORT_JSON = REPORT_DIR / "final_validation_report.json"


# ============================================================
# EXPECTED DATASET
# ============================================================

EXPECTED_TOTAL = 1000

EXPECTED_SUBCATEGORIES = {
    "T-Shirt": 261,
    "Casual Shoes": 177,
    "Sports Shoes": 150,
    "Polo": 121,
    "Sandals": 112,
    "Sweatshirt": 90,
    "Jacket": 89,
}

EXPECTED_GENDERS = {
    "Men": 810,
    "Unisex": 37,
    "Women": 153,
}

EXPECTED_CATEGORIES = {
    "Clothing": 561,
    "Shoes": 439,
}

SUBCATEGORY_TO_CATEGORY = {
    "T-Shirt": "Clothing",
    "Polo": "Clothing",
    "Sweatshirt": "Clothing",
    "Jacket": "Clothing",
    "Casual Shoes": "Shoes",
    "Sports Shoes": "Shoes",
    "Sandals": "Shoes",
}

GENDERS = {"Men", "Women", "Unisex"}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


# ============================================================
# HELPERS
# ============================================================

def md5_file(path):
    """Hash nội dung ảnh để phát hiện duplicate chính xác."""

    digest = hashlib.md5()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def load_products():
    if not PRODUCT_CSV.is_file():
        raise FileNotFoundError(
            f"Không tìm thấy file:\n{PRODUCT_CSV}"
        )

    with open(
        PRODUCT_CSV,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        products = list(reader)

    if not fields:
        raise ValueError("products.csv không có header.")

    return products, fields


def image_files_in_output():
    if not IMAGE_DIR.is_dir():
        raise FileNotFoundError(
            f"Không tìm thấy thư mục ảnh:\n{IMAGE_DIR}"
        )

    return sorted(
        path
        for path in IMAGE_DIR.iterdir()
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_dataset(products, fields, image_files):
    errors = []
    warnings = []

    def error(message):
        errors.append(message)
        print(f"[ERROR] {message}")

    def warning(message):
        warnings.append(message)
        print(f"[WARN]  {message}")

    required_fields = {
        "product_id",
        "name",
        "category",
        "sub_category",
        "gender",
        "color",
        "image_path",
        "canonical_text",
    }

    missing_fields = required_fields - set(fields)

    if missing_fields:
        error(f"Thiếu các cột: {sorted(missing_fields)}")

    row_count = len(products)

    # --------------------------------------------------------
    # 1. Row count
    # --------------------------------------------------------

    if row_count != EXPECTED_TOTAL:
        error(
            f"Số sản phẩm là {row_count}, "
            f"mong đợi {EXPECTED_TOTAL}."
        )

    # --------------------------------------------------------
    # 2. Product ID
    # --------------------------------------------------------

    product_ids = [
        p.get("product_id", "").strip()
        for p in products
    ]

    empty_ids = sum(not product_id for product_id in product_ids)

    if empty_ids:
        error(f"Có {empty_ids} product_id rỗng.")

    id_counts = Counter(
        product_id for product_id in product_ids if product_id
    )

    duplicate_ids = {
        product_id: count
        for product_id, count in id_counts.items()
        if count > 1
    }

    if duplicate_ids:
        error(
            f"Có {len(duplicate_ids)} product_id bị trùng: "
            f"{list(duplicate_ids.items())[:5]}"
        )

    # --------------------------------------------------------
    # 3. Category / sub-category / gender
    # --------------------------------------------------------

    category_counts = Counter()
    subcategory_counts = Counter()
    gender_counts = Counter()

    for product in products:
        product_id = product.get("product_id", "").strip()
        category = product.get("category", "").strip()
        subcategory = product.get("sub_category", "").strip()
        gender = product.get("gender", "").strip()

        category_counts[category] += 1
        subcategory_counts[subcategory] += 1
        gender_counts[gender] += 1

        expected_category = SUBCATEGORY_TO_CATEGORY.get(subcategory)

        if expected_category is None:
            error(
                f"{product_id}: sub_category không hợp lệ: "
                f"{subcategory!r}"
            )
        elif category != expected_category:
            error(
                f"{product_id}: category={category!r}, "
                f"nhưng {subcategory!r} thuộc {expected_category!r}."
            )

        if gender not in GENDERS:
            error(
                f"{product_id}: gender không hợp lệ: {gender!r}"
            )

        for field in ("name", "color", "canonical_text"):
            if not product.get(field, "").strip():
                error(f"{product_id}: trường {field!r} đang trống.")

    # Check exact counts from this sampling run.
    if dict(category_counts) != EXPECTED_CATEGORIES:
        error(
            f"Category counts sai. Actual={dict(category_counts)}, "
            f"expected={EXPECTED_CATEGORIES}"
        )

    if dict(subcategory_counts) != EXPECTED_SUBCATEGORIES:
        error(
            f"Sub-category counts sai. Actual={dict(subcategory_counts)}, "
            f"expected={EXPECTED_SUBCATEGORIES}"
        )

    if dict(gender_counts) != EXPECTED_GENDERS:
        error(
            f"Gender counts sai. Actual={dict(gender_counts)}, "
            f"expected={EXPECTED_GENDERS}"
        )

    # --------------------------------------------------------
    # 4. Image paths and image integrity
    # --------------------------------------------------------

    missing_images = []
    corrupt_images = []
    used_paths = Counter()
    dimensions = Counter()
    formats = Counter()
    modes = Counter()
    image_hashes = defaultdict(list)

    for product in products:
        product_id = product.get("product_id", "").strip()
        image_reference = product.get("image_path", "").strip()

        if not image_reference:
            missing_images.append(product_id)
            continue

        relative_path = Path(image_reference.replace("\\", "/"))

        # Image references must be relative paths within final/.
        if relative_path.is_absolute() or ".." in relative_path.parts:
            error(
                f"{product_id}: image_path không an toàn: "
                f"{image_reference!r}"
            )
            continue

        image_path = DATASET_DIR / relative_path

        if not image_path.is_file():
            missing_images.append(product_id)
            continue

        used_paths[str(image_path.resolve())] += 1

        try:
            with Image.open(image_path) as img:
                width, height = img.size
                image_format = img.format or "Unknown"
                image_mode = img.mode
                img.verify()

            dimensions[f"{width}x{height}"] += 1
            formats[image_format] += 1
            modes[image_mode] += 1

            if width < 60 or height < 80:
                warning(
                    f"{product_id}: ảnh nhỏ hơn 60x80 "
                    f"({width}x{height})."
                )

            digest = md5_file(image_path)
            image_hashes[digest].append(product_id)

        except Exception as exc:
            corrupt_images.append(product_id)
            error(
                f"{product_id}: không đọc được ảnh "
                f"{image_reference!r}: {exc}"
            )

    if missing_images:
        error(
            f"Thiếu ảnh của {len(missing_images)} sản phẩm. "
            f"Ví dụ: {missing_images[:10]}"
        )

    if corrupt_images:
        error(
            f"Có {len(corrupt_images)} ảnh lỗi. "
            f"Ví dụ: {corrupt_images[:10]}"
        )

    duplicated_paths = {
        path: count
        for path, count in used_paths.items()
        if count > 1
    }

    if duplicated_paths:
        error(
            f"Nhiều sản phẩm dùng chung đường dẫn ảnh: "
            f"{list(duplicated_paths.items())[:5]}"
        )

    duplicate_image_groups = {
        digest: ids
        for digest, ids in image_hashes.items()
        if len(ids) > 1
    }

    if duplicate_image_groups:
        sample = list(duplicate_image_groups.values())[:5]
        error(
            f"Có {len(duplicate_image_groups)} nhóm ảnh trùng MD5. "
            f"Ví dụ product IDs: {sample}"
        )

    # --------------------------------------------------------
    # 5. Orphan images
    # --------------------------------------------------------

    referenced_paths = {
        str((DATASET_DIR / Path(
            p.get("image_path", "").replace("\\", "/")
        )).resolve())
        for p in products
        if p.get("image_path", "").strip()
        and not Path(
            p["image_path"].replace("\\", "/")
        ).is_absolute()
        and ".." not in Path(
            p["image_path"].replace("\\", "/")
        ).parts
    }

    orphan_images = [
        str(path.resolve())
        for path in image_files
        if str(path.resolve()) not in referenced_paths
    ]

    if orphan_images:
        error(
            f"Có {len(orphan_images)} ảnh không được tham chiếu "
            f"trong products.csv. Ví dụ: {orphan_images[:5]}"
        )

    if len(image_files) != EXPECTED_TOTAL:
        error(
            f"Thư mục images có {len(image_files)} file ảnh, "
            f"mong đợi {EXPECTED_TOTAL}."
        )

    # --------------------------------------------------------
    # 6. Expected empty fields
    # --------------------------------------------------------

    missing_value_counts = {}

    for field in ("description", "price"):
        if field not in fields:
            continue

        count = sum(
            not p.get(field, "").strip()
            for p in products
        )

        missing_value_counts[field] = count

        if count:
            warning(
                f"{field} trống ở {count}/{row_count} sản phẩm. "
                "Không tự tạo dữ liệu giả."
            )

    # --------------------------------------------------------
    # 7. Report
    # --------------------------------------------------------

    report = {
        "created_at": datetime.now().isoformat(),
        "status": "PASS" if not errors else "FAIL",
        "dataset": {
            "csv": str(PRODUCT_CSV),
            "image_directory": str(IMAGE_DIR),
            "product_count": row_count,
            "image_file_count": len(image_files),
        },
        "counts": {
            "category": dict(category_counts),
            "sub_category": dict(subcategory_counts),
            "gender": dict(gender_counts),
        },
        "image_checks": {
            "missing_images": len(missing_images),
            "corrupt_images": len(corrupt_images),
            "duplicate_product_ids": len(duplicate_ids),
            "duplicate_image_groups": len(duplicate_image_groups),
            "orphan_images": len(orphan_images),
            "dimensions": dict(dimensions),
            "formats": dict(formats),
            "modes": dict(modes),
        },
        "missing_values": missing_value_counts,
        "errors": errors,
        "warnings": warnings,
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    # --------------------------------------------------------
    # Print summary
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL DATASET VALIDATION")
    print("=" * 70)

    print(f"Products            : {row_count:,}")
    print(f"Image files         : {len(image_files):,}")
    print(f"Category            : {dict(category_counts)}")
    print(f"Sub-category        : {dict(subcategory_counts)}")
    print(f"Gender              : {dict(gender_counts)}")
    print(f"Dimensions          : {dict(dimensions)}")
    print(f"Formats             : {dict(formats)}")
    print(f"Modes               : {dict(modes)}")
    print(f"Missing images      : {len(missing_images)}")
    print(f"Corrupt images      : {len(corrupt_images)}")
    print(f"Duplicate product IDs: {len(duplicate_ids)}")
    print(f"Duplicate image groups: {len(duplicate_image_groups)}")
    print(f"Orphan images       : {len(orphan_images)}")
    print(f"Errors              : {len(errors)}")
    print(f"Warnings            : {len(warnings)}")
    print(f"Report              : {REPORT_JSON}")

    print("\nSTATUS:", report["status"])

    return report


def main():
    print("Validating final MVP dataset...")
    print(f"Dataset directory: {DATASET_DIR}")

    if not DATASET_DIR.is_dir():
        raise FileNotFoundError(
            f"Không tìm thấy dataset:\n{DATASET_DIR}"
        )

    products, fields = load_products()
    image_files = image_files_in_output()

    report = validate_dataset(products, fields, image_files)

    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()