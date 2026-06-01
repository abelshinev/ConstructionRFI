import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, Text, JSON, DateTime, Integer, Float # content-types
from sqlalchemy import Enum, ForeignKey # for schema
from sqlalchemy.orm import Mapped, mapped_column

from storage.database.connect import Base

class ProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"

class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    sha256: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    stored_path: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    content_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    # Updated to use the strict Enum
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus, name="processingstatus"), 
        nullable=False, 
        default=ProcessingStatus.PENDING
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
    )

class ExtractedContent(Base):
    __tablename__ = "extracted_content"

    id: Mapped[str] = mapped_column(String, primary_key = True, default = lambda: str(uuid4()))
    asset_id: Mapped[str] = mapped_column(String, ForeignKey("assets.id"), nullable = True)
    
    # actual content
    extracted_text: Mapped[str] = mapped_column(Text, nullable = True)
    content_type: Mapped[str] = mapped_column(String, nullable=False)  # "ocr -> From images", "pdf_extract -> From pdfs"

    # metadata
    extraction_metadata: Mapped[dict] = mapped_column(JSON, nullable = True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

# Worker Result table for better data handling

class WorkerResult(Base):
    __tablename__ = "worker_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))
    asset_id: Mapped[str] = mapped_column(String, ForeignKey("assets.id"), nullable=False)

    # type of worker ["pdf", "image", "audio"] and associated data
    worker_type: Mapped[str] = mapped_column(String, nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)

    # confidence + processing status + time of creation
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

# CHUNKING TIME

class ContentChunk(Base):
    __tablename__ = "content_chunks"

    id: Mapped[str] = mapped_column(String,primary_key=True,default=lambda: str(uuid4()))
    asset_id: Mapped[str] = mapped_column(String, ForeignKey("assets.id"), nullable=False)

    worker_result_id: Mapped[str] = mapped_column(String, ForeignKey("worker_results.id"),nullable=False)

    chunk_idx: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_type: Mapped[str] = mapped_column(String,nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.now)


