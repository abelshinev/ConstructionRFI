from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from .enums import WorkerType


class WorkerInput(BaseModel):
    asset_id: str
    worker_type: WorkerType

    stored_path: str
    content_type: str

    correlation_id: str

    created_at: datetime

    retry_count: int = 0

    metadata: Optional[dict] = None