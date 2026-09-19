from typing import List
from packages.shared_schemas.graph import ContextGraph
from ..results import ActionResult, VerdictStatus
from ..rules import ConditionType, ComparisonOperator, RelationshipOperator, Rule

def evaluate_measurement(
        graph: ContextGraph,
        rule: Rule,
    ) -> List[ActionResult]:

        results = []

        condition = rule.condition

        if condition.measurement_name is None:
            raise ValueError(
                f"Measurement rule '{rule.rule_id}' "
                f"requires a measurement_name."
            )

        if condition.threshold is None:
            raise ValueError(
                f"Measurement rule '{rule.rule_id}' "
                f"requires a threshold."
            )

        if condition.relationship is None:
            raise ValueError(
                f"Measurement rule '{rule.rule_id}' "
                f"requires a relationship."
            )

        for edge in graph.edges:

            if edge.relationship != condition.relationship:
                continue

            source_node = graph.nodes.get(edge.source)
            target_node = graph.nodes.get(edge.target)

            if source_node is None or target_node is None:
                continue

            # The rule defines which node is the subject.
            if source_node.type != rule.target_node_type:
                continue

            # If the rule specifies a related node type,
            # make sure the edge points to that type.
            if (
                condition.related_node_type is not None
                and target_node.type != condition.related_node_type
            ):
                continue

            if condition.measurement_name not in edge.measurements:
                continue

            actual_value = edge.measurements[
                condition.measurement_name
            ]

            if condition.operator is None:
                raise ValueError(
                    f"Measurement rule '{rule.rule_id}' requires an operator."
                )

            if condition.operator == ComparisonOperator.GREATER_THAN:
                passed = actual_value > condition.threshold

            elif condition.operator == ComparisonOperator.GREATER_THAN_OR_EQUAL:
                passed = actual_value >= condition.threshold

            elif condition.operator == ComparisonOperator.LESS_THAN:
                passed = actual_value < condition.threshold

            elif condition.operator == ComparisonOperator.LESS_THAN_OR_EQUAL:
                passed = actual_value <= condition.threshold

            elif condition.operator == ComparisonOperator.EQUALS:
                passed = actual_value == condition.threshold

            elif condition.operator == ComparisonOperator.NOT_EQUALS:
                passed = actual_value != condition.threshold

            else:
                raise ValueError(
                    f"Unsupported operator for measurement rule: "
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
                    subject_node_id=edge.source,
                    related_node_ids=[edge.target],
                    measurements={
                        "observed_value": actual_value,
                        "required_value": condition.threshold,
                        "unit": condition.unit,
                    },
                    evidence=[
                        (
                            f"{condition.measurement_name}="
                            f"{actual_value}"
                        )
                    ],
                    metadata={
                        "operator": condition.operator.value,
                        "relationship": edge.relationship.value,
                    },
                )
            )

        return results

    