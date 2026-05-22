from uuid import uuid4
from pathlib import Path
from fastapi import UploadFile

# import cipher, paths, filetype detection and api response
from services.ingestion.hashing import sha256_file
from services.ingestion.storage import (
    IMAGE_DIR,
    PDF_DIR,
    TEMP_DIR,
    save_temp_file,
)
from services.ingestion.check_filetype import detect_mime_type
from packages.shared_schemas.asset import AssetResponse


# import logs
import logging
logger = logging.getLogger(__name__)

# Then use it in functions:


# define extension map to store images and pdfs accordingly
EXTENSION_MAP = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "application/pdf": ".pdf",
}

"""
Let there be an ingest file function : 
file -> res {
    filename: str
    path: str
    sha256: hash
    content: img / pdf

}
"""

def ingest_file(upload_file: UploadFile):
    """Used to process and store a given file.
    Args:
        upload_file: File uploaded -> treated as an object
    Returns:
        AssetResponse with filled fields and storage path
    Raises:
        ValueError: To show presence of unsupported filetypes
    """
    # create temp path : file -> TEMP_DIR/random_uuid4
    temp_filename = str(uuid4())
    temp_path = TEMP_DIR / temp_filename

    # save the file at the temp_path
    save_temp_file(upload_file, temp_path)
    logger.info(f"TEMP EXISTS AFTER SAVE: {temp_path.exists()}")

    # detect MIME -> file = img/pdf
    content_type = detect_mime_type(temp_path)

    print("DETECTED MIME:", content_type)

    """ 
    do file-type validation : 
        IF img -> store in img_dir / pdf -> store in pdf_dir, 
        ELSE:  show unsupporte filetype 
    """
    if content_type.startswith("image/"):
        save_dir = IMAGE_DIR

    elif content_type == "application/pdf":
        save_dir = PDF_DIR

    else:
        logger.error("Failed to save file -> unsupported file type")
        temp_path.unlink(missing_ok=True)
        raise ValueError("Unsupported file type")
        

    # compute sha256 hash on the file
    file_hash = sha256_file(temp_path)

    """ 
    check file extension :
        IF not  in extension map -> remove file from temp storage
    """
    extension = EXTENSION_MAP.get(content_type)

    if extension is None:
        temp_path.unlink(missing_ok=True)
        logger.error("Failed to save file -> unsupported file extension")
        raise ValueError("Unsupported extension")

    # save final path
    final_path = save_dir / f"{file_hash}{extension}"

    print("FINAL PATH:", final_path)

    # check for duplicates using the final path -> if exists, then unlink
    if not final_path.exists():
        temp_path.rename(final_path)
    else:
        logger.info(f"Found duplicate for file {final_path}")
        temp_path.unlink(missing_ok=True)

    return AssetResponse(
        filename=upload_file.filename,
        stored_path=str(final_path),
        sha256=file_hash,
        content_type=content_type,
    )