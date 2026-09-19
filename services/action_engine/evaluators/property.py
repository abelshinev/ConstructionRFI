from typing import List
from packages.shared_schemas.graph import ContextGraph
from ..results import ActionResult, VerdictStatus
from ..rules import ConditionType, ComparisonOperator, RelationshipOperator, Rule

def evaluate_property(
        graph: ContextGraph,
        rule: Rule,
    ) -> List[ActionResult]:

        results = []

        condition = rule.condition

        if condition.property_name is None:
            raise ValueError(
                f"Property rule '{rule.rule_id}' requires a property_name."
            )

        for node_id, node in graph.nodes.items():

            if node.type != rule.target_node_type:
                continue

            actual_value = getattr(
                node.properties,
                condition.property_name,
                None
            )

            if condition.operator is None:
                raise ValueError(
                    f"Property rule '{rule.rule_id}' requires an operator."
                )

            if condition.operator == ComparisonOperator.EQUALS:
                passed = actual_value == condition.expected_value

            elif condition.operator == ComparisonOperator.NOT_EQUALS:
                passed = actual_value != condition.expected_value

            else:
                raise ValueError(
                    f"Unsupported operator for property rule: "
                    f"{condition.operator}"
                )
            results.append(
                ActionResult(
                    rule_id=rule.rule_id,
                    finding_type=rule.finding_type,
                    status=(
                        VerdictStatus.PASS
                        if passed
                        else VerdictStatus.FAIL
                    ),
                    severity=rule.severity,
                    subject_node_id=node_id, # uncomment after testing
                    evidence=[
                        f"{condition.property_name}={actual_value}"
                    ],
                    metadata={
                        "expected_value": condition.expected_value,
                        "actual_value": actual_value,
                        "operator": condition.operator.value,
                    },
                )
            )

        return results