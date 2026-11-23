"""Metrics for user-provided, labeled test cases."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluate_user_cases(
    cases: list[dict[str, Any]],
    *,
    min_samples: int = 2,
) -> dict[str, Any] | None:
    """Return metrics for a labeled evaluation dataset."""
    if not cases:
        return None

    target = np.array([int(case["actual_label"]) for case in cases], dtype=int)
    prediction = np.array([int(case["predicted_label"]) for case in cases], dtype=int)
    probabilities = np.array([float(case["probability"]) for case in cases], dtype=float)

    if len(np.unique(target)) < 2:
        return {
            "available": False,
            "sample_count": len(cases),
            "reason": (
                "Data uji baru harus berisi minimal satu fungsi Long Method "
                "dan satu fungsi bukan Long Method."
            ),
        }
    if len(cases) < min_samples:
        return {
            "available": False,
            "sample_count": len(cases),
            "reason": (
                f"Minimal {min_samples} fungsi diperlukan agar metrik tidak "
                "dihitung dari sampel yang terlalu kecil."
            ),
        }

    tn, fp, fn, tp = confusion_matrix(target, prediction, labels=[0, 1]).ravel()
    roc_auc = (
        float(roc_auc_score(target, probabilities))
        if len(np.unique(target)) > 1 and len(np.unique(probabilities)) > 1
        else None
    )
    return {
        "available": True,
        "sufficient": len(cases) >= 10,
        "reason": (
            None
            if len(cases) >= 10
            else (
                f"Sampel relatif kecil ({len(cases)} record). Gunakan minimal "
                "10 fungsi dari kedua kelas agar hasil lebih stabil."
            )
        ),
        "sample_count": len(cases),
        "positive_count": int(target.sum()),
        "negative_count": int((1 - target).sum()),
        "precision": float(precision_score(target, prediction, zero_division=0)),
        "recall": float(recall_score(target, prediction, zero_division=0)),
        "f1_score": float(f1_score(target, prediction, zero_division=0)),
        "roc_auc": roc_auc,
        "confusion_matrix": {
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp),
        },
    }

