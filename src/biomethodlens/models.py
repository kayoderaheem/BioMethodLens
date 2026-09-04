"""Domain models and dependency-free semantic validation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional


SEVERITY_ORDER = {"critical": 0, "major": 1, "moderate": 2, "minor": 3}
ALLOWED_SEVERITIES = frozenset(SEVERITY_ORDER)
ALLOWED_CONFIDENCE = frozenset({"high", "medium", "low"})
ALLOWED_STATUS = frozenset({"ok", "partial", "cannot_verify", "failed"})
ALLOWED_ASSESSMENT = frozenset({"supported", "partially_supported", "unsupported", "cannot_verify"})
ALLOWED_VERIFICATION = frozenset({"verified", "cannot_verify", "not_applicable"})
ALLOWED_SOURCE_TYPES = frozenset({"manuscript", "external", "calculation", "data_artifact"})


class ValidationError(ValueError):
    """Raised when a reviewer result violates the semantic contract."""

    def __init__(self, errors: Iterable[str]):
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


@dataclass(frozen=True)
class Evidence:
    source_type: str
    locator: str
    excerpt: str
    note: str
    url: Optional[str] = None

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "Evidence":
        return cls(
            source_type=str(value.get("source_type", "")),
            locator=str(value.get("locator", "")),
            excerpt=str(value.get("excerpt", "")),
            note=str(value.get("note", "")),
            url=value.get("url"),
        )


@dataclass(frozen=True)
class Finding:
    id: str
    reviewer_id: str
    title: str
    category: str
    severity: str
    confidence: str
    assessment: str
    claim: str
    location: str
    rationale: str
    impact: str
    recommendation: str
    verification_status: str
    evidence: List[Evidence] = field(default_factory=list)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any], reviewer_id: str) -> "Finding":
        return cls(
            id=str(value.get("id", "")),
            reviewer_id=reviewer_id,
            title=str(value.get("title", "")),
            category=str(value.get("category", "")),
            severity=str(value.get("severity", "")),
            confidence=str(value.get("confidence", "")),
            assessment=str(value.get("assessment", "")),
            claim=str(value.get("claim", "")),
            location=str(value.get("location", "")),
            rationale=str(value.get("rationale", "")),
            impact=str(value.get("impact", "")),
            recommendation=str(value.get("recommendation", "")),
            verification_status=str(value.get("verification_status", "")),
            evidence=[Evidence.from_dict(item) for item in value.get("evidence", [])],
        )

    def fingerprint(self) -> str:
        """Return a conservative normalization key for exact-topic duplicates."""
        text = " ".join((self.category, self.title, self.claim, self.location)).lower()
        return re.sub(r"[^a-z0-9]+", " ", text).strip()


@dataclass(frozen=True)
class ReviewResult:
    reviewer_id: str
    paper_id: str
    status: str
    scope_summary: str
    findings: List[Finding]
    limitations: List[str]

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ReviewResult":
        reviewer_id = str(value.get("reviewer_id", ""))
        result = cls(
            reviewer_id=reviewer_id,
            paper_id=str(value.get("paper_id", "")),
            status=str(value.get("status", "")),
            scope_summary=str(value.get("scope_summary", "")),
            findings=[Finding.from_dict(item, reviewer_id) for item in value.get("findings", [])],
            limitations=[str(item) for item in value.get("limitations", [])],
        )
        validate_review_result(result)
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reviewer_id": self.reviewer_id,
            "paper_id": self.paper_id,
            "status": self.status,
            "scope_summary": self.scope_summary,
            "findings": [
                {
                    "id": item.id,
                    "title": item.title,
                    "category": item.category,
                    "severity": item.severity,
                    "confidence": item.confidence,
                    "assessment": item.assessment,
                    "claim": item.claim,
                    "location": item.location,
                    "evidence": [
                        {
                            "source_type": source.source_type,
                            "locator": source.locator,
                            "excerpt": source.excerpt,
                            "note": source.note,
                            "url": source.url,
                        }
                        for source in item.evidence
                    ],
                    "rationale": item.rationale,
                    "impact": item.impact,
                    "recommendation": item.recommendation,
                    "verification_status": item.verification_status,
                }
                for item in self.findings
            ],
            "limitations": list(self.limitations),
        }


def validate_review_result(result: ReviewResult) -> None:
    errors: List[str] = []
    if not result.reviewer_id.strip():
        errors.append("reviewer_id must not be empty")
    if not result.paper_id.strip():
        errors.append("paper_id must not be empty")
    if result.status not in ALLOWED_STATUS:
        errors.append("status is not recognized")
    if not result.scope_summary.strip():
        errors.append("scope_summary must not be empty")

    seen = set()
    for index, finding in enumerate(result.findings):
        label = "finding[{}]".format(index)
        for name in ("id", "title", "category", "rationale", "impact", "recommendation"):
            if not getattr(finding, name).strip():
                errors.append("{}.{} must not be empty".format(label, name))
        if finding.id in seen:
            errors.append("duplicate finding id: {}".format(finding.id))
        seen.add(finding.id)
        if finding.reviewer_id != result.reviewer_id:
            errors.append("{}.reviewer_id does not match the result".format(label))
        if finding.severity not in ALLOWED_SEVERITIES:
            errors.append("{}.severity is not recognized".format(label))
        if finding.confidence not in ALLOWED_CONFIDENCE:
            errors.append("{}.confidence is not recognized".format(label))
        if finding.assessment not in ALLOWED_ASSESSMENT:
            errors.append("{}.assessment is not recognized".format(label))
        if finding.verification_status not in ALLOWED_VERIFICATION:
            errors.append("{}.verification_status is not recognized".format(label))
        if finding.verification_status == "verified" and not finding.evidence:
            errors.append("{}.evidence is required for a verified finding".format(label))
        if finding.verification_status == "cannot_verify" and finding.confidence == "high":
            errors.append("{} cannot be both unverifiable and high confidence".format(label))
        for source_index, source in enumerate(finding.evidence):
            source_label = "{}.evidence[{}]".format(label, source_index)
            if source.source_type not in ALLOWED_SOURCE_TYPES:
                errors.append("{}.source_type is not recognized".format(source_label))
            if not source.locator.strip():
                errors.append("{}.locator must not be empty".format(source_label))
            if source.source_type == "external" and not source.url:
                errors.append("{}.url is required for external evidence".format(source_label))
    if result.status == "cannot_verify" and not result.limitations:
        errors.append("cannot_verify results must explain a limitation")
    if errors:
        raise ValidationError(errors)
