"""Search package public API.

Keep package import lightweight so query-normalization utilities and their unit
tests can be imported without loading SQLAlchemy, pgvector, or the encoder.
The public ``semantic_search_products`` symbol remains available lazily.
"""
from __future__ import annotations

from typing import Any

__all__ = ["semantic_search_products"]


def __getattr__(name: str) -> Any:
    if name == "semantic_search_products":
        from ai.search.semantic_search import semantic_search_products

        return semantic_search_products
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
