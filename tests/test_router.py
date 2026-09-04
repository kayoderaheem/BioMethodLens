import unittest

from biomethodlens.config import load_registry
from biomethodlens.router import ManuscriptProfile, select_reviewers


class RouterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reviewers = load_registry()

    def test_spatial_prediction_routes_expected_specialists(self):
        profile = ManuscriptProfile.build(
            modalities=["spatial-transcriptomics"], study_types=["prediction"]
        )
        selections = select_reviewers(self.reviewers, "A short methods summary.", profile)
        ids = {item.reviewer.id for item in selections}
        self.assertTrue({"spatial_omics", "ml_validation", "clinical_prediction", "benchmarking"}.issubset(ids))

    def test_keyword_routing_requires_two_cues(self):
        profile = ManuscriptProfile.build()
        text = "We performed single-cell analysis with explicit doublet removal."
        ids = {item.reviewer.id for item in select_reviewers(self.reviewers, text, profile)}
        self.assertIn("single_cell", ids)
        self.assertNotIn("survival_analysis", ids)

    def test_conservative_mode_selects_full_roster(self):
        selected = select_reviewers(
            self.reviewers, "Unknown manuscript type.", ManuscriptProfile.build(), mode="conservative"
        )
        self.assertEqual(len(selected), len(self.reviewers))

    def test_mandatory_reviewers_are_always_selected(self):
        selected = select_reviewers(self.reviewers, "No recognizable cues.", ManuscriptProfile.build(), mode="minimal")
        ids = {item.reviewer.id for item in selected}
        expected = {item.id for item in self.reviewers if item.mandatory}
        self.assertEqual(ids, expected)


if __name__ == "__main__":
    unittest.main()
