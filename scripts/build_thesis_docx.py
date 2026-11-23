"""Build the Ihsan Herdiansyah thesis draft through Chapter III."""

from __future__ import annotations

import json
import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import (
    WD_ALIGN_PARAGRAPH,
    WD_BREAK,
    WD_LINE_SPACING,
    WD_TAB_ALIGNMENT,
    WD_TAB_LEADER,
)
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets"
OUTPUT_DIR = ROOT / "outputs" / "01a1f4e7-15c2-7620-bb4b-e17fe7aa1889"
OUTPUT_PATH = OUTPUT_DIR / "Dokumen_Skripsi_Ihsan_Herdiansyah_222111011_BAB_I-III.docx"
METRICS_PATH = ROOT / "artifacts" / "metrics.json"
QUALITY_PATH = ROOT / "data" / "processed" / "data_quality.json"
PAGE_MAP_PATH = ROOT / "tmp" / "thesis" / "page_numbers.json"

AUTHOR = "IHSAN HERDIANSYAH"
NPM = "222111011"
PROGRAM = "PROGRAM STUDI INFORMATIKA"
TITLE = (
    "IMPLEMENTASI ALGORITMA DECISION TREE UNTUK KLASIFIKASI "
    "CODE SMELL LONG METHOD PADA KODE PYTHON BERBASIS FITUR STATIS"
)
SUBTITLE = "STUDI KASUS APLIKASI ANALISIS KODE BERBASIS STREAMLIT"


PAGE_DEFAULTS = {
    "judul_dalam": "i",
    "pengesahan": "ii",
    "motto": "iii",
    "pernyataan": "iv",
    "abstrak": "v",
    "abstract": "vi",
    "kata_pengantar": "vii",
    "daftar_isi": "viii",
    "daftar_tabel": "xi",
    "daftar_gambar": "xii",
    "bab1": "1",
    "bab1_1": "1",
    "bab1_2": "2",
    "bab1_3": "3",
    "bab1_4": "4",
    "bab1_5": "5",
    "bab1_6": "6",
    "bab1_7": "7",
    "bab2": "8",
    "bab2_1": "8",
    "bab2_1_1": "8",
    "bab2_1_2": "9",
    "bab2_2": "10",
    "bab2_3": "11",
    "bab2_4": "13",
    "bab2_4_1": "13",
    "bab2_4_2": "14",
    "bab2_4_3": "14",
    "bab2_5": "15",
    "bab2_5_1": "15",
    "bab2_5_2": "16",
    "bab2_5_3": "17",
    "bab2_5_4": "18",
    "bab2_6": "19",
    "bab2_6_1": "19",
    "bab2_6_2": "20",
    "bab2_6_3": "21",
    "bab2_7": "22",
    "bab2_7_1": "22",
    "bab2_7_2": "22",
    "bab2_7_3": "23",
    "bab2_7_4": "23",
    "bab2_8": "24",
    "bab2_9": "26",
    "bab3": "27",
    "bab3_1": "27",
    "bab3_2": "28",
    "bab3_3": "29",
    "bab3_3_1": "29",
    "bab3_3_2": "30",
    "bab3_4": "31",
    "bab3_5": "32",
    "bab3_5_1": "32",
    "bab3_5_2": "33",
    "bab3_5_3": "34",
    "bab3_5_4": "35",
    "bab3_5_5": "36",
    "bab3_6": "37",
    "bab3_6_1": "37",
    "bab3_6_2": "38",
    "bab3_6_3": "39",
    "bab3_6_4": "39",
    "bab3_7": "40",
    "bab3_8": "42",
    "bab3_9": "43",
    "bab3_9_1": "43",
    "bab3_9_2": "44",
    "bab3_9_3": "45",
    "bab3_10": "46",
    "bab3_10_1": "46",
    "bab3_10_2": "47",
    "bab3_10_3": "48",
    "bab3_11": "49",
    "bab3_11_1": "49",
    "bab3_11_2": "50",
    "bab3_11_3": "51",
    "bab3_11_4": "52",
    "bab3_11_5": "53",
    "bab3_11_6": "54",
    "bab3_12": "55",
    "bab3_13": "57",
    "bab3_14": "58",
    "daftar_pustaka": "59",
    "tabel_2_1": "18",
    "tabel_2_2": "20",
    "tabel_2_3": "24",
    "tabel_3_1": "28",
    "tabel_3_2": "31",
    "tabel_3_3": "32",
    "tabel_3_4": "39",
    "tabel_3_5": "40",
    "tabel_3_6": "42",
    "tabel_3_7": "43",
    "tabel_3_8": "45",
    "tabel_3_9": "46",
    "tabel_3_10": "50",
    "tabel_3_11": "56",
    "gambar_2_1": "15",
    "gambar_2_2": "26",
    "gambar_3_1": "28",
    "gambar_3_2": "50",
}


def load_data(path: Path, fallback: dict) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return fallback


def page_numbers() -> dict[str, str]:
    values = dict(PAGE_DEFAULTS)
    if PAGE_MAP_PATH.exists():
        values.update(json.loads(PAGE_MAP_PATH.read_text(encoding="utf-8")))
    return values


def set_run_font(
    run,
    *,
    name: str = "Times New Roman",
    size: float = 12,
    bold: bool | None = None,
    italic: bool | None = None,
    color: RGBColor | None = None,
) -> None:
    run.font.name = name
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = color
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:hAnsi"), name)
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), name)
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:cs"), name)


def style_font(
    style,
    *,
    name: str,
    size: float,
    bold: bool = False,
    italic: bool = False,
) -> None:
    style.font.name = name
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.italic = italic
    style.font.color.rgb = RGBColor(0, 0, 0)
    style._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:ascii"), name)
    style._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:hAnsi"), name)
    style._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), name)
    style._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:cs"), name)


def configure_document(document: Document) -> None:
    styles = document.styles
    style_font(styles["Normal"], name="Times New Roman", size=12)
    normal = styles["Normal"].paragraph_format
    normal.line_spacing = 1.5
    normal.space_before = Pt(0)
    normal.space_after = Pt(0)
    normal.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.first_line_indent = Cm(1.27)

    for style_name, before, after in (
        ("Heading 1", 0, 24),
        ("Heading 2", 18, 12),
        ("Heading 3", 14, 8),
    ):
        style = styles[style_name]
        style_font(style, name="Times New Roman", size=12, bold=True)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.line_spacing = 1.5
        style.paragraph_format.alignment = (
            WD_ALIGN_PARAGRAPH.CENTER
            if style_name == "Heading 1"
            else WD_ALIGN_PARAGRAPH.LEFT
        )
        style.paragraph_format.first_line_indent = Cm(0)

    if "Caption" in styles:
        style_font(styles["Caption"], name="Times New Roman", size=10)
        styles["Caption"].paragraph_format.line_spacing = 1.0
        styles["Caption"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        styles["Caption"].paragraph_format.first_line_indent = Cm(0)

    properties = document.core_properties
    properties.title = TITLE
    properties.author = "Ihsan Herdiansyah"
    properties.subject = "Skripsi sampai BAB III"
    properties.keywords = "code smell, Long Method, Decision Tree, Python, AST"


def configure_section(section) -> None:
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(4)
    section.left_margin = Cm(4)
    section.bottom_margin = Cm(3)
    section.right_margin = Cm(3)
    section.header_distance = Cm(1.5)
    section.footer_distance = Cm(1.5)


def set_page_number_format(section, fmt: str, start: int | None = None) -> None:
    sect_pr = section._sectPr
    page_num_type = sect_pr.find(qn("w:pgNumType"))
    if page_num_type is None:
        page_num_type = OxmlElement("w:pgNumType")
        sect_pr.append(page_num_type)
    page_num_type.set(qn("w:fmt"), fmt)
    if start is not None:
        page_num_type.set(qn("w:start"), str(start))
    elif qn("w:start") in page_num_type.attrib:
        del page_num_type.attrib[qn("w:start")]


def clear_paragraph(paragraph) -> None:
    for child in list(paragraph._element):
        paragraph._element.remove(child)


def set_page_field(paragraph, size: float = 12) -> None:
    run = paragraph.add_run()
    set_run_font(run, size=size)
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instruction, separate, text, end])


def configure_headers_footers(section, mode: str) -> None:
    for part in (section.header, section.footer, section.first_page_header, section.first_page_footer):
        part.is_linked_to_previous = False
        for paragraph in part.paragraphs:
            clear_paragraph(paragraph)

    if mode == "front-numbered":
        footer = section.footer.paragraphs[0]
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer.paragraph_format.space_before = Pt(0)
        footer.paragraph_format.space_after = Pt(0)
        set_page_field(footer)
    elif mode == "chapter":
        section.different_first_page_header_footer = True
        header = section.header.paragraphs[0]
        header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        header.paragraph_format.space_before = Pt(0)
        header.paragraph_format.space_after = Pt(0)
        set_page_field(header)
        footer = section.first_page_footer.paragraphs[0]
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer.paragraph_format.space_before = Pt(0)
        footer.paragraph_format.space_after = Pt(0)
        set_page_field(footer)


def add_new_section(document: Document, mode: str, start: int | None = None):
    section = document.add_section(WD_SECTION.NEW_PAGE)
    configure_section(section)
    configure_headers_footers(section, mode)
    if mode == "front-numbered":
        set_page_number_format(section, "lowerRoman", start)
    elif mode == "chapter":
        set_page_number_format(section, "decimal", start)
    else:
        set_page_number_format(section, "decimal")
    return section


def add_rich_text(paragraph, text: str, *, size: float = 12) -> None:
    tokens = re.split(r"(\*\*.+?\*\*|\*.+?\*)", text)
    for token in tokens:
        if not token:
            continue
        if token.startswith("**") and token.endswith("**"):
            run = paragraph.add_run(token[2:-2])
            set_run_font(run, size=size, bold=True)
        elif token.startswith("*") and token.endswith("*"):
            run = paragraph.add_run(token[1:-1])
            set_run_font(run, size=size, italic=True)
        else:
            run = paragraph.add_run(token)
            set_run_font(run, size=size)


def add_body(document: Document, text: str, *, indent: bool = True) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.line_spacing = 1.5
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.first_line_indent = Cm(1.27) if indent else Cm(0)
    add_rich_text(paragraph, text)


def add_list(document: Document, text: str, level: int = 1) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.left_indent = Cm(1.27 + 0.7 * (level - 1))
    paragraph.paragraph_format.first_line_indent = Cm(-0.5)
    paragraph.paragraph_format.line_spacing = 1.5
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.keep_together = True
    add_rich_text(paragraph, text)


def add_centered(
    document: Document,
    text: str,
    *,
    size: float = 12,
    bold: bool = False,
    italic: bool = False,
    font: str = "Times New Roman",
    before: float = 0,
    after: float = 0,
    line_spacing: float = 1,
) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(before)
    paragraph.paragraph_format.space_after = Pt(after)
    paragraph.paragraph_format.line_spacing = line_spacing
    paragraph.paragraph_format.first_line_indent = Cm(0)
    run = paragraph.add_run(text)
    set_run_font(run, name=font, size=size, bold=bold, italic=italic)


def add_spacer(document: Document, points: float = 12) -> None:
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(points)
    paragraph.paragraph_format.line_spacing = 1


def add_front_heading(
    document: Document,
    text: str,
    *,
    page_break_before: bool = False,
) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(24)
    paragraph.paragraph_format.line_spacing = 1.5
    paragraph.paragraph_format.first_line_indent = Cm(0)
    paragraph.paragraph_format.page_break_before = page_break_before
    run = paragraph.add_run(text)
    set_run_font(run, size=12, bold=True)


def add_chapter_heading(document: Document, number: str, title: str) -> None:
    paragraph = document.add_paragraph(style="Heading 1")
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.page_break_before = False
    run = paragraph.add_run(f"BAB {number}")
    set_run_font(run, size=12, bold=True)
    run.add_break()
    run = paragraph.add_run(title.upper())
    set_run_font(run, size=12, bold=True)
    paragraph.paragraph_format.space_after = Pt(36)


def add_heading(document: Document, text: str, level: int = 2) -> None:
    style_name = "Heading 2" if level == 2 else "Heading 3"
    paragraph = document.add_paragraph(style=style_name)
    run = paragraph.add_run(text)
    set_run_font(run, size=12, bold=True)


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shading = tc_pr.find(qn("w:shd"))
    if shading is None:
        shading = OxmlElement("w:shd")
        tc_pr.append(shading)
    shading.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=90, bottom=80, end=90) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    tr_pr.append(header)


def prevent_row_split(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    tr_pr.append(cant_split)


def fix_table_width(table, widths_cm: list[float]) -> None:
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:type"), "dxa")
    tbl_w.set(qn("w:w"), str(int(sum(widths_cm) * 567)))
    for grid_col, width in zip(table._tbl.tblGrid.gridCol_lst, widths_cm, strict=True):
        grid_col.set(qn("w:w"), str(int(width * 567)))


def add_table_caption(document: Document, number: str, title: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(6)
    paragraph.paragraph_format.space_after = Pt(6)
    paragraph.paragraph_format.line_spacing = 1
    paragraph.paragraph_format.keep_with_next = True
    run = paragraph.add_run(f"Tabel {number}")
    set_run_font(run, size=10)
    run.add_break()
    run = paragraph.add_run(title)
    set_run_font(run, size=10)


def add_table(
    document: Document,
    number: str,
    title: str,
    headers: list[str],
    rows: list[list[str]],
    widths_cm: list[float],
    source: str,
    *,
    alignments: list[str] | None = None,
) -> None:
    add_table_caption(document, number, title)
    table = document.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    table.autofit = False
    fix_table_width(table, widths_cm)
    prevent_row_split(table.rows[0])
    for index, header in enumerate(headers):
        cell = table.rows[0].cells[index]
        cell.width = Cm(widths_cm[index])
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_margins(cell)
        set_cell_shading(cell, "D9E2F3")
        paragraph = cell.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.line_spacing = 1
        paragraph.paragraph_format.first_line_indent = Cm(0)
        run = paragraph.add_run(header)
        set_run_font(run, size=10, bold=True)
    repeat_table_header(table.rows[0])

    for row_index, row_values in enumerate(rows):
        cells = table.add_row().cells
        prevent_row_split(table.rows[-1])
        for column_index, value in enumerate(row_values):
            cell = cells[column_index]
            cell.width = Cm(widths_cm[column_index])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)
            if row_index % 2 == 1:
                set_cell_shading(cell, "F7F9FC")
            paragraph = cell.paragraphs[0]
            alignment = alignments[column_index] if alignments else "left"
            paragraph.alignment = (
                WD_ALIGN_PARAGRAPH.CENTER
                if alignment == "center"
                else WD_ALIGN_PARAGRAPH.RIGHT
                if alignment == "right"
                else WD_ALIGN_PARAGRAPH.LEFT
            )
            paragraph.paragraph_format.line_spacing = 1
            paragraph.paragraph_format.first_line_indent = Cm(0)
            add_rich_text(paragraph, str(value), size=10)

    source_paragraph = document.add_paragraph()
    source_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    source_paragraph.paragraph_format.line_spacing = 1
    source_paragraph.paragraph_format.space_before = Pt(3)
    source_paragraph.paragraph_format.space_after = Pt(12)
    source_paragraph.paragraph_format.first_line_indent = Cm(0)
    run = source_paragraph.add_run(f"Sumber: {source}")
    set_run_font(run, size=10, bold=True)


def add_figure(
    document: Document,
    number: str,
    filename: str,
    caption: str,
    *,
    width_cm: float = 13.5,
) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(6)
    paragraph.paragraph_format.space_after = Pt(4)
    paragraph.paragraph_format.keep_with_next = True
    paragraph.paragraph_format.first_line_indent = Cm(0)
    run = paragraph.add_run()
    shape = run.add_picture(str(ASSET_DIR / filename), width=Cm(width_cm))
    shape._inline.docPr.set("descr", caption)
    shape._inline.docPr.set("title", caption)

    source = document.add_paragraph()
    source.alignment = WD_ALIGN_PARAGRAPH.CENTER
    source.paragraph_format.line_spacing = 1
    source.paragraph_format.space_after = Pt(0)
    source.paragraph_format.first_line_indent = Cm(0)
    run = source.add_run("Sumber: rancangan penelitian, 2026")
    set_run_font(run, size=10)

    caption_paragraph = document.add_paragraph()
    caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption_paragraph.paragraph_format.line_spacing = 1
    caption_paragraph.paragraph_format.space_before = Pt(3)
    caption_paragraph.paragraph_format.space_after = Pt(12)
    caption_paragraph.paragraph_format.first_line_indent = Cm(0)
    run = caption_paragraph.add_run(f"Gambar {number}")
    set_run_font(run, size=10)
    run.add_break()
    run = caption_paragraph.add_run(caption)
    set_run_font(run, size=10)


def add_cover(document: Document) -> None:
    add_spacer(document, 2)
    add_centered(document, TITLE, size=14, bold=True, line_spacing=1.05)
    add_spacer(document, 24)
    add_centered(document, SUBTITLE, size=12, bold=True, font="Tahoma")
    add_spacer(document, 42)
    add_centered(document, "TUGAS AKHIR", size=12, bold=True, font="Arial")
    add_centered(
        document,
        "Diajukan Sebagai Salah Satu Syarat\n"
        "Untuk Memperoleh Gelar Sarjana\n"
        "Di Universitas Informatika dan Bisnis Indonesia",
        size=11,
        font="Arial",
        line_spacing=1,
    )
    add_spacer(document, 36)
    add_centered(document, "Disusun oleh :", size=12, line_spacing=1)
    add_spacer(document, 12)
    add_centered(document, AUTHOR, size=14, bold=True)
    add_centered(document, NPM, size=14, bold=True)
    add_spacer(document, 24)
    logo = document.add_paragraph()
    logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    logo.paragraph_format.space_after = Pt(12)
    logo_shape = logo.add_run().add_picture(
        str(ASSET_DIR / "unibi_logo.png"),
        width=Cm(4.2),
    )
    logo_shape._inline.docPr.set(
        "descr",
        "Logo Universitas Informatika dan Bisnis Indonesia",
    )
    logo_shape._inline.docPr.set(
        "title",
        "Logo Universitas Informatika dan Bisnis Indonesia",
    )
    add_centered(document, PROGRAM, size=12, bold=True, font="Tahoma", line_spacing=1)
    add_centered(
        document,
        "FAKULTAS TEKNOLOGI DAN INFORMATIKA",
        size=12,
        bold=True,
        font="Tahoma",
        line_spacing=1,
    )
    add_centered(
        document,
        "UNIVERSITAS INFORMATIKA DAN BISNIS INDONESIA",
        size=12,
        bold=True,
        font="Tahoma",
        line_spacing=1,
    )
    add_centered(document, "2026", size=12, bold=True, font="Tahoma", line_spacing=1)


def add_approval_page(document: Document) -> None:
    add_front_heading(document, "LEMBAR PENGESAHAN")
    rows = [
        ("JUDUL", ":", TITLE),
        ("SUB JUDUL", ":", SUBTITLE),
        ("PENYUSUN", ":", AUTHOR),
        ("NPM", ":", NPM),
    ]
    table = document.add_table(rows=len(rows), cols=3)
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    widths = (3.1, 0.5, 10.4)
    fix_table_width(table, list(widths))
    for index, width in enumerate(widths):
        table.columns[index].width = Cm(width)
    repeat_table_header(table.rows[0])
    for row_index, row in enumerate(rows):
        for column_index, value in enumerate(row):
            cell = table.rows[row_index].cells[column_index]
            cell.width = Cm(widths[column_index])
            set_cell_margins(cell, top=40, bottom=40)
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.line_spacing = 1
            paragraph.paragraph_format.first_line_indent = Cm(0)
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = paragraph.add_run(str(value))
            set_run_font(run, size=11, bold=True if row_index < 4 else False)
    add_spacer(document, 24)
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.line_spacing = 1.15
    paragraph.paragraph_format.first_line_indent = Cm(0)
    run = paragraph.add_run(
        "Telah dilakukan sidang pada tanggal .................................... "
        "dan telah disahkan oleh:"
    )
    set_run_font(run, size=11)
    add_spacer(document, 72)
    signatures = document.add_table(rows=2, cols=3)
    signatures.autofit = False
    fix_table_width(signatures, [4.5, 4.5, 4.5])
    for column in signatures.columns:
        column.width = Cm(4.5)
    repeat_table_header(signatures.rows[0])
    labels = ["Ketua Penguji", "Pembimbing Utama", "Pembimbing Pendamping"]
    for index, label in enumerate(labels):
        cell = signatures.rows[0].cells[index]
        cell.width = Cm(4.5)
        paragraph = cell.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.first_line_indent = Cm(0)
        run = paragraph.add_run(label)
        set_run_font(run, size=11, bold=True)
        cell2 = signatures.rows[1].cells[index]
        cell2.width = Cm(4.5)
        paragraph = cell2.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.space_before = Pt(72)
        paragraph.paragraph_format.first_line_indent = Cm(0)
        run = paragraph.add_run("(.....................................)")
        set_run_font(run, size=10)
    add_spacer(document, 36)
    add_centered(document, "Bandung, .............................. 2026", size=11)


def add_motto_page(document: Document) -> None:
    add_front_heading(document, "MOTTO DAN PERSEMBAHAN")
    add_spacer(document, 48)
    add_centered(
        document,
        '"Kemudahan biasanya datang setelah pekerjaan sulit dikerjakan dengan tertib."',
        size=12,
        italic=True,
        line_spacing=1.5,
    )
    add_spacer(document, 96)
    add_centered(
        document,
        "Karya ini dipersembahkan kepada orang tua, keluarga, dosen pembimbing, "
        "serta rekan-rekan yang telah memberikan dukungan selama proses penyusunan "
        "Tugas Akhir.",
        size=12,
        line_spacing=1.5,
    )


def add_authenticity_page(document: Document) -> None:
    add_front_heading(document, "HALAMAN PERNYATAAN KEASLIAN")
    add_body(
        document,
        "Yang bertanda tangan di bawah ini:",
        indent=False,
    )
    for line in (
        f"**Nama mahasiswa :** {AUTHOR}",
        f"**NPM :** {NPM}",
        f"**Program Studi :** {PROGRAM.replace('PROGRAM STUDI ', '').title()}",
    ):
        add_body(document, line, indent=False)
    add_spacer(document, 2)
    add_body(document, "Menyatakan bahwa Tugas Akhir dengan judul:", indent=False)
    add_body(document, f"\u201c{TITLE}\u201d", indent=False)
    add_spacer(document, 2)
    items = [
        "Karya tulis ini adalah benar-benar asli dan belum pernah diajukan untuk memperoleh gelar akademik, baik di Universitas Informatika dan Bisnis Indonesia maupun di perguruan tinggi lain.",
        "Karya tulis ini merupakan gagasan, rumusan, dan penelitian penulis sendiri tanpa bantuan pihak lain, kecuali arahan dari tim dosen pembimbing.",
        "Dalam karya tulis ini tidak terdapat karya atau pendapat orang lain, kecuali yang secara tertulis dikutip dengan jelas sebagai acuan dan disebutkan dalam Daftar Pustaka.",
        "Perangkat lunak yang digunakan dalam penelitian ini menjadi tanggung jawab penulis, bukan tanggung jawab Universitas Informatika dan Bisnis Indonesia.",
        "Pernyataan ini dibuat dengan sungguh-sungguh. Apabila di kemudian hari terdapat penyimpangan atau ketidakbenaran, penulis bersedia menerima sanksi akademik sesuai ketentuan yang berlaku.",
    ]
    for index, item in enumerate(items, start=1):
        paragraph = document.add_paragraph()
        paragraph.paragraph_format.left_indent = Cm(1.27)
        paragraph.paragraph_format.first_line_indent = Cm(-0.6)
        paragraph.paragraph_format.line_spacing = 1
        paragraph.paragraph_format.space_after = Pt(2)
        add_rich_text(paragraph, f"{index}. {item}")
    add_spacer(document, 10)
    add_body(document, "Bandung, .............................. 2026", indent=False)
    add_body(document, "Yang menyatakan,", indent=False)
    add_spacer(document, 38)
    add_body(document, AUTHOR, indent=False)
    add_body(document, NPM, indent=False)


def add_abstracts(document: Document) -> None:
    metrics = load_data(METRICS_PATH, {"metrics": {}, "dataset": {}})
    metric = metrics["metrics"]
    dataset = metrics["dataset"]
    add_front_heading(document, "ABSTRAK")
    add_centered(document, AUTHOR, size=12, bold=True, line_spacing=1)
    add_centered(document, NPM, size=12, bold=True, line_spacing=1)
    add_spacer(document, 6)
    add_centered(document, TITLE, size=12, bold=True, line_spacing=1)
    add_spacer(document, 10)
    abstract_paragraphs = [
        (
            "Kualitas kode memengaruhi biaya pemeliharaan dan risiko kesalahan "
            "ketika perangkat lunak dikembangkan. Long Method merupakan salah satu "
            "code smell yang muncul ketika sebuah metode memuat terlalu banyak "
            "instruksi sehingga sulit dipahami dan diuji. Penelitian ini merancang "
            "prototipe web untuk mengklasifikasikan Long Method pada kode Python "
            "berdasarkan fitur statis."
        ),
        (
            f"Dataset awal berisi {int(dataset.get('raw_rows', 156151)):,} pesan "
            f"Pylint dari 118 repository. Setelah validasi dan deduplikasi berbasis "
            f"hash kode, diperoleh {int(dataset.get('rows', 53807)):,} fungsi unik. "
            "Setiap fungsi dianalisis menggunakan Abstract Syntax Tree untuk menghitung "
            "non-comment LOC, jumlah parameter, dan jumlah percabangan. Label positif "
            "ditentukan dari pesan R0915 atau too-many-statements. Model Decision Tree "
            "dilatih dengan pembagian repository 80 persen data latih dan 20 persen "
            "data uji."
        ),
        (
            "Rancangan evaluasi menggunakan confusion matrix, precision, recall, "
            "F1-score, ROC-AUC, dan average precision. Pengujian awal menghasilkan "
            f"precision {metric.get('precision', 0):.3f}, recall "
            f"{metric.get('recall', 0):.3f}, F1-score {metric.get('f1_score', 0):.3f}, "
            f"dan ROC-AUC {metric.get('roc_auc', 0):.3f}. Prototipe web menampilkan "
            "label prediksi, probabilitas, nilai fitur, jalur keputusan model, dan "
            "saran peninjauan agar hasil klasifikasi dapat dipahami."
        ),
    ]
    for paragraph_text in abstract_paragraphs:
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        paragraph.paragraph_format.line_spacing = 1
        paragraph.paragraph_format.space_after = Pt(12)
        paragraph.paragraph_format.first_line_indent = Cm(1.27)
        add_rich_text(paragraph, paragraph_text)
    keyword = document.add_paragraph()
    keyword.paragraph_format.line_spacing = 1
    keyword.paragraph_format.first_line_indent = Cm(0)
    add_rich_text(
        keyword,
        "**Kata kunci:** code smell, Long Method, Decision Tree, Python, fitur statis",
    )

    add_front_heading(document, "ABSTRACT", page_break_before=True)
    add_centered(document, AUTHOR.title(), size=12, bold=True, line_spacing=1, italic=True)
    add_centered(document, NPM, size=12, bold=True, line_spacing=1, italic=True)
    add_spacer(document, 6)
    add_centered(document, TITLE.title(), size=12, bold=True, line_spacing=1, italic=True)
    add_spacer(document, 10)
    english_paragraphs = [
        (
            "Code quality affects maintenance cost and the risk of defects as software "
            "evolves. Long Method is a code smell in which a function contains too many "
            "statements and becomes difficult to understand and test. This study designs "
            "a web prototype that classifies Long Method in Python functions using static "
            "code features."
        ),
        (
            f"The initial dataset contains {int(dataset.get('raw_rows', 156151)):,} Pylint "
            f"messages collected from 118 repositories. Validation and hash-based "
            f"deduplication produced {int(dataset.get('rows', 53807)):,} unique functions. "
            "A Python Abstract Syntax Tree is used to calculate non-comment lines of code, "
            "parameter count, and branch count. A function is labeled positive when its "
            "Pylint output includes R0915 or too-many-statements. A Decision Tree is trained "
            "using an 80/20 repository-based split."
        ),
        (
            "The evaluation protocol uses a confusion matrix, precision, recall, F1-score, "
            "ROC-AUC, and average precision. Preliminary testing produced precision "
            f"{metric.get('precision', 0):.3f}, recall {metric.get('recall', 0):.3f}, "
            f"F1-score {metric.get('f1_score', 0):.3f}, and ROC-AUC "
            f"{metric.get('roc_auc', 0):.3f}. The web interface presents the prediction, "
            "probability, feature values, decision path, and review recommendation."
        ),
    ]
    for paragraph_text in english_paragraphs:
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        paragraph.paragraph_format.line_spacing = 1
        paragraph.paragraph_format.space_after = Pt(12)
        paragraph.paragraph_format.first_line_indent = Cm(1.27)
        add_rich_text(paragraph, paragraph_text)
        for run in paragraph.runs:
            run.italic = True
    keyword = document.add_paragraph()
    keyword.paragraph_format.line_spacing = 1
    keyword.paragraph_format.first_line_indent = Cm(0)
    add_rich_text(
        keyword,
        "**Keywords:** code smell, Long Method, Decision Tree, Python, static features",
    )
    for run in keyword.runs:
        run.italic = True


def add_preface(document: Document) -> None:
    add_front_heading(document, "KATA PENGANTAR", page_break_before=True)
    paragraphs = [
        (
            "Puji syukur dipanjatkan kepada Tuhan Yang Maha Esa atas rahmat dan "
            "karunia-Nya sehingga penyusunan Tugas Akhir ini dapat berjalan "
            "sampai tahap perancangan metode dan sistem."
        ),
        (
            "Tugas Akhir ini disusun sebagai salah satu syarat untuk memperoleh "
            "gelar Sarjana pada Program Studi Informatika, Fakultas Teknologi dan "
            "Informatika, Universitas Informatika dan Bisnis Indonesia. Penelitian "
            "membahas penggunaan Decision Tree untuk mengklasifikasikan Long Method "
            "pada kode Python berdasarkan fitur statis."
        ),
        (
            "Penulis mengucapkan terima kasih kepada dosen pembimbing atas arahan "
            "metodologis, kepada program studi atas dukungan administrasi, kepada "
            "orang tua dan keluarga atas dukungan yang diberikan, serta kepada "
            "rekan-rekan yang membantu proses diskusi dan pengujian."
        ),
        (
            "Penulis menyadari bahwa dokumen ini masih dapat dikembangkan. Kritik "
            "dan saran yang berkaitan dengan ketepatan metode, penulisan, dan "
            "pengujian sistem akan digunakan untuk memperbaiki Tugas Akhir."
        ),
    ]
    for paragraph_text in paragraphs:
        add_body(document, paragraph_text)
    add_spacer(document, 24)
    add_body(document, "Bandung, 20 November 2026", indent=False)
    add_body(document, "Penulis", indent=False)


def add_toc_entry(
    document: Document,
    text: str,
    page: str,
    level: int = 0,
    *,
    bold: bool = False,
) -> None:
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.left_indent = Cm(0.7 * level)
    paragraph.paragraph_format.first_line_indent = Cm(0)
    paragraph.paragraph_format.line_spacing = 1.15
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.tab_stops.add_tab_stop(
        Cm(14 - 0.7 * level),
        WD_TAB_ALIGNMENT.RIGHT,
        WD_TAB_LEADER.DOTS,
    )
    run = paragraph.add_run(text)
    set_run_font(run, size=11, bold=bold)
    run = paragraph.add_run("\t" + page)
    set_run_font(run, size=11, bold=bold)


def add_toc(document: Document, pages: dict[str, str]) -> None:
    add_front_heading(document, "DAFTAR ISI", page_break_before=True)
    add_centered(document, "Halaman", size=10, bold=True, after=8)
    entries = [
        ("HALAMAN JUDUL DALAM", "judul_dalam", 0),
        ("LEMBAR PENGESAHAN", "pengesahan", 0),
        ("MOTTO DAN PERSEMBAHAN", "motto", 0),
        ("HALAMAN PERNYATAAN KEASLIAN", "pernyataan", 0),
        ("ABSTRAK", "abstrak", 0),
        ("ABSTRACT", "abstract", 0),
        ("KATA PENGANTAR", "kata_pengantar", 0),
        ("DAFTAR ISI", "daftar_isi", 0),
        ("DAFTAR TABEL", "daftar_tabel", 0),
        ("DAFTAR GAMBAR", "daftar_gambar", 0),
        ("BAB I PENDAHULUAN", "bab1", 0),
        ("1.1 Latar Belakang", "bab1_1", 1),
        ("1.2 Identifikasi Masalah", "bab1_2", 1),
        ("1.3 Rumusan Masalah", "bab1_3", 1),
        ("1.4 Batasan Masalah", "bab1_4", 1),
        ("1.5 Maksud dan Tujuan Penelitian", "bab1_5", 1),
        ("1.6 Manfaat Penelitian", "bab1_6", 1),
        ("1.7 Sistematika Penulisan", "bab1_7", 1),
        ("BAB II LANDASAN TEORI", "bab2", 0),
        ("2.1 Kualitas Perangkat Lunak dan Code Smell", "bab2_1", 1),
        ("2.1.1 Kualitas Perangkat Lunak", "bab2_1_1", 2),
        ("2.1.2 Code Smell", "bab2_1_2", 2),
        ("2.2 Long Method sebagai Code Smell", "bab2_2", 1),
        ("2.3 Analisis Statis dan Abstract Syntax Tree", "bab2_3", 1),
        ("2.4 Fitur Statis Long Method", "bab2_4", 1),
        ("2.4.1 Non-comment Lines of Code", "bab2_4_1", 2),
        ("2.4.2 Jumlah Parameter", "bab2_4_2", 2),
        ("2.4.3 Jumlah Percabangan", "bab2_4_3", 2),
        ("2.5 Algoritma Decision Tree", "bab2_5", 1),
        ("2.5.1 Konsep Dasar Decision Tree", "bab2_5_1", 2),
        ("2.5.2 Pembentukan Pohon Keputusan", "bab2_5_2", 2),
        ("2.5.3 Prediksi dan Threshold", "bab2_5_3", 2),
        ("2.5.4 Kelebihan dan Keterbatasan", "bab2_5_4", 2),
        ("2.6 Evaluasi Model Klasifikasi", "bab2_6", 1),
        ("2.6.1 Confusion Matrix", "bab2_6_1", 2),
        ("2.6.2 Precision, Recall, dan F1-score", "bab2_6_2", 2),
        ("2.6.3 ROC-AUC dan Average Precision", "bab2_6_3", 2),
        ("2.7 Teknologi Pendukung", "bab2_7", 1),
        ("2.7.1 Bahasa Pemrograman Python", "bab2_7_1", 2),
        ("2.7.2 pandas dan NumPy", "bab2_7_2", 2),
        ("2.7.3 scikit-learn", "bab2_7_3", 2),
        ("2.7.4 Streamlit", "bab2_7_4", 2),
        ("2.8 Penelitian Terdahulu", "bab2_8", 1),
        ("2.9 Kerangka Pemikiran", "bab2_9", 1),
        ("BAB III METODOLOGI PENELITIAN", "bab3", 0),
        ("3.1 Jenis dan Pendekatan Penelitian", "bab3_1", 1),
        ("3.2 Tahapan Penelitian", "bab3_2", 1),
        ("3.3 Sumber dan Objek Penelitian", "bab3_3", 1),
        ("3.3.1 Dataset Penelitian", "bab3_3_1", 2),
        ("3.3.2 Lingkungan Penelitian", "bab3_3_2", 2),
        ("3.4 Definisi Operasional Variabel", "bab3_4", 1),
        ("3.5 Pra-pemrosesan Dataset", "bab3_5", 1),
        ("3.5.1 Validasi Struktur Data", "bab3_5_1", 2),
        ("3.5.2 Pemeriksaan Nilai Kosong", "bab3_5_2", 2),
        ("3.5.3 Deduplikasi Data", "bab3_5_3", 2),
        ("3.5.4 Penentuan Label", "bab3_5_4", 2),
        ("3.5.5 Penanganan Data Tidak Valid", "bab3_5_5", 2),
        ("3.6 Ekstraksi Fitur Statis", "bab3_6", 1),
        ("3.6.1 Parsing Kode dengan AST", "bab3_6_1", 2),
        ("3.6.2 Perhitungan Non-comment LOC", "bab3_6_2", 2),
        ("3.6.3 Perhitungan Parameter", "bab3_6_3", 2),
        ("3.6.4 Perhitungan Percabangan", "bab3_6_4", 2),
        ("3.7 Profil Dataset Hasil Pembersihan", "bab3_7", 1),
        ("3.8 Pembagian Data Latih dan Data Uji", "bab3_8", 1),
        ("3.9 Pelatihan Model Decision Tree", "bab3_9", 1),
        ("3.9.1 Konfigurasi Pelatihan", "bab3_9_1", 2),
        ("3.9.2 Pencarian Hyperparameter", "bab3_9_2", 2),
        ("3.9.3 Penentuan Threshold", "bab3_9_3", 2),
        ("3.10 Rancangan Evaluasi Model", "bab3_10", 1),
        ("3.10.1 Confusion Matrix", "bab3_10_1", 2),
        ("3.10.2 Metrik Klasifikasi", "bab3_10_2", 2),
        ("3.10.3 Pengujian Generalisasi", "bab3_10_3", 2),
        ("3.11 Rancangan Sistem", "bab3_11", 1),
        ("3.11.1 Kebutuhan Fungsional", "bab3_11_1", 2),
        ("3.11.2 Kebutuhan Nonfungsional", "bab3_11_2", 2),
        ("3.11.3 Arsitektur Sistem", "bab3_11_3", 2),
        ("3.11.4 Alur Analisis Kode", "bab3_11_4", 2),
        ("3.11.5 Rancangan Dashboard", "bab3_11_5", 2),
        ("3.11.6 Penjelasan Istilah pada Antarmuka", "bab3_11_6", 2),
        ("3.12 Skenario Pengujian", "bab3_12", 1),
        ("3.13 Indikator Keberhasilan", "bab3_13", 1),
        ("3.14 Etika Penelitian dan Keterbatasan", "bab3_14", 1),
        ("DAFTAR PUSTAKA", "daftar_pustaka", 0),
    ]
    for text, key, level in entries:
        add_toc_entry(
            document,
            text,
            pages.get(key, "00"),
            level,
            bold=level == 0,
        )


def add_list_of_tables(document: Document, pages: dict[str, str]) -> None:
    add_front_heading(document, "DAFTAR TABEL", page_break_before=True)
    add_centered(document, "Halaman", size=10, bold=True, after=8)
    entries = [
        ("Tabel 2.1", "Perbandingan Fitur Statis Long Method", "tabel_2_1"),
        ("Tabel 2.2", "Confusion Matrix Dua Kelas", "tabel_2_2"),
        ("Tabel 2.3", "Ringkasan Penelitian Terdahulu", "tabel_2_3"),
        ("Tabel 3.1", "Tahapan, Aktivitas, dan Luaran Penelitian", "tabel_3_1"),
        ("Tabel 3.2", "Definisi Operasional Variabel", "tabel_3_2"),
        ("Tabel 3.3", "Aturan Pembersihan Dataset", "tabel_3_3"),
        ("Tabel 3.4", "Fitur Statis dan Cara Perhitungan", "tabel_3_4"),
        ("Tabel 3.5", "Profil Dataset Hasil Pembersihan", "tabel_3_5"),
        ("Tabel 3.6", "Perbandingan Rata-rata Fitur per Label", "tabel_3_6"),
        ("Tabel 3.7", "Pembagian Data Latih dan Data Uji", "tabel_3_7"),
        ("Tabel 3.8", "Konfigurasi Hyperparameter Decision Tree", "tabel_3_8"),
        ("Tabel 3.9", "Metrik dan Interpretasi Evaluasi", "tabel_3_9"),
        ("Tabel 3.10", "Kebutuhan Fungsional Aplikasi", "tabel_3_10"),
        ("Tabel 3.11", "Skenario Pengujian Sistem", "tabel_3_11"),
    ]
    for number, title, key in entries:
        add_toc_entry(document, f"{number} {title}", pages.get(key, "00"), 0)


def add_list_of_figures(document: Document, pages: dict[str, str]) -> None:
    add_front_heading(document, "DAFTAR GAMBAR", page_break_before=True)
    add_centered(document, "Halaman", size=10, bold=True, after=8)
    entries = [
        ("Gambar 2.1", "Struktur Konseptual Decision Tree", "gambar_2_1"),
        ("Gambar 2.2", "Kerangka Pemikiran Penelitian", "gambar_2_2"),
        ("Gambar 3.1", "Tahapan Penelitian", "gambar_3_1"),
        ("Gambar 3.2", "Arsitektur Aplikasi CodeScope", "gambar_3_2"),
    ]
    for number, title, key in entries:
        add_toc_entry(document, f"{number} {title}", pages.get(key, "00"), 0)


def add_numbered_items(document: Document, items: list[str]) -> None:
    for index, item in enumerate(items, start=1):
        add_list(document, f"{index}. {item}")


def add_bab_one_clean(document: Document) -> None:
    add_chapter_heading(document, "I", "PENDAHULUAN")
    add_heading(document, "1.1 Latar Belakang")
    for text in [
        (
            "Kualitas perangkat lunak dipengaruhi oleh struktur kode yang digunakan "
            "selama proses pengembangan. Kode yang sulit dipahami dapat meningkatkan "
            "biaya pemeliharaan, memperlambat penambahan fitur, dan memperbesar risiko "
            "kesalahan ketika perubahan dilakukan (Sommerville, 2016). Pemeriksaan "
            "kualitas tidak cukup dilakukan melalui pengujian fungsi, karena masalah "
            "struktur sering tetap terlihat pada kode yang menghasilkan keluaran benar."
        ),
        (
            "Fowler (2018) menjelaskan *code smell* sebagai tanda pada struktur kode "
            "yang menunjukkan kemungkinan adanya masalah desain. Salah satu jenis "
            "*code smell* yang umum ditemukan adalah *Long Method*, yaitu fungsi atau "
            "metode yang memiliki terlalu banyak instruksi, kondisi, atau langkah kerja. "
            "*Long Method* menyulitkan pembacaan, pengujian, pemakaian ulang, dan "
            "penelusuran kesalahan karena satu fungsi menangani beberapa tanggung jawab "
            "sekaligus."
        ),
        (
            "Pemeriksaan manual terhadap setiap fungsi tidak sebanding dengan jumlah "
            "kode yang harus ditinjau. Pendekatan berbasis aturan seperti *linter* dapat "
            "membantu, tetapi hasilnya bergantung pada ambang batas yang ditetapkan. "
            "Ambang yang terlalu rendah menghasilkan banyak peringatan, sedangkan ambang "
            "yang terlalu tinggi dapat melewatkan fungsi yang bermasalah. Aturan tunggal "
            "juga belum tentu menggambarkan hubungan antarbeberapa ukuran kode."
        ),
        (
            "Decision Tree merupakan algoritma klasifikasi yang menyusun keputusan "
            "melalui serangkaian aturan berbentuk pohon (Breiman et al., 1984). Setiap "
            "simpul memeriksa nilai fitur, lalu mengarahkan data ke cabang berikutnya "
            "sampai mencapai *leaf*. Bentuk aturan tersebut membuat hasil model dapat "
            "ditelusuri. Kemampuan ini sesuai untuk penelitian yang tidak hanya "
            "memerlukan label prediksi, tetapi juga penjelasan mengenai faktor yang "
            "memengaruhi prediksi (Pedregosa et al., 2011)."
        ),
        (
            "Penelitian ini menggunakan tiga fitur statis yang dapat diperoleh langsung "
            "dari struktur sintaks Python. *Non-comment lines of code* (LOC) mengukur "
            "banyaknya baris kode bermakna. Jumlah parameter menunjukkan banyaknya nilai "
            "yang harus diberikan kepada fungsi. Jumlah percabangan menunjukkan banyaknya "
            "jalur keputusan yang mungkin terjadi. Ketiga fitur diambil menggunakan "
            "*Abstract Syntax Tree* (AST) agar tidak bergantung pada pola teks tertentu "
            "(Python Software Foundation, 2026)."
        ),
        (
            "Dataset penelitian berisi pesan Pylint dari repository Python publik. "
            "Pesan dengan kode R0915, yaitu *too-many-statements*, digunakan sebagai "
            "sinyal positif *Long Method*. Dataset tersebut belum dapat langsung "
            "digunakan karena satu fungsi dapat muncul berulang kali pada beberapa pesan "
            "Pylint. Oleh karena itu, diperlukan validasi, deduplikasi, pelabelan, dan "
            "ekstraksi fitur yang konsisten sebelum model dilatih."
        ),
        (
            "Hasil penelitian dirancang dalam bentuk aplikasi web berbasis Streamlit. "
            "Pengguna memasukkan kode Python, sistem mengekstraksi fitur, model "
            "menghasilkan probabilitas, dan dashboard menampilkan keputusan beserta jalur "
            "aturan yang dilalui model. Aplikasi juga menyediakan penjelasan istilah "
            "melalui ikon informasi agar pengguna dapat memahami istilah teknis tanpa "
            "harus membaca dokumentasi terlebih dahulu."
        ),
    ]:
        add_body(document, text)
    add_heading(document, "1.2 Identifikasi Masalah")
    add_numbered_items(
        document,
        [
            "Struktur fungsi yang terlalu panjang dapat menyulitkan pembacaan, pengujian, dan pemeliharaan kode.",
            "Pemeriksaan *Long Method* secara manual tidak praktis ketika ukuran proyek bertambah.",
            "Pendekatan berbasis ambang tunggal belum menggabungkan beberapa ukuran struktur kode sekaligus.",
            "Diperlukan model klasifikasi yang menghasilkan keputusan dan penjelasan aturan yang dapat ditelusuri.",
            "Hasil model perlu disampaikan melalui antarmuka yang menampilkan fitur, probabilitas, dan istilah teknis secara mudah dipahami.",
        ],
    )
    add_heading(document, "1.3 Rumusan Masalah")
    add_body(
        document,
        "Berdasarkan identifikasi masalah, rumusan masalah penelitian disusun sebagai berikut.",
    )
    add_numbered_items(
        document,
        [
            "Bagaimana mengekstraksi fitur statis dari kode Python menggunakan AST?",
            "Bagaimana menyiapkan dataset pesan Pylint menjadi data klasifikasi *Long Method* yang bersih dan tidak memiliki duplikasi berlebih?",
            "Bagaimana menerapkan Decision Tree untuk mengklasifikasikan *Long Method* berdasarkan LOC, jumlah parameter, dan jumlah percabangan?",
            "Bagaimana merancang aplikasi web yang menampilkan hasil klasifikasi dan faktor yang memengaruhi prediksi?",
        ],
    )
    add_heading(document, "1.4 Batasan Masalah")
    add_body(
        document,
        "Agar penelitian memiliki ruang lingkup yang terukur, batasan masalah ditetapkan sebagai berikut.",
    )
    add_numbered_items(
        document,
        [
            "Kode yang dianalisis dibatasi pada fungsi dan metode Python yang dapat diuraikan oleh modul ast.",
            "Jenis *code smell* yang diklasifikasikan hanya *Long Method*.",
            "Label positif menggunakan pesan Pylint R0915 (*too-many-statements*) sebagai representasi *Long Method*.",
            "Fitur model dibatasi pada non-comment LOC, jumlah parameter, dan jumlah percabangan.",
            "Algoritma klasifikasi utama adalah Decision Tree dari *library* scikit-learn.",
            "Antarmuka prototipe dikembangkan menggunakan Streamlit.",
            "Dokumen ini disusun sampai BAB III sehingga pembahasan hasil akhir dan kesimpulan belum dicantumkan.",
        ],
    )
    add_heading(document, "1.5 Maksud dan Tujuan Penelitian")
    add_body(
        document,
        "Maksud penelitian adalah menyediakan prototipe yang membantu pengembang menentukan fungsi Python yang perlu diperiksa karena memiliki indikasi *Long Method*. Tujuan penelitian diuraikan sebagai berikut.",
    )
    add_numbered_items(
        document,
        [
            "Mengembangkan proses ekstraksi fitur statis dari kode Python.",
            "Menghasilkan dataset yang telah divalidasi, dideduplikasi, dan diberi label.",
            "Menerapkan Decision Tree untuk klasifikasi *Long Method*.",
            "Menyediakan dashboard yang menampilkan prediksi, probabilitas, fitur, dan jalur keputusan.",
        ],
    )
    add_heading(document, "1.6 Manfaat Penelitian")
    add_body(
        document,
        "Manfaat teoretis penelitian adalah menambah penerapan Decision Tree dan fitur AST pada klasifikasi kualitas kode, khususnya *Long Method*. Penelitian juga menunjukkan cara menyusun label dari pesan Pylint dan bagaimana menjaga pemisahan data agar evaluasi tidak mengalami kebocoran.",
    )
    add_body(
        document,
        "Manfaat praktis penelitian adalah menyediakan prototipe pemeriksaan awal bagi pengembang Python. Pengguna dapat memasukkan fungsi, melihat nilai fitur, dan mengetahui fungsi yang perlu diperiksa lebih lanjut. Dashboard membantu menjelaskan keputusan model meskipun pengguna tidak memiliki latar belakang *machine learning*.",
    )
    add_heading(document, "1.7 Sistematika Penulisan")
    add_body(
        document,
        "Dokumen ini terdiri atas tiga bab utama. BAB I menjelaskan latar belakang, masalah, batasan, tujuan, dan manfaat penelitian. BAB II menjelaskan landasan teori mengenai *code smell*, *Long Method*, AST, fitur statis, Decision Tree, evaluasi model, dan teknologi pendukung. BAB III menjelaskan metodologi pengolahan dataset, pelatihan model, rancangan evaluasi, dan perancangan aplikasi web.",
    )


def add_bab_two(document: Document) -> None:
    add_chapter_heading(document, "II", "LANDASAN TEORI")
    add_heading(document, "2.1 Kualitas Perangkat Lunak dan Code Smell")
    add_heading(document, "2.1.1 Kualitas Perangkat Lunak", 3)
    for text in [
        (
            "Kualitas perangkat lunak mencakup kemampuan perangkat lunak memenuhi "
            "kebutuhan pengguna, bekerja dengan benar, aman, mudah dipelihara, dan "
            "dikembangkan kembali. Sommerville (2016) menjelaskan bahwa biaya perubahan "
            "dipengaruhi oleh struktur internal kode. Kode dengan tanggung jawab yang "
            "tersebar, ketergantungan yang rumit, atau fungsi yang terlalu panjang lebih "
            "mahal untuk diubah dibanding kode yang tersusun dalam unit kecil."
        ),
        (
            "Pemeriksaan kualitas dapat dilakukan melalui pengujian perilaku, peninjauan "
            "kode, dan analisis statis. Pengujian perilaku memeriksa keluaran sistem, "
            "sedangkan analisis statis memeriksa bentuk kode tanpa menjalankannya. "
            "Keduanya saling melengkapi karena sistem dapat menghasilkan keluaran benar "
            "walaupun struktur internalnya sulit dipelihara."
        ),
    ]:
        add_body(document, text)
    add_heading(document, "2.1.2 Code Smell", 3)
    for text in [
        (
            "*Code smell* adalah karakteristik kode yang berhubungan dengan masalah "
            "desain dan pemeliharaan. Fowler (2018) menggunakan istilah ini untuk "
            "menandai bagian yang perlu diperiksa, bukan untuk menyatakan bahwa kode "
            "pasti gagal. Contoh *code smell* meliputi metode panjang, daftar parameter "
            "berlebihan, duplikasi, ketergantungan berlebihan, dan class dengan terlalu "
            "banyak tanggung jawab."
        ),
        (
            "Sharma dan Spinellis (2018) menjelaskan bahwa *software smells* dapat "
            "dideteksi dari sumber kode, riwayat perubahan, maupun hubungan antarunit. "
            "Penelitian ini memilih pendekatan berbasis sumber kode karena aplikasi perlu "
            "memberikan hasil langsung dari fungsi Python yang dimasukkan pengguna."
        ),
    ]:
        add_body(document, text)

    add_heading(document, "2.2 Long Method sebagai Code Smell")
    for text in [
        (
            "*Long Method* adalah fungsi atau metode yang berisi terlalu banyak "
            "pernyataan sehingga memiliki lebih dari satu tanggung jawab (Fowler, 2018). "
            "Metode seperti ini sulit dibaca karena pembaca harus menyimpan banyak konteks "
            "di dalam ingatan. Pengujian juga menjadi lebih rumit karena satu fungsi dapat "
            "memiliki kombinasi kondisi, perulangan, dan efek samping yang tinggi."
        ),
        (
            "Pada penelitian ini, *Long Method* tidak ditentukan hanya dari jumlah baris "
            "fisik. Fungsi dapat memiliki baris panjang, komentar, dan struktur penulisan "
            "multi-baris yang tidak menunjukkan kompleksitas logika. Penentuan label "
            "menggunakan pesan Pylint R0915 (*too-many-statements*) karena pesan tersebut "
            "dihasilkan dari jumlah pernyataan yang melewati batas pemeriksaan. Fitur "
            "model tetap dihitung ulang dari AST agar format data latih dan input web "
            "memiliki proses yang sama."
        ),
        (
            "Penggunaan R0915 memiliki keterbatasan. Pesan ini bergantung pada konfigurasi "
            "*linter* dan tidak menggantikan penilaian manusia. Meskipun demikian, pesan "
            "tersebut menyediakan label yang konsisten untuk dataset berskala besar dan "
            "dapat dijelaskan secara metodologis."
        ),
    ]:
        add_body(document, text)

    add_heading(document, "2.3 Analisis Statis dan Abstract Syntax Tree")
    for text in [
        (
            "Analisis statis memeriksa kode tanpa menjalankan program. Pendekatan ini "
            "dapat mengenali nama fungsi, parameter, kondisi, perulangan, percabangan, "
            "dan penanganan kesalahan. Kelebihan analisis statis adalah hasil dapat "
            "diperoleh dengan cepat serta tidak menimbulkan efek samping dari eksekusi "
            "kode yang belum dipercaya."
        ),
        (
            "Python menyediakan modul ast untuk mengubah teks program menjadi pohon "
            "sintaks (Python Software Foundation, 2026). Pohon tersebut memiliki node "
            "seperti FunctionDef, AsyncFunctionDef, If, For, While, ExceptHandler, dan "
            "Call. Bentuk pohon membuat aplikasi dapat menghitung fitur tanpa bergantung "
            "pada spasi atau pola penulisan tertentu."
        ),
        (
            "Tahap parsing diawali dengan normalisasi indentasi, lalu kode diubah menjadi "
            "AST. Apabila kode tidak valid, sistem menghentikan analisis dan menampilkan "
            "pesan kesalahan sintaks. Untuk kode yang valid, lokasi fungsi dan method "
            "digunakan untuk mengambil potongan kode yang akan dihitung fiturnya."
        ),
    ]:
        add_body(document, text)

    add_heading(document, "2.4 Fitur Statis Long Method")
    add_body(
        document,
        "Fitur statis dipilih karena dapat dihitung secara konsisten sebelum maupun sesudah model dilatih. Tabel 2.1 merangkum alasan pemilihan setiap fitur.",
    )
    add_table(
        document,
        "2.1",
        "Perbandingan Fitur Statis Long Method",
        ["Fitur", "Definisi", "Hubungan dengan Long Method"],
        [
            ["Non-comment LOC", "Baris berisi token kode tanpa komentar dan baris kosong", "Fungsi panjang cenderung memuat lebih banyak langkah"],
            ["Jumlah parameter", "Parameter posisi, keyword, *args, **kwargs, dan self", "Parameter berlebihan dapat menandakan tanggung jawab yang melebar"],
            ["Jumlah percabangan", "Kondisi, perulangan, except, comprehension, dan boolean", "Percabangan tinggi menambah jumlah jalur eksekusi dan beban pemahaman"],
        ],
        [3.7, 5.3, 5.0],
        "dikembangkan dari Fowler (2018), Martin (2008), dan kebutuhan rancangan penelitian",
    )
    add_heading(document, "2.4.1 Non-comment Lines of Code", 3)
    add_body(
        document,
        "Non-comment LOC menghitung baris fisik yang mengandung token Python. Baris kosong, komentar, dan baris yang hanya berisi indentasi tidak dihitung. Banyaknya baris bermakna memberi gambaran tentang panjang fungsi tanpa menjadikan komentar sebagai bukti kompleksitas.",
    )
    add_heading(document, "2.4.2 Jumlah Parameter", 3)
    add_body(
        document,
        "Jumlah parameter menghitung parameter posisi, parameter bernilai awal, *keyword-only argument*, *args, **kwargs, serta self pada method. Jumlah parameter yang tinggi dapat menandakan fungsi menerima terlalu banyak informasi atau beberapa tanggung jawab sekaligus.",
    )
    add_heading(document, "2.4.3 Jumlah Percabangan", 3)
    add_body(
        document,
        "Percabangan dihitung dari node If, For, AsyncFor, While, ExceptHandler, IfExp, MatchCase, comprehension, serta tambahan cabang dari operasi boolean. Semakin banyak percabangan, semakin besar jumlah jalur yang harus dipahami dan diuji.",
    )

    add_heading(document, "2.5 Algoritma Decision Tree")
    add_heading(document, "2.5.1 Konsep Dasar Decision Tree", 3)
    add_body(
        document,
        "Decision Tree terdiri atas akar, simpul internal, cabang, dan leaf. Akar merupakan pemeriksaan pertama. Simpul internal memeriksa satu fitur dengan batas tertentu, sedangkan cabang menunjukkan arah data jika kondisi terpenuhi atau tidak. Leaf memuat kelas akhir dan distribusi kelas pada data latih (Breiman et al., 1984).",
    )
    add_figure(
        document,
        "2.1",
        "gambar_2_1_decision_tree.png",
        "Struktur Konseptual Decision Tree",
    )
    add_heading(document, "2.5.2 Pembentukan Pohon Keputusan", 3)
    add_body(
        document,
        "Pohon dibentuk dengan memilih pemisahan yang paling mengurangi ketidakmurnian kelas. Implementasi CART pada scikit-learn menggunakan kriteria Gini. Nilai Gini bernilai nol ketika satu simpul hanya berisi satu kelas dan meningkat ketika kelas tercampur. Proses pemisahan dilakukan sampai batas kedalaman, jumlah sampel minimum, atau kriteria penghentian lain terpenuhi.",
    )
    add_body(
        document,
        "Parameter max_depth membatasi kedalaman pohon. min_samples_leaf menentukan jumlah minimum sampel pada leaf. Parameter tersebut membantu menjaga model tetap dapat dipahami dan mengurangi overfitting.",
    )
    add_heading(document, "2.5.3 Prediksi dan Threshold", 3)
    add_body(
        document,
        "Model Decision Tree dapat menghasilkan probabilitas kelas dari proporsi sampel latih yang berada pada leaf. Fungsi diklasifikasikan sebagai *Long Method* ketika probabilitasnya mencapai threshold. Penelitian ini tidak menggunakan threshold bawaan 50 persen karena kelas positif berjumlah lebih sedikit. Threshold dipilih dari data latih untuk memperoleh F1-score terbaik.",
    )
    add_heading(document, "2.5.4 Kelebihan dan Keterbatasan", 3)
    add_numbered_items(
        document,
        [
            "Decision Tree mudah dipahami karena setiap prediksi dapat ditelusuri melalui aturan bercabang.",
            "Model dapat menangani interaksi antarfitur tanpa memerlukan normalisasi skala yang rumit.",
            "Pohon yang terlalu dalam dapat menyesuaikan diri secara berlebihan terhadap data latih.",
            "Satu pohon dapat berubah ketika data latih berubah, sehingga hasil perlu dibandingkan dengan metrik evaluasi yang memadai.",
        ],
    )

    add_heading(document, "2.6 Evaluasi Model Klasifikasi")
    add_heading(document, "2.6.1 Confusion Matrix", 3)
    add_body(
        document,
        "Confusion matrix membandingkan hasil prediksi dan label sebenarnya. Pada klasifikasi biner terdapat empat kemungkinan hasil seperti ditunjukkan pada Tabel 2.2.",
    )
    add_table(
        document,
        "2.2",
        "Confusion Matrix Dua Kelas",
        ["", "Prediksi Negatif", "Prediksi Positif"],
        [
            ["Label negatif", "True Negative (TN)", "False Positive (FP)"],
            ["Label positif", "False Negative (FN)", "True Positive (TP)"],
        ],
        [4.0, 5.0, 5.0],
        "hasil sintesis Breiman et al. (1984) dan Pedregosa et al. (2011)",
        alignments=["left", "center", "center"],
    )
    add_heading(document, "2.6.2 Precision, Recall, dan F1-score", 3)
    add_numbered_items(
        document,
        [
            "Precision menunjukkan proporsi prediksi positif yang benar. Presisi dirumuskan sebagai TP dibagi TP ditambah FP.",
            "Recall menunjukkan proporsi *Long Method* sebenarnya yang berhasil ditemukan. Recall dirumuskan sebagai TP dibagi TP ditambah FN.",
            "F1-score merupakan rata-rata harmonik precision dan recall. Nilai ini digunakan sebagai metrik utama karena jumlah kelas negatif jauh lebih banyak daripada kelas positif.",
            "Accuracy adalah proporsi seluruh prediksi yang benar. Accuracy tetap dicatat, tetapi tidak dijadikan satu-satunya dasar penilaian karena dapat terlihat tinggi pada data yang tidak seimbang.",
        ],
    )
    add_heading(document, "2.6.3 ROC-AUC dan Average Precision", 3)
    add_body(
        document,
        "ROC-AUC mengukur kemampuan model mengurutkan sampel positif di atas sampel negatif pada berbagai threshold. Nilai mendekati satu menunjukkan pemisahan yang baik. Average Precision atau area di bawah kurva precision-recall lebih informatif ketika kelas positif jarang. Keduanya dilaporkan sebagai metrik tambahan.",
    )

    add_heading(document, "2.7 Teknologi Pendukung")
    add_heading(document, "2.7.1 Bahasa Pemrograman Python", 3)
    add_body(
        document,
        "Python digunakan karena menyediakan modul ast untuk analisis sintaks dan ekosistem *machine learning* yang lengkap. Kode aplikasi, proses data, dan pelatihan model dapat menggunakan bahasa yang sama sehingga pertukaran data lebih sederhana.",
    )
    add_heading(document, "2.7.2 pandas dan NumPy", 3)
    add_body(
        document,
        "pandas digunakan untuk membaca dataset tabular, memeriksa nilai kosong, dan mengelola data latih serta data uji. NumPy digunakan untuk operasi numerik dan perhitungan metrik. Kedua pustaka mempercepat pengolahan data berukuran besar dibanding perulangan Python biasa.",
    )
    add_heading(document, "2.7.3 scikit-learn", 3)
    add_body(
        document,
        "scikit-learn menyediakan implementasi DecisionTreeClassifier, GridSearchCV, GroupKFold, GroupShuffleSplit, dan metrik klasifikasi (Pedregosa et al., 2011). Pustaka ini digunakan untuk menjaga proses pelatihan dan evaluasi tetap tervalidasi.",
    )
    add_heading(document, "2.7.4 Streamlit", 3)
    add_body(
        document,
        "Streamlit digunakan untuk membangun antarmuka web tanpa memisahkan proyek frontend dan backend. Komponen text area, tombol, tabel, grafik, expander, dan ikon bantuan dapat disusun dalam satu halaman. Aplikasi menampilkan hasil model dan penjelasan aturan dalam dashboard yang sama.",
    )

    add_heading(document, "2.8 Penelitian Terdahulu")
    add_body(
        document,
        "Beberapa penelitian dan referensi yang menjadi dasar penelitian ini dirangkum pada Tabel 2.3.",
    )
    add_table(
        document,
        "2.3",
        "Ringkasan Penelitian Terdahulu",
        ["Sumber", "Fokus", "Relevansi dengan Penelitian Ini"],
        [
            ["Marinescu (2004)", "Deteksi cacat desain menggunakan strategi metrik", "Menunjukkan penggunaan kombinasi ukuran kode untuk mengenali masalah struktur"],
            ["Fowler (2018)", "Code smell dan refactoring", "Menjadi dasar konsep Long Method dan tindakan pemecahan fungsi"],
            ["Sharma dan Spinellis (2018)", "Survei software smells", "Memberikan kerangka jenis, sumber, dan deteksi code smell"],
            ["Breiman et al. (1984)", "Classification and Regression Trees", "Menjadi dasar algoritma Decision Tree yang digunakan"],
            ["Pedregosa et al. (2011)", "scikit-learn", "Menyediakan implementasi model dan metrik yang dipakai dalam penelitian"],
        ],
        [4.0, 4.5, 5.5],
        "hasil sintesis pustaka penelitian",
    )

    add_heading(document, "2.9 Kerangka Pemikiran")
    for text in [
        "Masalah utama penelitian adalah sulitnya memeriksa *Long Method* secara manual pada kode Python dalam jumlah besar. Dataset Pylint disiapkan sebagai sumber observasi. Deduplikasi dilakukan agar satu fungsi tidak mendominasi pelatihan. AST digunakan untuk menghitung tiga fitur statis dengan cara yang sama pada data latih dan input pengguna.",
        "Decision Tree mengubah pasangan fitur dan label menjadi aturan klasifikasi. Hasil model kemudian ditampilkan melalui dashboard yang memuat probabilitas, label, fitur, dan jalur keputusan. Peninjauan manusia tetap diperlukan karena prediksi model merupakan indikasi, bukan keputusan akhir.",
    ]:
        add_body(document, text)
    add_figure(
        document,
        "2.2",
        "gambar_2_2_kerangka_pemikiran.png",
        "Kerangka Pemikiran Penelitian",
        width_cm=14.0,
    )


def add_bab_three(document: Document) -> None:
    quality = load_data(
        QUALITY_PATH,
        {
            "raw_rows": 156151,
            "duplicate_rows_removed": 102338,
            "duplicates_promoted_to_positive": 3710,
            "parse_failed_unique_codes": 6,
        },
    )
    metrics = load_data(METRICS_PATH, {"metrics": {}, "dataset": {}})
    dataset = metrics["dataset"]
    metric = metrics["metrics"]
    hyper = metric.get("best_parameters", {})

    add_chapter_heading(document, "III", "METODOLOGI PENELITIAN")
    add_heading(document, "3.1 Jenis dan Pendekatan Penelitian")
    for text in [
        (
            "Penelitian ini menggunakan pendekatan kuantitatif eksperimental terapan. "
            "Objek penelitian adalah struktur fungsi Python, sedangkan perlakuan utama "
            "berupa ekstraksi fitur statis dan pelatihan Decision Tree. Eksperimen "
            "dilakukan dengan membandingkan beberapa konfigurasi pohon dan evaluasi pada "
            "repository yang dipisahkan dari data latih."
        ),
        (
            "Pendekatan kuantitatif dipilih karena keluaran model dapat diukur dengan "
            "precision, recall, F1-score, ROC-AUC, dan confusion matrix. Sifat terapan "
            "terlihat dari tujuan membangun prototipe yang dapat digunakan untuk "
            "memeriksa fungsi Python melalui antarmuka web."
        ),
    ]:
        add_body(document, text)

    add_heading(document, "3.2 Tahapan Penelitian")
    add_body(
        document,
        "Tahapan penelitian disusun berurutan dari identifikasi masalah sampai pengujian sistem. Hubungan tahapan ditunjukkan pada Gambar 3.1 dan rincian aktivitas disajikan pada Tabel 3.1.",
    )
    add_figure(
        document,
        "3.1",
        "gambar_3_1_tahapan_penelitian.png",
        "Tahapan Penelitian",
        width_cm=14.0,
    )
    add_table(
        document,
        "3.1",
        "Tahapan, Aktivitas, dan Luaran Penelitian",
        ["Tahap", "Aktivitas", "Luaran"],
        [
            ["1", "Identifikasi masalah dan batasan", "Rumusan masalah dan variabel"],
            ["2", "Pengumpulan dataset Pylint", "Dataset mentah Python"],
            ["3", "Validasi, deduplikasi, dan pembersihan", "Dataset unik dan audit kualitas"],
            ["4", "Ekstraksi fitur AST", "Tiga nilai fitur per fungsi"],
            ["5", "Pembagian data berdasarkan repository", "Data latih dan data uji"],
            ["6", "Pelatihan dan kalibrasi threshold", "Model Decision Tree siap pakai"],
            ["7", "Evaluasi model", "Metrik dan confusion matrix"],
            ["8", "Pengembangan web dan pengujian", "Prototipe dashboard"],
        ],
        [1.4, 6.6, 6.0],
        "rancangan penelitian, 2026",
        alignments=["center", "left", "left"],
    )

    add_heading(document, "3.3 Sumber dan Objek Penelitian")
    add_heading(document, "3.3.1 Dataset Penelitian", 3)
    add_body(
        document,
        "Dataset awal merupakan kumpulan pesan Pylint dari repository Python publik. Setiap baris memuat identitas pesan, potongan kode yang disorot, kode fungsi, nama fungsi, repository, commit, path, dan ukuran kode. Dataset mentah memiliki "
        f"{int(quality['raw_rows']):,} baris. Sebanyak 30 jenis pesan Pylint muncul, termasuk C0103, R0912, R0913, R0915, dan W0718.",
    )
    add_body(
        document,
        "Objek penelitian adalah fungsi atau method Python. Satu baris mentah tidak selalu mewakili satu fungsi karena fungsi yang sama dapat muncul pada beberapa pesan. Proses pembersihan mengubah representasi pesan menjadi representasi fungsi unik.",
    )
    add_heading(document, "3.3.2 Lingkungan Penelitian", 3)
    add_body(
        document,
        "Penelitian dijalankan pada lingkungan Python 3.10.6 dengan pandas 2.3.3, NumPy 2.2.6, scikit-learn 1.7.2, Streamlit 1.65.0, joblib 1.6.0, dan Plotly 6.9.0. Pengolahan dataset dan pelatihan dijalankan sebagai proses offline, sedangkan aplikasi web memuat model yang telah disimpan untuk melakukan prediksi.",
    )

    add_heading(document, "3.4 Definisi Operasional Variabel")
    add_body(
        document,
        "Variabel penelitian terdiri atas tiga fitur masukan dan satu label keluaran. Definisi operasional disajikan pada Tabel 3.2 agar setiap fitur dapat dihitung secara konsisten.",
    )
    add_table(
        document,
        "3.2",
        "Definisi Operasional Variabel",
        ["Variabel", "Jenis", "Definisi Operasional", "Skala"],
        [
            ["nloc", "Independen", "Jumlah baris fisik yang mengandung token Python tanpa komentar", "Rasio"],
            ["parameter_count", "Independen", "Jumlah parameter posisi, keyword, *args, **kwargs, dan self", "Rasio"],
            ["branch_count", "Independen", "Jumlah simpul kontrol alur dan tambahan cabang boolean", "Rasio"],
            ["long_method_label", "Dependen", "Bernilai 1 jika muncul R0915 dan 0 jika tidak", "Nominal biner"],
        ],
        [3.7, 2.4, 6.4, 1.5],
        "rancangan penelitian, 2026",
        alignments=["left", "center", "left", "center"],
    )

    add_heading(document, "3.5 Pra-pemrosesan Dataset")
    add_body(
        document,
        "Pra-pemrosesan dilakukan untuk memastikan setiap baris memiliki nilai wajib, mewakili satu fungsi unik, dapat diuraikan oleh AST, dan memiliki label yang konsisten.",
    )
    add_heading(document, "3.5.1 Validasi Struktur Data", 3)
    add_body(
        document,
        "Dataset dibaca sebagai CSV menggunakan Python. Batas panjang field dinaikkan karena potongan kode dapat melebihi batas bawaan modul csv. Kolom yang wajib tersedia adalah msg_id, code, func_name, repository, commit_id, dan path. Kolom nilai lain digunakan untuk audit dan pelacakan asal data.",
    )
    add_heading(document, "3.5.2 Pemeriksaan Nilai Kosong", 3)
    add_body(
        document,
        "Pemeriksaan nilai kosong menemukan 0 baris tanpa nilai wajib pada dataset yang digunakan. Jika dataset lain memiliki nilai kosong pada kolom wajib, baris tersebut tidak dimasukkan ke data latih dan dicatat pada audit kualitas.",
    )
    add_heading(document, "3.5.3 Deduplikasi Data", 3)
    add_body(
        document,
        "Kode fungsi dinormalisasi dengan SHA-256. Hash yang sama dianggap sebagai satu fungsi. Jika salah satu kemunculan duplikat memiliki R0915, label positif diterapkan pada record gabungan. Cara ini mencegah satu fungsi muncul berkali-kali hanya karena Pylint menghasilkan beberapa pesan.",
    )
    add_body(
        document,
        f"Dari {int(quality['raw_rows']):,} baris mentah, {int(quality['duplicate_rows_removed']):,} baris pengulangan dihapus. Sebanyak {int(quality['duplicates_promoted_to_positive']):,} duplikat menambahkan sinyal positif yang sebelumnya belum tercatat pada record pertama.",
    )
    add_heading(document, "3.5.4 Penentuan Label", 3)
    add_body(
        document,
        "Label biner Long Method diberi nilai 1 jika msg_id sama dengan R0915. Pesan lain menjadi label 0. R0915 dipilih karena pesan tersebut mengindikasikan jumlah pernyataan fungsi yang melewati batas Pylint. Label ini bersifat proksi operasional dan bukan pengganti pemeriksaan manusia.",
    )
    add_heading(document, "3.5.5 Penanganan Data Tidak Valid", 3)
    add_body(
        document,
        f"Sebanyak {int(quality['parse_failed_unique_codes']):,} kode unik tidak dapat diuraikan oleh AST dan dikeluarkan. Kode yang tidak valid tidak boleh diberi fitur hasil perkiraan karena dapat mengubah distribusi data dan menghasilkan label yang menyesatkan.",
    )
    add_table(
        document,
        "3.3",
        "Aturan Pembersihan Dataset",
        ["Pemeriksaan", "Aturan", "Tindakan"],
        [
            ["Nilai wajib", "msg_id, code, repository, commit_id, path harus tersedia", "Keluarkan dan catat"],
            ["Duplikasi", "Hash kode telah ada", "Gabungkan dan promosikan label R0915"],
            ["Sintaks", "Kode tidak dapat di-parse oleh AST", "Keluarkan dan catat"],
            ["Label", "msg_id R0915", "long_method_label = 1"],
            ["Label lain", "msg_id selain R0915", "long_method_label = 0"],
        ],
        [3.4, 6.4, 4.2],
        "implementasi pra-pemrosesan, 2026",
    )

    add_heading(document, "3.6 Ekstraksi Fitur Statis")
    add_heading(document, "3.6.1 Parsing Kode dengan AST", 3)
    add_body(
        document,
        "Setiap kode fungsi dinormalisasi dengan dedent agar indentasi luar tidak memengaruhi proses parsing. Kode diubah menjadi AST. Aplikasi mencari top-level function dan method di dalam class. Cuplikan pernyataan tanpa deklarasi fungsi dibungkus sebagai fungsi sementara agar tetap dapat dianalisis.",
    )
    add_heading(document, "3.6.2 Perhitungan Non-comment LOC", 3)
    add_body(
        document,
        "Sumber fungsi di-tokenize. Nomor baris dicatat hanya untuk token bermakna. Token komentar, newline, indentasi, dedentasi, dan akhir file tidak dihitung. Nilai minimal LOC adalah satu.",
    )
    add_heading(document, "3.6.3 Perhitungan Parameter", 3)
    add_body(
        document,
        "Parameter dihitung dari atribut arguments pada node fungsi. Perhitungan mencakup posonlyargs, args, kwonlyargs, vararg, dan kwarg. Parameter self tetap dihitung apabila kode yang dianalisis merupakan method.",
    )
    add_heading(document, "3.6.4 Perhitungan Percabangan", 3)
    add_body(
        document,
        "Percabangan dihitung menggunakan AST visitor. Simpul If, For, AsyncFor, While, ExceptHandler, IfExp, MatchCase, dan comprehension menambah satu cabang. Boolean Op dengan beberapa nilai menambah jumlah cabang sesuai jumlah operasi. Fungsi bersarang tidak dihitung ulang di dalam fungsi induk.",
    )
    add_table(
        document,
        "3.4",
        "Fitur Statis dan Cara Perhitungan",
        ["Fitur", "Sumber", "Aturan Ringkas"],
        [
            ["nloc", "Token Python", "Hitung baris unik yang memiliki token bermakna"],
            ["parameter_count", "AST arguments", "Jumlah parameter posisi, keyword, vararg, kwarg, dan self"],
            ["branch_count", "AST control-flow", "Hitung node keputusan, perulangan, exception, comprehension, dan boolean"],
        ],
        [3.4, 4.0, 6.6],
        "implementasi src/feature_extraction.py, 2026",
    )

    add_heading(document, "3.7 Profil Dataset Hasil Pembersihan")
    rows_count = int(dataset.get("rows", 53807))
    positive = int(dataset.get("positive_rows", 4119))
    negative = int(dataset.get("negative_rows", 49688))
    repositories = int(dataset.get("repositories", 118))
    positive_rate = float(dataset.get("positive_rate", positive / rows_count))
    add_body(
        document,
        "Dataset akhir bersifat tidak seimbang karena fungsi yang memiliki sinyal R0915 jauh lebih sedikit daripada fungsi dengan pesan Pylint lain. Profil dataset ditunjukkan pada Tabel 3.5.",
    )
    add_table(
        document,
        "3.5",
        "Profil Dataset Hasil Pembersihan",
        ["Komponen", "Jumlah", "Keterangan"],
        [
            ["Fungsi unik", f"{rows_count:,}", "Satu record per hash kode"],
            ["Long Method positif", f"{positive:,}", "Memiliki sinyal R0915"],
            ["Label negatif", f"{negative:,}", "Tidak memiliki R0915"],
            ["Proporsi positif", f"{positive_rate:.2%}", "Dari dataset bersih"],
            ["Repository", f"{repositories:,}", "Sumber proyek"],
        ],
        [4.2, 3.0, 6.8],
        "hasil pengolahan dataset penelitian, 2026",
        alignments=["left", "right", "left"],
    )
    positive_means = dataset.get("positive_feature_means", {})
    negative_means = dataset.get("negative_feature_means", {})
    add_table(
        document,
        "3.6",
        "Perbandingan Rata-rata Fitur per Label",
        ["Fitur", "Rata-rata Positif", "Rata-rata Negatif"],
        [
            ["Non-comment LOC", f"{positive_means.get('nloc', 0):.2f}", f"{negative_means.get('nloc', 0):.2f}"],
            ["Jumlah parameter", f"{positive_means.get('parameter_count', 0):.2f}", f"{negative_means.get('parameter_count', 0):.2f}"],
            ["Jumlah percabangan", f"{positive_means.get('branch_count', 0):.2f}", f"{negative_means.get('branch_count', 0):.2f}"],
        ],
        [4.2, 4.8, 5.0],
        "hasil pengolahan dataset penelitian, 2026",
        alignments=["left", "right", "right"],
    )
    add_body(
        document,
        "Rata-rata LOC dan percabangan pada kelas positif lebih tinggi dibanding kelas negatif. Rata-rata jumlah parameter relatif hampir sama, sehingga pengaruh fitur tersebut perlu dibaca dari aturan pohon dan kontribusi fitur, bukan hanya dari rata-rata.",
    )

    add_heading(document, "3.8 Pembagian Data Latih dan Data Uji")
    add_body(
        document,
        "Data dibagi 80 persen untuk pelatihan dan 20 persen untuk pengujian. Pembagian dilakukan berdasarkan repository, bukan secara acak per fungsi. Tujuannya agar model diuji pada proyek yang belum dilihat saat pelatihan dan mengurangi kemungkinan kebocoran data. Hasil pembagian disajikan pada Tabel 3.7.",
    )
    add_table(
        document,
        "3.7",
        "Pembagian Data Latih dan Data Uji",
        ["Bagian", "Jumlah Record", "Jumlah Repository", "Fungsi"],
        [
            ["Latih", f"{int(dataset.get('train_rows', 0)):,}", str(int(dataset.get('train_repositories', 0))), "Pemilihan hyperparameter dan pelatihan"],
            ["Uji", f"{int(dataset.get('test_rows', 0)):,}", str(int(dataset.get('test_repositories', 0))), "Evaluasi akhir tanpa digunakan untuk tuning"],
        ],
        [2.4, 3.5, 3.6, 4.5],
        "hasil pembagian data penelitian, 2026",
        alignments=["left", "right", "right", "left"],
    )

    add_heading(document, "3.9 Pelatihan Model Decision Tree")
    add_heading(document, "3.9.1 Konfigurasi Pelatihan", 3)
    add_body(
        document,
        "DecisionTreeClassifier digunakan dengan random_state 42. Class weight diatur menjadi balanced karena proporsi label positif hanya sekitar satu dari tiga belas record. Pembobotan membantu model tidak mengabaikan minoritas ketika meminimalkan ketidakmurnian.",
    )
    add_heading(document, "3.9.2 Pencarian Hyperparameter", 3)
    add_body(
        document,
        "GridSearchCV digunakan pada data latih dengan GroupKFold tiga lipatan. Group berupa repository. Konfigurasi yang diuji meliputi max_depth 3, 4, 5, 6, dan 8, serta min_samples_leaf 10, 30, dan 60. Parameter terbaik kemudian dilatih ulang pada seluruh data latih.",
    )
    add_table(
        document,
        "3.8",
        "Konfigurasi Hyperparameter Decision Tree",
        ["Parameter", "Nilai yang Diuji atau Digunakan", "Keterangan"],
        [
            ["criterion", "gini", "Mengukur ketidakmurnian simpul"],
            ["max_depth", "3, 4, 5, 6, 8", "Mengendalikan kedalaman pohon"],
            ["min_samples_leaf", "10, 30, 60", "Membatasi leaf terlalu kecil"],
            ["class_weight", "balanced", "Mengimbangi proporsi label"],
            ["Terpilih", f"max_depth={hyper.get('max_depth', 5)}, min_samples_leaf={hyper.get('min_samples_leaf', 10)}", "Berdasarkan F1 pada data latih"],
        ],
        [3.4, 5.4, 5.2],
        "hasil training model, 2026",
    )
    add_heading(document, "3.9.3 Penentuan Threshold", 3)
    add_body(
        document,
        "Probabilitas model tidak langsung dianggap positif pada nilai 0,5. Prediksi out-of-fold dibuat untuk seluruh data latih. Threshold diuji dari 0,50 sampai 0,95 dengan langkah 0,01. Nilai yang memaksimalkan F1 dipilih lalu dibekukan ke dalam artefak model. Data uji tidak digunakan dalam pemilihan threshold.",
    )

    add_heading(document, "3.10 Rancangan Evaluasi Model")
    add_heading(document, "3.10.1 Confusion Matrix", 3)
    add_body(
        document,
        "Confusion matrix dihitung pada data uji. True negative menunjukkan fungsi biasa yang benar tidak ditandai. False positive menunjukkan fungsi biasa yang keliru ditandai. False negative menunjukkan Long Method yang terlewat. True positive menunjukkan Long Method yang berhasil ditemukan.",
    )
    add_heading(document, "3.10.2 Metrik Klasifikasi", 3)
    add_body(
        document,
        "Precision, recall, F1-score, accuracy, ROC-AUC, dan average precision dihitung dari hasil data uji. Interpretasi dari setiap metrik dijelaskan pada Tabel 3.9.",
    )
    add_table(
        document,
        "3.9",
        "Metrik dan Interpretasi Evaluasi",
        ["Metrik", "Interpretasi"],
        [
            ["Precision", "Proporsi prediksi positif yang benar"],
            ["Recall", "Proporsi Long Method yang berhasil ditemukan"],
            ["F1-score", "Keseimbangan precision dan recall"],
            ["Accuracy", "Proporsi semua prediksi yang benar"],
            ["ROC-AUC", "Kemampuan mengurutkan kelas positif di atas kelas negatif"],
            ["Average Precision", "Ringkasan precision-recall untuk kelas positif yang jarang"],
        ],
        [4.2, 9.8],
        "dikembangkan dari Pedregosa et al. (2011)",
    )
    add_heading(document, "3.10.3 Pengujian Generalisasi", 3)
    add_body(
        document,
        "Data uji berasal dari repository yang tidak digunakan dalam pelatihan. Pengujian ini lebih ketat daripada pembagian acak antarbaris. Hasilnya menunjukkan kemampuan model ketika menerima gaya kode dari proyek yang berbeda.",
    )

    add_heading(document, "3.11 Rancangan Sistem")
    add_heading(document, "3.11.1 Kebutuhan Fungsional", 3)
    add_table(
        document,
        "3.10",
        "Kebutuhan Fungsional Aplikasi",
        ["Kode", "Kebutuhan", "Keluaran"],
        [
            ["F-01", "Menerima kode Python dari pengguna", "Teks kode"],
            ["F-02", "Mengenali fungsi dan method", "Daftar fungsi"],
            ["F-03", "Mengekstraksi tiga fitur statis", "LOC, parameter, percabangan"],
            ["F-04", "Melakukan klasifikasi Decision Tree", "Label dan probabilitas"],
            ["F-05", "Menampilkan dashboard", "Kartu ringkasan, diagram, tabel"],
            ["F-06", "Menjelaskan jalur keputusan", "Daftar aturan dan saran"],
            ["F-07", "Menjelaskan istilah melalui ikon", "Tooltip definisi"],
            ["F-08", "Mengunduh hasil analisis", "Berkas JSON"],
        ],
        [1.5, 6.6, 5.9],
        "rancangan sistem, 2026",
        alignments=["center", "left", "left"],
    )
    add_heading(document, "3.11.2 Kebutuhan Nonfungsional", 3)
    add_numbered_items(
        document,
        [
            "Aplikasi menggunakan antarmuka web yang dapat dibuka pada browser modern.",
            "Pesan kesalahan sintaks ditampilkan tanpa menghentikan seluruh halaman.",
            "Tooltip istilah dapat dipicu dengan kursor, fokus keyboard, atau sentuhan.",
            "Model dimuat satu kali melalui cache agar analisis berulang tidak memuat ulang berkas model.",
            "Hasil klasifikasi diberi batas interpretasi bahwa keputusan model hanya merupakan indikasi awal.",
        ],
    )
    add_heading(document, "3.11.3 Arsitektur Sistem", 3)
    add_body(
        document,
        "Aplikasi terdiri atas antarmuka Streamlit, modul ekstraksi fitur AST, artefak model Decision Tree, dan modul penyajian hasil. Arsitektur sistem ditunjukkan pada Gambar 3.2.",
    )
    add_figure(
        document,
        "3.2",
        "gambar_3_2_arsitektur_sistem.png",
        "Arsitektur Aplikasi CodeScope",
        width_cm=14.0,
    )
    add_heading(document, "3.11.4 Alur Analisis Kode", 3)
    add_numbered_items(
        document,
        [
            "Pengguna menempelkan kode Python pada editor aplikasi.",
            "Sistem memvalidasi sintaks dan mengekstraksi daftar fungsi atau method.",
            "Modul fitur menghitung lokasi baris, LOC, jumlah parameter, dan jumlah percabangan.",
            "Model Decision Tree menghitung probabilitas kelas Long Method.",
            "Probabilitas dibandingkan dengan threshold untuk menghasilkan label.",
            "Dashboard menampilkan ringkasan, grafik, tabel, jalur keputusan, dan saran peninjauan.",
        ],
    )
    add_heading(document, "3.11.5 Rancangan Dashboard", 3)
    add_body(
        document,
        "Bagian atas dashboard menampilkan konfigurasi model dan ringkasan hasil. Kartu metrik menunjukkan jumlah fungsi, jumlah fungsi terindikasi, jumlah fungsi tidak terindikasi, dan probabilitas tertinggi. Diagram donat menunjukkan komposisi prediksi, sedangkan diagram batang membandingkan probabilitas antar fungsi.",
    )
    add_body(
        document,
        "Tabel rincian memuat nama fungsi, rentang baris, prediksi, probabilitas, LOC, parameter, dan percabangan. Setiap fungsi dapat dibuka untuk melihat jalur keputusan. Dashboard juga menyediakan unduhan JSON untuk keperluan audit atau lampiran pengujian.",
    )
    add_heading(document, "3.11.6 Penjelasan Istilah pada Antarmuka", 3)
    add_body(
        document,
        "Istilah teknis seperti precision, recall, threshold, LOC, parameter, percabangan, dan confusion matrix diberi ikon informasi. Penjelasan muncul ketika ikon diarahkan dengan kursor atau difokuskan dengan keyboard. Fitur ini membantu pengguna membaca dashboard tanpa harus mengetahui definisi *machine learning* terlebih dahulu.",
    )

    add_heading(document, "3.12 Skenario Pengujian")
    add_body(
        document,
        "Pengujian dibagi menjadi pengujian model, fungsi aplikasi, dan tampilan. Skenario pengujian disajikan pada Tabel 3.11.",
    )
    add_table(
        document,
        "3.11",
        "Skenario Pengujian Sistem",
        ["Kode", "Skenario", "Hasil yang Diharapkan"],
        [
            ["U-01", "Memasukkan fungsi pendek", "Dashboard menampilkan tidak terindikasi"],
            ["U-02", "Memasukkan fungsi panjang", "Dashboard menampilkan prediksi dan probabilitas"],
            ["U-03", "Memasukkan beberapa fungsi", "Tabel dan ringkasan menghitung setiap fungsi"],
            ["U-04", "Memasukkan sintaks tidak valid", "Pesan kesalahan ditampilkan"],
            ["U-05", "Mengarahkan kursor ke ikon informasi", "Tooltip definisi muncul"],
            ["U-06", "Membuka expander jalur keputusan", "Aturan model dan saran tampil"],
            ["U-07", "Mengunduh hasil", "Berkas JSON dapat diunduh"],
            ["U-08", "Menguji data uji repository terpisah", "Metrik evaluasi dapat dihitung"],
        ],
        [1.5, 6.4, 6.1],
        "rancangan pengujian sistem, 2026",
        alignments=["center", "left", "left"],
    )

    add_heading(document, "3.13 Indikator Keberhasilan")
    add_numbered_items(
        document,
        [
            "Dataset berhasil divalidasi, dideduplikasi, dan diberi label tanpa kehilangan jejak asal data.",
            "Tiga fitur statis dihitung dengan proses yang sama pada data latih dan kode yang dimasukkan pengguna.",
            "Model Decision Tree dapat menghasilkan label dan probabilitas untuk fungsi Python.",
            "Dashboard menampilkan keputusan, fitur, jalur keputusan, dan penjelasan istilah yang dapat dipahami.",
            "Pengujian fungsi aplikasi tidak menemukan kesalahan sintaks atau kegagalan tampilan.",
        ],
    )

    add_heading(document, "3.14 Etika Penelitian dan Keterbatasan")
    add_body(
        document,
        "Penelitian tidak menjalankan kode sumber yang dimasukkan pengguna. Kode hanya diubah menjadi AST untuk menghitung fitur. Identitas repository, commit, dan path disimpan untuk audit, tetapi tidak digunakan sebagai fitur prediksi.",
    )
    add_body(
        document,
        "Keterbatasan penelitian meliputi label R0915 yang merupakan proksi operasional, penggunaan tiga fitur yang belum mencakup seluruh aspek desain, serta hasil aplikasi yang tetap memerlukan peninjauan manusia.",
    )


def add_references(document: Document) -> None:
    section = add_new_section(document, "hidden")
    set_page_number_format(section, "decimal")
    add_front_heading(document, "DAFTAR PUSTAKA")
    references = [
        "Breiman, L., Friedman, J. H., Olshen, R. A., dan Stone, C. J. 1984. *Classification and Regression Trees*. Belmont: Wadsworth.",
        "Fowler, M. 2018. *Refactoring: Improving the Design of Existing Code*. 2nd ed. Boston: Addison-Wesley.",
        "Marinescu, R. 2004. Detection Strategies: Metrics-Based Rules for Detecting Design Flaws. *Proceedings of the 20th IEEE International Conference on Software Maintenance*, 350-359.",
        "Martin, R. C. 2008. *Clean Code: A Handbook of Agile Software Craftsmanship*. Upper Saddle River: Prentice Hall.",
        "Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., dan Duchesnay, E. 2011. Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12: 2825-2830.",
        "Pressman, R. S. dan Maxim, B. R. 2020. *Software Engineering: A Practitioner's Approach*. 9th ed. New York: McGraw-Hill.",
        "Pylint. 2026. *Messages Overview*. https://pylint.readthedocs.io/en/stable/user_guide/messages/ (diakses 20 November 2026).",
        "Python Software Foundation. 2026. *ast - Abstract Syntax Trees*. https://docs.python.org/3/library/ast.html (diakses 20 November 2026).",
        "Sharma, T. dan Spinellis, D. 2018. A Survey on Software Smells. *Journal of Systems and Software*, 138: 158-173.",
        "Sommerville, I. 2016. *Software Engineering*. 10th ed. Boston: Pearson.",
        "Streamlit. 2026. *Streamlit Documentation*. https://docs.streamlit.io/ (diakses 20 November 2026).",
    ]
    for reference in references:
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        paragraph.paragraph_format.line_spacing = 1
        paragraph.paragraph_format.space_after = Pt(12)
        paragraph.paragraph_format.left_indent = Cm(1.27)
        paragraph.paragraph_format.first_line_indent = Cm(-1.27)
        add_rich_text(paragraph, reference)


def build_document() -> None:
    pages = page_numbers()
    document = Document()
    configure_document(document)
    first = document.sections[0]
    configure_section(first)
    configure_headers_footers(first, "hidden")
    set_page_number_format(first, "decimal", 1)

    add_cover(document)
    front_section = document.add_section(WD_SECTION.NEW_PAGE)
    configure_section(front_section)
    configure_headers_footers(front_section, "hidden")
    set_page_number_format(front_section, "lowerRoman", 1)
    add_cover(document)
    document.add_page_break()
    add_approval_page(document)
    document.add_page_break()
    add_motto_page(document)
    document.add_page_break()
    add_authenticity_page(document)

    front_numbered_section = document.add_section(WD_SECTION.NEW_PAGE)
    configure_section(front_numbered_section)
    configure_headers_footers(front_numbered_section, "front-numbered")
    set_page_number_format(front_numbered_section, "lowerRoman", 5)
    add_abstracts(document)
    add_preface(document)
    add_toc(document, pages)
    add_list_of_tables(document, pages)
    add_list_of_figures(document, pages)

    chapter_one_section = document.add_section(WD_SECTION.NEW_PAGE)
    configure_section(chapter_one_section)
    configure_headers_footers(chapter_one_section, "chapter")
    set_page_number_format(chapter_one_section, "decimal", 1)
    add_bab_one_clean(document)

    chapter_two_section = document.add_section(WD_SECTION.NEW_PAGE)
    configure_section(chapter_two_section)
    configure_headers_footers(chapter_two_section, "chapter")
    set_page_number_format(chapter_two_section, "decimal")
    add_bab_two(document)

    chapter_three_section = document.add_section(WD_SECTION.NEW_PAGE)
    configure_section(chapter_three_section)
    configure_headers_footers(chapter_three_section, "chapter")
    set_page_number_format(chapter_three_section, "decimal")
    add_bab_three(document)

    add_references(document)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    document.save(OUTPUT_PATH)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    build_document()

