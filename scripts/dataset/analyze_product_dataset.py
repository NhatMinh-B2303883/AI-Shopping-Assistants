from __future__ import annotations

import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PRODUCT_CSV = (
    PROJECT_ROOT
    / "data"
    / "product"
    / "products.csv"
)


def main() -> None:
    print("=" * 70)
    print("AI Shopping Assistant - Normalized Dataset Analysis")
    print("=" * 70)

    if not PRODUCT_CSV.exists():
        raise FileNotFoundError(
            f"products.csv not found:\n{PRODUCT_CSV}"
        )

    df = pd.read_csv(PRODUCT_CSV)

    print(f"\nTotal products: {len(df):,}")

    # ------------------------------------------------------------
    # Category
    # ------------------------------------------------------------

    print("\n=== CATEGORY ===")

    category = df["category"].value_counts()

    for name, count in category.items():
        percentage = count / len(df) * 100
        print(f"{name:20} {count:6,} ({percentage:5.2f}%)")

    # ------------------------------------------------------------
    # Sub-category
    # ------------------------------------------------------------

    print("\n=== SUB-CATEGORY ===")

    subcategory = df["sub_category"].value_counts()

    for name, count in subcategory.items():
        percentage = count / len(df) * 100
        print(f"{name:20} {count:6,} ({percentage:5.2f}%)")

    # ------------------------------------------------------------
    # Gender
    # ------------------------------------------------------------

    print("\n=== GENDER ===")

    gender = df["gender"].value_counts()

    for name, count in gender.items():
        percentage = count / len(df) * 100
        print(f"{name:20} {count:6,} ({percentage:5.2f}%)")

    # ------------------------------------------------------------
    # Sub-category x Gender
    # ------------------------------------------------------------

    print("\n=== SUB-CATEGORY × GENDER ===")

    cross = pd.crosstab(
        df["sub_category"],
        df["gender"],
    )

    print(cross.to_string())

    # ------------------------------------------------------------
    # Sub-category x Color
    # ------------------------------------------------------------

    print("\n=== SUB-CATEGORY × COLOR ===")

    color_cross = pd.crosstab(
        df["sub_category"],
        df["color"],
    )

    print(color_cross.to_string())

    # ------------------------------------------------------------
    # Top brands from product name (rough inspection only)
    # ------------------------------------------------------------

    print("\n=== SAMPLE PRODUCT NAMES ===")

    for subcategory_name in sorted(
        df["sub_category"].dropna().unique()
    ):
        print(f"\n[{subcategory_name}]")

        sample = (
            df[df["sub_category"] == subcategory_name]
            [["product_id", "name", "gender", "color"]]
            .head(10)
        )

        print(sample.to_string(index=False))

    # ------------------------------------------------------------
    # Missing values
    # ------------------------------------------------------------

    print("\n=== MISSING VALUES ===")

    missing = df.isnull().sum()

    for column, count in missing.items():
        if count > 0:
            percentage = count / len(df) * 100
            print(
                f"{column:20} "
                f"{count:6,} ({percentage:5.2f}%)"
            )

    print("\n=== DONE ===")


if __name__ == "__main__":
    main()