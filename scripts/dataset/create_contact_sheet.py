from pathlib import Path
import random
import csv

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# PATH CONFIG
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PRODUCT_CSV = PROJECT_ROOT / "data" / "product" / "products.csv"
IMAGE_DIR = PROJECT_ROOT / "data" / "product" / "images"

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "product"
    / "quality_reports"
    / "contact_sheets"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIG
# ============================================================

SAMPLES_PER_CATEGORY = 100

# 10 x 10 = 100 images
GRID_COLS = 10
GRID_ROWS = 10

# Display size of each image
IMAGE_WIDTH = 120
IMAGE_HEIGHT = 160

# Space for text under each image
LABEL_HEIGHT = 35

CELL_WIDTH = IMAGE_WIDTH
CELL_HEIGHT = IMAGE_HEIGHT + LABEL_HEIGHT

MARGIN = 20


# ============================================================
# RANDOM SEED
# ============================================================

RANDOM_SEED = 42
random.seed(RANDOM_SEED)


# ============================================================
# LOAD FONT
# ============================================================

def load_font(size=12):
    """
    Try to load a common Windows font.
    Fall back to PIL default font if unavailable.
    """
    font_candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/calibri.ttf"),
    ]

    for font_path in font_candidates:
        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), size)
            except Exception:
                pass

    return ImageFont.load_default()


FONT = load_font(11)
FONT_SMALL = load_font(10)
FONT_TITLE = load_font(20)


# ============================================================
# READ PRODUCTS.CSV
# ============================================================

def load_products():
    if not PRODUCT_CSV.exists():
        raise FileNotFoundError(
            f"Không tìm thấy products.csv:\n{PRODUCT_CSV}"
        )

    with open(PRODUCT_CSV, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError("products.csv không có dữ liệu.")

    print(f"Products loaded: {len(rows):,}")

    print("CSV columns:")
    for col in reader.fieldnames or []:
        print(f"  - {col}")

    return rows


# ============================================================
# FIND IMAGE
# ============================================================

def find_image(product_id):
    """
    Find image by product_id.
    Normally the dataset contains .jpg files,
    but we also check other common extensions.
    """

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
# SAMPLE PRODUCTS
# ============================================================

def sample_category(products, category, sample_size):
    """
    Stratified-ish sampling:
    Try to distribute samples across sub-categories.
    """

    category_products = [
        p
        for p in products
        if p.get("category", "").strip() == category
    ]

    if not category_products:
        print(f"\nWARNING: Không có sản phẩm category = {category}")
        return []

    # Group by subcategory
    groups = {}

    for product in category_products:
        sub_category = product.get("sub_category", "").strip()

        if not sub_category:
            sub_category = "Unknown"

        groups.setdefault(sub_category, []).append(product)

    print(f"\n=== {category} ===")
    print(f"Total products: {len(category_products):,}")

    for sub_category, items in sorted(groups.items()):
        print(f"  {sub_category:<20}: {len(items):,}")

    # --------------------------------------------------------
    # Allocate approximately equal number of samples
    # across sub-categories.
    # --------------------------------------------------------

    sub_categories = sorted(groups.keys())

    if len(sub_categories) == 0:
        return []

    base_count = sample_size // len(sub_categories)
    remainder = sample_size % len(sub_categories)

    selected = []

    for i, sub_category in enumerate(sub_categories):
        items = groups[sub_category]

        target_count = base_count

        if i < remainder:
            target_count += 1

        target_count = min(target_count, len(items))

        selected.extend(
            random.sample(items, target_count)
        )

    # If some groups were too small, fill the remaining slots
    # from the rest of the category.
    if len(selected) < sample_size:
        selected_ids = {
            p.get("product_id", "")
            for p in selected
        }

        remaining = [
            p
            for p in category_products
            if p.get("product_id", "") not in selected_ids
        ]

        remaining_count = sample_size - len(selected)

        if remaining_count > 0 and remaining:
            extra_count = min(
                remaining_count,
                len(remaining)
            )

            selected.extend(
                random.sample(remaining, extra_count)
            )

    random.shuffle(selected)

    return selected[:sample_size]


# ============================================================
# CREATE CONTACT SHEET
# ============================================================

def create_contact_sheet(products, category, output_filename):
    print(f"\nCreating contact sheet: {category}")

    width = (
        MARGIN * 2
        + GRID_COLS * CELL_WIDTH
    )

    height = (
        MARGIN * 2
        + 40
        + GRID_ROWS * CELL_HEIGHT
    )

    sheet = Image.new(
        "RGB",
        (width, height),
        "white"
    )

    draw = ImageDraw.Draw(sheet)

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    title = (
        f"{category} - "
        f"{len(products)} sample images"
    )

    draw.text(
        (MARGIN, MARGIN),
        title,
        fill="black",
        font=FONT_TITLE
    )

    # --------------------------------------------------------
    # Images
    # --------------------------------------------------------

    valid_count = 0

    for index, product in enumerate(products):

        product_id = product.get(
            "product_id",
            ""
        ).strip()

        sub_category = product.get(
            "sub_category",
            ""
        ).strip()

        image_path = find_image(product_id)

        row = index // GRID_COLS
        col = index % GRID_COLS

        x = MARGIN + col * CELL_WIDTH
        y = MARGIN + 40 + row * CELL_HEIGHT

        # ----------------------------------------------------
        # If image missing
        # ----------------------------------------------------

        if image_path is None:

            draw.rectangle(
                [
                    x,
                    y,
                    x + IMAGE_WIDTH - 1,
                    y + IMAGE_HEIGHT - 1,
                ],
                outline="black",
            )

            draw.text(
                (x + 5, y + 70),
                "MISSING",
                fill="black",
                font=FONT
            )

        else:

            try:
                with Image.open(image_path) as img:

                    img = img.convert("RGB")

                    # Preserve aspect ratio
                    img.thumbnail(
                        (IMAGE_WIDTH, IMAGE_HEIGHT)
                    )

                    # Center image
                    paste_x = (
                        x
                        + (IMAGE_WIDTH - img.width) // 2
                    )

                    paste_y = (
                        y
                        + (IMAGE_HEIGHT - img.height) // 2
                    )

                    sheet.paste(
                        img,
                        (paste_x, paste_y)
                    )

                    valid_count += 1

            except Exception as e:

                draw.rectangle(
                    [
                        x,
                        y,
                        x + IMAGE_WIDTH - 1,
                        y + IMAGE_HEIGHT - 1,
                    ],
                    outline="black",
                )

                draw.text(
                    (x + 5, y + 70),
                    "ERROR",
                    fill="black",
                    font=FONT
                )

                print(
                    f"Image error: "
                    f"{product_id} -> {e}"
                )

        # ----------------------------------------------------
        # Product ID
        # ----------------------------------------------------

        label1 = product_id

        draw.text(
            (x + 2, y + IMAGE_HEIGHT + 2),
            label1,
            fill="black",
            font=FONT_SMALL
        )

        # ----------------------------------------------------
        # Sub-category
        # ----------------------------------------------------

        label2 = sub_category

        draw.text(
            (x + 2, y + IMAGE_HEIGHT + 17),
            label2,
            fill="black",
            font=FONT_SMALL
        )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    output_path = OUTPUT_DIR / output_filename

    sheet.save(
        output_path,
        quality=95
    )

    print(
        f"Saved: {output_path}"
    )

    print(
        f"Valid images displayed: "
        f"{valid_count}/{len(products)}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("CREATE CONTACT SHEETS")
    print("=" * 60)

    print(f"Project root : {PROJECT_ROOT}")
    print(f"Products CSV : {PRODUCT_CSV}")
    print(f"Image folder : {IMAGE_DIR}")
    print(f"Output dir   : {OUTPUT_DIR}")

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
    # Load dataset
    # --------------------------------------------------------

    products = load_products()

    # --------------------------------------------------------
    # Create Clothing sheet
    # --------------------------------------------------------

    clothing = sample_category(
        products,
        "Clothing",
        SAMPLES_PER_CATEGORY
    )

    create_contact_sheet(
        clothing,
        "Clothing",
        "clothing_100.jpg"
    )

    # --------------------------------------------------------
    # Create Shoes sheet
    # --------------------------------------------------------

    shoes = sample_category(
        products,
        "Shoes",
        SAMPLES_PER_CATEGORY
    )

    create_contact_sheet(
        shoes,
        "Shoes",
        "shoes_100.jpg"
    )

    # --------------------------------------------------------
    # Done
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)

    print(
        f"\nContact sheets are located at:\n"
        f"{OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()