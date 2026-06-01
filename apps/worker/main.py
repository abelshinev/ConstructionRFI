import os
import asyncio

from pathlib import Path
from datetime import datetime
from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession


from services.ocr.recognition import extract_from_media  #ocr
from services.speech.whisper import transcribe_audio
from packages.shared_schemas import asset

from packages.shared_schemas.worker_data import ImageData, PdfData, SpeechTranscript
from packages.shared_schemas.worker_data import WorkerResult as WorkerResultSchema

from storage.database.connect import AsyncSessionLocal
from storage.database.models import Asset, ExtractedContent, ContentChunk, ProcessingStatus
from storage.database.models import (
    Asset,
    ContentChunk,
    ProcessingStatus,
    WorkerResult as WorkerResultModel,
)

# chunking and cleaning
from services.cleaning.cleaner import clean_extracted_text
from services.chunking.chunker import build_chunks, build_chunks_from_worker_result


REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("rfi_worker", broker=REDIS_URL, backend=REDIS_URL)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Set up logger
import logging
logger = logging.getLogger(__name__)

# --- ASYNC DB LOGIC ---

# helper to run worker for corresponding asset
async def run_worker_for_asset(asset: Asset) -> WorkerResultSchema:
    asset_path = Path(asset.stored_path)

    if asset.content_type.startswith("image/"):
        worker_type = "image-data"
        result = await extract_from_media(asset_path)

        data = ImageData(
            text = result.get("text", ""),
            source = result.get("source", "tesseract"),
            metadata = result.get("metadata") or {}
        )

    elif asset.content_type == "application/pdf":
        worker_type = "pdf-data"
        result = await extract_from_media(asset_path)

        data = PdfData(
            text = result.get("text", ""),
            pages = [],
            page_count = result.get("pages") or 0,
            source = result.get("source", "pdfplumber"),
            metadata = result.get("metadata") or {}
        )

    elif asset.content_type.startswith("audio/"):
        result = await transcribe_audio(asset_path)
        data = SpeechTranscript(
            text = result.get("text", ""),
            language= result.get("language"),
            segments = result.get("segments") or [],
            source = result.get("source", "openai-whisper"),
            metadata = result.get("metadata") or {}
        )
        worker_type = "speech-transcript"

    else:
        raise ValueError(f"Unsupported content type: {asset.content_type}")

    return WorkerResultSchema(
        asset_id=asset.id,
        worker_type=worker_type,
        data=data,
        confidence=None,
        status="SUCCESS",
        created_at=datetime.now(),
    )

async def process_asset_async(asset_id: str):
    async with AsyncSessionLocal() as db:
        asset = await db.get(Asset, asset_id)
        if not asset:
            print(f"Asset with ID {asset_id} not found.")
            return
        
        logger.info(f"Processing asset {asset_id} with status {asset.processing_status}")
        
        try:
            # Update status to PROCESSING
            asset.processing_status = ProcessingStatus.PROCESSING
            await db.commit()

            worker_result = await run_worker_for_asset(asset)

            db_worker_result = WorkerResultModel(
                asset_id = asset.id,
                worker_type = worker_result.worker_type,
                data = worker_result.data.model_dump(),
                confidence = worker_result.confidence,
                status = worker_result.status,
                created_at = worker_result.created_at
            )

            db.add(db_worker_result)
            await db.commit()
            await db.refresh(db_worker_result)

            # chunking pipeline
            chunks = build_chunks_from_worker_result(worker_result.model_dump())

            for chunk in chunks:
                db.add(
                    ContentChunk(
                        asset_id = asset.id,
                        worker_result_id = db_worker_result.id,
                        chunk_idx = chunk.chunk_idx,
                        text = chunk.text,
                        chunk_type = chunk.chunk_type,
                        chunk_metadata = chunk.chunk_metadata
                    )
                )
            await db.commit()

            logger.info(f"Extraction for {asset_id} stored successfully!")

            # Change processing status to READY
            asset.processing_status = ProcessingStatus.READY
            await db.commit()

        except Exception as err:
            await db.rollback()
            logger.error(f"Error processing asset {asset_id}: {err}")
            asset.processing_status = ProcessingStatus.FAILED
            await db.commit()
            raise 

# --- SYNC CELERY TASK WRAPPER ---
@celery_app.task(bind=True, max_retries=3)
def process_asset_task(self, asset_id: str):
    """Celery task to process an asset by its ID."""
    try:
        # Bridge the sync Celery worker to the async SQLAlchemy operations
        asyncio.run(process_asset_async(asset_id))
    except Exception as exc:
        # Let Celery handle retries gracefully
        raise self.retry(exc=exc)

@celery_app.task(name="test_task")
def test_task(x, y):
    logger.info(f"Executing task test_task with x={x}, y={y}")
    return x + y

if __name__ == "__main__":
    celery_app.start()
