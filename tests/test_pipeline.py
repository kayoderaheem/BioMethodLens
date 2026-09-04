import json
import tempfile
import unittest
from pathlib import Path

from biomethodlens.config import project_root
from biomethodlens.pipeline import ReviewPipeline
from biomethodlens.providers import SyntheticDemoProvider
from biomethodlens.router import ManuscriptProfile


class PipelineTests(unittest.TestCase):
    def test_demo_pipeline_writes_valid_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            manuscript = temp_path / "study.txt"
            manuscript.write_text(
                "Synthetic spatial transcriptomics study. " * 20
                + "Spots were randomly assigned to training and testing sets. "
                + "We evaluated performance using random five-fold cross-validation across tissue spots.",
                encoding="utf-8",
            )
            pipeline = ReviewPipeline(
                SyntheticDemoProvider(), root=project_root(), max_workers=3, routing_mode="balanced"
            )
            profile = ManuscriptProfile.build(
                modalities=["spatial-transcriptomics"], study_types=["prediction"]
            )
            summary = pipeline.run(manuscript, profile, output_base=temp_path / "runs")
            self.assertEqual(summary.selected_reviewers, summary.completed_reviews)
            self.assertTrue(summary.report_path.is_file())
            report = summary.report_path.read_text(encoding="utf-8")
            self.assertIn("spatial neighborhood information", report)
            manifest = json.loads((summary.output_dir / "run_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["paper_id"], "study")
            self.assertEqual(manifest["failures"], [])


if __name__ == "__main__":
    unittest.main()
