import unittest

from src.user_evaluation import evaluate_user_cases


class UserEvaluationTest(unittest.TestCase):
    def test_single_class_metrics_are_unavailable(self):
        result = evaluate_user_cases(
            [
                {
                    "actual_label": 1,
                    "predicted_label": 1,
                    "probability": 0.9,
                },
                {
                    "actual_label": 1,
                    "predicted_label": 1,
                    "probability": 0.8,
                },
            ]
        )
        self.assertFalse(result["available"])
        self.assertEqual(result["sample_count"], 2)
        self.assertIn("Long Method", result["reason"])

    def test_metrics_from_labeled_input(self):
        result = evaluate_user_cases(
            [
                {"actual_label": 1, "predicted_label": 1, "probability": 0.9},
                {"actual_label": 1, "predicted_label": 1, "probability": 0.8},
                {"actual_label": 0, "predicted_label": 0, "probability": 0.1},
                {"actual_label": 0, "predicted_label": 1, "probability": 0.7},
            ]
        )
        self.assertTrue(result["available"])
        self.assertAlmostEqual(result["precision"], 2 / 3)
        self.assertAlmostEqual(result["recall"], 1.0)
        self.assertAlmostEqual(result["f1_score"], 0.8)
        self.assertEqual(result["confusion_matrix"]["false_positive"], 1)

    def test_minimum_sample_gate(self):
        result = evaluate_user_cases(
            [
                {"actual_label": 1, "predicted_label": 1, "probability": 0.9},
                {"actual_label": 0, "predicted_label": 0, "probability": 0.1},
            ],
            min_samples=10,
        )
        self.assertFalse(result["available"])
        self.assertIn("Minimal 10 fungsi", result["reason"])


if __name__ == "__main__":
    unittest.main()

