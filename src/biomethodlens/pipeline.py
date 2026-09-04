"""Concurrent, resumable review orchestration."""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Sequence

from .config import ReviewerSpec, load_registry, project_root
from .io import load_manuscript
from .models import ReviewResult
from .prompts import build_prompt, load_schema
from .providers import ReviewProvider
from .report import build_report
from .router import ManuscriptProfile, ReviewerSelection, select_reviewers


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return value or "manuscript"


@dataclass(frozen=True)
class RunSummary:
    paper_id: str
    output_dir: Path
    report_path: Path
    selected_reviewers: int
    completed_reviews: int


class ReviewPipeline:
    def __init__(
        self,
        provider: ReviewProvider,
        root: Path = None,
        max_workers: int = 4,
        routing_mode: str = "balanced",
    ) -> None:
        self.root = (root or project_root()).resolve()
        self.provider = provider
        self.max_workers = max(1, max_workers)
        self.routing_mode = routing_mode
        self.reviewers = load_registry(self.root)
        self.schema = load_schema(self.root)

    def plan(self, manuscript_text: str, profile: ManuscriptProfile) -> List[ReviewerSelection]:
        return select_reviewers(self.reviewers, manuscript_text, profile, mode=self.routing_mode)

    def run(
        self,
        manuscript_path: Path,
        profile: ManuscriptProfile,
        paper_id: str = "",
        output_base: Path = None,
    ) -> RunSummary:
        manuscript = load_manuscript(manuscript_path)
        resolved_paper_id = slugify(paper_id or manuscript.path.stem)
        output_dir = (output_base or (self.root / "runs")) / resolved_paper_id
        reviews_dir = output_dir / "reviews"
        reviews_dir.mkdir(parents=True, exist_ok=True)
        selections = self.plan(manuscript.text, profile)
        if not selections:
            raise RuntimeError("No reviewers were selected")

        def run_one(selection: ReviewerSelection) -> ReviewResult:
            reviewer = selection.reviewer
            prompt = build_prompt(reviewer, resolved_paper_id, manuscript.text, self.root)
            raw = self.provider.review(
                reviewer=reviewer,
                paper_id=resolved_paper_id,
                prompt=prompt,
                schema=self.schema,
            )
            result = ReviewResult.from_dict(raw)
            if result.reviewer_id != reviewer.id:
                raise ValueError("provider returned reviewer_id={!r}, expected {!r}".format(result.reviewer_id, reviewer.id))
            if result.paper_id != resolved_paper_id:
                raise ValueError("provider returned paper_id={!r}, expected {!r}".format(result.paper_id, resolved_paper_id))
            path = reviews_dir / (reviewer.id + ".json")
            path.write_text(json.dumps(result.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            return result

        results: List[ReviewResult] = []
        errors = []
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(selections))) as executor:
            future_map = {executor.submit(run_one, item): item for item in selections}
            for future in as_completed(future_map):
                selection = future_map[future]
                try:
                    results.append(future.result())
                except Exception as exc:
                    errors.append({"reviewer_id": selection.reviewer.id, "error": str(exc)})
        results.sort(key=lambda item: item.reviewer_id)
        if not results:
            raise RuntimeError("Every selected reviewer failed: {}".format(errors))

        report = build_report(
            paper_id=resolved_paper_id,
            manuscript_sha256=manuscript.sha256,
            selections=selections,
            results=results,
        )
        report_path = output_dir / "report.md"
        report_path.write_text(report, encoding="utf-8")
        manifest = {
            "framework": "BioMethodLens",
            "framework_version": "0.1.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "paper_id": resolved_paper_id,
            "manuscript_sha256": manuscript.sha256,
            "input_filename": manuscript.path.name,
            "page_count": manuscript.page_count,
            "routing_mode": self.routing_mode,
            "selected_reviewers": [item.reviewer.id for item in selections],
            "completed_reviewers": [item.reviewer_id for item in results],
            "failures": errors,
        }
        (output_dir / "run_manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        return RunSummary(resolved_paper_id, output_dir, report_path, len(selections), len(results))
