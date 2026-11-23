import unittest

from src.glossary import TERM_HELP


class GlossaryTest(unittest.TestCase):
    def test_required_dashboard_terms_have_explanations(self):
        required = {
            "ast",
            "decision_tree",
            "function_count",
            "flagged",
            "clear",
            "max_probability",
            "probability",
            "prediction",
            "line_range",
            "nloc",
            "parameter_count",
            "branch_count",
            "decision_path",
            "recommendation",
            "precision",
            "recall",
            "f1_score",
            "roc_auc",
            "threshold",
            "feature_importance",
            "confusion_matrix",
            "raw_rows",
            "duplicates_removed",
            "clean_rows",
            "repositories",
            "ide_result",
            "test_metrics",
            "model_version",
        }
        self.assertTrue(required.issubset(TERM_HELP))
        self.assertTrue(all(explanation.strip() for explanation in TERM_HELP.values()))


if __name__ == "__main__":
    unittest.main()
