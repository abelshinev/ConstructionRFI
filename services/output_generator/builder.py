
from typing import List

from services.action_engine.results import Finding, VerdictStatus

from .schemas import FindingReference, GeneratedOutput


def build_outputs(findings: List[Finding]) -> List[GeneratedOutput]:
    """Convert actionable findings into structured output records."""

    outputs: List[GeneratedOutput] = []

    for finding in findings:
        if finding.status not in (
            VerdictStatus.FAIL,
            VerdictStatus.WARNING,
        ):
            continue

        title = finding.finding_type.replace("_", " ").title()

        if finding.status == VerdictStatus.FAIL:
            summary = (
                f"A {finding.finding_type.replace('_', ' ').lower()} "
                "has failed its configured rule check."
            )
        else:
            summary = (
                f"A {finding.finding_type.replace('_', ' ').lower()} "
                "requires further review because the result is inconclusive "
                "or indicates a potential issue."
            )

        reference = FindingReference(
            finding_type=finding.finding_type,
            status=finding.status,
            severity=finding.severity,
            subject_node_id=finding.subject_node_id,
            related_node_ids=finding.related_node_ids,
            rule_ids=finding.rule_ids,
            measurements=finding.measurements,
            evidence=finding.evidence,
        )

        outputs.append(
            GeneratedOutput(
                output_type="RFI",
                title=title,
                summary=summary,
                finding=reference,
                metadata={
                    "generation_mode": "deterministic",
                },
            )
        )

    return outputs
