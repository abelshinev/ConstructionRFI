from pathlib import Path
from typing import Dict, Any
import whisper

import logging
logger = logging.getLogger(__name__)

async def transcribe_audio(audio_path: Path) -> Dict[str, Any]:
    """Transcribe audio to text using Whisper (for now).
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        {
            "transcript": str,
            "language": str,
            "duration": float,
            "source": "openai-whisper"
        }
    """
    try:
        model = whisper.load_model("small")  # Options: tiny, base, small, medium, large
        result = model.transcribe(str(audio_path))
        
        return {
            "transcript": result["transcript"],
            "language": result["language"],
            "segments": result["segments"],
            "source": "openai-whisper"
        }
    except Exception as e:
        logger.error(f"Transcription failed for {audio_path}: {e}")
        raise