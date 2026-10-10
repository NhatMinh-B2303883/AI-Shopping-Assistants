from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import Counter
from pathlib import Path

import pandas as pd


# ============================================================================
# Project paths
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "fashion_product_images"
RAW_CSV = RAW_DIR / "styles.csv"
RAW_IMAGES_DIR = RAW_DIR / "images"

OUTPUT_DIR = PROJECT_ROOT / "data" / "product"
OUTPUT_CSV = OUTPUT_DIR / "products.csv"
OUTPUT_IMAGES_DIR = OUTPUT_DIR / "images"
POLO_REVIEW_CSV = OUTPUT_DIR / "polo_review.csv"
REPORT_JSON = OUTPUT_DIR / "normalize_report.json"


# ============================================================================
# Project taxonomy
# ============================================================================

ALLOWED_MASTER_CATEGORIES = {
    "Apparel",
    "Footwear",
}

ALLOWED_GENDERS = {
    "Men",
    "Women",
    "Unisex",
}


# Source articleType → project taxonomy
DIRECT_MAPPING = {
    "Sweatshirts": ("Clothing", "Sweatshirt"),
    "Jackets": ("Clothing", "Jacket"),
    "Rain Jacket": ("Clothing", "Jacket"),
    "Casual Shoes": ("Shoes", "Casual Shoes"),
    "Sports Shoes": ("Shoes", "Sports Shoes"),
    "Sandals": ("Shoes", "Sandals"),
    "Sports Sandals": ("Shoes", "Sandals"),
}


# Source article types that are intentionally excluded.
EXCLUDED_ARTICLE_TYPES = {
    "Shirts",
    "Nehru Jackets",
    "Booties",
}


# ============================================================================
# Helpers
# ============================================================================

def normalize_text(value: object) -> str:
    """Return a clean lowercase string."""
    if pd.isna(value):
        return ""

    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)

    return text.lower()


def make_project_product_id(source_id: str) -> str:
    """
    Create a stable product ID for the processed dataset.

    Example:
        source_id = 5891
        project ID = FP005891
    """
    clean_id = str(source_id).strip()

    if clean_id.isdigit():
        return f"FP{clean_id.zfill(6)}"

    # Fallback for unexpected non-numeric IDs.
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", clean_id)
    return f"FP{safe_id}"


def find_image(source_id: str) -> Path | None:
    """
    Find the source image for a product ID.

    The original dataset normally uses:
        images/<id>.jpg

    We also support jpeg/png/webp as a safety fallback.
    """
    source_id = str(source_id).strip()

    possible_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    ]

    for extension in possible_extensions:
        candidate = RAW_IMAGES_DIR / f"{source_id}{extension}"

        if candidate.is_file():
            return candidate

    return None


def is_polo_candidate(product_name: str) -> bool:
    """
    Determine whether a Tshirts product name contains 'Polo'.

    We intentionally flag obvious 'U.S. Polo Assn.' style brand names
    because 'Polo' may refer to the brand, not the product type.
    Those records will be placed into polo_review.csv for inspection.
    """
    name = normalize_text(product_name)

    return bool(re.search(r"\bpolo\b", name))


def is_likely_polo_product(product_name: str) -> bool:
    """
    Conservative Polo classification.

    A product is classified as Polo when the name contains 'polo',
    except obvious brand-name patterns such as:
        U.S. Polo Assn.
        US Polo Assn.
        Polo Assn.

    These exceptions are not discarded; they are classified as T-Shirt
    and included in polo_review.csv for manual review.
    """
    name = normalize_text(product_name)

    if not re.search(r"\bpolo\b", name):
        return False

    brand_patterns = [
        r"\bu\.?s\.?\s+polo\s+assn\b",
        r"\bus\s+polo\s+assn\b",
        r"\bpolo\s+assn\b",
    ]

    for pattern in brand_patterns:
        if re.search(pattern, name):
            return False

    return True


def classify_tshirt(product_name: str) -> tuple[str, str]:
    """
    Map source articleType='Tshirts' into:

        Clothing / Polo
    or
        Clothing / T-Shirt

    Returns:
        (sub_category, mapping_rule)
    """
    if is_likely_polo_product(product_name):
        return "Polo", "Tshirts + product name contains Polo"

    if is_polo_candidate(product_name):
        return (
            "T-Shirt",
            "Tshirts + Polo token appears to be brand-related; review",
        )

    return "T-Shirt", "Tshirts"


def build_canonical_text(
    name: str,
    category: str,
    sub_category: str,
    gender: str,
    color: str,
) -> str:
    """
    Build an English canonical text representation for later
    SigLIP 2 text embedding.

    No information is invented.
    Only existing metadata is combined into a consistent sentence.
    """
    parts = [
        f"Product: {name}.",
        f"Category: {category}.",
        f"Subcategory: {sub_category}.",
    ]

    if gender:
        parts.append(f"Gender: {gender}.")

    if color:
        parts.append(f"Color: {color}.")

    return " ".join(parts)


def clean_output_directory(clean: bool) -> None:
    """Prepare output directory."""
    if clean and OUTPUT_DIR.exists():
        print(f"[INFO] Removing existing output directory: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Main normalization
# ============================================================================

def normalize_dataset(clean: bool = False) -> None:
    print("=" * 72)
    print("AI Shopping Assistant - Dataset Normalization")
    print("=" * 72)

    # ------------------------------------------------------------------------
    # Validate raw dataset
    # ------------------------------------------------------------------------

    print("\n[1/7] Checking raw dataset...")

    if not RAW_CSV.is_file():
        raise FileNotFoundError(
            f"styles.csv not found:\n{RAW_CSV}"
        )

    if not RAW_IMAGES_DIR.is_dir():
        raise FileNotFoundError(
            f"images directory not found:\n{RAW_IMAGES_DIR}"
        )

    print(f"[OK] CSV: {RAW_CSV}")
    print(f"[OK] Images: {RAW_IMAGES_DIR}")

    # ------------------------------------------------------------------------
    # Prepare output
    # ------------------------------------------------------------------------

    print("\n[2/7] Preparing output directory...")

    clean_output_directory(clean)

    # ------------------------------------------------------------------------
    # Read CSV
    # ------------------------------------------------------------------------

    print("\n[3/7] Reading styles.csv...")

    try:
        df = pd.read_csv(
            RAW_CSV,
            dtype={"id": str},
        )
    except UnicodeDecodeError:
        print("[WARN] UTF-8 decoding failed. Retrying with latin-1...")
        df = pd.read_csv(
            RAW_CSV,
            dtype={"id": str},
            encoding="latin-1",
        )

    required_columns = {
        "id",
        "gender",
        "masterCategory",
        "subCategory",
        "articleType",
        "baseColour",
        "productDisplayName",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "styles.csv is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    original_count = len(df)

    print(f"[OK] Raw products: {original_count:,}")

    # ------------------------------------------------------------------------
    # Filter master category
    # ------------------------------------------------------------------------

    print("\n[4/7] Filtering and normalizing taxonomy...")

    master_mask = df["masterCategory"].isin(ALLOWED_MASTER_CATEGORIES)
    df = df[master_mask].copy()

    after_master_category = len(df)

    print(
        f"[INFO] After masterCategory filter: "
        f"{after_master_category:,}"
    )

    # ------------------------------------------------------------------------
    # Filter gender
    # ------------------------------------------------------------------------

    gender_mask = df["gender"].isin(ALLOWED_GENDERS)
    df = df[gender_mask].copy()

    after_gender = len(df)

    print(
        f"[INFO] After gender filter: "
        f"{after_gender:,}"
    )

    # ------------------------------------------------------------------------
    # Sort for reproducibility
    # ------------------------------------------------------------------------

    df["_id_numeric"] = pd.to_numeric(
        df["id"],
        errors="coerce",
    )

    df = df.sort_values(
        by=["_id_numeric", "id"],
        na_position="last",
    ).drop(columns=["_id_numeric"])

    # ------------------------------------------------------------------------
    # Mapping
    # ------------------------------------------------------------------------

    normalized_rows: list[dict] = []
    polo_review_rows: list[dict] = []

    skip_reasons = Counter()

    for _, row in df.iterrows():
        source_id = str(row["id"]).strip()
        article_type = str(row["articleType"]).strip()
        master_category = str(row["masterCategory"]).strip()
        gender = str(row["gender"]).strip()
        color = str(row["baseColour"]).strip()
        name = str(row["productDisplayName"]).strip()

        project_category: str | None = None
        project_sub_category: str | None = None
        mapping_rule: str | None = None

        # ------------------------------------------------------------
        # T-Shirts / Polo
        # ------------------------------------------------------------

        if article_type == "Tshirts":
            project_category = "Clothing"

            (
                project_sub_category,
                mapping_rule,
            ) = classify_tshirt(name)

            if is_polo_candidate(name):
                polo_review_rows.append(
                    {
                        "source_id": source_id,
                        "product_name": name,
                        "gender": gender,
                        "color": color,
                        "source_article_type": article_type,
                        "proposed_sub_category": project_sub_category,
                        "mapping_rule": mapping_rule,
                    }
                )

        # ------------------------------------------------------------
        # Direct mapping
        # ------------------------------------------------------------

        elif article_type in DIRECT_MAPPING:
            (
                project_category,
                project_sub_category,
            ) = DIRECT_MAPPING[article_type]

            mapping_rule = f"Exact articleType: {article_type}"

        # ------------------------------------------------------------
        # Explicit exclusions
        # ------------------------------------------------------------

        elif article_type in EXCLUDED_ARTICLE_TYPES:
            skip_reasons[f"Excluded articleType: {article_type}"] += 1
            continue

        else:
            skip_reasons[f"Not in project taxonomy: {article_type}"] += 1
            continue

        # ------------------------------------------------------------
        # Image validation
        # ------------------------------------------------------------

        source_image = find_image(source_id)

        if source_image is None:
            skip_reasons["Missing image"] += 1
            continue

        # ------------------------------------------------------------
        # Project IDs / paths
        # ------------------------------------------------------------

        project_product_id = make_project_product_id(source_id)

        destination_filename = f"{project_product_id}{source_image.suffix.lower()}"
        destination_image = OUTPUT_IMAGES_DIR / destination_filename

        shutil.copy2(
            source_image,
            destination_image,
        )

        relative_image_path = (
            Path("images") / destination_filename
        ).as_posix()

        canonical_text = build_canonical_text(
            name=name,
            category=project_category,
            sub_category=project_sub_category,
            gender=gender,
            color=color,
        )

        # ------------------------------------------------------------
        # Normalized record
        # ------------------------------------------------------------

        normalized_rows.append(
            {
                "product_id": project_product_id,
                "source_id": source_id,
                "name": name,
                "description": "",
                "category": project_category,
                "sub_category": project_sub_category,
                "gender": gender,
                "color": color,
                "price": "",
                "image_path": relative_image_path,
                "canonical_text": canonical_text,
                "source_dataset": "Fashion Product Images Small",
                "source_master_category": master_category,
                "source_sub_category": str(row["subCategory"]).strip(),
                "source_article_type": article_type,
                "mapping_rule": mapping_rule,
            }
        )

    # ------------------------------------------------------------------------
    # Create output DataFrame
    # ------------------------------------------------------------------------

    normalized_df = pd.DataFrame(normalized_rows)

    if normalized_df.empty:
        raise RuntimeError(
            "Normalization produced zero products. "
            "Check the raw dataset path and taxonomy rules."
        )

    # ------------------------------------------------------------------------
    # Remove duplicate project IDs
    # ------------------------------------------------------------------------

    duplicate_mask = normalized_df["product_id"].duplicated(
        keep="first"
    )

    duplicate_count = int(duplicate_mask.sum())

    if duplicate_count > 0:
        skip_reasons["Duplicate product_id"] += duplicate_count

        normalized_df = normalized_df[
            ~duplicate_mask
        ].copy()

    # ------------------------------------------------------------------------
    # Save normalized dataset
    # ------------------------------------------------------------------------

    normalized_df.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8-sig",
    )

    polo_review_df = pd.DataFrame(polo_review_rows)

    polo_review_df.to_csv(
        POLO_REVIEW_CSV,
        index=False,
        encoding="utf-8-sig",
    )

    # ------------------------------------------------------------------------
    # Build report
    # ------------------------------------------------------------------------

    category_counts = (
        normalized_df["category"]
        .value_counts()
        .to_dict()
    )

    sub_category_counts = (
        normalized_df["sub_category"]
        .value_counts()
        .to_dict()
    )

    gender_counts = (
        normalized_df["gender"]
        .value_counts()
        .to_dict()
    )

    report = {
        "raw_product_count": original_count,
        "after_master_category_filter": after_master_category,
        "after_gender_filter": after_gender,
        "normalized_product_count": len(normalized_df),
        "polo_review_count": len(polo_review_df),
        "category_counts": {
            str(key): int(value)
            for key, value in category_counts.items()
        },
        "sub_category_counts": {
            str(key): int(value)
            for key, value in sub_category_counts.items()
        },
        "gender_counts": {
            str(key): int(value)
            for key, value in gender_counts.items()
        },
        "skipped_products": {
            str(key): int(value)
            for key, value in skip_reasons.items()
        },
        "taxonomy": {
            "Clothing": [
                "T-Shirt",
                "Sweatshirt",
                "Jacket",
                "Polo",
            ],
            "Shoes": [
                "Casual Shoes",
                "Sports Shoes",
                "Sandals",
            ],
        },
        "allowed_genders": [
            "Men",
            "Women",
            "Unisex",
        ],
    }

    with REPORT_JSON.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2,
        )

    # ------------------------------------------------------------------------
    # Console summary
    # ------------------------------------------------------------------------

    print("\n[5/7] Normalization completed.")

    print("\n=== FINAL NORMALIZED COUNT ===")
    print(f"Products: {len(normalized_df):,}")

    print("\n=== CATEGORY ===")
    for category, count in category_counts.items():
        print(f"{category}: {count:,}")

    print("\n=== SUB-CATEGORY ===")
    for sub_category, count in sub_category_counts.items():
        print(f"{sub_category}: {count:,}")

    print("\n=== GENDER ===")
    for gender_value, count in gender_counts.items():
        print(f"{gender_value}: {count:,}")

    print("\n=== POLO REVIEW ===")
    print(
        "Polo candidates requiring review: "
        f"{len(polo_review_df):,}"
    )

    print("\n=== SKIPPED ===")
    skipped_total = sum(skip_reasons.values())

    print(f"Total skipped: {skipped_total:,}")

    for reason, count in skip_reasons.most_common():
        print(f"{reason}: {count:,}")

    print("\n[6/7] Output files:")
    print(f"  products.csv       : {OUTPUT_CSV}")
    print(f"  product images     : {OUTPUT_IMAGES_DIR}")
    print(f"  polo_review.csv    : {POLO_REVIEW_CSV}")
    print(f"  normalize_report   : {REPORT_JSON}")

    print("\n[7/7] Done.")
    print("=" * 72)


# ============================================================================
# CLI
# ============================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize Fashion Product Images dataset."
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help=(
            "Delete the existing data/product directory "
            "before generating new output."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    normalize_dataset(
        clean=args.clean,
    )


if __name__ == "__main__":
    main()