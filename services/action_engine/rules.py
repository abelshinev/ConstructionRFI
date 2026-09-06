from typing import Optional

from pydantic import BaseModel

from packages.shared_schemas.ontology import NodeType

from .results import ActionResult, Severity, VerdictStatus


class Rule(BaseModel):
    """
    A deterministic rule describing a condition that can be evaluated
    against the Context Graph.
    """

    rule_id: str
    finding_type: str
    severity: Severity

    target_node_type: NodeType

    property_name: Optional[str] = None
    expected_value: Optional[object] = None

# TESTING ONLY! Should be deleted and replaced with the real guidelines
SAMPLE_KNOWLEDGE_BASE = [
    Rule(
        rule_id="PPE_HELMET_REQUIRED",
        finding_type="PPE_NON_COMPLIANCE",
        severity=Severity.HIGH,
        target_node_type=NodeType.WORKER,
        property_name="helmet",
        expected_value=True,
    ),
    Rule(
        rule_id="PPE_VEST_REQUIRED",
        finding_type="PPE_NON_COMPLIANCE",
        severity=Severity.HIGH,
        target_node_type=NodeType.WORKER,
        property_name="vest",
        expected_value=True,
    ),
]