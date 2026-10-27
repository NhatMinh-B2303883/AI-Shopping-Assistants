"""Visual image search for products indexed with SigLIP 2 image embeddings.

Given raw image bytes (from a user upload), this module encodes the image into
a 768-dimensional vector using the SigLIP 2 Vision Encoder, then queries
pgvector for the most visually similar product images.  Optional metadata
filters (category, gender, price range) are applied in PostgreSQL before
vector ranking.

This module does NOT create its own database session or load the model per
query — both are injected by the caller.
"""
from __future__ import annotations

import io
from decimal import Decimal
from typing import Any
from uuid import UUID

from PIL import Image
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from ai.embedding.siglip2_encoder import DEFAULT_MODEL_NAME, Siglip2Encoder
from app.models.category import Category
from app.models.product import Product, ProductEmbedding, ProductImage


def image_search_products(
    db: Session,
    encoder: Siglip2Encoder,
    image_bytes: bytes,
    *,
    limit: int = 10,
    category_id: UUID | None = None,
    gender: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    min_similarity: float | None = None,
    model_name: str = DEFAULT_MODEL_NAME,
) -> list[dict[str, Any]]:
    """Find visually similar products by encoding an uploaded image.

    The uploaded image is processed entirely in memory and never persisted.
    Each product appears at most once in the results (the best-matching
    image embedding is kept when a product has multiple images).

    Args:
        db:             Active SQLAlchemy session.
        encoder:        Pre-loaded SigLIP 2 encoder instance.
        image_bytes:    Raw bytes of the query image (jpeg/png/webp).
        limit:          Maximum number of results (1–100).
        category_id:    Optional hard category filter (exact UUID).
        gender:         Optional gender filter (case-insensitive).
        min_price:      Optional minimum price filter.
        max_price:      Optional maximum price filter.
        min_similarity: Optional cosine similarity threshold; results
                        below this value are excluded.
        model_name:     Embedding model to query against.

    Returns:
        List of result dicts sorted by descending similarity, each with:
        product_id, external_id, name, category, gender, color, price,
        image_url, distance, similarity.
    """
    if not image_bytes:
        raise ValueError("Image bytes must not be empty.")
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100.")
    if min_similarity is not None and not -1.0 <= min_similarity <= 1.0:
        raise ValueError("min_similarity must be between -1.0 and 1.0.")
    if min_price is not None and max_price is not None and min_price > max_price:
        raise ValueError("min_price cannot be greater than max_price.")

    # Encode query image using SigLIP 2 Vision Encoder.
    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    query_vector = encoder.encode_images([pil_image])[0]
    pil_image.close()

    if len(query_vector) != 768:
        raise ValueError(
            f"Expected a 768-dimensional query vector, got {len(query_vector)}."
        )

    # Build the pgvector cosine distance query on image embeddings.
    distance_expr = ProductEmbedding.embedding.cosine_distance(query_vector)
    stmt = (
        select(Product, distance_expr.label("cosine_distance"))
        .join(ProductEmbedding, ProductEmbedding.product_id == Product.id)
        .options(joinedload(Product.category), selectinload(Product.images))
        .where(
            ProductEmbedding.embedding_type == "image",
            ProductEmbedding.product_image_id.is_not(None),
            ProductEmbedding.model_name == model_name,
        )
    )

    # Apply optional metadata filters.
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    if gender is not None:
        stmt = stmt.where(Product.gender.ilike(gender.strip()))
    if min_price is not None:
        stmt = stmt.where(Product.price.is_not(None), Product.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Product.price.is_not(None), Product.price <= max_price)
    if min_similarity is not None:
        stmt = stmt.where(distance_expr <= 1.0 - min_similarity)

    stmt = stmt.order_by(distance_expr.asc(), Product.name.asc()).limit(limit)
    rows = db.execute(stmt).all()

    results: list[dict[str, Any]] = []
    for product, raw_distance in rows:
        distance = float(raw_distance)
        primary_image = next(
            (img for img in product.images if img.is_primary),
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
