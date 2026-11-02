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
- Maximum upload size: 10 MB → HTTP 413.
- Zero-byte files → HTTP 400.
- Files with wrong magic bytes (e.g. PDF/text renamed to .jpg) → HTTP 400.
- Low-relevance results (similarity < threshold) are filtered out; an empty
  list is returned with a human-readable message instead of forced results.
"""

from __future__ import annotations

from decimal import Decimal
from functools import lru_cache
import time
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.api.deps import DBSession
from app.models.product import Product, ProductEmbedding, ProductImage
from app.models.category import Category
from app.schemas.search import (
    ImageSearchResponse,
    MultimodalSearchResponse,
    SearchResultItem,
    TextSearchResponse,
)
from app.service import ai

router = APIRouter()

_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
_MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB
_DEFAULT_MODEL = ai.MODEL_ID

# Cosine-similarity threshold below which image-search results are considered
# irrelevant (e.g. a cat photo, a coffee mug, or any non-fashion object).
# Results below this score are filtered out and an empty list is returned
# instead of force-matching unrelated items.
_MIN_IMAGE_SIMILARITY = 0.35

# Magic-byte signatures for formats we explicitly ALLOW.
# Key: first N bytes of the file; value: human-readable format name.
_IMAGE_MAGIC: list[tuple[bytes, str]] = [
    (b"\xff\xd8\xff", "JPEG"),
    (b"\x89PNG\r\n\x1a\n", "PNG"),
    (b"RIFF", "WebP"),   # WebP: bytes 0-3 == RIFF, bytes 8-11 == WEBP (checked below)
]


def _check_magic_bytes(data: bytes) -> bool:
    """Return True only when *data* starts with a recognised image signature."""
    if data[:3] == b"\xff\xd8\xff":
        return True
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return True
    # WebP container: RIFF????WEBP
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return True
    return False


def _validate_image(upload: UploadFile) -> None:
    ct = (upload.content_type or "").split(";")[0].strip().lower()
    if ct not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported image type '{ct}'. Accepted: jpeg, png, webp.",
        )


async def _read_image(upload: UploadFile) -> bytes:
    """Read and validate image bytes.

    Checks (in order):
    1. Zero-byte file          → HTTP 400
    2. File size > 10 MB       → HTTP 413
    3. Magic-byte mismatch     → HTTP 400  (catches disguised PDF/text files)
    """
    image_bytes = await upload.read()
    if len(image_bytes) > _MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"Image size ({len(image_bytes) / 1024 / 1024:.1f} MB) exceeds "
                "the 10 MB limit. Please upload a smaller image."
            ),
        )

    # Guard 3: magic-byte check — prevents disguised non-image files (PDF, text…)
    if not _check_magic_bytes(image_bytes):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "File content does not match a supported image format (jpeg/png/webp). "
                "Renaming a PDF or text file to .jpg is not accepted."
            ),
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

@lru_cache(maxsize=1)
def _get_siglip2_encoder():
    from ai.embedding.siglip2_encoder import Siglip2Encoder
    return Siglip2Encoder()


@router.get(
    "/text",
    response_model=TextSearchResponse,
    summary="Semantic Text Search",
    description="Perform hybrid semantic text search using SigLIP 2 embeddings and pgvector.",
)
def text_semantic_search(
    db: DBSession,
    q: str = Query(min_length=1, max_length=255, description="Natural language search query"),
    top_k: int = Query(default=10, ge=1, le=50, description="Number of results to return"),
    category_id: UUID | None = Query(default=None, description="Optional category filter"),
    gender: str | None = Query(default=None, description="Optional gender filter"),
    min_price: Decimal | None = Query(default=None, ge=0, description="Minimum price filter"),
    max_price: Decimal | None = Query(default=None, ge=0, description="Maximum price filter"),
    min_similarity: float | None = Query(default=None, ge=-1.0, le=1.0, description="Minimum cosine similarity threshold"),
) -> TextSearchResponse:
    from ai.search.semantic_search import normalize_search_query, semantic_search_products

    query_info = normalize_search_query(q)
    encoder = _get_siglip2_encoder()

    raw_results = semantic_search_products(
        db=db,
        encoder=encoder,
        query=q,
        limit=top_k,
        category_id=category_id,
        gender=gender,
        min_price=min_price,
        max_price=max_price,
        min_similarity=min_similarity,
    )

    results = [
        SearchResultItem(
            product_id=UUID(r["product_id"]),
            name=r["name"],
            description=None,
            gender=r["gender"],
            color=r["color"],
            price=Decimal(r["price"]) if r["price"] is not None else None,
            category_name=r["category"],
            primary_image_url=r["image_url"],
            score=max(0.0, min(1.0, float(r["similarity"]))),
        )
        for r in raw_results
    ]

    return TextSearchResponse(
        query=q,
        inferred_category=query_info.get("category"),
        inferred_color=query_info.get("color"),
        results=results,
        top_k=top_k,
    )


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
    category_id: UUID | None = Query(default=None, description="Optional category filter"),
    gender: str | None = Query(default=None, description="Optional gender filter"),
    min_price: Decimal | None = Query(default=None, ge=0, description="Minimum price filter"),
    max_price: Decimal | None = Query(default=None, ge=0, description="Maximum price filter"),
    min_similarity: float | None = Query(
        default=None,
        ge=-1.0,
        le=1.0,
        description=(
            "Minimum cosine similarity threshold. "
            f"Defaults to {_MIN_IMAGE_SIMILARITY} when not provided to suppress "
            "irrelevant results (e.g. non-fashion objects)."
        ),
    ),
) -> ImageSearchResponse:
    _validate_image(image)
    image_bytes = await _read_image(image)

    from ai.search.image_search import image_search_products

    # Use caller-supplied threshold or fall back to the global default so that
    # off-category images (cats, cups, trophies …) return an empty list instead
    # of force-matched fashion products.
    effective_min_similarity = (
        min_similarity if min_similarity is not None else _MIN_IMAGE_SIMILARITY
    )

    encoder = _get_siglip2_encoder()
    raw_results = image_search_products(
        db=db,
        encoder=encoder,
        image_bytes=image_bytes,
        limit=top_k,
        category_id=category_id,
        gender=gender,
        min_price=min_price,
        max_price=max_price,
        min_similarity=effective_min_similarity,
    )

    results = [
        SearchResultItem(
            product_id=UUID(r["product_id"]),
            name=r["name"],
            description=None,
            gender=r["gender"],
            color=r["color"],
            price=Decimal(r["price"]) if r["price"] is not None else None,
            category_name=r["category"],
            primary_image_url=r["image_url"],
            score=max(0.0, min(1.0, float(r["similarity"]))),
        )
        for r in raw_results
    ]

    no_results_message: str | None = None
    if not results:
        no_results_message = (
            "Không tìm thấy sản phẩm phù hợp với hình ảnh này. "
            "Hãy thử ảnh sản phẩm thời trang khác (áo, quần, giày…)."
        )

    return ImageSearchResponse(
        results=results,
        top_k=top_k,
        no_results_message=no_results_message,
    )


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
