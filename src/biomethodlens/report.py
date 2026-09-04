"""Deterministic report assembly and conservative duplicate grouping."""

from __future__ import annotations

from collections import Counter, OrderedDict
from typing import Iterable, List, Sequence, Tuple

from .models import Finding, ReviewResult, SEVERITY_ORDER
from .router import ReviewerSelection


def normalize_findings(results: Iterable[ReviewResult]) -> Tuple[List[Finding], int]:
    """Remove exact semantic duplicates only; preserve the higher-priority item."""
    ordered = sorted(
        (finding for result in results for finding in result.findings),
        key=lambda item: (SEVERITY_ORDER[item.severity], item.reviewer_id, item.id),
    )
    unique = OrderedDict()
    duplicate_count = 0
    for finding in ordered:
        key = finding.fingerprint()
        if key in unique:
            duplicate_count += 1
            continue
        unique[key] = finding
    return list(unique.values()), duplicate_count


def build_report(
    *,
    paper_id: str,
    manuscript_sha256: str,
    selections: Sequence[ReviewerSelection],
    results: Sequence[ReviewResult],
) -> str:
    findings, duplicate_count = normalize_findings(results)
    counts = Counter(item.severity for item in findings)
    lines = [
        "# BioMethodLens audit: {}".format(paper_id),
        "",
        "> Decision support for authors and reviewers—not a replacement for expert peer review, clinical judgment, or statistical consultation.",
        "",
        "## Executive summary",
        "",
        "BioMethodLens ran {} specialist lenses and retained {} evidence-linked finding(s): {} critical, {} major, {} moderate, and {} minor.".format(
            len(results),
            len(findings),
            counts["critical"],
            counts["major"],
            counts["moderate"],
            counts["minor"],
        ),
        "",
        "## Prioritized findings",
        "",
    ]
    if not findings:
        lines.extend(
            [
                "No findings were returned. This does not establish that the manuscript is error-free; review the scope and limitations below.",
                "",
            ]
        )
    for finding in findings:
        lines.extend(
            [
                "### [{} / {} confidence] {}".format(finding.severity.upper(), finding.confidence, finding.title),
                "",
                "- **Lens:** `{}`".format(finding.reviewer_id),
                "- **Category:** {}".format(finding.category),
                "- **Location:** {}".format(finding.location or "Not localized"),
                "- **Assessment:** {}".format(finding.assessment.replace("_", " ")),
                "- **Why it matters:** {}".format(finding.impact),
                "- **Recommended action:** {}".format(finding.recommendation),
                "",
                finding.rationale,
                "",
                "Evidence:",
                "",
            ]
        )
        if finding.evidence:
            for source in finding.evidence:
                citation = "`{}` — {}".format(source.locator, source.excerpt or source.note)
                if source.url:
                    citation += " ({})".format(source.url)
                lines.append("- " + citation)
        else:
            lines.append("- Evidence could not be verified.")
        lines.append("")

    lines.extend(["## Review coverage", ""])
    for selection in selections:
        result = next((item for item in results if item.reviewer_id == selection.reviewer.id), None)
        status = result.status if result else "failed"
        reasons = "; ".join(selection.reasons) or "selected by policy"
        lines.append("- **{}** (`{}`): {} — {}".format(selection.reviewer.display_name, selection.reviewer.id, status, reasons))

    lines.extend(["", "## Scope and limitations", ""])
    limitations = []
    for result in results:
        limitations.extend(result.limitations)
    for item in dict.fromkeys(limitations):
        lines.append("- " + item)
    if not limitations:
        lines.append("- No reviewer-specific limitation was recorded; normal limitations of automated review still apply.")
    lines.extend(
        [
            "",
            "## Reproducibility record",
            "",
            "- Paper ID: `{}`".format(paper_id),
            "- Manuscript SHA-256: `{}`".format(manuscript_sha256),
            "- Specialist results validated: {}".format(len(results)),
            "- Exact duplicate findings suppressed: {}".format(duplicate_count),
            "",
        ]
    )
    return "\n".join(lines)
