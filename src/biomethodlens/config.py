"""Load and validate the specialist reviewer registry."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Tuple


@dataclass(frozen=True)
class ReviewerSpec:
    id: str
    display_name: str
    description: str
    prompt: str
    mandatory: bool
    modalities: Tuple[str, ...]
    study_types: Tuple[str, ...]
    keywords: Tuple[str, ...]
    priority: int = 100


def project_root() -> Path:
    source_root = Path(__file__).resolve().parents[2]
    if (source_root / "config" / "reviewers.json").is_file():
        return source_root
    candidates = (
        Path(sys.prefix) / "share" / "biomethodlens",
        Path(__file__).resolve().parents[1] / "share" / "biomethodlens",
    )
    for installed_root in candidates:
        if (installed_root / "config" / "reviewers.json").is_file():
            return installed_root
    return source_root


def registry_path(root: Optional[Path] = None) -> Path:
    return (root or project_root()) / "config" / "reviewers.json"


def load_registry(root: Optional[Path] = None) -> List[ReviewerSpec]:
    path = registry_path(root)
    data = json.loads(path.read_text(encoding="utf-8"))
    errors: List[str] = []
    reviewers: List[ReviewerSpec] = []
    seen = set()
    for index, raw in enumerate(data.get("reviewers", [])):
        try:
            spec = ReviewerSpec(
                id=str(raw["id"]),
                display_name=str(raw["display_name"]),
                description=str(raw["description"]),
                prompt=str(raw["prompt"]),
                mandatory=bool(raw["mandatory"]),
                modalities=tuple(str(value).lower() for value in raw.get("modalities", [])),
                study_types=tuple(str(value).lower() for value in raw.get("study_types", [])),
                keywords=tuple(str(value).lower() for value in raw.get("keywords", [])),
                priority=int(raw.get("priority", 100)),
            )
        except (KeyError, TypeError, ValueError) as exc:
            errors.append("reviewer[{}]: {}".format(index, exc))
            continue
        if not spec.id or spec.id in seen:
            errors.append("reviewer[{}] has an empty or duplicate id".format(index))
        seen.add(spec.id)
        prompt_path = (root or project_root()) / "prompts" / "reviewers" / spec.prompt
        if not prompt_path.is_file():
            errors.append("missing prompt for {}: {}".format(spec.id, spec.prompt))
        reviewers.append(spec)
    if not reviewers:
        errors.append("the registry contains no reviewers")
    if errors:
        raise ValueError("Invalid reviewer registry: " + "; ".join(errors))
    return sorted(reviewers, key=lambda item: (item.priority, item.id))


def index_registry(reviewers: Iterable[ReviewerSpec]) -> Dict[str, ReviewerSpec]:
    return {reviewer.id: reviewer for reviewer in reviewers}
