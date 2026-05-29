from enum import Enum


class WorkerType(str, Enum):
    IMAGE = "image"
    VISION = "vision"
    OCR = "ocr"
    SPEECH = "speech"


class WorkerStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class AssetEvent(str, Enum):
    ASSET_UPLOADED = "asset.uploaded"
    IMAGE_READY = "asset.image.ready"
    AUDIO_READY = "asset.audio.ready"


class AssetProcessingState(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    PARTIAL_READY = "PARTIAL_READY"
    FAILED = "FAILED"