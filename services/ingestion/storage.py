from pathlib import Path
import shutil

BASE_STORAGE = Path("storage")

# store directory paths
RAW_DIR = BASE_STORAGE / "raw"
TEMP_DIR = BASE_STORAGE / "temp"
IMAGE_DIR = RAW_DIR / "images"
PDF_DIR = RAW_DIR / "pdfs"

# create directories if needed
IMAGE_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)


# save the file according to destination directory
def save_temp_file(upload_file, destination: Path):
    """Used to save the file in destination directory
    Args:
        upload_file: File uploaded -> treated as an object
        destination: Path to the designated directory where the file has to be stored
    Returns:
       None
    """
    with open(destination, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)