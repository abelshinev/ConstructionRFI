from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict

from .enums import WorkerType, WorkerStatus

"""FORMAT FOR CELERY'S TASK INFERENCE OUTPUT """
class WorkerOutput(BaseModel):
    asset_id: str

    worker_type: WorkerType

    status: WorkerStatus

    confidence: float = Field(ge=0.0, le=1.0)

    data: Dict[str, Any]

    processing_time_ms: int

    correlation_id: str

    created_at: datetime