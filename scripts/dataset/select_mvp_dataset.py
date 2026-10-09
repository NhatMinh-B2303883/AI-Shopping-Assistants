
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import csv
import json
import random
import shutil

from PIL import Image


# ============================================================
# PATH CONFIG
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "data" / "product" / "deduplicated"
INPUT_CSV = INPUT_DIR / "products.csv"
INPUT_IMAGE_DIR = INPUT_DIR / "images"

OUTPUT_DIR = PROJECT_ROOT / "data" / "product" / "final"
OUTPUT_CSV = OUTPUT_DIR / "products.csv"
OUTPUT_IMAGE_DIR = OUTPUT_DIR / "images"
REPORT_DIR = OUTPUT_DIR / "reports"


# ============================================================
# SAMPLING CONFIG
# ============================================================

TARGET_TOTAL = 1000
RANDOM_SEED = 42

# Tổng các quota phải bằng TARGET_TOTAL.
# Các nhóm nhỏ được tăng tỷ trọng để có đủ sản phẩm
# phục vụ demo và đánh giá image/text retrieval.
SUBCATEGORY_TARGETS = {
    "T-Shirt": 261,
    "Casual Shoes": 177,
    "Sports Shoes": 150,
    "Polo": 121,
    "Sandals": 112,
    "Sweatshirt": 90,
    "Jacket": 89,
}

GENDER_ORDER = [
    "Men",
    "Unisex",
    "Women",
]

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


# ============================================================
# CSV UTILITIES
# ============================================================

def load_products():
    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            f"Không tìm thấy dataset đầu vào:\n{INPUT_CSV}"
        )

    with open(
        INPUT_CSV,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        if not fieldnames:
            raise ValueError("products.csv không có header.")

        products = list(reader)

    required_columns = {
        "product_id",
        "category",
        "sub_category",
        "gender",
        "image_path",
    }

    missing_columns = required_columns - set(fieldnames)

    if missing_columns:
        raise ValueError(
            f"Thiếu các cột bắt buộc: {sorted(missing_columns)}"
        )

    if not products:
        raise ValueError("products.csv không có dữ liệu.")

    return products, fieldnames


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(
        path,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# VALIDATE SOURCE DATA
# ============================================================

def validate_source(products):
    product_ids = [
        p.get("product_id", "").strip()
        for p in products
    ]

    if any(not product_id for product_id in product_ids):
        raise ValueError("Dataset có product_id rỗng.")

    duplicate_ids = [
        product_id
        for product_id, count in Counter(product_ids).items()
        if count > 1
    ]

    if duplicate_ids:
        raise ValueError(
            "Dataset đầu vào có product_id trùng. "
            f"Ví dụ: {duplicate_ids[:10]}"
        )

    allowed_categories = {"Clothing", "Shoes"}
    allowed_genders = set(GENDER_ORDER)
    allowed_subcategories = set(SUBCATEGORY_TARGETS)

    for product in products:
        product_id = product["product_id"].strip()
        category = product.get("category", "").strip()
        subcategory = product.get("sub_category", "").strip()
        gender = product.get("gender", "").strip()

        if category not in allowed_categories:
            raise ValueError(
                f"{product_id}: category không hợp lệ: {category}"
            )

        if subcategory not in allowed_subcategories:
            raise ValueError(
                f"{product_id}: sub_category không hợp lệ: "
                f"{subcategory}"
            )

        if gender not in allowed_genders:
            raise ValueError(
                f"{product_id}: gender không hợp lệ: {gender}"
            )

    quota_total = sum(SUBCATEGORY_TARGETS.values())

    if quota_total != TARGET_TOTAL:
        raise ValueError(
            f"Tổng quota sub-category = {quota_total}, "
            f"khác TARGET_TOTAL = {TARGET_TOTAL}."
        )

    print(f"Source products: {len(products):,}")
    print(f"Unique product IDs: {len(set(product_ids)):,}")
    print(f"Requested sample size: {TARGET_TOTAL:,}")


# ============================================================
# IMAGE UTILITIES
# ============================================================

def find_source_image(product):
    """
    Ưu tiên image_path trong CSV.
    Nếu không tìm thấy, thử tìm theo product_id.
    """

    image_reference = product.get("image_path", "").strip()

    if image_reference:
        # CSV có thể dùng dấu / hoặc \.
        relative_path = Path(
            image_reference.replace("\\", "/")
        )

        candidate = INPUT_DIR / relative_path

        if candidate.is_file():
            return candidate

    product_id = product["product_id"].strip()

    for extension in IMAGE_EXTENSIONS:
        candidate = INPUT_IMAGE_DIR / f"{product_id}{extension}"

        if candidate.is_file():
            return candidate

    return None


def verify_image(image_path):
    """Kiểm tra ảnh có thể mở và đọc được hay không."""

    try:
        with Image.open(image_path) as img:
            img.verify()

        return True

    except Exception:
        return False


# ============================================================
# STRATIFIED GENDER ALLOCATION
# ============================================================

def allocate_gender_quotas(gender_counts, target):
    """
    Phân bổ quota gender theo tỷ lệ của sub-category.

    Dùng phương pháp largest remainder:
    1. Tính quota tỷ lệ cho từng gender.
    2. Lấy phần nguyên.
    3. Phân bổ phần còn thiếu cho các nhóm có phần thập phân lớn nhất.

    Tổng quota gender luôn bằng target.
    """

    available_total = sum(gender_counts.values())

    if available_total < target:
        raise ValueError(
            f"Không đủ dữ liệu: cần {target}, "
            f"chỉ có {available_total} sản phẩm."
        )

    if available_total == 0:
        raise ValueError("Không có sản phẩm để phân bổ quota.")

    quotas = {}
    remainders = {}

    for gender in GENDER_ORDER:
        count = gender_counts.get(gender, 0)

        exact_quota = target * count / available_total
        base_quota = int(exact_quota)

        quotas[gender] = base_quota
        remainders[gender] = exact_quota - base_quota

    remaining = target - sum(quotas.values())

    # Gender có phần thập phân lớn hơn được ưu tiên.
    # Nếu bằng nhau, thứ tự GENDER_ORDER được giữ ổn định.
    ranked_genders = sorted(
        GENDER_ORDER,
        key=lambda gender: (
            -remainders[gender],
            GENDER_ORDER.index(gender),
        ),
    )

    for gender in ranked_genders:
        if remaining == 0:
            break

        if quotas[gender] < gender_counts.get(gender, 0):
            quotas[gender] += 1
            remaining -= 1

    if remaining != 0:
        raise RuntimeError(
            f"Không phân bổ được hết quota: còn {remaining}."
        )

    return quotas


# ============================================================
# STRATIFIED PRODUCT SAMPLING
# ============================================================

def select_products(products):
    rng = random.Random(RANDOM_SEED)

    # Group theo sub-category và gender.
    groups = defaultdict(lambda: defaultdict(list))

    for product in products:
        subcategory = product["sub_category"].strip()
        gender = product["gender"].strip()

        groups[subcategory][gender].append(product)

    selected_ids = set()
    distribution_rows = []
    subcategory_gender_summary = {}
    selected_subcategory_counts = Counter()
    selected_gender_counts = Counter()
    selected_category_counts = Counter()

    print("\n" + "=" * 70)
    print("STRATIFIED SAMPLING")
    print("=" * 70)

    for subcategory, target in SUBCATEGORY_TARGETS.items():
        gender_groups = groups[subcategory]

        available_counts = {
            gender: len(gender_groups.get(gender, []))
            for gender in GENDER_ORDER
        }

        total_available = sum(available_counts.values())

        if total_available < target:
            raise ValueError(
                f"{subcategory}: cần {target} sản phẩm, "
                f"nhưng chỉ có {total_available}."
            )

        quotas = allocate_gender_quotas(
            available_counts,
            target,
        )

        print(
            f"\n{subcategory}: "
            f"available={total_available:,}, target={target:,}"
        )

        subcategory_gender_summary[subcategory] = {}

        for gender in GENDER_ORDER:
            available = available_counts[gender]
            quota = quotas[gender]

            candidates = sorted(
                gender_groups.get(gender, []),
                key=lambda p: p["product_id"],
            )

            chosen = rng.sample(candidates, quota) if quota else []

            for product in chosen:
                product_id = product["product_id"].strip()

                if product_id in selected_ids:
                    raise RuntimeError(
                        f"Product bị chọn trùng: {product_id}"
                    )

                selected_ids.add(product_id)

                selected_gender_counts[gender] += 1
                selected_subcategory_counts[subcategory] += 1
                selected_category_counts[
                    product["category"].strip()
                ] += 1

            subcategory_gender_summary[subcategory][gender] = {
                "available": available,
                "selected": quota,
            }

            distribution_rows.append({
                "category": (
                    candidates[0]["category"].strip()
                    if candidates
                    else (
                        "Clothing"
                        if subcategory in {
                            "T-Shirt", "Polo", "Sweatshirt", "Jacket"
                        }
                        else "Shoes"
                    )
                ),
                "sub_category": subcategory,
                "gender": gender,
                "available_count": available,
                "subcategory_target": target,
                "selected_count": quota,
            })

            print(
                f"  {gender:<8} "
                f"available={available:>5,}  "
                f"selected={quota:>3,}"
            )

    selected_products = [
        product
        for product in products
        if product["product_id"].strip() in selected_ids
    ]

    if len(selected_products) != TARGET_TOTAL:
        raise RuntimeError(
            f"Expected {TARGET_TOTAL} products, "
            f"got {len(selected_products)}."
        )

    return (
        selected_products,
        distribution_rows,
        subcategory_gender_summary,
        selected_subcategory_counts,
        selected_gender_counts,
        selected_category_counts,
    )


# ============================================================
# COPY SELECTED IMAGES
# ============================================================

def copy_selected_images(selected_products):
    """
    Preflight tất cả ảnh trước khi copy.
    Dataset nguồn không bị thay đổi.
    """

    source_images = {}

    for product in selected_products:
        product_id = product["product_id"].strip()
        image_path = find_source_image(product)

        if image_path is None:
            raise FileNotFoundError(
                f"Không tìm thấy ảnh cho product_id={product_id}"
            )

        if not verify_image(image_path):
            raise ValueError(
                f"Ảnh không đọc được: {product_id} -> {image_path}"
            )

        source_images[product_id] = image_path

    OUTPUT_IMAGE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    expected_names = {
        f"{product_id}{source_images[product_id].suffix.lower()}"
        for product_id in source_images
    }

    # Xóa ảnh cũ không còn thuộc selection hiện tại.
    # Chỉ quản lý các file ảnh trong final/images.
    for existing_file in OUTPUT_IMAGE_DIR.iterdir():
        if (
            existing_file.is_file()
            and existing_file.suffix.lower() in IMAGE_EXTENSIONS
            and existing_file.name not in expected_names
        ):
            existing_file.unlink()

    print("\nCopying selected images...")

    copied_count = 0

    for product in selected_products:
        product_id = product["product_id"].strip()
        source_path = source_images[product_id]

        filename = f"{product_id}{source_path.suffix.lower()}"
        destination_path = OUTPUT_IMAGE_DIR / filename

        shutil.copy2(source_path, destination_path)

        # CSV lưu đường dẫn tương đối để backend dễ sử dụng.
        product["image_path"] = f"images/{filename}"

        copied_count += 1

    if copied_count != TARGET_TOTAL:
        raise RuntimeError(
            f"Expected {TARGET_TOTAL} copied images, "
            f"got {copied_count}."
        )

    return copied_count


# ============================================================
# REPORTS
# ============================================================

def write_reports(
    all_products,
    selected_products,
    fieldnames,
    distribution_rows,
    subcategory_gender_summary,
    selected_subcategory_counts,
    selected_gender_counts,
    selected_category_counts,
    copied_count,
):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    selected_ids = {
        product["product_id"].strip()
        for product in selected_products
    }

    unselected_products = [
        product
        for product in all_products
        if product["product_id"].strip() not in selected_ids
    ]

    # --------------------------------------------------------
    # Save selected dataset
    # --------------------------------------------------------

    write_csv(
        OUTPUT_CSV,
        fieldnames,
        selected_products,
    )

    # --------------------------------------------------------
    # Save unselected products for traceability
    # --------------------------------------------------------

    write_csv(
        REPORT_DIR / "unselected_products.csv",
        fieldnames,
        unselected_products,
    )

    # --------------------------------------------------------
    # Save sampling distribution
    # --------------------------------------------------------

    distribution_fields = [
        "category",
        "sub_category",
        "gender",
        "available_count",
        "subcategory_target",
        "selected_count",
    ]

    write_csv(
        REPORT_DIR / "sampling_distribution.csv",
        distribution_fields,
        distribution_rows,
    )

    # --------------------------------------------------------
    # Summary JSON
    # --------------------------------------------------------

    summary = {
        "created_at": datetime.now().isoformat(),
        "sampling_method": (
            "Stratified sampling by sub_category, "
            "then proportional gender allocation "
            "using the largest remainder method."
        ),
        "random_seed": RANDOM_SEED,
        "input": {
            "products": len(all_products),
        },
        "sampling": {
            "target_total": TARGET_TOTAL,
            "selected_total": len(selected_products),
            "unselected_total": len(unselected_products),
            "subcategory_targets": SUBCATEGORY_TARGETS,
            "selected_by_category": dict(
                selected_category_counts
            ),
            "selected_by_sub_category": dict(
                selected_subcategory_counts
            ),
            "selected_by_gender": dict(
                selected_gender_counts
            ),
            "subcategory_gender_details": (
                subcategory_gender_summary
            ),
        },
        "image_validation": {
            "selected_products": len(selected_products),
            "images_copied": copied_count,
            "all_selected_images_verified": (
                copied_count == len(selected_products)
            ),
        },
        "output": {
            "products_csv": str(OUTPUT_CSV),
            "images_directory": str(OUTPUT_IMAGE_DIR),
            "reports_directory": str(REPORT_DIR),
        },
    }

    with open(
        REPORT_DIR / "sampling_report.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            summary,
            f,
            indent=4,
            ensure_ascii=False,
        )

    return len(unselected_products)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("SELECT MVP DATASET")
    print("=" * 70)

    print(f"Project root : {PROJECT_ROOT}")
    print(f"Input CSV    : {INPUT_CSV}")
    print(f"Input images : {INPUT_IMAGE_DIR}")
    print(f"Output dir   : {OUTPUT_DIR}")

    if not INPUT_IMAGE_DIR.is_dir():
        raise FileNotFoundError(
            f"Không tìm thấy thư mục ảnh:\n{INPUT_IMAGE_DIR}"
        )

    products, fieldnames = load_products()

    validate_source(products)

    (
        selected_products,
        distribution_rows,
        subcategory_gender_summary,
        selected_subcategory_counts,
        selected_gender_counts,
        selected_category_counts,
    ) = select_products(products)

    copied_count = copy_selected_images(selected_products)

    unselected_count = write_reports(
        all_products=products,
        selected_products=selected_products,
        fieldnames=fieldnames,
        distribution_rows=distribution_rows,
        subcategory_gender_summary=subcategory_gender_summary,
        selected_subcategory_counts=selected_subcategory_counts,
        selected_gender_counts=selected_gender_counts,
        selected_category_counts=selected_category_counts,
        copied_count=copied_count,
    )

    # --------------------------------------------------------
    # Final checks
    # --------------------------------------------------------

    final_ids = {
        product["product_id"].strip()
        for product in selected_products
    }

    actual_image_count = sum(
        1
        for product in selected_products
        if find_image_in_output(product["product_id"])
    )

    if len(final_ids) != TARGET_TOTAL:
        raise RuntimeError("Số product_id duy nhất không bằng 1000.")

    if actual_image_count != TARGET_TOTAL:
        raise RuntimeError(
            f"Số ảnh đầu ra không đúng: {actual_image_count}."
        )

    print("\n" + "=" * 70)
    print("MVP DATASET COMPLETE")
    print("=" * 70)

    print(f"Input products       : {len(products):,}")
    print(f"Selected products    : {len(selected_products):,}")
    print(f"Unselected products  : {unselected_count:,}")
    print(f"Images copied        : {copied_count:,}")
    print(f"Verified output imgs : {actual_image_count:,}")

    print("\n=== CATEGORY ===")
    for category, count in sorted(selected_category_counts.items()):
        print(f"{category:<20} {count:>5,}")

    print("\n=== SUB-CATEGORY ===")
    for subcategory in SUBCATEGORY_TARGETS:
        print(
            f"{subcategory:<20} "
            f"{selected_subcategory_counts[subcategory]:>5,}"
        )

    print("\n=== GENDER ===")
    for gender in GENDER_ORDER:
        print(
            f"{gender:<20} "
            f"{selected_gender_counts[gender]:>5,}"
        )

    print("\nOutput files:")
    print(f"  {OUTPUT_CSV}")
    print(f"  {OUTPUT_IMAGE_DIR}")
    print(f"  {REPORT_DIR / 'sampling_report.json'}")
    print(f"  {REPORT_DIR / 'sampling_distribution.csv'}")
    print(f"  {REPORT_DIR / 'unselected_products.csv'}")

    print("\nSampling completed successfully.")


def find_image_in_output(product_id):
    for extension in IMAGE_EXTENSIONS:
        candidate = OUTPUT_IMAGE_DIR / f"{product_id}{extension}"

        if candidate.is_file():
            return candidate

    return None


if __name__ == "__main__":
    main()