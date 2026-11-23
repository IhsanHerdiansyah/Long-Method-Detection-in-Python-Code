"""Train and evaluate the Decision Tree Long Method classifier."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

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
from sklearn.model_selection import (
    GridSearchCV,
    GroupKFold,
    GroupShuffleSplit,
    cross_val_predict,
)
from sklearn.tree import DecisionTreeClassifier

from src.feature_extraction import FEATURE_NAMES


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the Long Method classifier.")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/processed/long_method_dataset.csv"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts"),
    )
    return parser.parse_args()


def build_histogram(values: np.ndarray, bins: int = 12) -> dict[str, list[float]]:
    counts, edges = np.histogram(values, bins=bins)
    return {
        "edges": [round(float(value), 3) for value in edges],
        "counts": [int(value) for value in counts],
    }


def evaluate_predictions(
    target: pd.Series,
    probabilities: np.ndarray,
    threshold: float,
) -> dict:
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


def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    frame = pd.read_csv(args.data)
    required = {
        "repository",
        "long_method_label",
        *FEATURE_NAMES,
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing columns: {sorted(missing)}")

    x = frame[list(FEATURE_NAMES)].astype(float)
    y = frame["long_method_label"].astype(int)
    groups = frame["repository"].astype(str)
    if y.nunique() != 2:
        raise ValueError("The target must contain both Long Method and negative samples.")

    splitter = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    train_index, test_index = next(splitter.split(x, y, groups))
    x_train, x_test = x.iloc[train_index], x.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]
    groups_train = groups.iloc[train_index]

    parameter_grid = {
        "max_depth": [3, 4, 5, 6, 8],
        "min_samples_leaf": [10, 30, 60],
        "class_weight": ["balanced"],
        "criterion": ["gini"],
    }
    base_model = DecisionTreeClassifier(random_state=42)
    cv = GroupKFold(n_splits=3)
    search = GridSearchCV(
        base_model,
        parameter_grid,
        scoring="f1",
        cv=cv,
        n_jobs=-1,
        refit=False,
    )
    search.fit(x_train, y_train, groups=groups_train)

    model = clone(base_model).set_params(**search.best_params_)
    oof_probabilities = cross_val_predict(
        clone(model),
        x_train,
        y_train,
        groups=groups_train,
        cv=cv,
        method="predict_proba",
        n_jobs=-1,
    )[:, 1]
    threshold_candidates = np.arange(0.50, 0.951, 0.01)
    threshold_scores = {
        float(threshold): float(f1_score(y_train, oof_probabilities >= threshold))
        for threshold in threshold_candidates
    }
    selected_threshold = max(threshold_scores, key=threshold_scores.get)

    model.fit(x_train, y_train)
    train_probabilities = model.predict_proba(x_train)[:, 1]
    test_probabilities = model.predict_proba(x_test)[:, 1]
    training_metrics = evaluate_predictions(
        y_train,
        train_probabilities,
        selected_threshold,
    )
    testing_metrics = evaluate_predictions(
        y_test,
        test_probabilities,
        selected_threshold,
    )
    metrics = {
        **testing_metrics,
        "threshold": selected_threshold,
        "best_parameters": search.best_params_,
        "cv_f1_at_default_threshold": float(search.best_score_),
        "cv_f1_at_selected_threshold": threshold_scores[selected_threshold],
        "threshold_selection": (
            "Threshold dipilih dari out-of-fold predictions pada data latih saja "
            "untuk memaksimalkan F1-score."
        ),
        "training_metrics": training_metrics,
        "testing_metrics": testing_metrics,
    }

    positive_means = (
        frame.loc[frame["long_method_label"] == 1, FEATURE_NAMES].mean().round(3).to_dict()
    )
    negative_means = (
        frame.loc[frame["long_method_label"] == 0, FEATURE_NAMES].mean().round(3).to_dict()
    )
    summary = {
        "rows": int(len(frame)),
        "positive_rows": int(y.sum()),
        "negative_rows": int((1 - y).sum()),
        "positive_rate": float(y.mean()),
        "repositories": int(groups.nunique()),
        "train_rows": int(len(train_index)),
        "test_rows": int(len(test_index)),
        "train_repositories": int(groups_train.nunique()),
        "test_repositories": int(groups.iloc[test_index].nunique()),
        "positive_feature_means": positive_means,
        "negative_feature_means": negative_means,
        "feature_histograms": {
            feature: build_histogram(frame[feature].to_numpy(dtype=float))
            for feature in FEATURE_NAMES
        },
        "feature_importances": {
            feature: float(importance)
            for feature, importance in zip(FEATURE_NAMES, model.feature_importances_, strict=True)
        },
        "split_protocol": (
            "Holdout 20% berdasarkan repository. Repository pada data uji tidak "
            "digunakan untuk pemilihan hyperparameter atau pelatihan model."
        ),
    }
    metadata = {
        "model_name": "Decision Tree - Long Method",
        "model_type": "DecisionTreeClassifier",
        "feature_names": list(FEATURE_NAMES),
        "threshold": selected_threshold,
        "trained_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "dataset_rows": int(len(frame)),
        "training_seconds": round(time.perf_counter() - started, 3),
        "split_protocol": summary["split_protocol"],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "feature_names": list(FEATURE_NAMES),
            "threshold": selected_threshold,
            "metadata": metadata,
        },
        args.output_dir / "long_method_model.joblib",
        compress=3,
    )
    (args.output_dir / "metrics.json").write_text(
        json.dumps({"metrics": metrics, "dataset": summary}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (args.output_dir / "model_metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps({"metrics": metrics, "dataset": summary}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

