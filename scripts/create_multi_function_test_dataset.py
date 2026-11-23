"""Generate a larger multi-function IDE evaluation sample."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "examples" / "multi_function_test.py"


def true_positive(index: int) -> str:
    lines = [f"def test_tp_{index:02d}(value):"]
    for item in range(15):
        lines.extend(
            [
                f"    if value > {item}:",
                f"        result_{item} = value + {item}",
            ]
        )
    for item in range(30):
        lines.append(f"    nilai_{item} = value + {item}")
    lines.append("    return nilai_0")
    return "\n".join(lines)


def false_negative(index: int) -> str:
    lines = [f"def test_fn_{index:02d}(value):"]
    for row in range(5):
        assignments = []
        for item in range(10):
            assignments.append(f"nilai_{row}_{item} = value + {item}")
        lines.append("    " + "; ".join(assignments))
    lines.append("    return nilai_0_0")
    return "\n".join(lines)


def false_positive(index: int) -> str:
    lines = [f"def test_fp_{index:02d}(value):"]
    for item in range(15):
        lines.extend(
            [
                f"    if value > {item}:",
                f"        hasil_{item} = value + {item}",
            ]
        )
    for item in range(15):
        lines.append(f"    nilai_{item} = value + {item}")
    lines.append("    daftar_nilai = [")
    for item in range(12):
        lines.append(f"        {item},")
    lines.extend(["    ]", "    return hasil_0"])
    return "\n".join(lines)


def true_negative(index: int) -> str:
    lines = [f"def test_tn_{index:02d}(value):"]
    for item in range(10):
        lines.append(f"    nilai_{item} = value + {item}")
    lines.append("    return nilai_0")
    return "\n".join(lines)


def main() -> None:
    functions = []
    functions.extend(true_positive(index) for index in range(1, 26))
    functions.extend(false_negative(index) for index in range(1, 4))
    functions.extend(false_positive(index) for index in range(1, 8))
    functions.extend(true_negative(index) for index in range(1, 26))
    content = (
        "# Contoh data uji IDE dengan 60 fungsi.\n"
        "# Label aktual akan dihitung otomatis menggunakan Pylint R0915.\n\n"
        + "\n\n".join(functions)
        + "\n"
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(content, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()

