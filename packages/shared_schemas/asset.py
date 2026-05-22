from pydantic import BaseModel


""" 
    Let AssetResponse contain :
    1. filename
    2. the path to its storage 
    3. the hash (in sha cipher format)
    4. type of content
"""
class AssetResponse(BaseModel):
    filename: str
    stored_path: str
    sha256: str
    content_type: str