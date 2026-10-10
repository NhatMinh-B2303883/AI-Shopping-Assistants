"""Reusable text/image embedding wrapper for SigLIP 2.

Model: google/siglip2-base-patch16-256
Output: L2-normalized, 768-dimensional vectors suitable for cosine similarity.

This module only performs inference. Database access and persistence belong in
backend/scripts or backend services, not in this encoder.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import torch
import torch.nn.functional as F
from PIL import Image
from transformers import AutoModel, AutoProcessor


DEFAULT_MODEL_NAME = "google/siglip2-base-patch16-256"
DEFAULT_EMBEDDING_DIMENSION = 768
DEFAULT_TEXT_MAX_LENGTH = 64


class Siglip2Encoder:
    """Load SigLIP 2 once and expose text/image encoding methods."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        device: str | torch.device | None = None,
        local_files_only: bool = False,
    ) -> None:
        self.model_name = model_name
        self.device = torch.device(
            device or ("cuda" if torch.cuda.is_available() else "cpu")
        )
        dtype = torch.float16 if self.device.type == "cuda" else torch.float32

        # The first call may download model and processor files from Hugging Face.
        self.processor = AutoProcessor.from_pretrained(
            model_name,
            local_files_only=local_files_only,
        )
        self.model = AutoModel.from_pretrained(
            model_name,
            torch_dtype=dtype,
            local_files_only=local_files_only,
        ).to(self.device)
        self.model.eval()

    @staticmethod
    def _extract_tensor(output: object) -> torch.Tensor:
        """Support Tensor and ModelOutput return forms across Transformers versions."""
        if isinstance(output, torch.Tensor):
            tensor = output
        elif getattr(output, "pooler_output", None) is not None:
            tensor = output.pooler_output
        elif isinstance(output, (tuple, list)):
            candidates = [item for item in output if isinstance(item, torch.Tensor)]
            rank_two = [item for item in candidates if item.ndim == 2]
            if not rank_two:
                raise TypeError("Model output does not contain a 2-D pooled feature tensor.")
            tensor = rank_two[-1]
        else:
            raise TypeError(f"Unsupported model feature output type: {type(output)!r}")

        if tensor.ndim != 2:
            raise ValueError(
                f"Expected features shaped (batch, dimension), got {tuple(tensor.shape)}."
            )
        if tensor.shape[-1] != DEFAULT_EMBEDDING_DIMENSION:
            raise ValueError(
                f"Expected {DEFAULT_EMBEDDING_DIMENSION} dimensions, got {tensor.shape[-1]}."
            )
        tensor = F.normalize(tensor.float(), p=2, dim=-1)
        if not torch.isfinite(tensor).all().item():
            raise ValueError("Model produced NaN or infinite embedding values.")
        return tensor

    def encode_texts(
        self,
        texts: Sequence[str],
        *,
        max_length: int = DEFAULT_TEXT_MAX_LENGTH,
    ) -> list[list[float]]:
        """Encode a batch of strings as normalized 768-D vectors."""
        cleaned_texts = [str(text).strip() for text in texts]
        if not cleaned_texts:
            return []
        if any(not text for text in cleaned_texts):
            raise ValueError("Input text batch contains an empty string.")

        inputs = self.processor(
            text=cleaned_texts,
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        ).to(self.device)
        with torch.inference_mode():
            output = self.model.get_text_features(**inputs)
        return self._extract_tensor(output).cpu().tolist()

    def encode_images(
        self,
        images: Sequence[Image.Image | str | Path],
    ) -> list[list[float]]:
        """Encode a batch of PIL images or image paths as normalized 768-D vectors.

        Images opened by this method are closed internally. PIL Images passed by
        the caller are not closed by this method.
        """
        if not images:
            return []

        pil_images: list[Image.Image] = []
        opened_here: list[Image.Image] = []
        try:
            for image in images:
                if isinstance(image, Image.Image):
                    pil_images.append(image.convert("RGB"))
                else:
                    with Image.open(Path(image)) as source:
                        converted = source.convert("RGB")
                    pil_images.append(converted)
                    opened_here.append(converted)

            inputs = self.processor(images=pil_images, return_tensors="pt").to(self.device)
            with torch.inference_mode():
                output = self.model.get_image_features(**inputs)
            return self._extract_tensor(output).cpu().tolist()
        finally:
            for image in pil_images:
                image.close()
