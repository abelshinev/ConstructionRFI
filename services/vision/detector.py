from pathlib import Path
from ultralytics import YOLO, RTDETR
import logging

logger = logging.getLogger(__name__)

# Global variable to hold model in memory 
_detector_model = None
_ppe_model = None
_acid_model = None
# Home of the RF-DETR detection model

def get_models():
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
        _ppe_model = YOLO(str(ppe_path))
        
        logger.info("Loading ACID Equipment Model...")
        _acid_model = RTDETR(str(acid_path))
        
        logger.info("✅ Dual Models loaded successfully.")
    else:
        logger.debug("Models already in memory, reusing them.")

    return _ppe_model, _acid_model

def run_detection(image_path: str | Path, conf_ppe: float = 0.25, conf_acid: float = 0.25) -> dict:
    """Execute inference using `_detector_model`"""
    ppe_model, acid_model = get_models()

    ppe_results = ppe_model(str(image_path), conf=conf_ppe, imgsz=640, verbose=False)[0]    
    acid_results = acid_model(str(image_path), conf=conf_acid, imgsz=640, verbose=False)[0] # [0] to get one image at a time [TEMP]

    detected_ppe = []
    detected_equipment = []

    # Parse YOLO native PPE logic
    for box in ppe_results.boxes:
        class_id = int(box.cls[0].item())
        detected_ppe.append({
            "type": ppe_model.names.get(class_id, f"unknown {class_id}"),
            "confidence": float(box.conf[0].item()),
            "bounding_box": box.xyxy[0].tolist()  # [x1, y1, x2, y2]
        })

    # Parse RTDETR ACID logic
    for box in acid_results.boxes:
        class_id = int(box.cls[0].item())
        detected_equipment.append({
            "type": acid_model.names.get(class_id, f"unknown {class_id}"),
            "confidence": float(box.conf[0].item()),
            "bounding_box": box.xyxy[0].tolist()
        })

    return {
        "models_used": ["ppe_rtdetr-l", "acid_rtdetr-l"],
        "ppe_objects": detected_ppe,
        "equipment_objects": detected_equipment
    }