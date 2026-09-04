"""Command-line interface for planning, reviewing, demonstrating, and validating."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .config import load_registry, project_root
from .io import load_manuscript
from .models import ReviewResult, ValidationError
from .pipeline import ReviewPipeline
from .providers import OpenAIResponsesProvider, SyntheticDemoProvider
from .router import ManuscriptProfile, select_reviewers


def _csv(value: str):
    return [item.strip() for item in value.split(",") if item.strip()]


def _profile(args: argparse.Namespace) -> ManuscriptProfile:
    return ManuscriptProfile.build(_csv(args.modalities), _csv(args.study_types), _csv(args.domains))


def _add_profile_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--modalities", default="", help="Comma-separated data types, for example scrna-seq,spatial-transcriptomics")
    parser.add_argument("--study-types", default="", help="Comma-separated designs, for example prediction,survival")
    parser.add_argument("--domains", default="", help="Comma-separated biological domains")
    parser.add_argument("--routing", choices=("minimal", "balanced", "conservative"), default="balanced")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="biomethodlens", description="Evidence-linked bioinformatics manuscript review")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="Preview specialist routing without sending manuscript text anywhere")
    plan.add_argument("manuscript", type=Path)
    _add_profile_flags(plan)

    review = subparsers.add_parser("review", help="Run a review through the OpenAI Responses API")
    review.add_argument("manuscript", type=Path)
    review.add_argument("--paper-id", default="")
    review.add_argument("--model", default=os.environ.get("BIOMETHODLENS_MODEL", "gpt-5.2"))
    review.add_argument("--workers", type=int, default=4)
    review.add_argument("--output-dir", type=Path, default=None)
    _add_profile_flags(review)

    demo = subparsers.add_parser("demo", help="Run the included offline demonstration provider")
    demo.add_argument("manuscript", type=Path)
    demo.add_argument("--paper-id", default="")
    demo.add_argument("--workers", type=int, default=4)
    demo.add_argument("--output-dir", type=Path, default=None)
    _add_profile_flags(demo)

    validate = subparsers.add_parser("validate", help="Semantically validate one specialist JSON result")
    validate.add_argument("result", type=Path)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    root = project_root()
    try:
        if args.command == "validate":
            ReviewResult.from_dict(json.loads(args.result.read_text(encoding="utf-8")))
            print("Valid BioMethodLens reviewer result: {}".format(args.result))
            return 0
        manuscript = load_manuscript(args.manuscript)
        profile = _profile(args)
        if args.command == "plan":
            selections = select_reviewers(load_registry(root), manuscript.text, profile, mode=args.routing)
            print("Selected {} specialist lens(es):".format(len(selections)))
            for item in selections:
                print("- {}: {}".format(item.reviewer.id, "; ".join(item.reasons)))
            return 0
        provider = SyntheticDemoProvider() if args.command == "demo" else OpenAIResponsesProvider(model=args.model)
        pipeline = ReviewPipeline(provider, root=root, max_workers=args.workers, routing_mode=args.routing)
        summary = pipeline.run(args.manuscript, profile, paper_id=args.paper_id, output_base=args.output_dir)
        print("Completed {}/{} specialist reviews.".format(summary.completed_reviews, summary.selected_reviewers))
        print("Report: {}".format(summary.report_path))
        return 0
    except (OSError, ValueError, RuntimeError, ValidationError, json.JSONDecodeError) as exc:
        print("BioMethodLens error: {}".format(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
