from pydantic import BaseModel
from datetime import datetime

from .enums import AssetEvent


class WorkerEvent(BaseModel):
    event_type: AssetEvent

    asset_id: str

    correlation_id: str

    created_at: datetime

    payload: dict