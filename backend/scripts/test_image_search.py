"""Smoke-test visual image search against the local catalog.

Usage (from the repository root):

  docker compose exec backend python scripts/test_image_search.py \
      /data/products/images/FP010042.jpg --limit 5

  docker compose exec backend python scripts/test_image_search.py \
      /data/products/images/FP010830.jpg --limit 5 --gender Women
"""
from __future__ import annotations

import argparse
import sys
import time
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from ai.embedding.siglip2_encoder import Siglip2Encoder
from ai.search.image_search import image_search_products
from app.db.session import SessionLocal


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test visual image search using SigLIP 2 image embeddings."
    )
    parser.add_argument(
        "image_path",
        help="Path to a query image file (jpeg/png/webp) inside the container.",
    )
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--category-id", type=UUID, default=None)
    parser.add_argument("--gender", default=None)
    parser.add_argument("--min-price", type=Decimal, default=None)
    parser.add_argument("--max-price", type=Decimal, default=None)
    parser.add_argument(
        "--min-similarity",
        type=float,
        default=None,
        help="Optional cosine-similarity threshold.",
    )
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100")
    return args


def main() -> None:
    args = parse_args()

    image_path = Path(args.image_path)
    if not image_path.is_file():
        print(f"ERROR: Image file not found: {image_path}")
        sys.exit(1)

    image_bytes = image_path.read_bytes()
    print(f"\nQuery image: {image_path}")
    print(f"Image size: {len(image_bytes):,} bytes")

    print("\nLoading SigLIP 2 encoder...")
    t0 = time.perf_counter()
    encoder = Siglip2Encoder()
    t_load = time.perf_counter() - t0
    print(f"Model loaded in {t_load:.2f}s")

    db = SessionLocal()
    try:
        print(f"\nSearching for top {args.limit} similar products...")
        t0 = time.perf_counter()
        results = image_search_products(
            db,
            encoder,
            image_bytes,
            limit=args.limit,
            category_id=args.category_id,
            gender=args.gender,
            min_price=args.min_price,
            max_price=args.max_price,
            min_similarity=args.min_similarity,
        )
        t_search = time.perf_counter() - t0
        print(f"Search completed in {t_search:.3f}s")

        print(f"\nResults: {len(results)}")
        for rank, result in enumerate(results, start=1):
            print("-" * 72)
            print(f"Rank: {rank}")
            print(f"Product: {result['name']} [{result['external_id']}]")
            print(f"Category: {result['category']}")
            print(f"Gender/color: {result['gender']} / {result['color']}")
            price = result["price"]
            print(f"Price: {price if price is not None else 'not provided'}")
            print(f"Cosine similarity: {result['similarity']:.6f}")
            print(f"Cosine distance:   {result['distance']:.6f}")
            print(f"Image URL: {result['image_url']}")

        if not results:
            print("\n⚠ No results found. Possible causes:")
            print("  - No image embeddings have been generated yet.")
            print("  - Run: docker compose exec backend python scripts/generate_embeddings.py")
    finally:
        db.close()


if __name__ == "__main__":
    main()
