"""AI inference service — SigLIP 2 image & text embeddings.

Model: google/siglip2-base-patch16-256
Output dimension: 768
Usage: Image Search, Multimodal Search.

The model is loaded once at process startup and reused across requests.
Torch inference runs on CPU at MVP stage (no GPU required).
"""

from __future__ import annotations

import io
from functools import lru_cache
from typing import TYPE_CHECKING

import torch
from PIL import Image
from transformers import AutoProcessor, AutoModel

MODEL_ID = "google/siglip2-base-patch16-256"
EMBEDDING_DIM = 768


@lru_cache(maxsize=1)
def _load_model() -> tuple:
    """Load SigLIP 2 model and processor (cached — loaded only once)."""
    processor = AutoProcessor.from_pretrained(MODEL_ID)
    model = AutoModel.from_pretrained(MODEL_ID)
    model.eval()
    return processor, model


def _normalize(tensor: torch.Tensor) -> torch.Tensor:
    """L2-normalize along the last dimension."""
    return tensor / tensor.norm(dim=-1, keepdim=True)


def embed_image_bytes(image_bytes: bytes) -> list[float]:
    """Return an L2-normalized 768-dim image embedding from raw image bytes.

    The returned vector is ready for cosine-similarity search in pgvector.
    The original bytes are NOT stored anywhere — they are discarded after
    inference.
    """
    processor, model = _load_model()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        image_features = model.get_image_features(**inputs)

    embedding = _normalize(image_features).squeeze(0)
    return embedding.tolist()


def embed_text(text: str) -> list[float]:
    """Return an L2-normalized 768-dim text embedding.

    Used for generating product text embeddings during indexing,
    and for text-based queries in Multimodal Search.
    """
    processor, model = _load_model()

    inputs = processor(text=[text], return_tensors="pt", padding=True)
    with torch.no_grad():
        text_features = model.get_text_features(**inputs)

    embedding = _normalize(text_features).squeeze(0)
    return embedding.tolist()


def embed_multimodal(image_bytes: bytes, text: str, alpha: float = 0.5) -> list[float]:
    """Fuse image + text embeddings into a single query vector.

    The fusion is a weighted average:
        query = alpha * image_embedding + (1 - alpha) * text_embedding

    Both embeddings are L2-normalized before fusion, and the fused vector
    is L2-normalized again before being returned.

    Args:
        image_bytes: Raw bytes of the uploaded query image.
        text:        Refinement text supplied by the user.
        alpha:       Weight of the image embedding (0.0–1.0).
                     Default 0.5 = equal weight.

    Returns:
        L2-normalized 768-dim fused embedding as a list of floats.
    """
    processor, model = _load_model()

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_inputs = processor(images=image, return_tensors="pt")

    txt_inputs = processor(text=[text], return_tensors="pt", padding=True)

    with torch.no_grad():
        img_feat = model.get_image_features(**img_inputs)
        txt_feat = model.get_text_features(**txt_inputs)

    img_norm = _normalize(img_feat).squeeze(0)
    txt_norm = _normalize(txt_feat).squeeze(0)

    fused = alpha * img_norm + (1.0 - alpha) * txt_norm
    fused = _normalize(fused.unsqueeze(0)).squeeze(0)
    return fused.tolist()
