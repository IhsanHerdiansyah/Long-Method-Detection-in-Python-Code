"""Plain-language explanations shown by the dashboard tooltip icons."""


TERM_HELP = {
    "tooltip": (
        "Arahkan kursor ke ikon i untuk membaca definisi. Pada perangkat "
        "sentuh, ketuk ikon agar penjelasan tetap tampil."
    ),
    "ast": (
        "AST (Abstract Syntax Tree) adalah representasi struktur sintaks "
        "Python. Melalui AST, aplikasi dapat mengenali fungsi, parameter, "
        "perulangan, kondisi, dan blok penanganan error."
    ),
    "static_features": (
        "Fitur statis adalah nilai yang dihitung dari struktur kode tanpa "
        "menjalankannya. Model ini memakai LOC, jumlah parameter, dan jumlah "
        "percabangan."
    ),
    "decision_tree": (
        "Decision Tree adalah model klasifikasi berbentuk pohon aturan. Model "
        "memilih cabang berdasarkan nilai fitur sampai mencapai keputusan "
        "Long Method atau bukan."
    ),
    "dashboard": (
        "Dashboard menggabungkan hasil prediksi, probabilitas, fitur kode, "
        "aturan keputusan, dan ringkasan kualitas model dalam satu tampilan."
    ),
    "model_version": (
        "Versi model adalah salinan model dan metriknya yang disimpan terpisah. "
        "V1 adalah model awal yang dibekukan. Setelah kode baru ditambahkan ke "
        "data latih, sistem membuat V2 atau versi berikutnya tanpa mengubah "
        "threshold dan nilai versi lama. Semua versi diuji pada benchmark yang sama."
    ),
    "function_count": (
        "Jumlah fungsi dan method yang berhasil dikenali dari kode yang "
        "dimasukkan. Satu class dapat menghasilkan beberapa fungsi analisis."
    ),
    "flagged": (
        "Jumlah fungsi yang probabilitas Long Method-nya mencapai atau "
        "melewati threshold model. Status ini berarti perlu ditinjau."
    ),
    "clear": (
        "Jumlah fungsi yang probabilitas Long Method-nya masih berada di bawah "
        "threshold. Artinya model tidak menemukan indikasi yang cukup kuat."
    ),
    "max_probability": (
        "Nilai probabilitas paling tinggi dari seluruh fungsi yang dianalisis. "
        "Nilai ini membantu menentukan fungsi yang paling perlu diperiksa."
    ),
    "composition": (
        "Perbandingan jumlah fungsi yang terindikasi dan tidak terindikasi. "
        "Diagram ini memudahkan pembacaan ketika kode berisi banyak fungsi."
    ),
    "probability": (
        "Skor keluaran Decision Tree untuk kelas Long Method dalam rentang 0 "
        "hingga 100 persen. Skor ini bukan ukuran mutlak bahwa kode salah."
    ),
    "prediction": (
        "Hasil akhir setelah probabilitas dibandingkan dengan threshold. "
        "Prediksi hanya menunjukkan indikasi yang perlu diperiksa manusia."
    ),
    "line_range": (
        "Rentang baris fisik tempat fungsi berada di editor. Rentang ini "
        "berbeda dari LOC karena baris kosong dan komentar tetap termasuk "
        "dalam nomor baris."
    ),
    "nloc": (
        "Non-comment LOC adalah jumlah baris fisik yang mengandung token "
        "Python. Baris kosong, komentar, dan indentasi saja tidak dihitung."
    ),
    "parameter_count": (
        "Jumlah parameter pada definisi fungsi, termasuk parameter posisi, "
        "nilai default, keyword-only, *args, **kwargs, dan self pada method."
    ),
    "branch_count": (
        "Jumlah jalur keputusan seperti if, for, while, except, ekspresi "
        "bersyarat, match case, comprehension, serta tambahan cabang boolean."
    ),
    "decision_path": (
        "Urutan aturan Decision Tree yang dilalui fungsi sampai mencapai "
        "prediksi. Simbol <= berarti nilai fitur tidak lebih besar dari batas, "
        "sedangkan > berarti nilai fitur lebih besar dari batas."
    ),
    "recommendation": (
        "Saran yang diturunkan dari fitur paling menonjol. Saran bukan "
        "keputusan otomatis, tetapi titik awal untuk meninjau dan merapikan kode."
    ),
    "json": (
        "JSON adalah format data terstruktur. Hasil dapat diunduh untuk "
        "disimpan, diolah kembali, atau dilampirkan sebagai bukti pengujian."
    ),
    "precision": (
        "Dari semua fungsi yang diprediksi positif, precision menunjukkan "
        "proporsi yang benar-benar positif. Nilai rendah berarti ada lebih "
        "banyak peringatan palsu."
    ),
    "recall": (
        "Dari semua fungsi yang sebenarnya positif, recall menunjukkan "
        "proporsi yang berhasil ditemukan model. Nilai rendah berarti lebih "
        "banyak Long Method terlewat."
    ),
    "f1_score": (
        "F1-score menggabungkan precision dan recall menggunakan harmonic "
        "mean. Nilai ini cocok untuk data dengan jumlah kelas positif yang "
        "jauh lebih sedikit daripada kelas negatif."
    ),
    "roc_auc": (
        "ROC-AUC mengukur kemampuan model mengurutkan kelas positif di atas "
        "kelas negatif. Nilai tinggi tidak berarti akurasi atau probabilitas "
        "kebenaran juga sebesar itu."
    ),
    "accuracy": (
        "Accuracy adalah proporsi seluruh prediksi yang benar. Nilai ini dapat "
        "terlihat tinggi ketika jumlah kelas negatif jauh lebih banyak."
    ),
    "threshold": (
        "Ambang batas probabilitas untuk menentukan kelas akhir. Pada model "
        "ini, fungsi disebut terindikasi jika probabilitasnya minimal 88 persen."
    ),
    "feature_importance": (
        "Feature importance menunjukkan seberapa besar kontribusi suatu fitur "
        "dalam membentuk cabang Decision Tree. Nilai ini bukan tingkat akurasi "
        "masing-masing fitur."
    ),
    "confusion_matrix": (
        "Confusion matrix membandingkan prediksi dengan label sebenarnya. "
        "Matriks menunjukkan prediksi benar dan salah untuk kelas positif dan "
        "negatif."
    ),
    "true_negative": (
        "Benar negatif berarti model memprediksi tidak terindikasi dan label "
        "sebenarnya juga tidak terindikasi."
    ),
    "false_positive": (
        "Salah positif adalah peringatan palsu: model memprediksi terindikasi, "
        "sedangkan label sebenarnya negatif."
    ),
    "false_negative": (
        "Salah negatif berarti Long Method terlewat: model memprediksi tidak "
        "terindikasi, sedangkan label sebenarnya positif."
    ),
    "true_positive": (
        "Benar positif berarti model memprediksi terindikasi dan label "
        "sebenarnya juga Long Method."
    ),
    "raw_rows": (
        "Jumlah pesan Pylint pada dataset awal. Satu fungsi dapat muncul "
        "berkali-kali bila menghasilkan beberapa pesan code smell."
    ),
    "duplicates_removed": (
        "Jumlah baris berulang yang dihapus agar setiap kode unik hanya "
        "memiliki satu record. Ini mencegah kebocoran dan bias saat pelatihan."
    ),
    "clean_rows": (
        "Jumlah record fungsi unik yang sudah melalui pemeriksaan nilai wajib, "
        "deduplikasi, dan ekstraksi fitur."
    ),
    "repositories": (
        "Jumlah repository sumber data. Repository dipakai sebagai kelompok "
        "saat membagi data latih dan uji agar tidak terjadi kebocoran data."
    ),
    "train_test": (
        "Data dipisahkan berdasarkan repository. Repository pada data uji "
        "tidak dipakai untuk memilih hyperparameter atau melatih model."
    ),
    "ide_result": (
        "Hasil prediksi untuk kode yang sedang dimasukkan melalui IDE. Satu "
        "input akan dibandingkan dengan label otomatis Pylint R0915, lalu "
        "ditampilkan label prediksi, probabilitas, dan status pengujiannya."
    ),
    "test_metrics": (
        "Metrik precision, recall, dan F1-score dihitung dengan membandingkan "
        "label aktual R0915 dan prediksi model pada file data uji baru yang "
        "diunggah pengguna."
    ),
    "automatic_label": (
        "Label pembanding otomatis diperoleh dengan menjalankan Pylint R0915 "
        "tanpa mengeksekusi kode. Label ini independen dari prediksi Decision "
        "Tree sehingga dapat digunakan untuk menghitung metrik pengujian."
    ),
}

