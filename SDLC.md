# SDLC (Software Development Life Cycle) untuk Proyek Analisis Sentimen

Dokumen ini menjelaskan siklus hidup pengembangan perangkat lunak (SDLC) proyek Analisis Sentimen dan Dashboard Visualisasi.

## 1. Perencanaan (Planning)
- Menentukan tujuan sistem: menganalisis sentimen ulasan wisata dan menampilkan hasil dalam dashboard interaktif.
- Mendefinisikan ruang lingkup: pengambilan data Google Maps, preprocessing teks Bahasa Indonesia, pelatihan model machine learning, frontend web interaktif, serta evaluasi usability.
- Menyusun kebutuhan fungsional dan non-fungsional: upload dataset CSV, prediksi teks, histori, dashboard, kinerja model, dan kemudahan penggunaan.
- Membuat jadwal pengembangan dan merencanakan sumber daya.

## 2. Analisis Kebutuhan (Requirements Analysis)
- Kebutuhan data: ulasan dari 8 titik lokasi (6 objek wisata, 2 dermaga), format CSV, atribut teks, rating, tanggal.
- Kebutuhan fungsional:
  - Import dan merge data
  - Cleansing, deduplication, preprocessing
  - Training model dan prediksi real-time
  - Dashboard visualisasi statistik dan tren
  - Manajemen histori prediksi
- Kebutuhan non-fungsional:
  - Waktu respons yang wajar
  - Kebersihan data dan ketelitian preprocessing
  - Kemudahan penggunaan antarmuka
  - Kualitas metrik evaluasi model

## 3. Perancangan Sistem (Design)
### 3.1 Desain Arsitektur
- Backend: Python + Flask
- Database: PostgreSQL via SQLAlchemy
- NLP & ML: NLTK, Sastrawi, scikit-learn
- Frontend: HTML, CSS, JavaScript, Chart.js
- Penyimpanan model: joblib pada folder `model/`

### 3.2 Desain Data
- Dataset master hasil merge dari 8 lokasi
- Struktur tabel: `training_data`, `prediction_history`, `training_logs`
- Field penting: `text`, `label`, `rating`, `tahun`, `bulan`, `tanggal_asli`, `nb_predicted_label`, `nb_confidence`

### 3.3 Desain Antarmuka
- Halaman utama: upload data, prediksi teks, hasil, preprocessing
- Halaman training: statistik dataset, training, hasil evaluasi, logs, reset sistem
- Halaman dashboard: tren, distribusi, keyword, sample review
- Halaman histori: tabel prediksi, filter, pencarian, pagination

## 4. Implementasi (Development)
- Membangun modul preprocessing (`preprocessing.py`) untuk cleansing, tokenisasi, stopword removal, dan stemming.
- Membangun model ML (`ml_model.py`) dengan TF-IDF dan Complement Naive Bayes.
- Mengembangkan route Flask (`routes.py`) untuk API upload, training, prediksi, statistik, histori, dan reset.
- Mengembangkan frontend template (`templates/`) dan JavaScript (`static/js/`) untuk interaksi pengguna.
- Menambahkan konfigurasi lingkungan di `config.py` dan file `.env.example`.

## 5. Pengujian (Testing)
- Unit test/validasi preprocessing dan model dapat dilakukan secara lokal.
- Verifikasi integrasi alur data: upload CSV → training → prediksi → tampilan dashboard.
- Evaluasi model dengan confusion matrix, accuracy, precision, recall, F1-score.
- Pengujian usability dengan kuesioner SUS untuk menilai antarmuka dan kemudahan penggunaan.

## 6. Deployment
- Menjalankan aplikasi lokal dengan `python app.py`.
- Untuk deployment produksi, gunakan WSGI server (misalnya Gunicorn) dan reverse proxy (misalnya Nginx).
- Pastikan koneksi ke PostgreSQL aman dan konfigurasi environment file disimpan terbatas.

## 7. Pemeliharaan (Maintenance)
- Memperbarui dataset dan melakukan retraining saat data baru tersedia.
- Menangani bug pada preprocessing, upload, atau antarmuka.
- Meningkatkan model dan fitur dashboard berdasarkan feedback pengguna.

## 8. Revisi dan Iterasi
- Mengadaptasi model jika performa tidak memadai atau data berubah.
- Menambah fitur baru seperti export report, deteksi topik aspek, atau rekomendasi.
- Mengulang siklus SDLC untuk perbaikan terus-menerus.

## 9. Hubungan SDLC dengan Bab III Skripsi
- Bab III dapat menggunakan kerangka SDLC ini sebagai landasan proses metodologi.
- Setiap fase SDLC dapat dijabarkan menjadi subbab: perencanaan, analisis, desain, implementasi, pengujian, dan deployment.
- Dokumentasikan setiap langkah agar penelitian dapat direplikasi.
