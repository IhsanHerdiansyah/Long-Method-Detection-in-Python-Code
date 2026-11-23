"""Create a small new test dataset from the built-in examples."""

from pathlib import Path

from src.examples import LONG_METHOD, SHORT_METHOD


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "examples" / "data_uji_baru.py"


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        "# Dataset uji baru: satu fungsi pendek dan satu fungsi panjang.\n"
        "# Label aktual akan dihitung otomatis dengan Pylint R0915.\n\n"
        f"{SHORT_METHOD}\n\n{LONG_METHOD}",
        encoding="utf-8",
    )
    print(OUTPUT)


if __name__ == "__main__":
    main()

