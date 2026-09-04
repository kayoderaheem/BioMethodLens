"""LLM provider interface and an OpenAI Responses API adapter."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Protocol

from .config import ReviewerSpec


class ReviewProvider(Protocol):
    def review(
        self,
        *,
        reviewer: ReviewerSpec,
        paper_id: str,
        prompt: str,
        schema: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        ...


@dataclass
class OpenAIResponsesProvider:
    """Minimal standard-library adapter using strict Structured Outputs."""

    model: str
    api_key: str = ""
    timeout_seconds: int = 300
    store: bool = False

    def __post_init__(self) -> None:
        self.api_key = self.api_key or os.environ.get("OPENAI_API_KEY", "")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for the OpenAI provider")

    def review(
        self,
        *,
        reviewer: ReviewerSpec,
        paper_id: str,
        prompt: str,
        schema: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        payload = {
            "model": self.model,
            "instructions": "Return a rigorous, evidence-linked bioinformatics methods audit.",
            "input": prompt,
            "store": self.store,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "biomethodlens_review_result",
                    "strict": True,
                    "schema": schema,
                }
            },
        }
        request = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self.api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError("OpenAI request failed (HTTP {}): {}".format(exc.code, detail[:1000])) from exc
        output_text = body.get("output_text") or self._extract_output_text(body)
        if not output_text:
            raise RuntimeError("OpenAI response did not contain output text")
        return json.loads(output_text)

    @staticmethod
    def _extract_output_text(body: Mapping[str, Any]) -> str:
        for item in body.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    return str(content.get("text", ""))
        return ""


class SyntheticDemoProvider:
    """Offline provider for examples, tests, and installation checks."""

    def review(
        self,
        *,
        reviewer: ReviewerSpec,
        paper_id: str,
        prompt: str,
        schema: Mapping[str, Any]
    ) -> Mapping[str, Any]:
        finding_map: Dict[str, Dict[str, str]] = {
            "ml_validation": {
                "title": "The validation split is not described at the patient level",
                "category": "data leakage",
                "claim": "The reported cross-validation performance estimates generalization.",
                "location": "Methods, Model evaluation",
                "rationale": "The manuscript mentions five-fold cross-validation but does not state whether all samples from one patient stay in the same fold.",
                "impact": "Sample-level splitting can leak patient-specific signal and inflate performance.",
                "recommendation": "Repeat evaluation with grouped patient-level folds and report confidence intervals across repeated splits.",
                "excerpt": "We evaluated performance using random five-fold cross-validation across tissue spots.",
            },
            "spatial_omics": {
                "title": "Random spot splits may leak spatial neighborhood information",
                "category": "spatial leakage",
                "claim": "Held-out spots constitute an independent test set.",
                "location": "Methods, Spatial prediction",
                "rationale": "Adjacent spots from the same tissue section can share morphology, expression, and graph neighbors across folds.",
                "impact": "The reported accuracy may not represent transfer to unseen sections or patients.",
                "recommendation": "Use leave-section-out and leave-patient-out evaluation, with spatially blocked sensitivity analyses.",
                "excerpt": "Spots were randomly assigned to training and testing sets.",
            },
        }
        item = finding_map.get(reviewer.id)
        findings = []
        if item:
            findings.append(
                {
                    "id": reviewer.id.upper() + "-001",
                    "title": item["title"],
                    "category": item["category"],
                    "severity": "major",
                    "confidence": "high",
                    "assessment": "partially_supported",
                    "claim": item["claim"],
                    "location": item["location"],
                    "evidence": [
                        {
                            "source_type": "manuscript",
                            "locator": item["location"],
                            "excerpt": item["excerpt"],
                            "note": "Directly reported evaluation design.",
                            "url": None,
                        }
                    ],
                    "rationale": item["rationale"],
                    "impact": item["impact"],
                    "recommendation": item["recommendation"],
                    "verification_status": "verified",
                }
            )
        return {
            "reviewer_id": reviewer.id,
            "paper_id": paper_id,
            "status": "ok",
            "scope_summary": "Offline demonstration of the {} scope.".format(reviewer.display_name),
            "findings": findings,
            "limitations": ["Synthetic demo provider; no model-generated scientific judgment was used."],
        }
