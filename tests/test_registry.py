import unittest

from biomethodlens.config import load_registry


class RegistryTests(unittest.TestCase):
    def test_registry_is_unique_and_has_specialist_depth(self):
        reviewers = load_registry()
        ids = [item.id for item in reviewers]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 15)
        self.assertGreaterEqual(sum(not item.mandatory for item in reviewers), 10)

    def test_every_reviewer_has_routing_metadata(self):
        for reviewer in load_registry():
            self.assertTrue(reviewer.display_name)
            self.assertTrue(reviewer.description)
            self.assertTrue(reviewer.prompt)


if __name__ == "__main__":
    unittest.main()
