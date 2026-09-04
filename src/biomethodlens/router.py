"""Transparent, deterministic routing to bioinformatics specialists."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, List, Sequence, Tuple

from .config import ReviewerSpec


@dataclass(frozen=True)
class ManuscriptProfile:
    modalities: Tuple[str, ...] = field(default_factory=tuple)
    study_types: Tuple[str, ...] = field(default_factory=tuple)
    domains: Tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def build(
        cls,
        modalities: Iterable[str] = (),
        study_types: Iterable[str] = (),
        domains: Iterable[str] = (),
    ) -> "ManuscriptProfile":
        clean = lambda values: tuple(sorted({str(value).strip().lower() for value in values if str(value).strip()}))
        return cls(clean(modalities), clean(study_types), clean(domains))


@dataclass(frozen=True)
class ReviewerSelection:
    reviewer: ReviewerSpec
    score: int
    reasons: Tuple[str, ...]


def _term_present(text: str, term: str) -> bool:
    return re.search(r"(?<![a-z0-9]){}(?![a-z0-9])".format(re.escape(term)), text) is not None


def select_reviewers(
    reviewers: Sequence[ReviewerSpec],
    manuscript_text: str,
    profile: ManuscriptProfile,
    mode: str = "balanced",
    keyword_threshold: int = 2,
) -> List[ReviewerSelection]:
    """Select specialists and expose the exact reason for every selection.

    ``balanced`` selects mandatory reviewers plus specialists with an explicit
    profile match or at least ``keyword_threshold`` text cues. ``conservative``
    runs every specialist. ``minimal`` requires explicit profile matches.
    """
    if mode not in {"balanced", "conservative", "minimal"}:
        raise ValueError("mode must be balanced, conservative, or minimal")
    if keyword_threshold < 1:
        raise ValueError("keyword_threshold must be positive")
    text = " ".join(manuscript_text.lower().split())
    modality_set = set(profile.modalities)
    study_type_set = set(profile.study_types)
    output: List[ReviewerSelection] = []

    for reviewer in reviewers:
        reasons: List[str] = []
        score = 0
        if reviewer.mandatory:
            score += 100
            reasons.append("universal methods safeguard")
        modality_matches = sorted(modality_set.intersection(reviewer.modalities))
        if modality_matches:
            score += 20 * len(modality_matches)
            reasons.append("modality: " + ", ".join(modality_matches))
        study_matches = sorted(study_type_set.intersection(reviewer.study_types))
        if study_matches:
            score += 20 * len(study_matches)
            reasons.append("study type: " + ", ".join(study_matches))
        keyword_matches = [term for term in reviewer.keywords if _term_present(text, term)]
        if keyword_matches:
            score += min(len(keyword_matches), 5)
            reasons.append("text cues: " + ", ".join(keyword_matches[:5]))

        explicit_match = bool(modality_matches or study_matches)
        keyword_match = len(keyword_matches) >= keyword_threshold
        selected = reviewer.mandatory or mode == "conservative"
        if mode == "balanced":
            selected = selected or explicit_match or keyword_match
        elif mode == "minimal":
            selected = selected or explicit_match
        if selected:
            if mode == "conservative" and not reasons:
                reasons.append("conservative full-panel mode")
            output.append(ReviewerSelection(reviewer, score, tuple(reasons)))
    return sorted(output, key=lambda item: (item.reviewer.priority, -item.score, item.reviewer.id))
