from pydantic import BaseModel
from datetime import datetime

from .enums import AssetEvent

class WorkerEvent(BaseModel):
    """Worker event is format for workers that need to communicate. Using typed events,
    workers can be assigned to listen to specific events as triggers. They can respond on trigger
    """
    event_type: AssetEvent

    asset_id: str

    correlation_id: str

    created_at: datetime

    payload: dict