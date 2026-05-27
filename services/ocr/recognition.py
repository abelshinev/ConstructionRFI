from pathlib import Path
from typing import Dict, Any
import pytesseract # for images
import pdfplumber # for pdfs
from PIL import Image

# check filetype
from services.ingestion.check_filetype import detect_mime_type

# logs
import logging
logger = logging.getLogger(__name__)

async def extract_from_media(media_path: Path) -> Dict[str, Any]:
    """Extract text from any form of media (images/PDFs) using OCR.
    
    Args:
        media_path: Path to the input file (image or PDF)
        
    Returns: 
        {
            "text": str,
            "source": str,
            "pages": int (PDFs only),
            "metadata": dict
        }
        
    Raises:
        ValueError: If file type unsupported
        Exception: If extraction fails
    """
    # Check file type (detect_mime_type is async)
    content_type = await detect_mime_type(media_path)

    if content_type.startswith("image/"):
        # Handle image files
        try:
            img = Image.open(media_path)
            text = pytesseract.image_to_string(img)
            return {
                "text": text,
                "source": "tesseract",
                "metadata": {}
            }
        except Exception as err:
            logger.error(f"OCR failed on image {media_path}: {err}")
            raise
    
    elif content_type == "application/pdf":
        # Handle PDF files
        try:
            full_text = []
            with pdfplumber.open(media_path) as pdf:
                for page in pdf.pages:
                    full_text.append(page.extract_text())
            return {
                "text": "\n".join(full_text),
                "pages": len(pdf.pages),
                "source": "pdfplumber",
                "metadata": {}
            }
        except Exception as err:
            logger.error(f"PDF extraction failed on {media_path}: {err}")
            raise
    
    else:
        error_msg = f"Unsupported file type: {content_type}"
        logger.error(error_msg)
        raise ValueError(error_msg)

