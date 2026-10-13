"""Hybrid text search for products indexed with SigLIP 2 text embeddings.

The vector model supplies semantic ranking. Product type and color are parsed
from common English/Vietnamese aliases and applied as deterministic SQL filters
before ranking. This module does not create its own database session or load the
model per query.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from ai.embedding.siglip2_encoder import DEFAULT_MODEL_NAME, Siglip2Encoder
from app.models.category import Category
from app.models.product import Product, ProductEmbedding


from ai.search.query_normalization import _COLOR_FILTER_PATTERNS, normalize_search_query


def semantic_search_products(
    db: Session,
    encoder: Siglip2Encoder,
    query: str,
    *,
    limit: int = 10,
    category_id: UUID | None = None,
    gender: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    min_similarity: float | None = None,
    model_name: str = DEFAULT_MODEL_NAME,
) -> list[dict[str, Any]]:
    """Return hybrid results: inferred metadata filters, then vector ranking.

    ``similarity`` is cosine similarity, not a probability. ``distance`` is
    pgvector cosine distance (smaller is closer). Recognized category/color
    intent is applied in PostgreSQL before ranking. If those filters produce no
    matches, no unrelated products are substituted.
    """
    query = query.strip()
    if not query:
        raise ValueError("Search query must not be empty.")
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100.")
    if min_similarity is not None and not -1.0 <= min_similarity <= 1.0:
        raise ValueError("min_similarity must be between -1.0 and 1.0.")
    if min_price is not None and max_price is not None and min_price > max_price:
        raise ValueError("min_price cannot be greater than max_price.")

    query_info = normalize_search_query(query)
    if query_info["unsupported_type"] is not None:
        return []

    normalized_query = query_info["normalized_query"] or query
    query_vector = encoder.encode_texts([normalized_query])[0]
    if len(query_vector) != 768:
        raise ValueError(f"Expected a 768-dimensional query vector, got {len(query_vector)}.")

    distance_expr = ProductEmbedding.embedding.cosine_distance(query_vector)
    stmt = (
        select(Product, distance_expr.label("cosine_distance"))
        .join(ProductEmbedding, ProductEmbedding.product_id == Product.id)
        .options(joinedload(Product.category), selectinload(Product.images))
        .where(
            ProductEmbedding.embedding_type == "text",
            ProductEmbedding.product_image_id.is_(None),
            ProductEmbedding.model_name == model_name,
        )
    )

    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    inferred_category = query_info["category"]
    if inferred_category is not None:
        stmt = stmt.where(Product.category.has(Category.name.ilike(inferred_category)))

    inferred_color = query_info["color"]
    if inferred_color is not None:
        patterns = _COLOR_FILTER_PATTERNS.get(inferred_color, (inferred_color.lower(),))
        stmt = stmt.where(or_(*(Product.color.ilike(f"%{pattern}%") for pattern in patterns)))

    if gender is not None:
        stmt = stmt.where(Product.gender.ilike(gender.strip()))
    if min_price is not None:
        stmt = stmt.where(Product.price.is_not(None), Product.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Product.price.is_not(None), Product.price <= max_price)
    if min_similarity is not None:
        # pgvector cosine distance is 1 - cosine similarity.
        stmt = stmt.where(distance_expr <= 1.0 - min_similarity)

    stmt = stmt.order_by(distance_expr.asc(), Product.name.asc()).limit(limit)
    rows = db.execute(stmt).all()
    results: list[dict[str, Any]] = []

    for product, raw_distance in rows:
        distance = float(raw_distance)
        primary_image = next(
            (image for image in product.images if image.is_primary),
            product.images[0] if product.images else None,
        )
        results.append(
            {
                "product_id": str(product.id),
                "external_id": product.external_id,
                "name": product.name,
                "category": product.category.name if product.category else None,
                "gender": product.gender,
                "color": product.color,
                "price": str(product.price) if product.price is not None else None,
                "image_url": primary_image.image_url if primary_image else None,
                "distance": distance,
                "similarity": 1.0 - distance,
            }
        )
    return results
