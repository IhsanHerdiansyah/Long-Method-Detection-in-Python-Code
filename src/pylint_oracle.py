"""Independent Pylint R0915 labels for user-provided Python code."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def detect_r0915(source: str) -> list[dict[str, Any]]:
    """Return Pylint R0915 messages without executing the user's code."""
    source = source.replace("\r\n", "\n").replace("\r", "\n")
    combined: dict[tuple[int, int], dict[str, Any]] = {}
    last_error = ""
    saw_valid_output = False
    for _ in range(3):
        with tempfile.TemporaryDirectory(prefix="codescope-pylint-") as temp_dir:
            source_path = Path(temp_dir) / "input_analysis.py"
            source_path.write_text(source, encoding="utf-8")
            process = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pylint",
                    "--disable=all",
                    "--enable=R0915",
                    "--output-format=json",
                    "--reports=no",
                    "--score=no",
                    "--persistent=no",
                    str(source_path),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=20,
                check=False,
            )
        if not process.stdout.strip():
            last_error = process.stderr.strip()
            continue
        saw_valid_output = True
        for message in json.loads(process.stdout):
            if message.get("message-id") != "R0915":
                continue
            parsed = {
                "message_id": "R0915",
                "line": int(message.get("line", 0)),
                "column": int(message.get("column", 0)),
                "symbol": message.get("symbol", "too-many-statements"),
                "message": message.get("message", ""),
            }
            combined[(parsed["line"], parsed["column"])] = parsed

    if not combined and not saw_valid_output:
        raise RuntimeError(
            "Pemeriksa R0915 tidak menghasilkan keluaran."
            f" Detail: {last_error}"
        )
    return [combined[key] for key in sorted(combined)]


def add_automatic_labels(source: str, result: dict[str, Any]) -> dict[str, Any]:
    """Attach independent R0915 labels to every analyzed function."""
    messages = detect_r0915(source)
    for function in result["functions"]:
        actual_label = int(
            any(
                function["line_start"] <= message["line"] <= function["line_end"]
                for message in messages
            )
        )
        function["actual_label"] = actual_label
        function["actual_label_name"] = (
            "Long Method" if actual_label else "Bukan Long Method"
        )
        function["actual_label_source"] = "Pylint R0915"
        predicted = int(function["is_flagged"])
        function["test_outcome"] = {
            (0, 0): "Benar negatif",
            (0, 1): "Salah positif",
            (1, 0): "Salah negatif",
            (1, 1): "Benar positif",
        }[(actual_label, predicted)]
    result["oracle"] = {
        "name": "Pylint R0915",
        "message_count": len(messages),
        "messages": messages,
    }
    return result

