import json
import unittest
from unittest.mock import patch

from biomethodlens.config import load_registry
from biomethodlens.providers import OpenAIResponsesProvider


class _Response:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.body).encode("utf-8")


class ProviderTests(unittest.TestCase):
    def test_openai_adapter_requests_strict_schema_without_storage(self):
        captured = {}
        body = {
            "output": [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": json.dumps(
                                {
                                    "reviewer_id": "study_design",
                                    "paper_id": "paper-1",
                                    "status": "ok",
                                    "scope_summary": "Checked.",
                                    "findings": [],
                                    "limitations": [],
                                }
                            ),
                        }
                    ]
                }
            ]
        }

        def fake_urlopen(request, timeout):
            captured.update(json.loads(request.data.decode("utf-8")))
            return _Response(body)

        provider = OpenAIResponsesProvider(model="test-model", api_key="test-key")
        reviewer = next(item for item in load_registry() if item.id == "study_design")
        with patch("urllib.request.urlopen", fake_urlopen):
            result = provider.review(
                reviewer=reviewer,
                paper_id="paper-1",
                prompt="Review this synthetic manuscript.",
                schema={"type": "object"},
            )
        self.assertEqual(result["reviewer_id"], "study_design")
        self.assertFalse(captured["store"])
        self.assertTrue(captured["text"]["format"]["strict"])
        self.assertEqual(captured["text"]["format"]["type"], "json_schema")


if __name__ == "__main__":
    unittest.main()
