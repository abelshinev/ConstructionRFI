from pathlib import Path
from ultralytics import RTDETR
import logging

logger = logging.getLogger(__name__)

# Global variable to hold model in memory 
_detector_model = None
_ppe_model = None
_acid_model = None
# Home of the RF-DETR detection model

def get_detector_model():
    """Lazy load model into memory once, reuse it for subsequent calls"""
    global _ppe_model, _acid_model
    if _ppe_model is None or _acid_model is None:
        logger.info("Loading RF-DETR model into memory...")

        # Simulate loading the model (replace with actual loading code)
        current_dir = Path(__file__).resolve().parent
        weights_dir = current_dir / "weights"

        ppe_path = weights_dir / "ppe_best.pt"
        acid_path = weights_dir / "acid_best.pt"

        if not ppe_path.exists() or not acid_path.exists():
            raise FileNotFoundError(f"Model weights not found. Ensure {ppe_path} and {acid_path} exists")
        
        logger.info("Loading PPE Model...")
        _ppe_model = RTDETR(str(ppe_path))
        
        logger.info("Loading ACID Equipment Model...")
        _acid_model = RTDETR(str(acid_path))
        
        logger.info("✅ Dual Models loaded successfully.")
    else:
        logger.debug("Models already in memory, reusing them.")

    return _ppe_model, _acid_model

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