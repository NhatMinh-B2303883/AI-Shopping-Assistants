"""Create contact sheets to visually compare current and staged catalog images.

Run from repository root:
    .\backend\.venv\Scripts\python.exe scripts\dataset\review_highres_staging.py

Reads the existing final images and highres_staging outputs.
Writes only review JPEGs inside data/product/highres_staging/.
Does not change product data, final images, or database.
"""

from __future__ import annotations

import csv
import random
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
FINAL_IMAGES = ROOT / "data" / "product" / "final" / "images"
STAGING_ROOT = ROOT / "data" / "product" / "highres_staging"
SOURCE_IMAGES = STAGING_ROOT / "images"
WEB_IMAGES = STAGING_ROOT / "images_web"
MANIFEST = STAGING_ROOT / "staging_manifest.csv"

CELL_W = 240
CELL_H = 300
LABEL_H = 45
PADDING = 12
BACKGROUND = (245, 245, 245)
TEXT_COLOR = (25, 25, 25)


def load_manifest() -> list[dict[str, str]]:
    if not MANIFEST.is_file():
        raise FileNotFoundError(f"Missing staging manifest: {MANIFEST}")
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def open_fit(path: Path, size: tuple[int, int]) -> Image.Image:
    if not path.is_file():
        image = Image.new("RGB", size, (225, 225, 225))
        draw = ImageDraw.Draw(image)
        draw.text((8, 8), "MISSING", fill=(180, 0, 0))
        return image
    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
        image.thumbnail(size, Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", size, "white")
        x = (size[0] - image.width) // 2
        y = (size[1] - image.height) // 2
        canvas.paste(image, (x, y))
        image.close()
        return canvas


def actual_size(path: Path) -> str:
    if not path.is_file():
        return "missing"
    try:
        with Image.open(path) as image:
            return f"{image.width}x{image.height}"
    except Exception:
        return "invalid"


def draw_contact_sheet(
    records: list[dict[str, str]],
    output_path: Path,
    title: str,
) -> None:
    column_names = ["Current final", "High-res source", "Web optimized"]
    width = PADDING + 3 * (CELL_W + PADDING)
    height = PADDING + 50 + len(records) * (CELL_H + LABEL_H + PADDING)
    sheet = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        small_font = ImageFont.truetype("arial.ttf", 12)
    except OSError:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    draw.text((PADDING, 12), title, fill=TEXT_COLOR, font=font)
    y = PADDING + 35
    for col, name in enumerate(column_names):
        x = PADDING + col * (CELL_W + PADDING)
        draw.text((x, y), name, fill=TEXT_COLOR, font=font)
    y += 25

    for record in records:
        product_id = record.get("product_id", "")
        paths = [
            FINAL_IMAGES / f"{product_id}.jpg",
            SOURCE_IMAGES / f"{product_id}.jpg",
            WEB_IMAGES / f"{product_id}.jpg",
        ]
        for col, path in enumerate(paths):
            x = PADDING + col * (CELL_W + PADDING)
            image = open_fit(path, (CELL_W, CELL_H))
            sheet.paste(image, (x, y))
            image.close()
            draw.text(
                (x, y + CELL_H + 2),
                f"{product_id} | {actual_size(path)}",
                fill=TEXT_COLOR,
                font=small_font,
            )
        y += CELL_H + LABEL_H + PADDING

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path, format="JPEG", quality=92, optimize=True)
    print(f"Created: {output_path}")


def main() -> None:
    if not FINAL_IMAGES.is_dir():
        raise FileNotFoundError(f"Current final images directory missing: {FINAL_IMAGES}")
    if not SOURCE_IMAGES.is_dir() or not WEB_IMAGES.is_dir():
        raise FileNotFoundError("Staging image folders are missing. Run stage_highres_images.py first.")

    rows = load_manifest()
    if len(rows) != 1000:
        raise ValueError(f"Expected 1000 staging manifest rows; found {len(rows)}.")

    lowres = [
        row for row in rows
        if int(row.get("source_width", 0)) < 800 or int(row.get("source_height", 0)) < 800
    ]
    if not lowres:
        print("No source images below 800 pixels.")
    else:
        draw_contact_sheet(
            lowres,
            STAGING_ROOT / "review_contact_sheet_lowres.jpg",
            f"Low-resolution source review ({len(lowres)} products)",
        )

    # A deterministic sample of 12 products to inspect normal high-res source and web output.
    sample = sorted(rows, key=lambda row: row.get("product_id", ""))
    random.Random(20261012).shuffle(sample)
    sample = sample[:12]
    draw_contact_sheet(
        sample,
        STAGING_ROOT / "review_contact_sheet_sample.jpg",
        "Representative sample (12 products)",
    )

    print("=" * 72)
    print(f"Low-resolution rows reviewed: {len(lowres)}")
    print(f"Sample rows reviewed       : {len(sample)}")
    print("Only contact sheets were written; source and final dataset were not changed.")
    print("Open both JPEG contact sheets to compare sharpness and visual fit.")
    print("=" * 72)


if __name__ == "__main__":
    main()
