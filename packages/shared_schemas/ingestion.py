from pydantic import BaseModel

class IngestionResult(BaseModel):
    filename: str | None
    temp_path: str
    final_path: str
    sha256: str
    content_type: str