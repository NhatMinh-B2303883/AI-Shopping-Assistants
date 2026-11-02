"""Multimodal search: fuse image + text embeddings for product retrieval.

Given raw image bytes and a text refinement query, this module encodes each
modality independently using the SigLIP 2 encoder, then combines them via
weighted late fusion:

    v_fused = α · v_image + (1 − α) · v_text      (L2-normalised)

The fused vector is used to query pgvector (cosine distance) against product
image embeddings, returning products that match both the visual style and the
textual intent.

This module does NOT create its own database session or load the model per
query — both are injected by the caller.
"""
from __future__ import annotations

import io
import math
from decimal import Decimal
from typing import Any
from uuid import UUID

from PIL import Image
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from ai.embedding.siglip2_encoder import DEFAULT_MODEL_NAME, Siglip2Encoder

DEFAULT_MIN_SIMILARITY: float = 0.70  # Ngưỡng tương đồng mặc định 70%

from app.models.category import Category
from app.models.product import Product, ProductEmbedding, ProductImage


def _l2_normalize(vec: list[float]) -> list[float]:
    """Return a unit-length copy of *vec* (L2 normalisation)."""
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0.0:
        return vec
    return [v / norm for v in vec]


def _fuse_vectors(
    image_vector: list[float],
    text_vector: list[float],
    image_weight: float,
) -> list[float]:
    """Weighted late fusion of two L2-normalised vectors.

    ``image_weight`` (α) controls the blend:
    - α = 1.0  → pure image search
    - α = 0.0  → pure text search
    - α = 0.5  → equal blend (default)

    The result is L2-normalised so that cosine distance remains meaningful.
    """
    if not 0.0 <= image_weight <= 1.0:
        raise ValueError("image_weight (α) must be between 0.0 and 1.0.")
    if len(image_vector) != len(text_vector):
        raise ValueError(
            f"Vector dimension mismatch: image={len(image_vector)}, "
            f"text={len(text_vector)}."
        )

    text_weight = 1.0 - image_weight
    fused = [
        image_weight * iv + text_weight * tv
        for iv, tv in zip(image_vector, text_vector)
    ]
    return _l2_normalize(fused)


def multimodal_search_products(
    db: Session,
    encoder: Siglip2Encoder,
    image_bytes: bytes,
    text_query: str,
    *,
    limit: int = 10,
    image_weight: float = 0.5,
    category_id: UUID | None = None,
    gender: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    min_similarity: float | None = DEFAULT_MIN_SIMILARITY,
    model_name: str = DEFAULT_MODEL_NAME,
) -> list[dict[str, Any]]:
    """Find products matching both a query image and a text refinement.

    The uploaded image and text query are each encoded into 768-dim vectors
    by SigLIP 2, then combined via weighted late fusion before querying
    pgvector.  Optional metadata filters (category, gender, price range) are
    applied in PostgreSQL before vector ranking.

    Args:
        db:             Active SQLAlchemy session.
        encoder:        Pre-loaded SigLIP 2 encoder instance.
        image_bytes:    Raw bytes of the query image (jpeg/png/webp).
        text_query:     Text refinement query (e.g. "white sneakers").
        limit:          Maximum number of results (1–100).
        image_weight:   α in [0, 1]. 1 = image only, 0 = text only.
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
    # --- Validate inputs ---
    if not image_bytes:
        raise ValueError("Image bytes must not be empty.")
    text_query = text_query.strip()
    if not text_query:
        raise ValueError("Text query must not be empty.")
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100.")
    if not 0.0 <= image_weight <= 1.0:
        raise ValueError("image_weight must be between 0.0 and 1.0.")
    if min_similarity is None:
        min_similarity = DEFAULT_MIN_SIMILARITY
    if not -1.0 <= min_similarity <= 1.0:
        raise ValueError("min_similarity must be between -1.0 and 1.0.")
    if min_price is not None and max_price is not None and min_price > max_price:
        raise ValueError("min_price cannot be greater than max_price.")

    # --- Encode image ---
    try:
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ValueError(f"Cannot decode query image: {exc}") from exc

    image_vector = encoder.encode_images([pil_image])[0]
    pil_image.close()

    # --- Encode text ---
    text_vector = encoder.encode_texts([text_query])[0]

    # --- Validate dimensions ---
    if len(image_vector) != 768:
        raise ValueError(
            f"Expected a 768-dimensional image vector, got {len(image_vector)}."
        )
    if len(text_vector) != 768:
        raise ValueError(
            f"Expected a 768-dimensional text vector, got {len(text_vector)}."
        )

    # --- Weighted late fusion + L2 normalisation ---
    query_vector = _fuse_vectors(image_vector, text_vector, image_weight)

    # --- Build pgvector cosine distance query on image embeddings ---
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

    # --- Apply optional metadata filters ---
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

    # --- Build result dicts ---
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
