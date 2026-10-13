"""Build a validated 992-product candidate dataset using High Resolution images.

This script DOES NOT modify data/product/final and DOES NOT touch PostgreSQL.
It copies validated high-res source and web-optimized images into:
  data/product/highres_final_candidate/
and excludes the 8 explicitly reviewed low-resolution products.

Run from repository root:
  .\backend\.venv\Scripts\python.exe scripts\dataset\build_highres_final_candidate.py
"""

from __future__ import annotations

import csv
import json
import shutil
from collections import Counter
from pathlib import Path

from PIL import Image, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[2]
FINAL_DIR = ROOT / "data" / "product" / "final"
FINAL_CSV = FINAL_DIR / "products.csv"
STAGING_ROOT = ROOT / "data" / "product" / "highres_staging"
SOURCE_IMAGES = STAGING_ROOT / "images"
WEB_IMAGES = STAGING_ROOT / "images_web"
STAGING_MANIFEST = STAGING_ROOT / "staging_manifest.csv"
CANDIDATE_DIR = ROOT / "data" / "product" / "highres_final_candidate"

EXCLUDED_PRODUCT_IDS = {
    "FP002749",
    "FP002751",
    "FP003191",
    "FP003213",
    "FP005397",
    "FP015852",
    "FP015856",
    "FP015864",
}
EXPECTED_SOURCE_PRODUCTS = 1000
MIN_SOURCE_SHORT_EDGE = 800


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"Missing header in {path}")
        return list(reader.fieldnames), list(reader)


def verify_image(path: Path) -> tuple[int, int]:
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")
    try:
        with Image.open(path) as im:
            width, height = im.size
            im.verify()
        with Image.open(path) as im:
            im.load()
            if im.width <= 0 or im.height <= 0:
                raise ValueError("Non-positive image dimension")
        return width, height
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"Image is unreadable/corrupt: {path}: {exc}") from exc


def main() -> int:
    for required in (FINAL_CSV, SOURCE_IMAGES, WEB_IMAGES, STAGING_MANIFEST):
        if not required.exists():
            raise FileNotFoundError(f"Required input does not exist: {required}")

    if CANDIDATE_DIR.exists() and any(CANDIDATE_DIR.iterdir()):
        raise FileExistsError(
            f"Candidate directory is not empty: {CANDIDATE_DIR}\n"
            "Review/rename that directory before rerunning; it will not be overwritten."
        )

    original_columns, original_rows = read_rows(FINAL_CSV)
    if len(original_rows) != EXPECTED_SOURCE_PRODUCTS:
        raise ValueError(
            f"Expected 1000 rows in final/products.csv, found {len(original_rows)}."
        )
    if "product_id" not in original_columns:
        raise ValueError("products.csv must contain product_id.")
    current_ids = [row.get("product_id", "").strip() for row in original_rows]
    if not all(current_ids) or len(set(current_ids)) != len(current_ids):
        raise ValueError("product_id is empty or duplicated in final/products.csv.")

    manifest_columns, manifest_rows = read_rows(STAGING_MANIFEST)
    required_manifest = {
        "product_id", "source_image", "source_width", "source_height",
        "web_image", "web_width", "web_height",
    }
    if not required_manifest.issubset(set(manifest_columns)):
        raise ValueError(
            f"staging_manifest.csv is missing columns: "
            f"{sorted(required_manifest - set(manifest_columns))}"
        )
    manifest_by_id: dict[str, dict[str, str]] = {}
    for row in manifest_rows:
        pid = row.get("product_id", "").strip()
        if not pid or pid in manifest_by_id:
            raise ValueError(f"Empty/duplicate product_id in staging manifest: {pid!r}")
        manifest_by_id[pid] = row

    found_excluded = set(current_ids) & EXCLUDED_PRODUCT_IDS
    if found_excluded != EXCLUDED_PRODUCT_IDS:
        raise ValueError(
            "The expected eight low-resolution product IDs do not match the current "
            f"final dataset. Found {len(found_excluded)}/8: {sorted(found_excluded)}"
        )

    kept_rows = [row for row in original_rows if row["product_id"].strip() not in EXCLUDED_PRODUCT_IDS]
    excluded_rows = [row for row in original_rows if row["product_id"].strip() in EXCLUDED_PRODUCT_IDS]
    if len(kept_rows) != 992 or len(excluded_rows) != 8:
        raise ValueError(f"Unexpected selection result: kept={len(kept_rows)}, excluded={len(excluded_rows)}")

    # Preflight every row before creating the candidate directory.
    failures: list[str] = []
    for row in kept_rows:
        pid = row["product_id"].strip()
        manifest = manifest_by_id.get(pid)
        if manifest is None:
            failures.append(f"{pid}: missing from staging manifest")
            continue
        source = ROOT / Path(manifest["source_image"])
        web = ROOT / Path(manifest["web_image"])
        try:
            sw, sh = verify_image(source)
            ww, wh = verify_image(web)
            if min(sw, sh) < MIN_SOURCE_SHORT_EDGE:
                failures.append(f"{pid}: source is still low resolution ({sw}x{sh})")
            if max(ww, wh) > 1200:
                failures.append(f"{pid}: web image longest edge exceeds 1200 ({ww}x{wh})")
        except (FileNotFoundError, ValueError) as exc:
            failures.append(str(exc))

    if failures:
        print("PREFLIGHT FAILED. Candidate was not built.")
        for failure in failures[:40]:
            print(" -", failure)
        if len(failures) > 40:
            print(f" ... and {len(failures) - 40} additional failures")
        return 1

    candidate_images = CANDIDATE_DIR / "images"
    candidate_web_images = CANDIDATE_DIR / "images_web"
    reports_dir = CANDIDATE_DIR / "reports"
    candidate_images.mkdir(parents=True, exist_ok=True)
    candidate_web_images.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    updated_rows: list[dict[str, str]] = []
    dimensions: Counter[tuple[int, int]] = Counter()
    source_size = 0
    web_size = 0

    try:
        for idx, row in enumerate(kept_rows, start=1):
            pid = row["product_id"].strip()
            manifest = manifest_by_id[pid]
            source = ROOT / Path(manifest["source_image"])
            web = ROOT / Path(manifest["web_image"])
            dest_source = candidate_images / f"{pid}.jpg"
            dest_web = candidate_web_images / f"{pid}.jpg"

            # Staging script currently produces JPEGs. Refuse unexpected formats
            # rather than silently changing extensions and breaking URLs.
            if source.suffix.lower() not in {".jpg", ".jpeg"}:
                raise ValueError(f"{pid}: expected JPEG high-res source, got {source.suffix}")
            if web.suffix.lower() not in {".jpg", ".jpeg"}:
                raise ValueError(f"{pid}: expected JPEG web image, got {web.suffix}")

            shutil.copy2(source, dest_source)
            shutil.copy2(web, dest_web)
            sw, sh = verify_image(dest_source)
            dimensions[(sw, sh)] += 1
            source_size += dest_source.stat().st_size
            web_size += dest_web.stat().st_size

            new_row = dict(row)
            new_row["image_path"] = f"images/{pid}.jpg"
            # New metadata column for frontend/API integration. Existing importer can ignore it.
            new_row["image_web_path"] = f"images_web/{pid}.jpg"
            updated_rows.append(new_row)

            if idx % 100 == 0 or idx == len(kept_rows):
                print(f"Prepared {idx}/{len(kept_rows)} products.")

        output_columns = list(original_columns)
        if "image_web_path" not in output_columns:
            output_columns.append("image_web_path")
        with (CANDIDATE_DIR / "products.csv").open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=output_columns)
            writer.writeheader()
            writer.writerows(updated_rows)

        with (reports_dir / "excluded_low_resolution_products.csv").open(
            "w", encoding="utf-8-sig", newline=""
        ) as handle:
            columns = list(original_columns) + ["exclusion_reason"]
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            for row in excluded_rows:
                record = dict(row)
                record["exclusion_reason"] = "High-resolution source mapping was under 800px on the shorter edge."
                writer.writerow(record)

        summary = {
            "status": "PASS",
            "source_products": len(original_rows),
            "included_products": len(updated_rows),
            "excluded_low_resolution_products": len(excluded_rows),
            "excluded_product_ids": sorted(EXCLUDED_PRODUCT_IDS),
            "source_image_count": len(list(candidate_images.glob("*.jpg"))),
            "web_image_count": len(list(candidate_web_images.glob("*.jpg"))),
            "min_source_short_edge": MIN_SOURCE_SHORT_EDGE,
            "web_max_edge": 1200,
            "source_image_total_mb": round(source_size / (1024 * 1024), 2),
            "web_image_total_mb": round(web_size / (1024 * 1024), 2),
            "source_dimensions": {f"{w}x{h}": n for (w, h), n in dimensions.most_common()},
        }
        (reports_dir / "candidate_validation.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
    except Exception:
        print(
            "\nCandidate generation stopped. Current final dataset was not modified. "
            f"Partial candidate is at {CANDIDATE_DIR}; review/delete it before rerunning."
        )
        raise

    # Final count checks.
    candidate_rows = read_rows(CANDIDATE_DIR / "products.csv")[1]
    source_files = list(candidate_images.glob("*.jpg"))
    web_files = list(candidate_web_images.glob("*.jpg"))
    if len(candidate_rows) != 992 or len(source_files) != 992 or len(web_files) != 992:
        raise RuntimeError(
            f"Post-check failed: CSV={len(candidate_rows)}, source={len(source_files)}, web={len(web_files)}"
        )

    print("=" * 72)
    print("HIGH-RES CANDIDATE BUILT AND VALIDATED")
    print("Current data/product/final and PostgreSQL were not changed.")
    print(f"Products in candidate : {len(candidate_rows)}")
    print(f"Source images         : {len(source_files)}")
    print(f"Web images            : {len(web_files)}")
    print(f"Source total MB       : {source_size / (1024 * 1024):.2f}")
    print(f"Web total MB          : {web_size / (1024 * 1024):.2f}")
    print(f"Candidate folder      : {CANDIDATE_DIR}")
    print(f"Manifest/report       : {reports_dir}")
    print("=" * 72)
    print("NEXT: visually review the candidate before promoting it to data/product/final.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
