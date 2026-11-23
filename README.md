# CodeScope

Prototipe Streamlit untuk mengklasifikasikan Long Method pada kode Python berdasarkan tiga fitur statis: non-comment LOC, jumlah parameter, dan jumlah percabangan.

## Menjalankan aplikasi

1. Jalankan `run_app.bat`, atau:

   ```powershell
   .\.venv\Scripts\streamlit.exe run app.py
   ```

2. Buka `http://localhost:8501`.
3. Pilih contoh kode atau tempel fungsi Python, lalu tekan **Analisis dan tampilkan dashboard**.

Dashboard menampilkan status per fungsi, probabilitas Long Method, tiga fitur
statis, jalur keputusan model, saran peninjauan, dan unduhan hasil JSON.
Ikon informasi di samping istilah dapat diarahkan dengan kursor atau diketuk
untuk menampilkan definisi singkat.

Panel kanan membedakan hasil prediksi untuk kode yang dimasukkan melalui IDE
dari perbandingan metrik data latih dan data uji. Precision, recall, dan
F1-score dihitung pada data berlabel; satu input IDE belum memiliki label
aktual sehingga tidak dapat digunakan untuk menghitung metrik tersebut.

Untuk membuat data uji dari kode input:

1. Buka **Uji dataset baru dari file**.
2. Klik **Gunakan data uji internal** untuk memakai 16.209 data uji holdout
   tanpa upload, atau unggah file `.py`/`.csv` baru.
3. File unggahan harus berisi beberapa fungsi atau CSV dengan kolom
   `code`.
4. Aplikasi memberi label R0915 secara otomatis dan menghitung prediksi model.
5. File harus memuat sekurang-kurangnya satu fungsi Long Method dan satu fungsi
   bukan Long Method.
6. Metrik data uji input akan tampil dan dibandingkan dengan metrik data latih.

Input satu fungsi tetap digunakan untuk prediksi satuan. Precision, recall, dan
F1-score membutuhkan minimal dua kelas. Jika jumlah sampel kurang dari 10,
metrik tetap ditampilkan bersama peringatan bahwa sampelnya relatif kecil.

## Versi model V1 dan V2

Setiap submit dengan kode baru dari editor membentuk snapshot latih versi baru. V1 tidak
ditimpa; model baru disimpan sebagai V2, V3, dan seterusnya. Threshold setiap
versi dikalibrasi hanya dari out-of-fold snapshot latih versi tersebut.
Seluruh versi diuji pada file benchmark repository holdout yang sama sehingga
perubahan precision, recall, dan F1-score dapat dibandingkan secara adil.

Input yang kodenya identik dengan data benchmark dilewati agar tidak terjadi
data leakage. File yang diunggah melalui panel evaluasi hanya dipakai untuk
menguji model dan tidak otomatis masuk ke snapshot latih.

Lokasi hasil versi:

- `artifacts/model_registry.json`: daftar versi, parent, threshold, dan jumlah record.
- `artifacts/model_versions/V1/`: model awal, metrik, snapshot latih, dan benchmark beku.
- `artifacts/model_versions/V2/`: model hasil submit pertama beserta snapshot latihnya.

Dashboard menampilkan V1 dan versi terbaru berdampingan, termasuk metrik data
latih, metrik benchmark, jumlah record, dan threshold.

Untuk kembali sepenuhnya ke V1, buka **Kembali ke model V1**, centang
konfirmasi, lalu tekan tombol reset. Tindakan ini menghapus permanen folder
V2 dan seluruh versi setelahnya. Setelah halaman di-refresh, registry hanya
berisi V1 dan tidak ada versi tambahan yang muncul kembali.

## Pipeline data

Dataset mentah berisi satu baris untuk setiap pesan Pylint. Pipeline mengubahnya menjadi satu baris untuk setiap potongan kode unik:

```powershell
.\.venv\Scripts\python.exe -m scripts.prepare_dataset "C:\path\ke\codesmell_dataset.csv"
.\.venv\Scripts\python.exe -m scripts.train_model
```

Pipeline melakukan:

- Pemeriksaan nilai wajib dan file CSV berukuran besar.
- Deduplikasi berdasarkan SHA-256 dari kode.
- Pembentukan label Long Method dari sinyal Pylint `R0915` (too-many-statements).
- Ekstraksi fitur dari Python AST.
- Pemisahan data uji berdasarkan repository agar tidak ada kebocoran antarkumpulan data.
- Pemilihan hyperparameter dengan GroupKFold.
- Kalibrasi threshold hanya dari out-of-fold data latih.

## Pengujian

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Artifact utama

- `app.py`: antarmuka Streamlit dan dashboard.
- `src/feature_extraction.py`: ekstraksi fungsi dan fitur statis.
- `src/analysis.py`: inferensi dan penjelasan jalur Decision Tree.
- `src/model_versions.py`: snapshot, pelatihan ulang, dan registry versi model.
- `artifacts/long_method_model.joblib`: model siap pakai.
- `artifacts/metrics.json`: metrik evaluasi dan statistik dataset.
- `data/processed/long_method_dataset.csv`: dataset siap latih.
- `data/processed/data_quality.json`: audit pembersihan data.
- `outputs/<thread-id>/CodeScope_Dataset_Audit.xlsx`: ringkasan kualitas data
  dan evaluasi model untuk kebutuhan bimbingan.

Hasil evaluasi saat ini pada repository uji:

| Metrik | Data latih | Data uji |
| --- | ---: | ---: |
| Precision | 0.786 | 0.618 |
| Recall | 0.893 | 0.839 |
| F1-score | 0.836 | 0.712 |
| ROC-AUC | 0.992 | 0.989 |
| Threshold klasifikasi | 0.880 | 0.880 |

## Batasan

Model hanya diklasifikasikan untuk Long Method. Dataset asal adalah contoh pesan Pylint dari repository publik; performa dapat berubah pada gaya penulisan, versi Python, atau domain proyek yang berbeda. Hasil aplikasi adalah indikator untuk peninjauan kode, bukan penilaian mutlak kualitas perangkat lunak.

