"""Smoke-test hybrid text search against the local catalog.

Examples from the repository root:
  docker compose exec -e PYTHONPATH=/app:/workspace backend \
      python scripts/test_semantic_search.py "black hoodie" --limit 5
  docker compose exec -e PYTHONPATH=/app:/workspace backend \
      python scripts/test_semantic_search.py "áo hoodie đen" --limit 5
"""
from __future__ import annotations

import argparse
from decimal import Decimal
from uuid import UUID

from ai.embedding.siglip2_encoder import Siglip2Encoder
from ai.search.semantic_search import normalize_search_query, semantic_search_products
from app.db.session import SessionLocal


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test hybrid semantic product search.")
    parser.add_argument("query", help="Natural-language search query.")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--category-id", type=UUID, default=None)
    parser.add_argument("--gender", default=None)
    parser.add_argument("--min-price", type=Decimal, default=None)
    parser.add_argument("--max-price", type=Decimal, default=None)
    parser.add_argument(
        "--min-similarity", type=float, default=None,
        help="Optional cosine-similarity threshold; not a probability.",
    )
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100")
    return args


def main() -> None:
    args = parse_args()
    query_info = normalize_search_query(args.query)
    print(f"\nOriginal query: {args.query!r}")
    print(f"Normalized embedding query: {query_info['normalized_query']!r}")
    print(f"Inferred product type: {query_info['category'] or 'none'}")
    print(f"Inferred color: {query_info['color'] or 'none'}")
    if query_info["unsupported_type"]:
        print(f"Known out-of-scope type: {query_info['unsupported_type']!r}; returning no results.")
        print("Results: 0")
        return

    db = SessionLocal()
    try:
        encoder = Siglip2Encoder()
        results = semantic_search_products(
            db,
            encoder,
            args.query,
            limit=args.limit,
            category_id=args.category_id,
            gender=args.gender,
            min_price=args.min_price,
            max_price=args.max_price,
            min_similarity=args.min_similarity,
        )
        print(f"Results: {len(results)}")
        for rank, result in enumerate(results, start=1):
            print("-" * 72)
            print(f"Rank: {rank}")
            print(f"Product: {result['name']} [{result['external_id']}]")
            print(f"Category: {result['category']}")
            print(f"Gender/color: {result['gender']} / {result['color']}")
            print(f"Price: {result['price'] if result['price'] is not None else 'not provided'}")
            print(f"Cosine similarity: {result['similarity']:.6f}")
            print(f"Cosine distance:   {result['distance']:.6f}")
            print(f"Image URL: {result['image_url']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
