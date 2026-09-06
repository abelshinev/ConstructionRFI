from typing import List

from packages.shared_schemas.graph import ContextGraph
from packages.shared_schemas.ontology import NodeType

from .results import ActionResult, VerdictStatus
from .rules import Rule


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

    def _evaluate_rule(
        self,
        graph: ContextGraph,
        rule: Rule,
    ) -> List[ActionResult]:

        results = []

        for node_id, node in graph.nodes.items():

            if node.type != rule.target_node_type:
                continue

            if not rule.property_name:
                continue

            actual_value = getattr(
                node.properties,
                rule.property_name,
                None
            )

            if actual_value == rule.expected_value:
                status = VerdictStatus.PASS
            else:
                status = VerdictStatus.FAIL

            results.append(
                ActionResult(
                    rule_id=rule.rule_id,
                    finding_type=rule.finding_type,
                    status=status,
                    severity=rule.severity,
                    subject_node_id=node_id,
                    evidence=[
                        f"{rule.property_name}={actual_value}"
                    ],
                    metadata={
                        "expected_value": rule.expected_value,
                        "actual_value": actual_value,
                    },
                )
            )

        return results