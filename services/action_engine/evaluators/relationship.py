from typing import List
from packages.shared_schemas.graph import ContextGraph
from ..results import ActionResult, VerdictStatus
from ..rules import ConditionType, ComparisonOperator, RelationshipOperator, Rule

def evaluate_relationship(
        graph: ContextGraph,
        rule: Rule,
    ) -> List[ActionResult]:

        results = []

        condition = rule.condition

        if condition.relationship is None:
            raise ValueError(
                f"Relationship rule '{rule.rule_id}' "
                f"requires a relationship."
            )

        if condition.relationship_operator is None:
            raise ValueError(
                f"Relationship rule '{rule.rule_id}' "
                f"requires a relationship_operator."
            )

        if condition.related_node_type is None:
            raise ValueError(
                f"Relationship rule '{rule.rule_id}' "
                f"requires a related_node_type."
            )

        relationship = condition.relationship
        relationship_operator = condition.relationship_operator
        related_node_type = condition.related_node_type

        if relationship_operator == RelationshipOperator.EXISTS:

            for edge in graph.edges:

                if edge.relationship != relationship:
                    continue

                source_node = graph.nodes.get(edge.source)
                target_node = graph.nodes.get(edge.target)

                if source_node is None or target_node is None:
                    continue

                if source_node.type != rule.target_node_type:
                    continue

                if target_node.type != related_node_type:
                    continue

                results.append(
                    ActionResult(
                        rule_id=rule.rule_id,
                        finding_type=rule.finding_type,
                        status=VerdictStatus.FAIL,
                        severity=rule.severity,
                        subject_node_id=edge.source,
                        related_node_ids=[edge.target],
                        measurements=edge.measurements,
                        evidence=[
                            (
                                f"{source_node.type.value} "
                                f"{relationship.value} "
                                f"{target_node.type.value}"
                            )
                        ],
                        metadata={
                            "relationship": relationship.value,
                            "relationship_operator": (
                                relationship_operator.value
                            ),
                        },
                    )
                )

            return results