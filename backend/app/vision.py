"""Fridge/pantry photo -> list of ingredient labels, using Gemini Flash."""

from typing import Protocol

from pydantic import BaseModel

from app.gemini import GeminiClient, gemini
from app.schemas import Confidence


class VisionItem(BaseModel):
    name: str
    confidence: Confidence


class IngredientDetector(Protocol):
    def detect(self, image: bytes, mime_type: str, vocabulary: list[str]) -> list[VisionItem]: ...


PROMPT = """You are looking at a photo of someone's fridge, pantry or groceries.
List every distinct food ingredient you can clearly identify.

Rules:
- Prefer names from this list when one fits: {vocabulary}
- Otherwise use a short, common grocery name (e.g. "red onion", not "allium").
- One entry per ingredient; do not count quantities.
- Skip anything you cannot identify, and skip non-food items.
- confidence: "high" if clearly visible, "medium" if partially visible or the
  label is unreadable, "low" if you are guessing from shape or color."""


class GeminiDetector:
    def __init__(self, client: GeminiClient = gemini):
        self.client = client

    def detect(self, image: bytes, mime_type: str, vocabulary: list[str]) -> list[VisionItem]:
        from google.genai import types

        return self.client.generate_json(
            contents=[
                types.Part.from_bytes(data=image, mime_type=mime_type),
                PROMPT.format(vocabulary=", ".join(vocabulary)),
            ],
            schema=list[VisionItem],
            temperature=0.1,
        )


_detector: IngredientDetector = GeminiDetector()


def get_detector() -> IngredientDetector:
    """FastAPI dependency; overridden with a fake in tests."""
    return _detector
