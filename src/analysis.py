"""Model-backed code smell analysis and local decision explanations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from src.feature_extraction import (
    FEATURE_LABELS,
    FEATURE_NAMES,
    ExtractedFunction,
    extract_functions,
)


def load_model_bundle(path: str | Path) -> dict[str, Any]:
    bundle = joblib.load(Path(path))
    required = {"model", "feature_names", "threshold", "metadata"}
    missing = required.difference(bundle)
    if missing:
        raise ValueError(f"Model artifact is incomplete: {sorted(missing)}")
    return bundle


def _decision_rules(model: Any, feature_row: np.ndarray) -> list[str]:
    tree = model.tree_
    feature_frame = pd.DataFrame(
        [feature_row], columns=FEATURE_NAMES, dtype=float
    )
    node_indicator = model.decision_path(feature_frame)
    path_nodes = node_indicator.indices[
        node_indicator.indptr[0] : node_indicator.indptr[1]
    ].tolist()
    rules: list[str] = []
    for node_id in path_nodes[:-1]:
        feature_index = int(tree.feature[node_id])
        threshold = float(tree.threshold[node_id])
        feature_name = FEATURE_NAMES[feature_index]
        value = float(feature_row[feature_index])
        operator = "<=" if value <= threshold else ">"
        label = FEATURE_LABELS[feature_name]
        rules.append(f"{label} {operator} {threshold:.2f}")
    return rules


def _suggestion(features: dict[str, int], is_flagged: bool) -> str:
    candidates: list[tuple[int, str]] = []
    if features["nloc"] >= 40:
        candidates.append(
            (
                features["nloc"],
                "Pecah metode panjang menjadi fungsi dengan satu tanggung jawab.",
            )
        )
    if features["parameter_count"] >= 5:
        candidates.append(
            (
                features["parameter_count"],
                "Kelompokkan parameter terkait ke objek konfigurasi atau data class.",
            )
        )
    if features["branch_count"] >= 8:
        candidates.append(
            (
                features["branch_count"],
                "Pisahkan blok percabangan utama ke helper yang lebih kecil.",
            )
        )
    if candidates:
        return max(candidates)[1]
    if is_flagged:
        return "Tinjau panjang metode dan pisahkan logika yang dapat berdiri sendiri."
    return "Tidak ada pola dominan. Pertahankan metode tetap pendek dan mudah diuji."


def analyze_code(source: str, bundle: dict[str, Any]) -> dict[str, Any]:
    functions = extract_functions(source)
    model = bundle["model"]
    threshold = float(bundle["threshold"])
    feature_matrix = np.array(
        [[getattr(function, feature) for feature in FEATURE_NAMES] for function in functions],
        dtype=float,
    )
    feature_table = pd.DataFrame(feature_matrix, columns=FEATURE_NAMES)
    probabilities = model.predict_proba(feature_table)[:, 1]

    results = []
    for function, feature_row, probability in zip(
        functions, feature_matrix, probabilities, strict=True
    ):
        is_flagged = bool(probability >= threshold)
        features = function.features
        results.append(
            {
                "name": function.name,
                "line_start": function.line_start,
                "line_end": function.line_end,
                "code_hash": function.code_hash,
                "features": features,
                "probability": float(probability),
                "confidence": float(probability if is_flagged else 1 - probability),
                "is_flagged": is_flagged,
                "label": "Terindikasi Long Method" if is_flagged else "Tidak terindikasi",
                "decision_rules": _decision_rules(model, feature_row),
                "suggestion": _suggestion(features, is_flagged),
            }
        )

    flagged_count = sum(item["is_flagged"] for item in results)
    return {
        "summary": {
            "function_count": len(results),
            "flagged_count": flagged_count,
            "clear_count": len(results) - flagged_count,
            "max_probability": max(item["probability"] for item in results),
            "threshold": threshold,
        },
        "functions": results,
        "model": {
            "name": bundle["metadata"].get("model_name", "Decision Tree"),
            "feature_names": list(FEATURE_NAMES),
            "feature_labels": dict(FEATURE_LABELS),
            "global_importances": {
                feature: float(importance)
                for feature, importance in zip(
                    FEATURE_NAMES, model.feature_importances_, strict=True
                )
            },
        },
    }


def result_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in result["functions"]:
        row = {
            "Fungsi": item["name"],
            "Baris": f"{item['line_start']}-{item['line_end']}",
            "Prediksi": item["label"],
            "Probabilitas": round(item["probability"], 4),
            "LOC": item["features"]["nloc"],
            "Parameter": item["features"]["parameter_count"],
            "Percabangan": item["features"]["branch_count"],
        }
        if "actual_label" in item:
            row["Aktual R0915"] = item["actual_label_name"]
            row["Status uji"] = item["test_outcome"]
        rows.append(row)
    return rows

