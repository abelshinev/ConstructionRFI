import os
import asyncio

from pathlib import Path
from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession


from services.ocr.recognition import extract_from_media
from packages.shared_schemas import asset

from storage.database.connect import AsyncSessionLocal
from storage.database.models import Asset, ExtractedContent, ProcessingStatus
import logging

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
logger = logging.getLogger(__name__)

# --- ASYNC DB LOGIC ---

async def process_asset_async(asset_id: str):
    async with AsyncSessionLocal() as db:
        asset = await db.get(Asset, asset_id)
        if not asset:
            print(f"Asset with ID {asset_id} not found.")
            return
        
        print(f"Processing asset {asset_id} with status {asset.processing_status}")
        
        try:
            # Update status to PROCESSING
            asset.processing_status = ProcessingStatus.PROCESSING
            await db.commit()
            
            # # Simulate processing time
            # print(f"Processing asset {asset.original_filename} at {asset.stored_path}...")            
            # await asyncio.sleep(3)  # <---  simulting ocr or vision work
            # # ^^^ Replace with actual processing logic 

            # Adding OCR pipeline
            asset_path = Path(asset.stored_path)
            extracted_content = None

            # Apply OCR based on content
            if asset.content_type.startswith("image/"):
                logger.info(f"Extracting text from Image: {asset.original_filename}")
                extracted_content = await extract_from_media(asset_path)

            elif asset.content_type.startswith("pdf/"):
                logger.info(f"Extracting text from PDF: {asset.original_filename}")
                extracted_content = await extract_from_media(asset_path)
            
            # Store extracted content in new DB table
            if extracted_content:
                new_extracted = ExtractedContent(
                    asset_id=asset.id,
                    extracted_text=extracted_content.get("text"),
                    content_type=extracted_content.get("source"),  # 'tesseract' or 'pdfplumber'
                    extraction_metadata={
                        "pages": extracted_content.get("pages"),
                        "source": extracted_content.get("source"),
                        **extracted_content.get("metadata", {})
                    }
                )
                db.add(new_extracted)
                await db.commit()
                logger.info(f"Extracted content stored for asset {asset_id}")
            
            # Update Status to Ready

            logger.info(f"Extraction done! {extracted_content}")
            asset.processing_status = ProcessingStatus.READY
            await db.commit()

            # # Update status to READY
            # asset.processing_status = ProcessingStatus.READY
            # await db.commit()
            # print(f"Asset {asset_id} processed successfully.")
        
        except Exception as err:
            await db.rollback()
            print(f"Error processing asset {asset_id}: {err}")
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
