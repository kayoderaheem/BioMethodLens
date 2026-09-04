import unittest

from biomethodlens.models import ReviewResult, ValidationError


def valid_result():
    return {
        "reviewer_id": "statistics",
        "paper_id": "paper-1",
        "status": "ok",
        "scope_summary": "Statistical scope checked.",
        "findings": [
            {
                "id": "STAT-001",
                "title": "Experimental unit is unclear",
                "category": "pseudoreplication",
                "severity": "major",
                "confidence": "high",
                "assessment": "partially_supported",
                "claim": "Tests use independent observations.",
                "location": "Methods",
                "evidence": [
                    {
                        "source_type": "manuscript",
                        "locator": "Methods, paragraph 2",
                        "excerpt": "Cells were compared using a t-test.",
                        "note": "Donor aggregation was not described.",
                        "url": None,
                    }
                ],
                "rationale": "Cells may be nested within donors.",
                "impact": "Standard errors may be underestimated.",
                "recommendation": "Use donor-level inference.",
                "verification_status": "verified",
            }
        ],
        "limitations": [],
    }


class ModelValidationTests(unittest.TestCase):
    def test_valid_result_round_trips(self):
        result = ReviewResult.from_dict(valid_result())
        self.assertEqual(result.to_dict()["findings"][0]["id"], "STAT-001")

    def test_verified_finding_requires_evidence(self):
        data = valid_result()
        data["findings"][0]["evidence"] = []
        with self.assertRaises(ValidationError):
            ReviewResult.from_dict(data)

    def test_unverifiable_high_confidence_is_rejected(self):
        data = valid_result()
        data["findings"][0]["verification_status"] = "cannot_verify"
        with self.assertRaises(ValidationError):
            ReviewResult.from_dict(data)

    def test_external_evidence_requires_url(self):
        data = valid_result()
        data["findings"][0]["evidence"][0]["source_type"] = "external"
        with self.assertRaises(ValidationError):
            ReviewResult.from_dict(data)


if __name__ == "__main__":
    unittest.main()
