# SentimentAI - Analisis Sentimen Ulasan Wisata Pulau Merak

Sistem Analisis Sentimen berbasis web menggunakan algoritma **Complement Naive Bayes (CNB)** untuk mengklasifikasikan ulasan wisatawan ke dalam tiga kategori: **Positif**, **Netral**, dan **Negatif**.

Aplikasi ini dibangun menggunakan **Flask** untuk backend, **PostgreSQL** untuk penyimpanan data, dan **Chart.js** untuk dashboard visualisasi interaktif.

## 🚀 Fitur Utama
- **Prediksi Sentimen**: Analisis teks ulasan secara real-time dengan visualisasi probabilitas.
- **Preprocessing Pipeline**: Case folding, cleaning, normalization (slang handling), tokenization, stopword removal (preserving negation), dan stemming (Sastrawi).
- **Dashboard Interaktif**: Visualisasi tren sentimen per tahun, distribusi total, dan analisis kata kunci keluhan.
- **Manajemen Data**: CRUD Riwayat prediksi dan pengelolaan data training.
- **Oversampling Strategy**: Mengatasi data imbalance untuk meningkatkan akurasi pada ulasan negatif dan netral.

## 🛠️ Tech Stack
- **Backend**: Python 3.12+, Flask, SQLAlchemy
- **Machine Learning**: Scikit-learn (ComplementNB, TF-IDF Vectorizer)
- **NLP**: NLTK, Sastrawi
- **Database**: PostgreSQL
- **Frontend**: HTML5, Vanilla CSS, JavaScript (ES6), Chart.js, FontAwesome

## 📋 Prasyarat
- Python 3.12 atau lebih baru
- PostgreSQL 13+
- Virtual Environment (direkomendasikan)

## 🔧 Instalasi & Setup

1. **Clone Repositori**
   ```bash
   git clone https://github.com/username/sentiment-analysis-flask.git
   cd sentiment-analysis-flask
   ```

2. **Buat & Aktifkan Virtual Environment**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

   Jika PowerShell menolak menjalankan skrip `activate`, jalankan Python langsung dari virtual environment:
   ```bash
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. **Install Dependensi**
   ```bash
   pip install -r requirements.txt
   ```

4. **Konfigurasi Database**
   - Buat database baru di PostgreSQL dengan nama `sentimen`.
   - Salin file `.env.example` menjadi `.env`:
     ```bash
     cp .env.example .env
     ```
   - Sesuaikan kredensial database Anda di file `.env`.

5. **Persiapkan Dataset**
   - Buat folder `dataset/` di direktori utama.
   - Masukkan file ulasan Anda (CSV) ke dalam folder tersebut dengan nama `dataset_master_merak_lengkap.csv`.

6. **Inisialisasi & Seed Data**
   ```bash
   python seed_data.py
   ```

7. **Jalankan Aplikasi**
   ```bash
   python app.py
   ```

   Jika aktivasi virtual environment tidak berhasil di Windows PowerShell, jalankan:
   ```bash
   .\venv\Scripts\python.exe app.py
   ```

   Aplikasi akan berjalan di `http://127.0.0.1:5000`.

## 🧠 Alur Kerja Sistem
1. **Input**: Teks ulasan dari pengguna.
2. **Preprocessing**: Pembersihan teks dan normalisasi bahasa.
3. **Feature Extraction**: Pembobotan kata menggunakan TF-IDF (n-gram 1-2).
4. **Classification**: Prediksi kategori menggunakan model Complement Naive Bayes yang sudah dilatih.
5. **Output**: Label sentimen, skor kepercayaan, dan visualisasi distribusi peluang.

## 📂 Struktur Proyek
- `app.py`: Entry point aplikasi Flask.
- `routes.py`: Definisi endpoint API dan rute halaman.
- `models.py`: Definisi skema database SQLAlchemy.
- `ml_model.py`: Logika pelatihan dan prediksi machine learning.
- `preprocessing.py`: Pipeline pemrosesan teks bahasa Indonesia.
- `seed_data.py`: Script untuk migrasi dan import data dari CSV.
- `static/`: File aset (CSS, JS, Gambar).
- `templates/`: File template HTML (Jinja2).

## 📝 Lisensi
Distribusi di bawah lisensi MIT. Lihat `LICENSE` untuk informasi lebih lanjut.
