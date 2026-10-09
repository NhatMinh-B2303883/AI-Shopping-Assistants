"""Search endpoints — Image Search and Multimodal Search.

POST /api/v1/search/image
    Upload an image → SigLIP 2 Image Encoder → 768-dim embedding
    → pgvector cosine similarity search → Top-K products.

POST /api/v1/search/multimodal
    Upload an image + text query → SigLIP 2 (image + text encoders)
    → weighted fusion of embeddings → pgvector search → Top-K products.

Design constraints:
- Uploaded images are NEVER persisted. They are decoded in-memory,
  passed through the model, then discarded.
- Only product_image embeddings (embedding_type = 'image') are searched
  for Image Search and Multimodal Search.
- Accepted image MIME types: image/jpeg, image/png, image/webp.
- Maximum upload size is enforced by FastAPI's default request body limit
  (can be tuned via Starlette's max_upload_size if needed).
"""

from __future__ import annotations

import time
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.api.deps import DBSession
from app.models.product import Product, ProductEmbedding, ProductImage
from app.models.category import Category
from app.schemas.search import ImageSearchResponse, MultimodalSearchResponse, SearchResultItem
from app.service import ai

router = APIRouter()

_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
_MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB
_DEFAULT_MODEL = ai.MODEL_ID


def _validate_image(upload: UploadFile) -> None:
    if upload.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported image type '{upload.content_type}'. Accepted: jpeg, png, webp.",
        )


async def _read_image(upload: UploadFile) -> bytes:
    image_bytes = await upload.read()
    if len(image_bytes) > _MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image exceeds the 10 MB size limit.",
        )
    return image_bytes


def _vector_search(
    db: Session,
    query_vector: list[float],
    top_k: int,
    model_name: str,
) -> list[SearchResultItem]:
    """Search product_embeddings (image type only) using cosine similarity.

    Returns up to top_k results ordered by descending similarity score.
    pgvector operator <=> computes cosine distance; score = 1 - distance.
    """
    vector_literal = f"'[{','.join(str(v) for v in query_vector)}]'::vector"

    raw_sql = text(f"""
        SELECT
            p.id          AS product_id,
            p.name        AS name,
            p.description AS description,
            p.gender      AS gender,
            p.color       AS color,
            p.price       AS price,
            c.name        AS category_name,
            pi_primary.image_url AS primary_image_url,
            1 - (pe.embedding <=> {vector_literal}) AS score
        FROM product_embeddings pe
        JOIN products p          ON p.id  = pe.product_id
        LEFT JOIN categories c   ON c.id  = p.category_id
        LEFT JOIN product_images pi_primary
            ON pi_primary.product_id = p.id
           AND pi_primary.is_primary = TRUE
        WHERE pe.embedding_type = 'image'
          AND pe.model_name     = :model_name
        ORDER BY pe.embedding <=> {vector_literal}
        LIMIT :top_k
    """)

    rows = db.execute(raw_sql, {"model_name": model_name, "top_k": top_k}).fetchall()

    return [
        SearchResultItem(
            product_id=row.product_id,
            name=row.name,
            description=row.description,
            gender=row.gender,
            color=row.color,
            price=row.price,
            category_name=row.category_name,
            primary_image_url=row.primary_image_url,
            score=float(row.score),
        )
        for row in rows
    ]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/image",
    response_model=ImageSearchResponse,
    summary="Image Search",
    description=(
        "Upload a product image to find visually similar products. "
        "The image is processed in memory and never saved to the database."
    ),
)
async def image_search(
    db: DBSession,
    image: Annotated[UploadFile, File(description="Query image (jpeg / png / webp, max 10 MB)")],
    top_k: int = Query(default=10, ge=1, le=50, description="Number of results to return"),
    model_name: str = Query(default=_DEFAULT_MODEL, description="Embedding model to query against"),
) -> ImageSearchResponse:
    _validate_image(image)
    image_bytes = await _read_image(image)

    query_vector = ai.embed_image_bytes(image_bytes)

    results = _vector_search(db, query_vector, top_k, model_name)

    return ImageSearchResponse(results=results, top_k=top_k)


@router.post(
    "/multimodal",
    response_model=MultimodalSearchResponse,
    summary="Multimodal Search (Image + Text)",
    description=(
        "Upload an image along with a text refinement query. "
        "The two embeddings are fused into a single query vector used "
        "to find products matching both the visual style and textual intent. "
        "The uploaded image is processed in memory and never saved."
    ),
)
async def multimodal_search(
    db: DBSession,
    image: Annotated[UploadFile, File(description="Query image (jpeg / png / webp, max 10 MB)")],
    text_query: Annotated[str, Form(min_length=1, max_length=512, description="Text refinement, e.g. 'white color, for running'")],
    top_k: int = Query(default=10, ge=1, le=50, description="Number of results to return"),
    image_weight: float = Query(default=0.5, ge=0.0, le=1.0, description="Weight of the image embedding (0=text only, 1=image only)"),
    model_name: str = Query(default=_DEFAULT_MODEL, description="Embedding model to query against"),
) -> MultimodalSearchResponse:
    _validate_image(image)
    image_bytes = await _read_image(image)

    query_vector = ai.embed_multimodal(image_bytes, text_query, alpha=image_weight)

    results = _vector_search(db, query_vector, top_k, model_name)

    return MultimodalSearchResponse(
        text_query=text_query,
        image_weight=image_weight,
        text_weight=round(1.0 - image_weight, 4),
        results=results,
        top_k=top_k,
    )
