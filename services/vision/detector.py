from pathlib import Path
from ultralytics import RTDETR
import logging

logger = logging.getLogger(__name__)

# Global variable to hold model in memory 
_detector_model = None

# Home of the RF-DETR detection model

def get_detector_model():
    """Lazy load model into memory once, reuse it for subsequent calls"""
    global _detector_model
    if _detector_model is None:
        logger.info("Loading RF-DETR model into memory...")

        # Simulate loading the model (replace with actual loading code)
        cache_dir = Path("/ml-cache/ultralytics")

        if cache_dir.parent.exists():
            cache_dir.mkdir(parents=True, exist_ok=True)
            model_path = cache_dir / "rtdetr-l.pt"
        else:
            model_path = Path("rtdetr-l.pt")

        _detector_model = RTDETR(str(model_path))
        logger.info("Model loaded successfully.")
    else:
        logger.info("Model already in memory, reusing it.")

    return _detector_model

def run_detection(image_path: str | Path, confidence_threshold: float = 0.5) -> dict:
    """Execute inference using `_detector_model`"""
    model = get_detector_model()

    results = model(str(image_path), conf=confidence_threshold)[0] # [0] to get one image at a time [TEMP]

    detected_objects = []

    for box in results.boxes:
        class_id = int(box.cls[0])
        class_name = model.names[class_id]
        confidence = float(box.conf[0])

        bounding_box = box.xyxy[0].tolist()  # [x1, y1, x2, y2]

        detected_objects.append({
            "type": class_name,
            "confidence": confidence,
            "bounding_box": bounding_box
        })

    return {
        "model_used": "rtdetr-l",
        "objects": detected_objects,
    }