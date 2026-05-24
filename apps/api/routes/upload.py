from fastapi import APIRouter, UploadFile, File, HTTPException
import logging

from services.ingestion.pipeline import ingest_file

logger = logging.getLogger(__name__)
router = APIRouter()

# upload functionality
@router.post("/upload")
async def upload(file: UploadFile = File(...)):
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
        return await ingest_file(file)

    except ValueError as e:
        # File validation errors
        logger.warning(f"Upload validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # Unexpected errors (DB connection, file I/O, etc.)
        logger.error(f"Upload failed with unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="File upload failed")