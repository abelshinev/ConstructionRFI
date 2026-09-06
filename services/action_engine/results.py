from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class VerdictStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ActionResult(BaseModel):
    """
    Deterministic result produced by the Action / Verdict Engine.

    This object describes WHAT the engine determined,
    not HOW that determination should be communicated.
    """

    rule_id: str
    finding_type: str

    status: VerdictStatus
    severity: Optional[Severity] = None

    subject_node_id: Optional[UUID] = None
    related_node_ids: List[UUID] = Field(default_factory=list)

    measurements: Dict[str, Any] = Field(default_factory=dict)

    evidence: List[str] = Field(default_factory=list)

    metadata: Dict[str, Any] = Field(default_factory=dict)