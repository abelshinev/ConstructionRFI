from typing import List

from packages.shared_schemas.graph import ContextGraph

from .results import ActionResult, VerdictStatus
from .rules import ConditionType, ComparisonOperator, RelationshipOperator, Rule

from .evaluators.property import evaluate_property
from .evaluators.measurement import evaluate_measurement
from .evaluators.relationship import evaluate_relationship

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

    
    def _evaluate_rule(self, graph: ContextGraph, rule: Rule,) -> List[ActionResult]:

        if rule.condition.type == ConditionType.PROPERTY:
            return evaluate_property(graph, rule)

        if rule.condition.type == ConditionType.MEASUREMENT:
            return evaluate_measurement(graph, rule)

        if rule.condition.type == ConditionType.RELATIONSHIP:
            return evaluate_relationship(graph, rule)

        raise ValueError(
            f"Unsupported condition type: {rule.condition.type}"
        )