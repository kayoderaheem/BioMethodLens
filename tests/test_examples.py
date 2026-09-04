import json
import unittest

from biomethodlens.config import project_root
from biomethodlens.models import ReviewResult


class ExampleTests(unittest.TestCase):
    def test_published_example_review_is_valid(self):
        path = project_root() / "examples" / "synthetic-spatial-study" / "example_review.json"
        result = ReviewResult.from_dict(json.loads(path.read_text(encoding="utf-8")))
        self.assertEqual(result.reviewer_id, "spatial_omics")
        self.assertEqual(result.findings[0].severity, "major")


if __name__ == "__main__":
    unittest.main()
