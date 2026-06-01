from pydantic import BaseModel, Field
from typing import Any, Literal
from datetime import datetime

class ImageData(BaseModel):
    text: str
    source: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class PdfPage(BaseModel):
    page_number: int
    text: str

class PdfData(BaseModel):
    text: str
    pages : list[PdfPage] = Field(default_factory=list)
    page_count: int
    source: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class SpeechSegment(BaseModel):
    id: int | None = None
    start: float | None = None
    end: float | None = None
    text: str

class SpeechTranscript(BaseModel):
    text: str
    language: str | None = None
    segments: list[SpeechSegment] = Field(default_factory=list)
    source: str
    metadata: dict[str, Any] = Field(default_factory=dict)


WorkerType = Literal["image-data", "pdf-data", "speech-transcript"]
WorkerStatus = Literal["SUCCESS", "FAILED"]

class WorkerResult(BaseModel):
    asset_id: str
    worker_type: WorkerType
    data: ImageData | PdfData | SpeechTranscript
    confidence: float | None = None
    status: WorkerStatus
    created_at: datetime
