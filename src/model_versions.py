"""Immutable model versions and benchmark-consistent retraining."""

from __future__ import annotations

import hashlib
import json
import shutil
import time
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GroupKFold, GroupShuffleSplit, cross_val_predict
from sklearn.tree import DecisionTreeClassifier

from src.feature_extraction import FEATURE_NAMES


REGISTRY_FILENAME = "model_registry.json"
VERSION_DIRECTORY = "model_versions"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    temporary.replace(path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _evaluate(
    target: pd.Series,
    probabilities: np.ndarray,
    threshold: float,
) -> dict[str, Any]:
    predictions = (probabilities >= threshold).astype(int)
    labels = [0, 1]
    tn, fp, fn, tp = confusion_matrix(target, predictions, labels=labels).ravel()
    report = classification_report(
        target,
        predictions,
        labels=labels,
        target_names=["Tidak terindikasi", "Long Method"],
        output_dict=True,
        zero_division=0,
    )
    return {
        "precision": float(precision_score(target, predictions, zero_division=0)),
        "recall": float(recall_score(target, predictions, zero_division=0)),
        "f1_score": float(f1_score(target, predictions, zero_division=0)),
        "accuracy": float(report["accuracy"]),
        "roc_auc": float(roc_auc_score(target, probabilities)),
        "pr_auc": float(average_precision_score(target, probabilities)),
        "confusion_matrix": {
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp),
        },
        "classification_report": report,
    }


def _build_histogram(values: np.ndarray, bins: int = 12) -> dict[str, list[float]]:
    counts, edges = np.histogram(values, bins=bins)
    return {
        "edges": [round(float(value), 3) for value in edges],
        "counts": [int(value) for value in counts],
    }


def _registry_path(artifacts_dir: Path) -> Path:
    return artifacts_dir / REGISTRY_FILENAME


def _version_root(artifacts_dir: Path) -> Path:
    return artifacts_dir / VERSION_DIRECTORY


def _version_dir(artifacts_dir: Path, version: int) -> Path:
    return _version_root(artifacts_dir) / f"V{version}"


def _split_reference_dataset(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    x = frame[list(FEATURE_NAMES)].astype(float)
    y = frame["long_method_label"].astype(int)
    groups = frame["repository"].astype(str)
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    train_index, test_index = next(splitter.split(x, y, groups))
    return frame.iloc[train_index].copy(), frame.iloc[test_index].copy()


def ensure_version_store(
    artifacts_dir: str | Path,
    processed_data: str | Path,
) -> dict[str, Any]:
    """Create immutable V1 artifacts from the original model and dataset split."""
    artifacts_dir = Path(artifacts_dir)
    processed_data = Path(processed_data)
    registry_path = _registry_path(artifacts_dir)
    version_root = _version_root(artifacts_dir)
    version_root.mkdir(parents=True, exist_ok=True)

    registry = (
        _read_json(registry_path)
        if registry_path.exists()
        else {"schema_version": 1, "versions": []}
    )
    if registry.get("versions"):
        return registry

    required = [
        artifacts_dir / "long_method_model.joblib",
        artifacts_dir / "metrics.json",
        artifacts_dir / "model_metadata.json",
        processed_data,
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Artifact versi awal belum lengkap: " + ", ".join(missing)
        )

    frame = pd.read_csv(processed_data)
    required_columns = {
        "code_hash",
        "repository",
        "long_method_label",
        *FEATURE_NAMES,
    }
    missing_columns = required_columns.difference(frame.columns)
    if missing_columns:
        raise ValueError(
            "Dataset tidak memiliki kolom: " + ", ".join(sorted(missing_columns))
        )

    train_frame, test_frame = _split_reference_dataset(frame)
    metrics_payload = _read_json(artifacts_dir / "metrics.json")
    expected_train = int(metrics_payload["dataset"]["train_rows"])
    expected_test = int(metrics_payload["dataset"]["test_rows"])
    if len(train_frame) != expected_train or len(test_frame) != expected_test:
        raise RuntimeError(
            "Split dataset tidak konsisten dengan artifact model awal: "
            f"{len(train_frame)}/{len(test_frame)} versus "
            f"{expected_train}/{expected_test}."
        )

    v1_dir = _version_dir(artifacts_dir, 1)
    if not v1_dir.exists():
        v1_dir.mkdir(parents=True)
        shutil.copy2(artifacts_dir / "long_method_model.joblib", v1_dir)
        shutil.copy2(artifacts_dir / "metrics.json", v1_dir)
        shutil.copy2(artifacts_dir / "model_metadata.json", v1_dir)
        train_frame.to_csv(v1_dir / "training_snapshot.csv", index=False)
        test_frame.to_csv(v1_dir / "benchmark_snapshot.csv", index=False)

    metadata = _read_json(v1_dir / "model_metadata.json")
    dataset = metrics_payload["dataset"]
    registry = {
        "schema_version": 1,
        "benchmark": {
            "path": str(
                (v1_dir / "benchmark_snapshot.csv").relative_to(artifacts_dir)
            ).replace("\\", "/"),
            "rows": len(test_frame),
            "repositories": int(test_frame["repository"].nunique()),
            "sha256": _sha256(v1_dir / "benchmark_snapshot.csv"),
        },
        "versions": [
            {
                "version": 1,
                "label": "V1",
                "description": "Dataset awal dan model pembanding",
                "status": "frozen",
                "directory": "model_versions/V1",
                "created_at": metadata.get("trained_at", ""),
                "parent_version": None,
                "training_rows": int(dataset["train_rows"]),
                "benchmark_rows": int(dataset["test_rows"]),
                "added_rows": 0,
                "duplicates_skipped": 0,
                "benchmark_overlap_skipped": 0,
                "threshold": float(metadata["threshold"]),
            }
        ],
    }
    _write_json(registry_path, registry)
    return registry


def load_version_registry(
    artifacts_dir: str | Path,
    processed_data: str | Path,
) -> dict[str, Any]:
    return ensure_version_store(artifacts_dir, processed_data)


def version_paths(artifacts_dir: str | Path, version: int) -> dict[str, Path]:
    directory = _version_dir(Path(artifacts_dir), version)
    return {
        "directory": directory,
        "model": directory / "long_method_model.joblib",
        "metrics": directory / "metrics.json",
        "metadata": directory / "model_metadata.json",
        "training": directory / "training_snapshot.csv",
        "added_records": directory / "added_records.csv",
    }


def load_version_payload(
    artifacts_dir: str | Path,
    version: int,
) -> tuple[Path, dict[str, Any]]:
    paths = version_paths(artifacts_dir, version)
    if not paths["model"].exists() or not paths["metrics"].exists():
        raise FileNotFoundError(f"Artifact model V{version} tidak lengkap.")
    return paths["model"], _read_json(paths["metrics"])


def reset_versions_to_v1(
    artifacts_dir: str | Path,
    processed_data: str | Path,
) -> dict[str, Any]:
    """Delete versioned retraining artifacts after V1 and reset the registry."""
    artifacts_dir = Path(artifacts_dir)
    registry = ensure_version_store(artifacts_dir, processed_data)
    version_root = _version_root(artifacts_dir).resolve()
    directories_to_remove: list[tuple[int, Path]] = []

    for directory in version_root.iterdir():
        if not directory.is_dir() or not directory.name.startswith("V"):
            continue
        suffix = directory.name[1:]
        if not suffix.isdigit() or int(suffix) <= 1:
            continue
        resolved = directory.resolve()
        try:
            resolved.relative_to(version_root)
        except ValueError as exc:
            raise RuntimeError(
                f"Target reset berada di luar folder versi: {resolved}"
            ) from exc
        directories_to_remove.append((int(suffix), resolved))

    directories_to_remove.sort(key=lambda item: item[0])
    for _, directory in directories_to_remove:
        shutil.rmtree(directory)

    baseline = next(
        version
        for version in registry["versions"]
        if int(version["version"]) == 1
    )
    registry["versions"] = [baseline]
    _write_json(_registry_path(artifacts_dir), registry)
    return {
        "reset": True,
        "kept_version": 1,
        "removed_versions": [
            version for version, _ in directories_to_remove
        ],
        "registry": registry,
    }


def _normalise_input_records(records: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for record in records:
        if record.get("actual_label") is None:
            continue
        code_hash = str(record.get("code_hash", "")).strip()
        if not code_hash:
            continue
        rows.append(
            {
                "code_hash": code_hash,
                "function_name": str(record.get("function_name", "fungsi")),
                "nloc": int(record["features"]["nloc"]),
                "parameter_count": int(record["features"]["parameter_count"]),
                "branch_count": int(record["features"]["branch_count"]),
                "long_method_label": int(record["actual_label"]),
                "repository": "",
                "commit_id": "",
                "source_path": "editor_submission",
            }
        )
    return pd.DataFrame(rows)


def create_next_version(
    artifacts_dir: str | Path,
    processed_data: str | Path,
    records: list[dict[str, Any]],
    *,
    n_jobs: int = -1,
) -> dict[str, Any] | None:
    """Train a new immutable version using editor rows and a fixed benchmark."""
    started = time.perf_counter()
    artifacts_dir = Path(artifacts_dir)
    registry = load_version_registry(artifacts_dir, processed_data)
    versions = registry["versions"]
    parent = versions[-1]
    parent_version = int(parent["version"])
    next_version = parent_version + 1

    additions = _normalise_input_records(records)
    if additions.empty:
        return None

    parent_paths = version_paths(artifacts_dir, parent_version)
    benchmark_path = artifacts_dir / registry["benchmark"]["path"]
    train_frame = pd.read_csv(parent_paths["training"])
    benchmark_frame = pd.read_csv(benchmark_path)

    benchmark_hashes = set(benchmark_frame["code_hash"].astype(str))
    train_hashes = set(train_frame["code_hash"].astype(str))
    overlap_mask = additions["code_hash"].isin(benchmark_hashes)
    duplicate_mask = additions["code_hash"].isin(train_hashes)
    benchmark_overlap_skipped = int(overlap_mask.sum())
    duplicates_skipped = int(duplicate_mask.sum())
    additions = additions.loc[~overlap_mask & ~duplicate_mask].copy()
    additions = additions.drop_duplicates(subset=["code_hash"], keep="first")
    if additions.empty:
        return {
            "created": False,
            "reason": (
                "Tidak ada record baru yang dapat dipakai. Record yang sama "
                "dengan data latih atau data benchmark dilewati."
            ),
            "duplicates_skipped": duplicates_skipped,
            "benchmark_overlap_skipped": benchmark_overlap_skipped,
        }

    creation_time = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    group_name = f"ide_submission_V{next_version}_{int(time.time() * 1000)}"
    additions["record_id"] = [
        f"IDE-V{next_version}-{index:04d}"
        for index in range(1, len(additions) + 1)
    ]
    additions["repository"] = group_name
    combined_train = pd.concat([train_frame, additions], ignore_index=True)

    parent_metrics = _read_json(parent_paths["metrics"])["metrics"]
    best_parameters = parent_metrics.get("best_parameters", {})
    model_params = {
        "max_depth": int(best_parameters.get("max_depth", 5)),
        "min_samples_leaf": int(best_parameters.get("min_samples_leaf", 10)),
        "class_weight": best_parameters.get("class_weight", "balanced"),
        "criterion": best_parameters.get("criterion", "gini"),
    }
    x_train = combined_train[list(FEATURE_NAMES)].astype(float)
    y_train = combined_train["long_method_label"].astype(int)
    groups_train = combined_train["repository"].astype(str)
    x_test = benchmark_frame[list(FEATURE_NAMES)].astype(float)
    y_test = benchmark_frame["long_method_label"].astype(int)
    model = DecisionTreeClassifier(random_state=42, **model_params)

    cv = GroupKFold(n_splits=3)
    oof_probabilities = cross_val_predict(
        clone(model),
        x_train,
        y_train,
        groups=groups_train,
        cv=cv,
        method="predict_proba",
        n_jobs=n_jobs,
    )[:, 1]
    threshold_candidates = np.arange(0.50, 0.951, 0.01)
    threshold_scores = {
        float(threshold): float(f1_score(y_train, oof_probabilities >= threshold))
        for threshold in threshold_candidates
    }
    selected_threshold = max(threshold_scores, key=threshold_scores.get)

    model.fit(x_train, y_train)
    training_metrics = _evaluate(
        y_train,
        model.predict_proba(x_train)[:, 1],
        selected_threshold,
    )
    testing_metrics = _evaluate(
        y_test,
        model.predict_proba(x_test)[:, 1],
        selected_threshold,
    )
    metrics = {
        **testing_metrics,
        "threshold": selected_threshold,
        "best_parameters": model_params,
        "cv_f1_at_default_threshold": float(
            threshold_scores.get(0.50, testing_metrics["f1_score"])
        ),
        "cv_f1_at_selected_threshold": threshold_scores[selected_threshold],
        "threshold_selection": (
            "Threshold V baru dipilih hanya dari out-of-fold snapshot data "
            "latih kumulatif. Data benchmark tidak dipakai untuk kalibrasi."
        ),
        "training_metrics": training_metrics,
        "testing_metrics": testing_metrics,
    }

    complete_frame = pd.concat([combined_train, benchmark_frame], ignore_index=True)
    positive = complete_frame["long_method_label"].astype(int) == 1
    feature_importances = {
        feature: float(importance)
        for feature, importance in zip(
            FEATURE_NAMES,
            model.feature_importances_,
            strict=True,
        )
    }
    summary = {
        "rows": int(len(complete_frame)),
        "positive_rows": int(positive.sum()),
        "negative_rows": int((~positive).sum()),
        "positive_rate": float(positive.mean()),
        "repositories": int(complete_frame["repository"].nunique()),
        "train_rows": int(len(combined_train)),
        "test_rows": int(len(benchmark_frame)),
        "train_repositories": int(combined_train["repository"].nunique()),
        "test_repositories": int(benchmark_frame["repository"].nunique()),
        "positive_feature_means": (
            complete_frame.loc[positive, FEATURE_NAMES].mean().round(3).to_dict()
        ),
        "negative_feature_means": (
            complete_frame.loc[~positive, FEATURE_NAMES].mean().round(3).to_dict()
        ),
        "feature_histograms": {
            feature: _build_histogram(
                complete_frame[feature].to_numpy(dtype=float)
            )
            for feature in FEATURE_NAMES
        },
        "feature_importances": feature_importances,
        "split_protocol": (
            "Model baru dilatih pada snapshot data awal ditambah input IDE. "
            "Seluruh versi dievaluasi pada benchmark repository holdout yang sama."
        ),
    }
    metadata = {
        "model_name": "Decision Tree - Long Method",
        "model_type": "DecisionTreeClassifier",
        "feature_names": list(FEATURE_NAMES),
        "threshold": selected_threshold,
        "trained_at": creation_time,
        "dataset_rows": int(len(complete_frame)),
        "training_seconds": round(time.perf_counter() - started, 3),
        "split_protocol": summary["split_protocol"],
        "version": next_version,
        "parent_version": parent_version,
        "training_additions": int(len(additions)),
    }

    target_dir = _version_dir(artifacts_dir, next_version)
    if target_dir.exists():
        raise FileExistsError(
            f"Direktori V{next_version} sudah ada; versi lama tidak ditimpa."
        )
    target_dir.mkdir(parents=True)
    paths = version_paths(artifacts_dir, next_version)
    combined_train.to_csv(paths["training"], index=False)
    additions.to_csv(paths["added_records"], index=False)
    joblib.dump(
        {
            "model": model,
            "feature_names": list(FEATURE_NAMES),
            "threshold": selected_threshold,
            "metadata": metadata,
        },
        paths["model"],
        compress=3,
    )
    _write_json(
        paths["metrics"],
        {"metrics": metrics, "dataset": summary},
    )
    _write_json(paths["metadata"], metadata)

    versions.append(
        {
            "version": next_version,
            "label": f"V{next_version}",
            "description": "Dataset awal ditambah input IDE",
            "status": "frozen",
            "directory": f"model_versions/V{next_version}",
            "created_at": creation_time,
            "parent_version": parent_version,
            "training_rows": int(len(combined_train)),
            "benchmark_rows": int(len(benchmark_frame)),
            "added_rows": int(len(additions)),
            "duplicates_skipped": duplicates_skipped,
            "benchmark_overlap_skipped": benchmark_overlap_skipped,
            "threshold": float(selected_threshold),
        }
    )
    registry["versions"] = versions
    _write_json(_registry_path(artifacts_dir), registry)
    return {
        "created": True,
        "version": next_version,
        "parent_version": parent_version,
        "added_rows": int(len(additions)),
        "duplicates_skipped": duplicates_skipped,
        "benchmark_overlap_skipped": benchmark_overlap_skipped,
        "threshold": float(selected_threshold),
        "metrics": metrics,
        "dataset": summary,
    }
