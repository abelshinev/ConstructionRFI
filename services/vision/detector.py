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
        # _detector_model = load_rf_detr_model()
        _detector_model = "RF-DETR Model Loaded"
        logger.info("Model loaded successfully.")
    else:
        logger.info("Model already in memory, reusing it.")
    return _detector_model

def run_detection(image_path: str):
    """Execute inference using `_detector_model`"""
    model = get_detector_model()

    # Run inference Code
    # results = model(image_path)

    return {
        "objects": [
            {"type": "helmet", "confidence": 0.92, "bbox": [10, 20, 50, 60]},
        ]
    }
