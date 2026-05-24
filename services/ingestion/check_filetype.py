import magic
from pathlib import Path


async def detect_mime_type(path: Path) -> str:
    return magic.from_file(str(path), mime=True)