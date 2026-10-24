
from collections import defaultdict
from typing import Any, Dict, List, Tuple
from uuid import UUID

from .results import ActionResult, Finding, Severity, VerdictStatus


SEVERITY_RANK = {
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}


def aggregate_findings(
    results: List[ActionResult],
) -> List[Finding]:
    """
    Consolidate actionable ActionResults into Findings.

    PASS and NOT_APPLICABLE results remain available in the
    original ActionResult list but do not produce Findings.

    Results are grouped by finding type, subject, and status
    so conflicting statuses are never silently merged.
    """

    groups: Dict[
        Tuple[str, UUID | None, VerdictStatus],
        List[ActionResult],
    ] = defaultdict(list)

    for result in results:
        if result.status not in (
            VerdictStatus.FAIL,
            VerdictStatus.WARNING,
        ):
            continue

        key = (
            result.finding_type,
            result.subject_node_id,
            result.status,
        )
        groups[key].append(result)

    findings: List[Finding] = []

    for (finding_type, subject_id, status), group in groups.items():
        rule_ids = list(dict.fromkeys(
            result.rule_id for result in group
        ))

        related_node_ids = list(dict.fromkeys(
            node_id
            for result in group
            for node_id in result.related_node_ids
        ))

        evidence = list(dict.fromkeys(
            item
            for result in group
            for item in result.evidence
        ))

        # Retain measurements without silently overwriting conflicts.
        measurements = {}
        measurement_conflicts = {}

        for result in group:
            for name, value in result.measurements.items():
                if name not in measurements:
                    measurements[name] = value
                elif measurements[name] != value:
                    measurement_conflicts.setdefault(
                        name, [measurements[name]]
                    )
                    if value not in measurement_conflicts[name]:
                        measurement_conflicts[name].append(value)

        severities = [
            result.severity
            for result in group
            if result.severity is not None
        ]
        severity = (
            max(severities, key=lambda item: SEVERITY_RANK[item])
            if severities
            else None
        )

        metadata: Dict[str, Any] = {
            "source_metadata": [
                {
                    "rule_id": result.rule_id,
                    "metadata": result.metadata,
                }
                for result in group
            ]
        }

        if measurement_conflicts:
            metadata["measurement_conflicts"] = measurement_conflicts

        findings.append(
            Finding(
                finding_type=finding_type,
                status=status,
                severity=severity,
                subject_node_id=subject_id,
                related_node_ids=related_node_ids,
                rule_ids=rule_ids,
                measurements=measurements,
                evidence=evidence,
                metadata=metadata,
            )
        )

    return findings
