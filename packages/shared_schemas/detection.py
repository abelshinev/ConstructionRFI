from pydantic import BaseModel, Field
from typing import List


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(BaseModel):
    label: str

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    bbox: BoundingBox