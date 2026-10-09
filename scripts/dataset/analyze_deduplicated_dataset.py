from pathlib import Path
import csv
from collections import Counter, defaultdict

from PIL import Image


# ============================================================
# PATH CONFIG
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PRODUCT_CSV = (
    PROJECT_ROOT
    / "data"
    / "product"
    / "deduplicated"
    / "products.csv"
)

IMAGE_DIR = (
    PROJECT_ROOT
    / "data"
    / "product"
    / "deduplicated"
    / "images"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_products():
    if not PRODUCT_CSV.exists():
        raise FileNotFoundError(
            f"Không tìm thấy:\n{PRODUCT_CSV}"
        )

    with open(
        PRODUCT_CSV,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        reader = csv.DictReader(f)

        fieldnames = reader.fieldnames or []
        products = list(reader)

    if not products:
        raise ValueError(
            "products.csv không có dữ liệu."
        )

    return products, fieldnames


# ============================================================
# IMAGE FINDER
# ============================================================

def find_image(product_id):
    extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    ]

    for ext in extensions:
        path = IMAGE_DIR / f"{product_id}{ext}"

        if path.exists():
            return path

    return None


# ============================================================
# PRINT COUNTER
# ============================================================

def print_counter(title, counter):
    print(f"\n=== {title} ===")

    total = sum(counter.values())

    for key, count in counter.most_common():
        percentage = (
            count / total * 100
            if total > 0
            else 0
        )

        print(
            f"{str(key):<25} "
            f"{count:>7,} "
            f"({percentage:>6.2f}%)"
        )


# ============================================================
# CATEGORY x GENDER
# ============================================================

def print_subcategory_gender(products):
    data = defaultdict(Counter)

    for product in products:
        sub_category = (
            product.get("sub_category", "").strip()
            or "Unknown"
        )

        gender = (
            product.get("gender", "").strip()
            or "Unknown"
        )

        data[sub_category][gender] += 1

    print("\n=== SUB-CATEGORY × GENDER ===")

    genders = [
        "Men",
        "Unisex",
        "Women",
        "Unknown",
    ]

    header = (
        f"{'Sub-category':<25}"
        + "".join(
            f"{gender:>10}"
            for gender in genders
        )
        + f"{'Total':>10}"
    )

    print(header)
    print("-" * len(header))

    for sub_category in sorted(data.keys()):

        total = sum(data[sub_category].values())

        row = f"{sub_category:<25}"

        for gender in genders:
            row += f"{data[sub_category][gender]:>10,}"

        row += f"{total:>10,}"

        print(row)


# ============================================================
# CATEGORY x GENDER
# ============================================================

def print_category_gender(products):
    data = defaultdict(Counter)

    for product in products:
        category = (
            product.get("category", "").strip()
            or "Unknown"
        )

        gender = (
            product.get("gender", "").strip()
            or "Unknown"
        )

        data[category][gender] += 1

    print("\n=== CATEGORY × GENDER ===")

    genders = [
        "Men",
        "Unisex",
        "Women",
        "Unknown",
    ]

    header = (
        f"{'Category':<25}"
        + "".join(
            f"{gender:>10}"
            for gender in genders
        )
        + f"{'Total':>10}"
    )

    print(header)
    print("-" * len(header))

    for category in sorted(data.keys()):

        total = sum(data[category].values())

        row = f"{category:<25}"

        for gender in genders:
            row += f"{data[category][gender]:>10,}"

        row += f"{total:>10,}"

        print(row)


# ============================================================
# VALIDATE PRODUCT IDs
# ============================================================

def check_duplicate_product_ids(products):
    counter = Counter(
        p.get("product_id", "").strip()
        for p in products
    )

    duplicates = {
        product_id: count
        for product_id, count in counter.items()
        if product_id and count > 1
    }

    empty_ids = sum(
        1
        for p in products
        if not p.get("product_id", "").strip()
    )

    print("\n=== PRODUCT ID VALIDATION ===")

    print(
        f"Total rows           : "
        f"{len(products):,}"
    )

    print(
        f"Empty product_id     : "
        f"{empty_ids:,}"
    )

    print(
        f"Duplicate product_id : "
        f"{len(duplicates):,}"
    )

    if duplicates:
        print("\nDuplicate ID sample:")

        for product_id, count in list(
            duplicates.items()
        )[:20]:
            print(
                f"  {product_id}: {count}"
            )


# ============================================================
# VALIDATE IMAGES
# ============================================================

def validate_images(products):
    missing = []
    corrupt = []
    dimensions = Counter()
    modes = Counter()
    formats = Counter()

    for product in products:

        product_id = (
            product.get("product_id", "").strip()
        )

        image_path = find_image(product_id)

        if image_path is None:

            missing.append(product_id)

            continue

        try:
            with Image.open(image_path) as img:

                # Force read of image metadata.
                width, height = img.size

                dimensions[
                    f"{width}x{height}"
                ] += 1

                modes[img.mode] += 1

                image_format = (
                    img.format
                    if img.format
                    else "Unknown"
                )

                formats[image_format] += 1

                # Verify image data.
                img.verify()

        except Exception as e:

            corrupt.append({
                "product_id": product_id,
                "error": str(e),
            })

    print("\n=== IMAGE VALIDATION ===")

    print(
        f"Products              : "
        f"{len(products):,}"
    )

    print(
        f"Missing images        : "
        f"{len(missing):,}"
    )

    print(
        f"Corrupt images        : "
        f"{len(corrupt):,}"
    )

    print_counter(
        "IMAGE DIMENSIONS",
        dimensions
    )

    print_counter(
        "IMAGE FORMAT",
        formats
    )

    print_counter(
        "IMAGE MODE",
        modes
    )

    if missing:
        print("\nMissing image sample:")

        for product_id in missing[:20]:
            print(
                f"  {product_id}"
            )

    if corrupt:
        print("\nCorrupt image sample:")

        for item in corrupt[:20]:
            print(
                f"  {item['product_id']}: "
                f"{item['error']}"
            )

    return {
        "missing": missing,
        "corrupt": corrupt,
        "dimensions": dimensions,
        "modes": modes,
        "formats": formats,
    }


# ============================================================
# REQUIRED TAXONOMY VALIDATION
# ============================================================

def validate_taxonomy(products):

    expected_categories = {
        "Clothing",
        "Shoes",
    }

    expected_sub_categories = {
        "T-Shirt",
        "Polo",
        "Sweatshirt",
        "Jacket",
        "Casual Shoes",
        "Sports Shoes",
        "Sandals",
    }

    expected_genders = {
        "Men",
        "Women",
        "Unisex",
    }

    invalid_category = []
    invalid_sub_category = []
    invalid_gender = []

    for product in products:

        product_id = (
            product.get("product_id", "").strip()
        )

        category = (
            product.get("category", "").strip()
        )

        sub_category = (
            product.get("sub_category", "").strip()
        )

        gender = (
            product.get("gender", "").strip()
        )

        if category not in expected_categories:
            invalid_category.append({
                "product_id": product_id,
                "value": category,
            })

        if sub_category not in expected_sub_categories:
            invalid_sub_category.append({
                "product_id": product_id,
                "value": sub_category,
            })

        if gender not in expected_genders:
            invalid_gender.append({
                "product_id": product_id,
                "value": gender,
            })

    print("\n=== TAXONOMY VALIDATION ===")

    print(
        f"Invalid category     : "
        f"{len(invalid_category):,}"
    )

    print(
        f"Invalid sub-category : "
        f"{len(invalid_sub_category):,}"
    )

    print(
        f"Invalid gender       : "
        f"{len(invalid_gender):,}"
    )

    if invalid_category:
        print("\nInvalid category sample:")

        for item in invalid_category[:20]:
            print(
                f"  {item['product_id']} "
                f"-> {item['value']}"
            )

    if invalid_sub_category:
        print("\nInvalid sub-category sample:")

        for item in invalid_sub_category[:20]:
            print(
                f"  {item['product_id']} "
                f"-> {item['value']}"
            )

    if invalid_gender:
        print("\nInvalid gender sample:")

        for item in invalid_gender[:20]:
            print(
                f"  {item['product_id']} "
                f"-> {item['value']}"
            )


# ============================================================
# MISSING FIELD ANALYSIS
# ============================================================

def analyze_missing_fields(products, fieldnames):

    print("\n=== MISSING VALUES ===")

    for field in fieldnames:

        missing = 0

        for product in products:

            value = product.get(field)

            if value is None or not str(value).strip():
                missing += 1

        percentage = (
            missing / len(products) * 100
        )

        print(
            f"{field:<25} "
            f"{missing:>7,} "
            f"({percentage:>6.2f}%)"
        )


# ============================================================
# SAMPLE PRODUCTS
# ============================================================

def print_samples(products, count=10):

    print(
        f"\n=== SAMPLE PRODUCTS ({count}) ==="
    )

    for index, product in enumerate(
        products[:count],
        start=1
    ):

        print(
            f"\n[{index}] "
            f"{product.get('product_id', '')}"
        )

        print(
            f"  Name       : "
            f"{product.get('name', '')}"
        )

        print(
            f"  Category   : "
            f"{product.get('category', '')}"
        )

        print(
            f"  Sub-category: "
            f"{product.get('sub_category', '')}"
        )

        print(
            f"  Gender     : "
            f"{product.get('gender', '')}"
        )

        print(
            f"  Color      : "
            f"{product.get('color', '')}"
        )

        print(
            f"  Image      : "
            f"{product.get('image_path', '')}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("ANALYZE DEDUPLICATED DATASET")
    print("=" * 70)

    print(
        f"Product CSV : {PRODUCT_CSV}"
    )

    print(
        f"Image dir   : {IMAGE_DIR}"
    )

    # --------------------------------------------------------
    # Check paths
    # --------------------------------------------------------

    if not PRODUCT_CSV.exists():

        raise FileNotFoundError(
            f"\nKhông tìm thấy:\n{PRODUCT_CSV}"
        )

    if not IMAGE_DIR.exists():

        raise FileNotFoundError(
            f"\nKhông tìm thấy:\n{IMAGE_DIR}"
        )

    # --------------------------------------------------------
    # Load products
    # --------------------------------------------------------

    products, fieldnames = load_products()

    total = len(products)

    print(
        f"\nProducts loaded: "
        f"{total:,}"
    )

    # --------------------------------------------------------
    # Basic counts
    # --------------------------------------------------------

    category_counter = Counter(
        p.get("category", "").strip()
        for p in products
    )

    sub_category_counter = Counter(
        p.get("sub_category", "").strip()
        for p in products
    )

    gender_counter = Counter(
        p.get("gender", "").strip()
        for p in products
    )

    color_counter = Counter(
        p.get("color", "").strip()
        for p in products
    )

    print_counter(
        "CATEGORY",
        category_counter
    )

    print_counter(
        "SUB-CATEGORY",
        sub_category_counter
    )

    print_counter(
        "GENDER",
        gender_counter
    )

    print_counter(
        "COLOR",
        color_counter
    )

    # --------------------------------------------------------
    # Cross tables
    # --------------------------------------------------------

    print_category_gender(products)

    print_subcategory_gender(products)

    # --------------------------------------------------------
    # Validate IDs
    # --------------------------------------------------------

    check_duplicate_product_ids(products)

    # --------------------------------------------------------
    # Validate images
    # --------------------------------------------------------

    image_result = validate_images(products)

    # --------------------------------------------------------
    # Validate taxonomy
    # --------------------------------------------------------

    validate_taxonomy(products)

    # --------------------------------------------------------
    # Missing fields
    # --------------------------------------------------------

    analyze_missing_fields(
        products,
        fieldnames
    )

    # --------------------------------------------------------
    # Samples
    # --------------------------------------------------------

    print_samples(
        products,
        count=10
    )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    print(
        f"Products               : "
        f"{total:,}"
    )

    print(
        f"Categories             : "
        f"{len(category_counter)}"
    )

    print(
        f"Sub-categories         : "
        f"{len(sub_category_counter)}"
    )

    print(
        f"Genders                : "
        f"{len(gender_counter)}"
    )

    print(
        f"Colors                 : "
        f"{len(color_counter)}"
    )

    print(
        f"Missing images         : "
        f"{len(image_result['missing']):,}"
    )

    print(
        f"Corrupt images         : "
        f"{len(image_result['corrupt']):,}"
    )

    duplicate_ids = {
        product_id
        for product_id, count
        in Counter(
            p.get("product_id", "").strip()
            for p in products
        ).items()
        if product_id and count > 1
    }

    print(
        f"Duplicate product IDs  : "
        f"{len(duplicate_ids):,}"
    )

    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()