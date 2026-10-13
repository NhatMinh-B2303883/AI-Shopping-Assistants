"""Validate mapping from final products.csv to High Resolution source images.

This script is read-only for dataset images, CSV files, and PostgreSQL.
It writes only a report to data/product/quality_reports/.

Run from repository root:
    python scripts/dataset/validate_highres_mapping.py
"""
from __future__ import annotations

import csv
import statistics
from collections import Counter
from pathlib import Path

from PIL import Image, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[2]
FINAL_CSV = ROOT / "data" / "product" / "final" / "products.csv"
HIGHRES_ROOT = ROOT / "data" / "raw" / "fashion-dataset"
HIGHRES_IMAGES = HIGHRES_ROOT / "images"
STYLES_CSV = HIGHRES_ROOT / "styles.csv"
REPORT_DIR = ROOT / "data" / "product" / "quality_reports"
REPORT_CSV = REPORT_DIR / "highres_mapping_report.csv"


def normalize_id(value: str | None) -> str:
    value = (value or "").strip()
    if value.endswith(".0") and value[:-2].isdigit():
        return value[:-2]
    return value


def read_style_ids(path: Path) -> set[str]:
    ids: set[str] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "id" not in reader.fieldnames:
            raise ValueError(f"'id' column not found in {path}")
        for row in reader:
            sid = normalize_id(row.get("id"))
            if sid:
                ids.add(sid)
    return ids


def build_image_index(root: Path) -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = {}
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            index.setdefault(path.stem.strip(), []).append(path)
    return index


def main() -> int:
    for required in (FINAL_CSV, STYLES_CSV, HIGHRES_IMAGES):
        if not required.exists():
            raise FileNotFoundError(f"Required path not found: {required}")

    with FINAL_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required_cols = {"product_id", "source_id", "name"}
        missing = required_cols - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing columns in products.csv: {sorted(missing)}")
        products = list(reader)

    style_ids = read_style_ids(STYLES_CSV)
    image_index = build_image_index(HIGHRES_IMAGES)
    source_id_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    valid_dimensions: list[tuple[int, int]] = []
    file_sizes: list[int] = []
    report_rows: list[dict[str, str | int]] = []

    for product in products:
        product_id = (product.get("product_id") or "").strip()
        source_id = normalize_id(product.get("source_id"))
        name = (product.get("name") or "").strip()
        if source_id:
            source_id_counts[source_id] += 1

        reasons: list[str] = []
        candidates = image_index.get(source_id, []) if source_id else []
        matched_styles = bool(source_id and source_id in style_ids)

        if not source_id:
            reasons.append("MISSING_SOURCE_ID")
        elif not matched_styles:
            reasons.append("SOURCE_ID_NOT_IN_STYLES_CSV")

        selected = None
        if not candidates:
            reasons.append("HIGHRES_IMAGE_NOT_FOUND")
        else:
            selected = sorted(candidates, key=lambda p: (len(p.parts), str(p)))[0]
            if len(candidates) > 1:
                reasons.append("AMBIGUOUS_IMAGE_STEM")

        width = height = size_bytes = 0
        if selected is not None:
            try:
                size_bytes = selected.stat().st_size
                with Image.open(selected) as im:
                    width, height = im.size
                    im.verify()
                with Image.open(selected) as im:
                    im.load()
                    if width <= 0 or height <= 0:
                        raise ValueError("Invalid dimensions")
                valid_dimensions.append((width, height))
                file_sizes.append(size_bytes)
            except (UnidentifiedImageError, OSError, ValueError) as exc:
                reasons.append(f"IMAGE_INVALID:{type(exc).__name__}")

        status = "PASS" if not reasons else "FAIL"
        status_counts[status] += 1
        report_rows.append({
            "product_id": product_id,
            "source_id": source_id,
            "product_name": name,
            "highres_image_path": str(selected.relative_to(ROOT)) if selected else "",
            "matched_in_styles_csv": "YES" if matched_styles else "NO",
            "width": width,
            "height": height,
            "file_size_bytes": size_bytes,
            "status": status,
            "details": ";".join(reasons),
        })

    duplicate_ids = sorted(sid for sid, count in source_id_counts.items() if count > 1)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    columns = [
        "product_id", "source_id", "product_name", "highres_image_path",
        "matched_in_styles_csv", "width", "height", "file_size_bytes",
        "status", "details",
    ]
    with REPORT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(report_rows)

    print("=" * 72)
    print("HIGH RESOLUTION IMAGE MAPPING VALIDATION")
    print(f"Products checked    : {len(products)}")
    print(f"Unique style IDs    : {len(style_ids)}")
    print(f"Image files indexed : {sum(map(len, image_index.values()))}")
    print(f"PASS rows           : {status_counts['PASS']}")
    print(f"FAIL rows           : {status_counts['FAIL']}")
    print(f"Duplicate source IDs: {len(duplicate_ids)}")
    if duplicate_ids:
        print("Duplicate source ID sample:", ", ".join(duplicate_ids[:20]))
    if valid_dimensions:
        widths = [w for w, _ in valid_dimensions]
        heights = [h for _, h in valid_dimensions]
        print(f"Image width min/median/max : {min(widths)}/{int(statistics.median(widths))}/{max(widths)}")
        print(f"Image height min/median/max: {min(heights)}/{int(statistics.median(heights))}/{max(heights)}")
        print("Most common dimensions:")
        for (w, h), count in Counter(valid_dimensions).most_common(10):
            print(f"  {w}x{h}: {count}")
        print(f"File size min/median/max bytes: {min(file_sizes)}/{int(statistics.median(file_sizes))}/{max(file_sizes)}")
    print(f"Report saved        : {REPORT_CSV}")
    print("=" * 72)

    if status_counts["FAIL"] or duplicate_ids:
        print("STATUS: REVIEW REQUIRED — do not replace the current images.")
        return 1
    print("STATUS: PASS — mapping is clean; no images were copied or replaced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
