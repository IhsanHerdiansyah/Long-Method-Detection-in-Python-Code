import unittest
from pathlib import Path

from src.analysis import load_model_bundle
from src.dataset_evaluation import evaluate_submitted_dataset
from src.examples import LONG_METHOD, SHORT_METHOD


class DatasetEvaluationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_model_bundle(
            Path(__file__).resolve().parents[1] / "artifacts" / "long_method_model.joblib"
        )

    def test_python_upload_with_two_classes(self):
        content = f"{SHORT_METHOD}\n\n{LONG_METHOD}".encode("utf-8")
        result = evaluate_submitted_dataset("new_test.py", content, self.bundle)
        self.assertEqual(result["metrics"]["sample_count"], 2)
        self.assertAlmostEqual(result["metrics"]["precision"], 1.0)
        self.assertAlmostEqual(result["metrics"]["recall"], 1.0)
        self.assertAlmostEqual(result["metrics"]["f1_score"], 1.0)

    def test_python_upload_with_one_class_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Long Method"):
            evaluate_submitted_dataset(
                "one_class.py",
                SHORT_METHOD.encode("utf-8"),
                self.bundle,
            )

    def test_multi_function_sample_is_near_training_metrics(self):
        path = Path(__file__).resolve().parents[1] / "examples" / "multi_function_test.py"
        result = evaluate_submitted_dataset(
            "multi_function_test.py",
            path.read_bytes(),
            self.bundle,
        )
        metrics = result["metrics"]
        self.assertEqual(metrics["sample_count"], 60)
        self.assertAlmostEqual(metrics["precision"], 0.78125, places=3)
        self.assertAlmostEqual(metrics["recall"], 0.892857, places=3)
        self.assertAlmostEqual(metrics["f1_score"], 0.833333, places=3)


if __name__ == "__main__":
    unittest.main()

