"""Stage High Resolution images for the 1,000 selected products.

Reads:
  data/product/final/products.csv
  data/product/quality_reports/highres_mapping_report.csv
  data/raw/fashion-dataset/images/...

Writes ONLY to:
  data/product/highres_staging/images/      (source-resolution copies)
  data/product/highres_staging/images_web/  (web-optimized JPEGs)
  data/product/highres_staging/staging_manifest.csv

It does not overwrite final/images, update CSVs, or touch PostgreSQL.

Run from repository root:
  .\backend\.venv\Scripts\python.exe scripts\dataset\stage_highres_images.py
"""

from __future__ import annotations

import csv
import shutil
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[2]
FINAL_CSV = ROOT / "data" / "product" / "final" / "products.csv"
MAPPING_REPORT = ROOT / "data" / "product" / "quality_reports" / "highres_mapping_report.csv"
STAGING_ROOT = ROOT / "data" / "product" / "highres_staging"
SOURCE_OUT = STAGING_ROOT / "images"
WEB_OUT = STAGING_ROOT / "images_web"
MANIFEST = STAGING_ROOT / "staging_manifest.csv"

WEB_MAX_EDGE = 1200
WEB_JPEG_QUALITY = 88
EXPECTED_PRODUCTS = 1000


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    for required in (FINAL_CSV, MAPPING_REPORT):
        if not required.is_file():
            raise FileNotFoundError(f"Required file not found: {required}")

    products = read_csv(FINAL_CSV)
    reports = read_csv(MAPPING_REPORT)

    if len(products) != EXPECTED_PRODUCTS:
        raise ValueError(
            f"Expected {EXPECTED_PRODUCTS} final products, found {len(products)}. "
            "Review the source CSV before staging."
        )
    if len(reports) != len(products):
        raise ValueError(
            f"Mapping report has {len(reports)} rows but final CSV has {len(products)}."
        )

    product_ids = [row.get("product_id", "").strip() for row in products]
    if not all(product_ids) or len(set(product_ids)) != len(product_ids):
        raise ValueError("product_id values are empty or duplicated in final/products.csv.")

    report_by_product: dict[str, dict[str, str]] = {}
    for row in reports:
        product_id = (row.get("product_id") or "").strip()
        if not product_id or product_id in report_by_product:
            raise ValueError(f"Empty or duplicate product_id in mapping report: {product_id!r}")
        report_by_product[product_id] = row

    failures: list[str] = []
    for product in products:
        product_id = product["product_id"].strip()
        row = report_by_product.get(product_id)
        if row is None:
            failures.append(f"{product_id}: missing from mapping report")
            continue
        if (row.get("status") or "").strip() != "PASS":
            failures.append(
                f"{product_id}: mapping status is {(row.get('status') or '').strip()!r}"
            )
        if (row.get("source_id") or "").strip() != (product.get("source_id") or "").strip():
            failures.append(f"{product_id}: source_id does not match mapping report")

    if failures:
        print("VALIDATION FAILED. No staging files were written.")
        for message in failures[:30]:
            print(" -", message)
        if len(failures) > 30:
            print(f" ... and {len(failures) - 30} more")
        return 1

    # Refuse to reuse a non-empty staging area, to avoid mixing runs silently.
    if STAGING_ROOT.exists() and any(STAGING_ROOT.iterdir()):
        raise FileExistsError(
            f"Staging directory already exists and is not empty: {STAGING_ROOT}\n"
            "Move it aside or delete it after reviewing its contents, then rerun."
        )

    SOURCE_OUT.mkdir(parents=True, exist_ok=True)
    WEB_OUT.mkdir(parents=True, exist_ok=True)
    manifest_rows: list[dict[str, str | int]] = []
    low_resolution: list[str] = []

    try:
        for index, product in enumerate(products, start=1):
            product_id = product["product_id"].strip()
            report = report_by_product[product_id]
            src = ROOT / Path(report["highres_image_path"])
            if not src.is_file():
                raise FileNotFoundError(f"{product_id}: source image not found: {src}")

            # Use the current product_id filename to preserve existing URL identity.
            # The matching was established via source_id, not through the product name.
            output_name = f"{product_id}.jpg"
            source_dest = SOURCE_OUT / output_name
            web_dest = WEB_OUT / output_name

            with Image.open(src) as opened:
                original = ImageOps.exif_transpose(opened).convert("RGB")
                original_width, original_height = original.size
                original.load()

                if min(original_width, original_height) < 800:
                    low_resolution.append(
                        f"{product_id}: {original_width}x{original_height} ({src.name})"
                    )

                # Keep a byte-for-byte copy as the high-resolution/source variant.
                # The source dataset is expected to contain JPEG images; if it does
                # not, preserve original bytes but write a .jpg name only for known
                # JPEG source files.
                suffix = src.suffix.lower()
                if suffix not in {".jpg", ".jpeg"}:
                    source_dest = SOURCE_OUT / f"{product_id}{suffix}"
                    output_name = source_dest.name
                    web_dest = WEB_OUT / f"{product_id}.jpg"

                shutil.copy2(src, source_dest)

                web_image = original.copy()
                web_image.thumbnail(
                    (WEB_MAX_EDGE, WEB_MAX_EDGE),
                    resample=Image.Resampling.LANCZOS,
                )
                web_width, web_height = web_image.size
                web_image.save(
                    web_dest,
                    format="JPEG",
                    quality=WEB_JPEG_QUALITY,
                    optimize=True,
                    progressive=True,
                )
                web_image.close()
                original.close()

            manifest_rows.append({
                "product_id": product_id,
                "source_id": (product.get("source_id") or "").strip(),
                "product_name": (product.get("name") or "").strip(),
                "source_image": str(source_dest.relative_to(ROOT)),
                "source_width": original_width,
                "source_height": original_height,
                "source_size_bytes": source_dest.stat().st_size,
                "web_image": str(web_dest.relative_to(ROOT)),
                "web_width": web_width,
                "web_height": web_height,
                "web_size_bytes": web_dest.stat().st_size,
                "web_jpeg_quality": WEB_JPEG_QUALITY,
            })

            if index % 100 == 0 or index == len(products):
                print(f"Staged {index}/{len(products)} products.")

        with MANIFEST.open("w", encoding="utf-8-sig", newline="") as handle:
            columns = [
                "product_id", "source_id", "product_name",
                "source_image", "source_width", "source_height", "source_size_bytes",
                "web_image", "web_width", "web_height", "web_size_bytes",
                "web_jpeg_quality",
            ]
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(manifest_rows)

    except Exception:
        print(
            "\nStaging did not finish. Current final dataset was not modified. "
            f"Inspect or remove the partial staging folder before retrying: {STAGING_ROOT}"
        )
        raise

    total_source = sum(int(row["source_size_bytes"]) for row in manifest_rows)
    total_web = sum(int(row["web_size_bytes"]) for row in manifest_rows)

    print("=" * 72)
    print("STAGING COMPLETE — the current dataset and database are unchanged.")
    print(f"Products staged      : {len(manifest_rows)}")
    print(f"Source images        : {SOURCE_OUT}")
    print(f"Web optimized images : {WEB_OUT}")
    print(f"Manifest             : {MANIFEST}")
    print(f"Total source size MB : {total_source / (1024 * 1024):.2f}")
    print(f"Total web size MB    : {total_web / (1024 * 1024):.2f}")
    print(f"Web/source size ratio: {total_web / total_source:.1%}" if total_source else "Web/source size ratio: n/a")
    print(f"Images below 800px minimum side: {len(low_resolution)}")
    for item in low_resolution[:20]:
        print(" LOW RES:", item)
    if len(low_resolution) > 20:
        print(f" ... and {len(low_resolution) - 20} more low-resolution images")
    print("=" * 72)
    print("Do not replace final/images until the staged images are visually reviewed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
