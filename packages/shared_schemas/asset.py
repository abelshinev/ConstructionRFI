from pydantic import BaseModel
from fastapi import UploadFile

""" 
    Let AssetResponse contain :
    1. filename
    2. the path to its storage 
    3. the hash (in sha cipher format)
    4. type of content
"""
class AssetResponse(BaseModel):
    filename: str | None
    stored_path: str
    sha256: str
    content_type: str