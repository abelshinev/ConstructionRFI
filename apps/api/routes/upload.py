from fastapi import APIRouter, UploadFile, File, HTTPException

from services.ingestion.pipeline import ingest_file

router = APIRouter()

# upload functionality
@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        return ingest_file(file)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))