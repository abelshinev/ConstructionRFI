from typing import List

from packages.shared_schemas.graph import ContextGraph

from .results import ActionResult, VerdictStatus
from .rules import ConditionType, Operator, Rule

class ActionEngine:

    def __init__(self, rules: List[Rule]):
        self.rules = rules

    def evaluate(self, graph: ContextGraph) -> List[ActionResult]:
        results = []

        for rule in self.rules:
            results.extend(
                self._evaluate_rule(graph, rule)
            )

        return results

    def _evaluate_property_rule(
        self,
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

            if condition.operator.value == "EQUALS":
                passed = actual_value == condition.expected_value

            elif condition.operator.value == "NOT_EQUALS":
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
                    subject_node_id=node_id,
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

    def _evaluate_rule(self, graph: ContextGraph, rule: Rule,) -> List[ActionResult]:

        if rule.condition.type == ConditionType.PROPERTY:
            return self._evaluate_property_rule(graph, rule)

        if rule.condition.type == ConditionType.MEASUREMENT:
            return self._evaluate_measurement_rule(graph, rule)

        if rule.condition.type == ConditionType.RELATIONSHIP:
            return self._evaluate_relationship_rule(graph, rule)

        raise ValueError(
            f"Unsupported condition type: {rule.condition.type}"
        )