from typing import List
from packages.shared_schemas.graph import ContextGraph
from ..results import ActionResult, VerdictStatus
from ..rules import RelationshipOperator, Rule

def evaluate_relationship(
    graph: ContextGraph,
    rule: Rule,
) -> List[ActionResult]:

    condition = rule.condition

    if condition.relationship is None:
        raise ValueError(
            f"Relationship rule '{rule.rule_id}' "
            "requires a relationship."
        )

    if condition.relationship_operator is None:
        raise ValueError(
            f"Relationship rule '{rule.rule_id}' "
            "requires a relationship_operator."
        )

    if condition.related_node_type is None:
        raise ValueError(
            f"Relationship rule '{rule.rule_id}' "
            "requires a related_node_type."
        )

    relationship = condition.relationship
    operator = condition.relationship_operator
    related_type = condition.related_node_type

    if operator not in (
        RelationshipOperator.EXISTS,
        RelationshipOperator.NOT_EXISTS,
    ):
        raise ValueError(
            f"Unsupported relationship operator: {operator}"
        )

    results: List[ActionResult] = []

    # Evaluate each node to which this rule applies.
    for subject in graph.nodes.values():
        if subject.type != rule.target_node_type:
            continue

        matching_edges = []

        for edge in graph.edges:
            if edge.source != subject.id:
                continue

            if edge.relationship != relationship:
                continue

            related_node = graph.nodes.get(edge.target)

            if related_node is None:
                continue

            if related_node.type != related_type:
                continue

            matching_edges.append((edge, related_node))

        if matching_edges:
            # A confirmed relationship satisfies EXISTS
            # and violates NOT_EXISTS.
            status = (
                VerdictStatus.PASS
                if operator == RelationshipOperator.EXISTS
                else VerdictStatus.FAIL
            )

            for edge, related_node in matching_edges:
                results.append(
                    ActionResult(
                        rule_id=rule.rule_id,
                        finding_type=rule.finding_type,
                        status=status,
                        severity=rule.severity,
                        subject_node_id=subject.id,
                        related_node_ids=[related_node.id],
                        measurements=edge.measurements,
                        evidence=[
                            (
                                f"{subject.type.value} "
                                f"{relationship.value} "
                                f"{related_node.type.value}"
                            )
                        ],
                        metadata={
                            "relationship": relationship.value,
                            "relationship_operator": operator.value,
                            "evaluation_state": "DETERMINED",
                            "condition_satisfied": (
                                operator == RelationshipOperator.EXISTS
                            ),
                        },
                    )
                )

        else:
            # No edge is not proof of absence.
            results.append(
                ActionResult(
                    rule_id=rule.rule_id,
                    finding_type=rule.finding_type,
                    status=VerdictStatus.WARNING,
                    severity=rule.severity,
                    subject_node_id=subject.id,
                    evidence=[],
                    metadata={
                        "relationship": relationship.value,
                        "relationship_operator": operator.value,
                        "evaluation_state": "INCONCLUSIVE",
                        "condition_satisfied": None,
                        "reason": "RELATIONSHIP_NOT_OBSERVED",
                    },
                )
            )

    return results
