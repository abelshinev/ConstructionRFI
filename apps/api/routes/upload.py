from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import logging
from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path

from services.ingestion.pipeline import ingest_file
from storage.database.models import Asset, ProcessingStatus
from packages.shared_schemas.worker_input import WorkerInput
from packages.shared_schemas.enums import WorkerType
from apps.api.dependencies import get_db
from apps.worker.main import process_asset_task

logger = logging.getLogger(__name__)
router = APIRouter()

# upload functionality
@router.post("/upload")
async def upload(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """Upload and ingest a file (image or PDF).
    
    Args:
        file: File to upload
        
    Returns:
        AssetResponse with file metadata
        
    Raises:
        400: Invalid file type or duplicate file
        500: Server error (DB, file I/O, etc.)
    """
    try:
        asset_response = await ingest_file(file)
    
    except ValueError as e:
        logger.warning(f"Upload validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    temp_path = Path(asset_response.temp_path)
    final_path = Path(asset_response.final_path)

    try:

        # Insert row into DB with status 'PENDING
        new_asset = Asset(
            sha256=asset_response.sha256,
            original_filename=asset_response.filename,
            stored_path=asset_response.final_path,
            content_type=asset_response.content_type,
            processing_status=ProcessingStatus.PENDING
        )
        db.add(new_asset)
        await db.commit()
        await db.refresh(new_asset)

        # Pipeline Logic Moved here

        if not final_path.exists():
            temp_path.rename(final_path) # Wrap with try/except and set processing_status to FAILED on error
        else:
            temp_path.unlink(missing_ok=True) # Edge case: File already on disk

        payload = WorkerInput(
            asset_id=new_asset.id,
            worker_type=WorkerType.IMAGE,
            stored_path=new_asset.stored_path,
            content_type=new_asset.content_type,
            correlation_id=str(uuid4()),
            created_at=datetime.now(timezone.utc)
        )

        process_asset_task.delay(payload.model_dump()) # Uses Schematic input validation 

        return {
            "id": new_asset.id,
            "status": new_asset.processing_status,
            "message": "File ingested and queued for processing"
        }

    except IntegrityError:
        # Hash already exists in DB
        await db.rollback()
        temp_path.unlink(missing_ok=True)
        logger.warning(f"Duplicate upload attempt for hash: {asset_response.sha256}")
        raise HTTPException(status_code=409, detail="File already exists.")
    
    except Exception as e:
        # Unexpected errors (DB connection, file I/O, etc.)
        temp_path.unlink(missing_ok=True)
        logger.error(f"Upload failed with unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="File upload failed")