"""Build a de-duplicated, model-ready Long Method dataset."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path

from src.feature_extraction import CodeFormatError, extract_functions


TARGET_MESSAGE_ID = "R0915"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean and transform the raw Pylint code smell dataset."
    )
    parser.add_argument("input_csv", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/long_method_dataset.csv"),
    )
    parser.add_argument(
        "--audit",
        type=Path,
        default=Path("data/processed/data_quality.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    csv.field_size_limit(min(sys.maxsize, 2_147_483_647))
    started = time.perf_counter()
    records: dict[str, dict[str, object]] = {}
    message_counts: Counter[str] = Counter()
    raw_rows = 0
    missing_required = 0
    parse_failed = 0
    promoted_by_duplicate = 0
    multi_function_codes = 0

    with args.input_csv.open("r", encoding="utf-8", newline="", errors="replace") as stream:
        reader = csv.DictReader(stream)
        required = {"msg_id", "code", "func_name", "repository", "commit_id", "path"}
        missing_columns = required.difference(reader.fieldnames or [])
        if missing_columns:
            raise ValueError(f"Missing required CSV columns: {sorted(missing_columns)}")

        for row in reader:
            raw_rows += 1
            code = (row.get("code") or "").strip()
            msg_id = (row.get("msg_id") or "").strip()
            repository = (row.get("repository") or "").strip()
            commit_id = (row.get("commit_id") or "").strip()
            path = (row.get("path") or "").strip()
            if not all((code, msg_id, repository, commit_id, path)):
                missing_required += 1
                continue

            message_counts[msg_id] += 1
            code_hash = hashlib.sha256(code.encode("utf-8")).hexdigest()
            existing = records.get(code_hash)
            if existing is not None:
                if msg_id == TARGET_MESSAGE_ID and not existing["long_method_label"]:
                    existing["long_method_label"] = 1
                    promoted_by_duplicate += 1
                continue

            try:
                functions = extract_functions(code)
            except (CodeFormatError, RecursionError):
                parse_failed += 1
                continue

            if len(functions) > 1:
                multi_function_codes += 1
            function = functions[0]
            records[code_hash] = {
                "record_id": f"LM-{len(records) + 1:06d}",
                "code_hash": code_hash,
                "function_name": function.name or row.get("func_name", ""),
                "nloc": function.nloc,
                "parameter_count": function.parameter_count,
                "branch_count": function.branch_count,
                "long_method_label": int(msg_id == TARGET_MESSAGE_ID),
                "repository": repository,
                "commit_id": commit_id,
                "source_path": path,
            }

            if raw_rows % 25000 == 0:
                print(
                    f"Processed {raw_rows:,} rows; retained {len(records):,} unique functions",
                    flush=True,
                )

    output_rows = list(records.values())
    positives = sum(int(row["long_method_label"]) for row in output_rows)
    negatives = len(output_rows) - positives
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", encoding="utf-8", newline="") as stream:
        fieldnames = list(output_rows[0].keys()) if output_rows else []
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    audit = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source_file": str(args.input_csv),
        "target_definition": (
            "Long Method positif jika fungsi memiliki pesan Pylint R0915 "
            "(too-many-statements) pada salah satu kemunculan duplikat."
        ),
        "feature_definition": {
            "nloc": "Jumlah baris fisik berisi token Python, tanpa baris kosong/komentar.",
            "parameter_count": "Total parameter posisi, keyword, *args, dan **kwargs.",
            "branch_count": (
                "If, For, AsyncFor, While, ExceptHandler, IfExp, MatchCase, "
                "comprehension, dan tambahan cabang pada operasi boolean."
            ),
        },
        "raw_rows": raw_rows,
        "rows_missing_required_values": missing_required,
        "unique_code_functions_after_deduplication": len(output_rows),
        "duplicate_rows_removed": raw_rows - missing_required - parse_failed - len(output_rows),
        "duplicates_promoted_to_positive": promoted_by_duplicate,
        "parse_failed_unique_codes": parse_failed,
        "multi_function_source_codes": multi_function_codes,
        "positive_rows": positives,
        "negative_rows": negatives,
        "positive_rate": round(positives / len(output_rows), 6) if output_rows else 0,
        "raw_message_distribution": dict(message_counts.most_common()),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
    }
    args.audit.parent.mkdir(parents=True, exist_ok=True)
    args.audit.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(audit, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

