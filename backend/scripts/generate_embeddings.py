"""Generate SigLIP 2 text/image embeddings for the imported catalog.

Run from the repository root inside Docker:
    docker compose exec -e PYTHONPATH=/app:/workspace backend python scripts/generate_embeddings.py --dry-run --limit 2
    docker compose exec -e PYTHONPATH=/app:/workspace backend python scripts/generate_embeddings.py --limit 2
    docker compose exec -e PYTHONPATH=/app:/workspace backend python scripts/generate_embeddings.py

Default behavior skips vectors already stored for this model. Use --force to
recompute existing vectors after canonical_text or catalog images change.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ai.embedding.siglip2_encoder import Siglip2Encoder
from app.db.session import SessionLocal
from app.models.product import Product, ProductEmbedding, ProductImage

MODEL_NAME = "google/siglip2-base-patch16-256"
IMAGE_ROOT = Path("/data/products/images")
EXPECTED_DIMENSION = 768


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate SigLIP 2 embeddings and save them to PostgreSQL."
    )
    parser.add_argument("--dry-run", action="store_true", help="Compute vectors but rollback database changes.")
    parser.add_argument("--limit", type=int, default=None, help="Process only the first N products.")
    parser.add_argument("--batch-size", type=int, default=8, help="Inference batch size; reduce if memory is limited.")
    parser.add_argument("--force", action="store_true", help="Recompute vectors already present for this model.")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be at least 1")
    if args.batch_size < 1:
        parser.error("--batch-size must be at least 1")
    return args


def image_path_for(image: ProductImage) -> Path:
    """Resolve a stored local catalog image URL to a safe mounted file path."""
    filename = Path(urlparse(image.image_url).path).name
    if not filename or filename in {".", ".."}:
        raise ValueError(f"Cannot resolve image filename from {image.image_url!r}")
    root = IMAGE_ROOT.resolve()
    path = (root / filename).resolve()
    if path.parent != root or not path.is_file():
        raise FileNotFoundError(
            f"Missing image for product {image.product_id}: {path}"
        )
    return path


def upsert_embedding(
    db,
    embedding_map: dict[tuple[str, Any], ProductEmbedding],
    *,
    product_id,
    product_image_id,
    embedding_type: str,
    vector: list[float],
    force: bool,
) -> str:
    if len(vector) != EXPECTED_DIMENSION:
        raise ValueError(f"Expected a {EXPECTED_DIMENSION}-D vector, got {len(vector)}.")

    key_id = product_id if embedding_type == "text" else product_image_id
    key = (embedding_type, key_id)
    existing = embedding_map.get(key)
    if existing is not None and not force:
        return "skipped"

    if existing is None:
        row = ProductEmbedding(
            product_id=product_id,
            product_image_id=product_image_id,
            embedding_type=embedding_type,
            embedding=vector,
            model_name=MODEL_NAME,
        )
        db.add(row)
        embedding_map[key] = row
        return "created"

    existing.embedding = vector
    existing.product_id = product_id
    existing.product_image_id = product_image_id
    existing.embedding_type = embedding_type
    existing.model_name = MODEL_NAME
    return "updated"


def main() -> None:
    args = parse_args()
    device = "cuda" if __import__("torch").cuda.is_available() else "cpu"
    print("=" * 72)
    print(f"Model: {MODEL_NAME}")
    print(f"Device: {device}")
    print(f"Mode: {'DRY RUN (rollback)' if args.dry_run else 'WRITE TO DATABASE'}")
    print(f"Batch size: {args.batch_size}")
    print("=" * 72)

    if not IMAGE_ROOT.is_dir():
        raise FileNotFoundError(
            f"Image directory not found: {IMAGE_ROOT}. Check the catalog volume in docker-compose.yml."
        )

    db = SessionLocal()
    committed_batches = 0
    try:
        statement = (
            select(Product)
            .options(selectinload(Product.images))
            .order_by(Product.external_id, Product.id)
        )
        if args.limit is not None:
            statement = statement.limit(args.limit)
        products = list(db.scalars(statement).unique().all())
        if not products:
            raise ValueError("No products found. Import the catalog before generating embeddings.")

        image_records: list[tuple[Product, ProductImage, Path]] = []
        for product in products:
            if not product.canonical_text or not product.canonical_text.strip():
                raise ValueError(f"Product {product.external_id or product.id} has empty canonical_text.")
            if not product.images:
                raise ValueError(f"Product {product.external_id or product.id} has no images.")
            for product_image in product.images:
                image_records.append((product, product_image, image_path_for(product_image)))

        existing_rows = list(
            db.scalars(
                select(ProductEmbedding).where(
                    ProductEmbedding.model_name == MODEL_NAME,
                    ProductEmbedding.product_id.in_([p.id for p in products]),
                )
            ).all()
        )
        embedding_map: dict[tuple[str, Any], ProductEmbedding] = {}
        for row in existing_rows:
            key_id = row.product_id if row.embedding_type == "text" else row.product_image_id
            embedding_map[(row.embedding_type, key_id)] = row

        pending_text = [p for p in products if args.force or ("text", p.id) not in embedding_map]
        pending_images = [
            item for item in image_records
            if args.force or ("image", item[1].id) not in embedding_map
        ]
        print(f"Products selected: {len(products)}")
        print(f"Text embeddings to compute: {len(pending_text)}")
        print(f"Image embeddings to compute: {len(pending_images)}")
        print("Loading SigLIP 2 (first run may download model files)...")

        encoder = Siglip2Encoder(model_name=MODEL_NAME)
        counts = {"text_created": 0, "text_updated": 0, "image_created": 0, "image_updated": 0, "skipped": 0}

        def record_count(kind: str, result: str) -> None:
            key = f"{kind}_{result}"
            counts[key] = counts.get(key, 0) + 1

        text_batches = (len(pending_text) + args.batch_size - 1) // args.batch_size
        for offset in range(0, len(pending_text), args.batch_size):
            batch = pending_text[offset : offset + args.batch_size]
            vectors = encoder.encode_texts([p.canonical_text for p in batch])
            for product, vector in zip(batch, vectors):
                result = upsert_embedding(
                    db, embedding_map, product_id=product.id, product_image_id=None,
                    embedding_type="text", vector=vector, force=args.force,
                )
                record_count("text", result)
            db.flush()
            if not args.dry_run:
                db.commit()
                committed_batches += 1
            print(f"Text batch {offset // args.batch_size + 1}/{text_batches} complete.")

        image_batches = (len(pending_images) + args.batch_size - 1) // args.batch_size
        for offset in range(0, len(pending_images), args.batch_size):
            batch = pending_images[offset : offset + args.batch_size]
            vectors = encoder.encode_images([path for _, _, path in batch])
            for (product, product_image, _), vector in zip(batch, vectors):
                result = upsert_embedding(
                    db, embedding_map, product_id=product.id, product_image_id=product_image.id,
                    embedding_type="image", vector=vector, force=args.force,
                )
                record_count("image", result)
            db.flush()
            if not args.dry_run:
                db.commit()
                committed_batches += 1
            print(f"Image batch {offset // args.batch_size + 1}/{image_batches} complete.")

        if args.dry_run:
            db.rollback()
            print("\nDRY RUN complete: database changes were rolled back; nothing was saved.")
        else:
            db.commit()
            print("\nEmbedding generation complete. All completed batches were committed.")

        print(
            "Counts: "
            f"text created={counts['text_created']}, text updated={counts['text_updated']}, "
            f"image created={counts['image_created']}, image updated={counts['image_updated']}, "
            f"skipped={counts['skipped']}"
        )
        print(f"Model={MODEL_NAME}; dimension={EXPECTED_DIMENSION}; device={encoder.device}.")
    except Exception:
        db.rollback()
        print("\nOperation failed. Current uncommitted work was rolled back.")
        if committed_batches:
            print(f"Warning: {committed_batches} previous batch(es) were already committed and remain in the database; rerun without --force to continue missing embeddings.")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
