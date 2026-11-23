import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from src.model_versions import (
    create_next_version,
    load_version_payload,
    load_version_registry,
    reset_versions_to_v1,
    version_paths,
)


ROOT = Path(__file__).resolve().parents[1]


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ModelVersionTest(unittest.TestCase):
    def test_new_version_preserves_v1_and_uses_same_benchmark(self):
        with tempfile.TemporaryDirectory() as temporary:
            artifacts = Path(temporary) / "artifacts"
            artifacts.mkdir()
            for name in (
                "long_method_model.joblib",
                "metrics.json",
                "model_metadata.json",
            ):
                shutil.copy2(ROOT / "artifacts" / name, artifacts / name)

            processed_data = ROOT / "data" / "processed" / "long_method_dataset.csv"
            registry = load_version_registry(artifacts, processed_data)
            benchmark_hash = registry["benchmark"]["sha256"]
            v1_paths = version_paths(artifacts, 1)
            v1_hashes = {
                "model": file_hash(v1_paths["model"]),
                "metrics": file_hash(v1_paths["metrics"]),
                "metadata": file_hash(v1_paths["metadata"]),
            }

            additions = [
                {
                    "code_hash": "unit-positive-a",
                    "function_name": "long_a",
                    "features": {
                        "nloc": 90,
                        "parameter_count": 4,
                        "branch_count": 18,
                    },
                    "actual_label": 1,
                },
                {
                    "code_hash": "unit-positive-b",
                    "function_name": "long_b",
                    "features": {
                        "nloc": 70,
                        "parameter_count": 3,
                        "branch_count": 12,
                    },
                    "actual_label": 1,
                },
                {
                    "code_hash": "unit-negative-a",
                    "function_name": "short_a",
                    "features": {
                        "nloc": 8,
                        "parameter_count": 1,
                        "branch_count": 1,
                    },
                    "actual_label": 0,
                },
                {
                    "code_hash": "unit-negative-b",
                    "function_name": "short_b",
                    "features": {
                        "nloc": 14,
                        "parameter_count": 2,
                        "branch_count": 2,
                    },
                    "actual_label": 0,
                },
            ]
            result = create_next_version(
                artifacts,
                processed_data,
                additions,
                n_jobs=1,
            )

            self.assertIsNotNone(result)
            self.assertTrue(result["created"])
            self.assertEqual(result["version"], 2)
            self.assertEqual(result["added_rows"], 4)
            self.assertEqual(file_hash(v1_paths["model"]), v1_hashes["model"])
            self.assertEqual(file_hash(v1_paths["metrics"]), v1_hashes["metrics"])
            self.assertEqual(file_hash(v1_paths["metadata"]), v1_hashes["metadata"])

            updated_registry = load_version_registry(artifacts, processed_data)
            self.assertEqual(len(updated_registry["versions"]), 2)
            self.assertEqual(updated_registry["benchmark"]["sha256"], benchmark_hash)
            _, v2_payload = load_version_payload(artifacts, 2)
            self.assertEqual(v2_payload["dataset"]["train_rows"], 37602)
            self.assertEqual(v2_payload["dataset"]["test_rows"], 16209)
            self.assertIn("training_metrics", v2_payload["metrics"])
            self.assertIn("testing_metrics", v2_payload["metrics"])

            registry_data = json.loads(
                (artifacts / "model_registry.json").read_text(encoding="utf-8")
            )
            self.assertEqual(registry_data["versions"][1]["parent_version"], 1)

            reset_result = reset_versions_to_v1(artifacts, processed_data)
            self.assertEqual(reset_result["removed_versions"], [2])
            self.assertTrue(v1_paths["model"].exists())
            self.assertFalse(version_paths(artifacts, 2)["directory"].exists())
            reset_registry = load_version_registry(artifacts, processed_data)
            self.assertEqual(
                [version["version"] for version in reset_registry["versions"]],
                [1],
            )


if __name__ == "__main__":
    unittest.main()
