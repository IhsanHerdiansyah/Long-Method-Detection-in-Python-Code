import unittest
from pathlib import Path

from src.analysis import analyze_code, load_model_bundle
from src.examples import LONG_METHOD, SHORT_METHOD


class ModelAnalysisTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_model_bundle(
            Path(__file__).resolve().parents[1] / "artifacts" / "long_method_model.joblib"
        )

    def test_long_method_probability_is_higher_than_short_method(self):
        short = analyze_code(SHORT_METHOD, self.bundle)["functions"][0]
        long = analyze_code(LONG_METHOD, self.bundle)["functions"][0]
        self.assertGreater(long["probability"], short["probability"])
        self.assertTrue(long["is_flagged"])
        self.assertFalse(short["is_flagged"])
        self.assertTrue(long["decision_rules"])

    def test_multiple_functions_are_summarized(self):
        result = analyze_code(f"{SHORT_METHOD}\n\n{LONG_METHOD}", self.bundle)
        self.assertEqual(result["summary"]["function_count"], 2)
        self.assertGreaterEqual(result["summary"]["flagged_count"], 1)


if __name__ == "__main__":
    unittest.main()

