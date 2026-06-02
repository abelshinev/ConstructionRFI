import os
import asyncio

from pathlib import Path
from celery import Celery
import logging

from pathlib import Path
from celery import Celery
from celery.signals import setup_logging
from sqlalchemy.ext.asyncio import AsyncSession

# MODELS
from services.ocr.recognition import extract_from_media # OCR model
from services.speech.whisper import transcribe_audio
from services.vision.detector import run_detection # Vision model

from packages.shared_schemas.worker_input import WorkerInput

from storage.database.connect import AsyncSessionLocal
from storage.database.models import Asset, AssetOutput, ExtractedContent, ContentChunk, ProcessingStatus

# chunking and cleaning
from services.cleaning.cleaner import clean_extracted_text
from services.chunking.chunker import build_chunks

from services.ocr.recognition import extract_from_media
from packages.shared_schemas import asset

from storage.database.connect import AsyncSessionLocal
from storage.database.models import Asset, ExtractedContent, ProcessingStatus

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("rfi_worker", broker=REDIS_URL, backend=REDIS_URL)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_hijack_root_logger=False,
)

# Set up logger
import logging
LOG_PATH = Path("logs/app.log")


@setup_logging.connect
def configure_worker_logging(*args, **kwargs):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler(),
        ],
        force=True,
    )


logger = logging.getLogger(__name__)

# --- ASYNC DB LOGIC ---

async def process_asset_async(worker_input: WorkerInput):

    asset_id = worker_input.asset_id
    corr_id = worker_input.correlation_id

    async with AsyncSessionLocal() as db:
        asset = await db.get(Asset, asset_id)
        if not asset:
            logger.warning(f"[{corr_id}] Asset with ID {asset_id} not found in DB.")
            return
        
        logger.info(f"[{corr_id}] Processing asset {asset_id} with status {asset.processing_status}")
        
        try:
            # Update status to PROCESSING
            asset.processing_status = ProcessingStatus.PROCESSING
            await db.commit()
            
            asset_path = Path(asset.stored_path)
            extracted_content = None

            # Apply OCR/Transcription based on content
            if asset.content_type.startswith("image/"):
                logger.info(f"[{corr_id}] Extracting text from Image: {asset.original_filename}")
                extracted_content = await extract_from_media(asset_path)

                geometry_data = run_detection(str(asset_path))
                logger.info(f"[{corr_id}] Detection Complete. Found {len(geometry_data['objects'])} objects.")
                print(f"Detection Results: {geometry_data}") # TEMP

                # 2. Persist the output contract to the database
                new_output = AssetOutput(
                    asset_id=asset.id,
                    worker_type="vision_geometry",
                    data=geometry_data
                )
                db.add(new_output)
                
                logger.info(f"[{corr_id}] Geometry data persisted to DB.")

            elif asset.content_type == "application/pdf":
                logger.info(f"[{corr_id}] Extracting text from PDF: {asset.original_filename}")
                extracted_content = await extract_from_media(asset_path)
            
            elif asset.content_type.startswith("audio/"):
                logger.info(f"[{corr_id}] Transcribing audio, File : {asset.original_filename}")
                extracted_content = await transcribe_audio(asset_path)
            

            if not extracted_content:
                logger.warning(f"[{corr_id}] No extracted content produced for asset {asset_id}")
                asset.processing_status = ProcessingStatus.READY
                await db.commit()
                return
            
            raw_text = extracted_content.get("text") or ""
            cleaned_text = clean_extracted_text(str(raw_text))
            extracted_content["text"] = cleaned_text

            new_extracted  = ExtractedContent(
                asset_id = asset.id,
                extracted_text = cleaned_text,
                content_type = extracted_content.get("source"),
                extraction_metadata = {
                    "pages" : extracted_content.get("pages"),
                    "language" : extracted_content.get("language"),
                    "segments" : extracted_content.get("segments"),
                    "source" : extracted_content.get("source"),
                    "cleaning": {
                        "pipeline": [
                            "normalize_newlines",
                            "remove_control_chars",
                            "normalize_spaces",
                            "fix_hyphenated_line_breaks",
                            "normalize_paragraph_spacing",
                        ]
                    },
                    **(extracted_content.get("metadata") or {}),
                },
            )
        
            db.add(new_extracted)
            await db.commit() 
            await db.refresh(new_extracted)

            # chunking pipeline
            chunks = build_chunks(extracted_content, asset.content_type)

            for chunk in chunks:
                db.add(
                    ContentChunk(
                        asset_id = asset.id,
                        extracted_content_id = new_extracted.id,
                        chunk_idx = chunk.chunk_idx,
                        text = chunk.text,
                        chunk_type = chunk.chunk_type,
                        chunk_metadata = chunk.chunk_metadata
                    )
                )
            await db.commit()

            logger.info(f"[{corr_id}] Extraction for {asset_id} stored successfully!")

            # Change processing status to READY
            asset.processing_status = ProcessingStatus.READY
            await db.commit() 

        except Exception as err:
            await db.rollback()
            logger.error(f"[{corr_id}] Error processing asset {asset_id}: {err}")
            asset.processing_status = ProcessingStatus.FAILED
            await db.commit()
            raise 

# --- SYNC CELERY TASK WRAPPER ---
@celery_app.task(bind=True, max_retries=3)
def process_asset_task(self, payload: dict):
    """Celery task to process an asset by its ID."""
    try:
        # Bridge the sync Celery worker to the async SQLAlchemy operations
        worker_input = WorkerInput.model_validate(payload)
        asyncio.run(process_asset_async(worker_input))
    except Exception as exc:
        # Let Celery handle retries gracefully
        logger.error(f"[{worker_input.correlation_id}] Error in process_asset_task: {exc}")
        raise self.retry(exc=exc)

@celery_app.task(name="test_task")
def test_task(x, y):
    logger.info(f"Executing task test_task with x={x}, y={y}")
    return x + y

if __name__ == "__main__":
    celery_app.start()
