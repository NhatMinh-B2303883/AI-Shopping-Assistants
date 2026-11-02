"""Smoke-test multimodal search (image + text) against the local catalog.

Usage (from the repository root):

  docker compose exec backend python scripts/test_multimodal_search.py \
      /data/products/images/FP010042.jpg --text-query "white sneakers" --limit 5

  docker compose exec backend python scripts/test_multimodal_search.py \
      /data/products/images/FP010830.jpg --text-query "red dress" \
      --image-weight 0.3 --gender Women
"""
from __future__ import annotations

import argparse
import sys
import time
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from ai.embedding.siglip2_encoder import Siglip2Encoder
from ai.search.multimodal_search import multimodal_search_products
from app.db.session import SessionLocal


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test multimodal search (image + text) using SigLIP 2."
    )
    parser.add_argument(
        "image_path",
        help="Path to a query image file (jpeg/png/webp) inside the container.",
    )
    parser.add_argument(
        "--text-query",
        required=True,
        help="Text refinement query (e.g. 'white sneakers for running').",
    )
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument(
        "--image-weight",
        type=float,
        default=0.5,
        help="Weight α for image embedding (0=text only, 0.5=balanced, 1=image only).",
    )
    parser.add_argument("--category-id", type=UUID, default=None)
    parser.add_argument("--gender", default=None)
    parser.add_argument("--min-price", type=Decimal, default=None)
    parser.add_argument("--max-price", type=Decimal, default=None)
    parser.add_argument(
        "--min-similarity",
        type=float,
        default=0.70,
        help="Cosine-similarity threshold (default: 0.70 for 70%%).",
    )
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100")
    if not 0.0 <= args.image_weight <= 1.0:
        parser.error("--image-weight must be between 0.0 and 1.0")
    return args


def main() -> None:
    args = parse_args()

    image_path = Path(args.image_path)
    if not image_path.is_file():
        print(f"ERROR: Image file not found: {image_path}")
        sys.exit(1)

    image_bytes = image_path.read_bytes()

    text_weight = round(1.0 - args.image_weight, 4)
    print(f"\n{'=' * 72}")
    print("MULTIMODAL SEARCH (Image + Text)")
    print(f"{'=' * 72}")
    print(f"Query image : {image_path}")
    print(f"Image size  : {len(image_bytes):,} bytes")
    print(f"Text query  : {args.text_query}")
    print(f"Image weight: {args.image_weight}  (α)")
    print(f"Text weight : {text_weight}  (1 − α)")
    if args.gender:
        print(f"Gender filter: {args.gender}")
    print(f"Min similarity: {args.min_similarity * 100:.0f}%")

    print("\nLoading SigLIP 2 encoder...")
    t0 = time.perf_counter()
    encoder = Siglip2Encoder()
    t_load = time.perf_counter() - t0
    print(f"Model loaded in {t_load:.2f}s")

    db = SessionLocal()
    try:
        print(f"\nSearching for top {args.limit} products...")
        t0 = time.perf_counter()
        results = multimodal_search_products(
            db,
            encoder,
            image_bytes,
            args.text_query,
            limit=args.limit,
            image_weight=args.image_weight,
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
            print(f"Product  : {result['name']} [{result['external_id']}]")
            print(f"Category : {result['category']}")
            print(f"Gender   : {result['gender']}  |  Color: {result['color']}")
            price = result["price"]
            print(f"Price    : {price if price is not None else 'not provided'}")
            print(f"Similarity: {result['similarity']:.6f}  ({result['similarity']*100:.2f}%)")
            print(f"Distance  : {result['distance']:.6f}")
            print(f"Image URL : {result['image_url']}")

        if not results:
            threshold_pct = (args.min_similarity or 0.70) * 100
            print(f"\n⚠ No products met the similarity threshold (>= {threshold_pct:.1f}%).")
            print("  Possible causes:")
            print("  - The query image is out-of-domain (non-fashion, unsupported category).")
            print("  - Image and text conflict too strongly.")
            print("  - Try adjusting --image-weight or lowering --min-similarity 0.50")
    finally:
        db.close()


if __name__ == "__main__":
    main()
