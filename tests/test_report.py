import unittest

from biomethodlens.models import ReviewResult
from biomethodlens.report import build_report, normalize_findings

from tests.test_models import valid_result


class ReportTests(unittest.TestCase):
    def test_report_contains_priority_and_reproducibility_sections(self):
        result = ReviewResult.from_dict(valid_result())
        report = build_report(
            paper_id="paper-1", manuscript_sha256="abc123", selections=[], results=[result]
        )
        self.assertIn("## Prioritized findings", report)
        self.assertIn("[MAJOR / high confidence]", report)
        self.assertIn("Manuscript SHA-256: `abc123`", report)

    def test_exact_duplicates_are_suppressed(self):
        first = valid_result()
        second = valid_result()
        second["reviewer_id"] = "another_statistics_lens"
        second["findings"][0]["id"] = "OTHER-001"
        results = [ReviewResult.from_dict(first), ReviewResult.from_dict(second)]
        findings, duplicates = normalize_findings(results)
        self.assertEqual(len(findings), 1)
        self.assertEqual(duplicates, 1)


if __name__ == "__main__":
    unittest.main()
