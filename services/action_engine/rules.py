from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel

from packages.shared_schemas.ontology import NodeType, RelationshipType

from .results import Severity


class ConditionType(str, Enum):
    PROPERTY = "PROPERTY"
    RELATIONSHIP = "RELATIONSHIP"
    MEASUREMENT = "MEASUREMENT"


class ComparisonOperator(str, Enum):
    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"
    GREATER_THAN = "GREATER_THAN"
    GREATER_THAN_OR_EQUAL = "GREATER_THAN_OR_EQUAL"
    LESS_THAN = "LESS_THAN"
    LESS_THAN_OR_EQUAL = "LESS_THAN_OR_EQUAL"


class RelationshipOperator(str, Enum):
    EXISTS = "EXISTS"
    NOT_EXISTS = "NOT_EXISTS"


class RuleCondition(BaseModel):
    type: ConditionType

    # Property / measurement comparisons
    operator: Optional[ComparisonOperator] = None
    expected_value: Optional[Any] = None

    # Property conditions
    property_name: Optional[str] = None

    # Relationship conditions
    related_node_type: Optional[NodeType] = None
    relationship: Optional[RelationshipType] = None
    relationship_operator: Optional[RelationshipOperator] = None

    # Measurement conditions
    measurement_name: Optional[str] = None
    threshold: Optional[float] = None
    unit: Optional[str] = None


class Rule(BaseModel):
    """
    Declarative requirement that can be evaluated against
    the current Context Graph.
    """

    rule_id: str
    finding_type: str
    severity: Severity

    target_node_type: NodeType

    condition: RuleCondition