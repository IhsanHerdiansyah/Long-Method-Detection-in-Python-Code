"""Generate the conceptual diagrams used in the thesis draft."""

from __future__ import annotations

from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets"
FONT_DIR = Path("C:/Windows/Fonts")


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    text_font: ImageFont.FreeTypeFont,
    max_chars: int,
    fill: str = "#17201E",
) -> None:
    left, top, right, bottom = box
    lines: list[str] = []
    for paragraph in text.split("\n"):
        lines.extend(wrap(paragraph, width=max_chars) or [""])
    spacing = 8
    heights = [draw.textbbox((0, 0), line, font=text_font)[3] for line in lines]
    total_height = sum(heights) + spacing * (len(lines) - 1)
    y = top + (bottom - top - total_height) / 2
    for line, height in zip(lines, heights, strict=True):
        width = draw.textbbox((0, 0), line, font=text_font)[2]
        draw.text(
            (left + (right - left - width) / 2, y),
            line,
            font=text_font,
            fill=fill,
        )
        y += height + spacing


def rounded_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    text_font: ImageFont.FreeTypeFont,
    *,
    fill: str = "#F3F7F6",
    outline: str = "#44645E",
    text_fill: str = "#17201E",
    max_chars: int = 26,
) -> None:
    draw.rounded_rectangle(box, radius=22, fill=fill, outline=outline, width=4)
    draw_centered_text(draw, box, text, text_font, max_chars, text_fill)


def arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    *,
    width: int = 6,
) -> None:
    draw.line([start, end], fill="#36524D", width=width)
    x1, y1 = start
    x2, y2 = end
    if abs(x2 - x1) >= abs(y2 - y1):
        direction = 1 if x2 > x1 else -1
        points = [
            (x2, y2),
            (x2 - direction * 18, y2 - 11),
            (x2 - direction * 18, y2 + 11),
        ]
    else:
        direction = 1 if y2 > y1 else -1
        points = [
            (x2, y2),
            (x2 - 11, y2 - direction * 18),
            (x2 + 11, y2 - direction * 18),
        ]
    draw.polygon(points, fill="#36524D")


def save(image: Image.Image, filename: str) -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    image.save(ASSET_DIR / filename, dpi=(300, 300))


def create_decision_tree() -> None:
    image = Image.new("RGB", (1800, 900), "white")
    draw = ImageDraw.Draw(image)
    title = font("arial.ttf", 34)
    body = font("arial.ttf", 28)
    small = font("arial.ttf", 24)

    draw.text((70, 44), "Struktur konseptual Decision Tree", font=title, fill="#17201E")
    rounded_box(draw, (590, 135, 1210, 260), "Fitur kode\nLOC, parameter, percabangan", body, fill="#1F4E5A", outline="#1F4E5A", text_fill="white")
    rounded_box(draw, (230, 390, 740, 515), "Aturan cabang pertama\n(mis. LOC > batas)", body)
    rounded_box(draw, (1060, 390, 1570, 515), "Aturan cabang berikutnya\n(mis. percabangan > batas)", body)
    rounded_box(draw, (130, 700, 660, 820), "Leaf negatif\nBukan Long Method", small, fill="#E7EFEC")
    rounded_box(draw, (670, 700, 1200, 820), "Leaf positif\nLong Method", small, fill="#F3E9E7", outline="#8E5A50")
    rounded_box(draw, (1210, 700, 1700, 820), "Leaf negatif\nBukan Long Method", small, fill="#E7EFEC")

    arrow(draw, (760, 260), (500, 390))
    arrow(draw, (1040, 260), (1320, 390))
    arrow(draw, (370, 515), (310, 700))
    arrow(draw, (600, 515), (920, 700))
    arrow(draw, (1430, 515), (1450, 700))
    draw.text((510, 615), "Ya", font=small, fill="#36524D")
    draw.text((1240, 615), "Tidak", font=small, fill="#36524D")
    save(image, "gambar_2_1_decision_tree.png")


def create_framework() -> None:
    image = Image.new("RGB", (2200, 850), "white")
    draw = ImageDraw.Draw(image)
    body = font("arial.ttf", 27)
    small = font("arial.ttf", 23)
    boxes = [
        (55, 215, 430, 515, "Masalah\nLong Method"),
        (505, 215, 880, 515, "Dataset Pylint\n156.151 pesan"),
        (955, 215, 1330, 515, "Deduplikasi\n53.807 fungsi unik"),
        (1405, 215, 1780, 515, "AST\n3 fitur statis"),
        (1855, 215, 2160, 515, "Decision Tree"),
    ]
    for i, (left, top, right, bottom, label) in enumerate(boxes):
        fill = "#1F4E5A" if i == 4 else "#F3F7F6"
        outline = "#1F4E5A" if i == 4 else "#44645E"
        text_fill = "white" if i == 4 else "#17201E"
        rounded_box(draw, (left, top, right, bottom), label, body, fill=fill, outline=outline, text_fill=text_fill, max_chars=20)
        if i < len(boxes) - 1:
            arrow(draw, (right + 8, 365), (boxes[i + 1][0] - 8, 365))

    rounded_box(
        draw,
        (955, 635, 2160, 785),
        "Dashboard hasil klasifikasi dan penjelasan untuk ditinjau manusia",
        body,
        fill="#E7EFEC",
        max_chars=48,
    )
    arrow(draw, (1555, 515), (1555, 635))
    draw.text((55, 52), "Kerangka pemikiran penelitian", font=font("arial.ttf", 34), fill="#17201E")
    save(image, "gambar_2_2_kerangka_pemikiran.png")


def create_research_flow() -> None:
    image = Image.new("RGB", (2000, 1120), "white")
    draw = ImageDraw.Draw(image)
    body = font("arial.ttf", 25)
    steps = [
        "1. Identifikasi masalah",
        "2. Pengumpulan dataset",
        "3. Validasi dan deduplikasi",
        "4. Pelabelan R0915",
        "5. Ekstraksi fitur AST",
        "6. Pembagian repository",
        "7. Pelatihan Decision Tree",
        "8. Evaluasi model",
        "9. Pengembangan web",
        "10. Pengujian sistem",
    ]
    positions = [
        (60, 170, 600, 330),
        (730, 170, 1270, 330),
        (1400, 170, 1940, 330),
        (60, 455, 600, 615),
        (730, 455, 1270, 615),
        (1400, 455, 1940, 615),
        (60, 740, 600, 900),
        (730, 740, 1270, 900),
        (1400, 740, 1940, 900),
        (730, 960, 1270, 1080),
    ]
    draw.text((60, 48), "Tahapan penelitian", font=font("arial.ttf", 34), fill="#17201E")
    for index, ((left, top, right, bottom), label) in enumerate(zip(positions, steps, strict=True)):
        rounded_box(
            draw,
            (left, top, right, bottom),
            label,
            body,
            fill="#1F4E5A" if index in (3, 6, 9) else "#F3F7F6",
            outline="#1F4E5A" if index in (3, 6, 9) else "#44645E",
            text_fill="white" if index in (3, 6, 9) else "#17201E",
        )
    arrow(draw, (600, 250), (730, 250))
    arrow(draw, (1270, 250), (1400, 250))
    arrow(draw, (1670, 330), (1670, 455))
    arrow(draw, (1400, 535), (1270, 535))
    arrow(draw, (730, 535), (600, 535))
    arrow(draw, (330, 615), (330, 740))
    arrow(draw, (600, 820), (730, 820))
    arrow(draw, (1270, 820), (1400, 820))
    arrow(draw, (1670, 900), (1200, 965))
    save(image, "gambar_3_1_tahapan_penelitian.png")


def create_system_architecture() -> None:
    image = Image.new("RGB", (2200, 880), "white")
    draw = ImageDraw.Draw(image)
    body = font("arial.ttf", 26)
    small = font("arial.ttf", 22)
    draw.text((55, 45), "Arsitektur aplikasi CodeScope", font=font("arial.ttf", 34), fill="#17201E")

    rounded_box(draw, (45, 220, 385, 540), "Pengguna\nmemasukkan kode\nPython", body)
    rounded_box(draw, (465, 220, 835, 540), "Antarmuka web\nStreamlit", body, fill="#1F4E5A", outline="#1F4E5A", text_fill="white")
    rounded_box(draw, (915, 220, 1285, 540), "Analisis statis\nPython AST", body)
    rounded_box(draw, (1365, 220, 1735, 540), "Model\nDecision Tree", body, fill="#1F4E5A", outline="#1F4E5A", text_fill="white")
    rounded_box(draw, (1815, 220, 2155, 540), "Dashboard\nhasil analisis", body)

    arrow(draw, (385, 380), (465, 380))
    arrow(draw, (835, 380), (915, 380))
    arrow(draw, (1285, 380), (1365, 380))
    arrow(draw, (1735, 380), (1815, 380))

    rounded_box(draw, (465, 680, 1285, 805), "Fitur: LOC, parameter, percabangan", small, fill="#E7EFEC")
    rounded_box(draw, (1365, 680, 2155, 805), "Probabilitas, label, jalur keputusan, saran", small, fill="#E7EFEC")
    save(image, "gambar_3_2_arsitektur_sistem.png")


def main() -> None:
    create_decision_tree()
    create_framework()
    create_research_flow()
    create_system_architecture()
    print(f"Figures written to {ASSET_DIR}")


if __name__ == "__main__":
    main()

