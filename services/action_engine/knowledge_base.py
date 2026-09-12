from packages.shared_schemas.ontology import NodeType
from packages.shared_schemas.ontology import NodeType, RelationshipType

from .results import Severity
from .rules import (
    ComparisonOperator,
    ConditionType,
    RelationshipOperator,
    Rule,
    RuleCondition,
)


SAMPLE_KNOWLEDGE_BASE = [
    Rule(
        rule_id="PPE_HELMET_REQUIRED",
        finding_type="PPE_NON_COMPLIANCE",
        severity=Severity.HIGH,
        target_node_type=NodeType.WORKER,
        condition=RuleCondition(
            type=ConditionType.PROPERTY,
            property_name="helmet",
            operator=ComparisonOperator.EQUALS,
            expected_value=True,
        ),
    ),

    Rule(
        rule_id="PPE_VEST_REQUIRED",
        finding_type="PPE_NON_COMPLIANCE",
        severity=Severity.HIGH,
        target_node_type=NodeType.WORKER,
        condition=RuleCondition(
            type=ConditionType.PROPERTY,
            property_name="vest",
            operator=ComparisonOperator.EQUALS,
            expected_value=True,
        ),
    ),
        Rule(
        rule_id="EQUIPMENT_CLEARANCE_TEST",
        finding_type="EQUIPMENT_PROXIMITY",
        severity=Severity.HIGH,
        target_node_type=NodeType.WORKER,
        condition=RuleCondition(
            type=ConditionType.MEASUREMENT,
            related_node_type=NodeType.EQUIPMENT,
            relationship=RelationshipType.NEAR,
            measurement_name="distance_pixels",
            operator=ComparisonOperator.GREATER_THAN_OR_EQUAL,
            threshold=100.0,
            unit="pixels",
        ),
    ),
        Rule(
        rule_id="EQUIPMENT_PROXIMITY_TEST",
        finding_type="EQUIPMENT_PROXIMITY",
        severity=Severity.HIGH,
        target_node_type=NodeType.WORKER,
        condition=RuleCondition(
            type=ConditionType.RELATIONSHIP,
            related_node_type=NodeType.EQUIPMENT,
            relationship=RelationshipType.NEAR,
            relationship_operator=RelationshipOperator.EXISTS,
        ),
    ),
]