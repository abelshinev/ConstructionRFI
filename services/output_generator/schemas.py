
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from services.action_engine.results import Severity, VerdictStatus


class FindingReference(BaseModel):
    """Traceability back to the Action / Verdict Engine."""

    finding_type: str
    status: VerdictStatus
    severity: Optional[Severity] = None

    subject_node_id: Optional[UUID] = None
    related_node_ids: List[UUID] = Field(default_factory=list)

    rule_ids: List[str] = Field(default_factory=list)
    measurements: Dict[str, Any] = Field(default_factory=dict)
    evidence: List[str] = Field(default_factory=list)


class GeneratedOutput(BaseModel):
    """Structured output prepared for an RFI or compliance report."""

    output_type: str
    title: str
    summary: str

    finding: FindingReference

    recommended_action: Optional[str] = None
    clarification_questions: List[str] = Field(default_factory=list)

    metadata: Dict[str, Any] = Field(default_factory=dict)
