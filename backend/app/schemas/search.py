"""Pydantic schemas for Image Search and Multimodal Search responses."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SearchResultItem(BaseModel):
    """A single ranked product returned by vector search."""

    model_config = ConfigDict(from_attributes=False)

    product_id: UUID
    name: str
    description: str | None = None
    gender: str | None = None
    color: str | None = None
    price: Decimal | None = None
    category_name: str | None = None
    primary_image_url: str | None = None

    # Cosine similarity score in [0, 1].
    # Higher = more similar to the query.
    score: float = Field(ge=0.0, le=1.0)


class TextSearchResponse(BaseModel):
    """Response envelope for GET /api/v1/search/text."""

    query_type: str = "text"
    query: str
    inferred_category: str | None = None
    inferred_color: str | None = None
    results: list[SearchResultItem]
    top_k: int


class ImageSearchResponse(BaseModel):
    """Response envelope for POST /api/v1/search/image."""

    query_type: str = "image"
    results: list[SearchResultItem]
    top_k: int


class MultimodalSearchResponse(BaseModel):
    """Response envelope for POST /api/v1/search/multimodal."""

    query_type: str = "multimodal"
    text_query: str
    image_weight: float
    text_weight: float
    results: list[SearchResultItem]
    top_k: int
