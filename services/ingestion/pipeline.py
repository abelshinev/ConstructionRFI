from uuid import uuid4
from pathlib import Path


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
def ingest_file(upload_file):

    # create temp path : file -> TEMP_DIR/random_uuid4
    temp_filename = str(uuid4())
    temp_path = TEMP_DIR / temp_filename

    print("TEMP PATH:", temp_path)

    # save the file at the temp_path
    save_temp_file(upload_file, temp_path)

    print("TEMP EXISTS AFTER SAVE:", temp_path.exists())

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
        raise ValueError("Unsupported extension")

    # save final path
    final_path = save_dir / f"{file_hash}{extension}"

    print("FINAL PATH:", final_path)

    # check for duplicates using the final path -> if exists, then unlink
    if not final_path.exists():
        temp_path.rename(final_path)
    else:
        temp_path.unlink(missing_ok=True)

    # generate response
    return AssetResponse(
        filename=upload_file.filename,
        stored_path=str(final_path),
        sha256=file_hash,
        content_type=content_type,
    )