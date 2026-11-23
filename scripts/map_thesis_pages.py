"""Map thesis headings, tables, and figures to rendered page numbers."""

from __future__ import annotations

import json
import re
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = (
    ROOT
    / "tmp"
    / "thesis"
    / "render_final"
    / "Draft_Skripsi_Ihsan_Herdiansyah_222111011_BAB_I-III.pdf"
)
OUTPUT_PATH = ROOT / "tmp" / "thesis" / "page_numbers.json"

BODY_START_INDEX = 12
BODY_PAGE_OFFSET = 12


HEADINGS = {
    "bab1": "BAB I PENDAHULUAN",
    "bab1_1": "1.1 Latar Belakang",
    "bab1_2": "1.2 Identifikasi Masalah",
    "bab1_3": "1.3 Rumusan Masalah",
    "bab1_4": "1.4 Batasan Masalah",
    "bab1_5": "1.5 Maksud dan Tujuan Penelitian",
    "bab1_6": "1.6 Manfaat Penelitian",
    "bab1_7": "1.7 Sistematika Penulisan",
    "bab2": "BAB II LANDASAN TEORI",
    "bab2_1": "2.1 Kualitas Perangkat Lunak dan Code Smell",
    "bab2_1_1": "2.1.1 Kualitas Perangkat Lunak",
    "bab2_1_2": "2.1.2 Code Smell",
    "bab2_2": "2.2 Long Method sebagai Code Smell",
    "bab2_3": "2.3 Analisis Statis dan Abstract Syntax Tree",
    "bab2_4": "2.4 Fitur Statis Long Method",
    "bab2_4_1": "2.4.1 Non-comment Lines of Code",
    "bab2_4_2": "2.4.2 Jumlah Parameter",
    "bab2_4_3": "2.4.3 Jumlah Percabangan",
    "bab2_5": "2.5 Algoritma Decision Tree",
    "bab2_5_1": "2.5.1 Konsep Dasar Decision Tree",
    "bab2_5_2": "2.5.2 Pembentukan Pohon Keputusan",
    "bab2_5_3": "2.5.3 Prediksi dan Threshold",
    "bab2_5_4": "2.5.4 Kelebihan dan Keterbatasan",
    "bab2_6": "2.6 Evaluasi Model Klasifikasi",
    "bab2_6_1": "2.6.1 Confusion Matrix",
    "bab2_6_2": "2.6.2 Precision, Recall, dan F1-score",
    "bab2_6_3": "2.6.3 ROC-AUC dan Average Precision",
    "bab2_7": "2.7 Teknologi Pendukung",
    "bab2_7_1": "2.7.1 Bahasa Pemrograman Python",
    "bab2_7_2": "2.7.2 pandas dan NumPy",
    "bab2_7_3": "2.7.3 scikit-learn",
    "bab2_7_4": "2.7.4 Streamlit",
    "bab2_8": "2.8 Penelitian Terdahulu",
    "bab2_9": "2.9 Kerangka Pemikiran",
    "bab3": "BAB III METODOLOGI PENELITIAN",
    "bab3_1": "3.1 Jenis dan Pendekatan Penelitian",
    "bab3_2": "3.2 Tahapan Penelitian",
    "bab3_3": "3.3 Sumber dan Objek Penelitian",
    "bab3_3_1": "3.3.1 Dataset Penelitian",
    "bab3_3_2": "3.3.2 Lingkungan Penelitian",
    "bab3_4": "3.4 Definisi Operasional Variabel",
    "bab3_5": "3.5 Pra-pemrosesan Dataset",
    "bab3_5_1": "3.5.1 Validasi Struktur Data",
    "bab3_5_2": "3.5.2 Pemeriksaan Nilai Kosong",
    "bab3_5_3": "3.5.3 Deduplikasi Data",
    "bab3_5_4": "3.5.4 Penentuan Label",
    "bab3_5_5": "3.5.5 Penanganan Data Tidak Valid",
    "bab3_6": "3.6 Ekstraksi Fitur Statis",
    "bab3_6_1": "3.6.1 Parsing Kode dengan AST",
    "bab3_6_2": "3.6.2 Perhitungan Non-comment LOC",
    "bab3_6_3": "3.6.3 Perhitungan Parameter",
    "bab3_6_4": "3.6.4 Perhitungan Percabangan",
    "bab3_7": "3.7 Profil Dataset Hasil Pembersihan",
    "bab3_8": "3.8 Pembagian Data Latih dan Data Uji",
    "bab3_9": "3.9 Pelatihan Model Decision Tree",
    "bab3_9_1": "3.9.1 Konfigurasi Pelatihan",
    "bab3_9_2": "3.9.2 Pencarian Hyperparameter",
    "bab3_9_3": "3.9.3 Penentuan Threshold",
    "bab3_10": "3.10 Rancangan Evaluasi Model",
    "bab3_10_1": "3.10.1 Confusion Matrix",
    "bab3_10_2": "3.10.2 Metrik Klasifikasi",
    "bab3_10_3": "3.10.3 Pengujian Generalisasi",
    "bab3_11": "3.11 Rancangan Sistem",
    "bab3_11_1": "3.11.1 Kebutuhan Fungsional",
    "bab3_11_2": "3.11.2 Kebutuhan Nonfungsional",
    "bab3_11_3": "3.11.3 Arsitektur Sistem",
    "bab3_11_4": "3.11.4 Alur Analisis Kode",
    "bab3_11_5": "3.11.5 Rancangan Dashboard",
    "bab3_11_6": "3.11.6 Penjelasan Istilah pada Antarmuka",
    "bab3_12": "3.12 Skenario Pengujian",
    "bab3_13": "3.13 Indikator Keberhasilan",
    "bab3_14": "3.14 Etika Penelitian dan Keterbatasan",
    "tabel_2_1": "Tabel 2.1 Perbandingan Fitur Statis Long Method",
    "tabel_2_2": "Tabel 2.2 Confusion Matrix Dua Kelas",
    "tabel_2_3": "Tabel 2.3 Ringkasan Penelitian Terdahulu",
    "tabel_3_1": "Tabel 3.1 Tahapan, Aktivitas, dan Luaran Penelitian",
    "tabel_3_2": "Tabel 3.2 Definisi Operasional Variabel",
    "tabel_3_3": "Tabel 3.3 Aturan Pembersihan Dataset",
    "tabel_3_4": "Tabel 3.4 Fitur Statis dan Cara Perhitungan",
    "tabel_3_5": "Tabel 3.5 Profil Dataset Hasil Pembersihan",
    "tabel_3_6": "Tabel 3.6 Perbandingan Rata-rata Fitur per Label",
    "tabel_3_7": "Tabel 3.7 Pembagian Data Latih dan Data Uji",
    "tabel_3_8": "Tabel 3.8 Konfigurasi Hyperparameter Decision Tree",
    "tabel_3_9": "Tabel 3.9 Metrik dan Interpretasi Evaluasi",
    "tabel_3_10": "Tabel 3.10 Kebutuhan Fungsional Aplikasi",
    "tabel_3_11": "Tabel 3.11 Skenario Pengujian Sistem",
    "gambar_2_1": "Gambar 2.1 Struktur Konseptual Decision Tree",
    "gambar_2_2": "Gambar 2.2 Kerangka Pemikiran Penelitian",
    "gambar_3_1": "Gambar 3.1 Tahapan Penelitian",
    "gambar_3_2": "Gambar 3.2 Arsitektur Aplikasi CodeScope",
    "daftar_pustaka": "DAFTAR PUSTAKA",
}


def main() -> None:
    reader = PdfReader(PDF_PATH)
    normalized_pages = []
    for page in reader.pages:
        text = re.sub(r"\s+", "", page.extract_text() or "")
        normalized_pages.append(text)

    pages = {
        "judul_dalam": "i",
        "pengesahan": "ii",
        "motto": "iii",
        "pernyataan": "iv",
        "abstrak": "v",
        "abstract": "vi",
        "kata_pengantar": "vii",
        "daftar_isi": "viii",
        "daftar_tabel": "x",
        "daftar_gambar": "xi",
    }
    missing = []
    for key, needle in HEADINGS.items():
        needle = re.sub(r"\s+", "", needle)
        found = None
        for page_index in range(BODY_START_INDEX, len(normalized_pages)):
            if needle in normalized_pages[page_index]:
                found = page_index + 1 - BODY_PAGE_OFFSET
                break
        if found is None:
            missing.append(key)
        else:
            pages[key] = str(found)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(pages, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps({"missing": missing, "pages": pages}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

