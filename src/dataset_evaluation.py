"""Evaluate a newly submitted Python or CSV test dataset."""

from __future__ import annotations

import csv
import io
import textwrap
from pathlib import Path
from typing import Any

from src.analysis import analyze_code
from src.pylint_oracle import add_automatic_labels
from src.user_evaluation import evaluate_user_cases


MAX_UPLOAD_BYTES = 5 * 1024 * 1024


def _read_sources(filename: str, content: bytes) -> list[str]:
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError("Ukuran data uji maksimal 5 MB.")

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("File data uji harus menggunakan encoding UTF-8.") from exc
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    suffix = Path(filename).suffix.lower()
    if suffix == ".py":
        return [text]
    if suffix != ".csv":
        raise ValueError("Format data uji harus .py atau .csv.")

    reader = csv.DictReader(io.StringIO(text))
    headers = reader.fieldnames or []
    code_column = next(
        (
            header
            for header in headers
            if header.strip().lower() in {"code", "function_code", "source"}
        ),
        None,
    )
    if code_column is None:
        raise ValueError(
            "CSV data uji harus memiliki kolom code, function_code, atau source."
        )

    sources = []
    for row_number, row in enumerate(reader, start=2):
        source = textwrap.dedent(row.get(code_column) or "").strip()
        if not source:
            raise ValueError(f"Kolom kode kosong pada baris CSV {row_number}.")
        sources.append(source)
    if not sources:
        raise ValueError("File CSV tidak berisi data kode.")
    return sources


def evaluate_submitted_dataset(
    filename: str,
    content: bytes,
    bundle: dict[str, Any],
) -> dict[str, Any]:
    """Analyze submitted functions and return comparison-ready metrics."""
    sources = _read_sources(filename, content)
    combined_source = "\n\n".join(textwrap.dedent(source).strip() for source in sources)
    result = analyze_code(combined_source, bundle)
    result = add_automatic_labels(combined_source, result)

    unique_records: dict[str, dict[str, Any]] = {}
    for function in result["functions"]:
        if function.get("actual_label") is None:
            continue
        unique_records[function["code_hash"]] = {
            "code_hash": function["code_hash"],
            "function_name": function["name"],
            "actual_label": function["actual_label"],
            "predicted_label": int(function["is_flagged"]),
            "probability": float(function["probability"]),
            "test_outcome": function["test_outcome"],
        }

    records = list(unique_records.values())
    metrics = evaluate_user_cases(records)
    if metrics is None or not metrics.get("available"):
        reason = metrics.get("reason") if metrics else "Tidak ada fungsi yang dapat diuji."
        raise ValueError(reason)

    return {
        "filename": filename,
        "source": "upload",
        "metrics": metrics,
        "records": records,
        "oracle": result["oracle"],
    }

