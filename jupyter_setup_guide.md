# Panduan Setup dan Penggunaan Jupyter Notebook di VS Code

Dokumen ini berisi panduan lengkap untuk memasang ekstensi Jupyter di VS Code, mengonfigurasi virtual environment proyek, dan menjalankan file notebook interaktif `sentiment_analysis.ipynb` dari dalam editor VS Code secara langsung.

---

## 1. Memasang Ekstensi Jupyter di VS Code

Untuk dapat menampilkan dan menjalankan file Jupyter Notebook (`.ipynb`) di dalam editor VS Code, Anda perlu memasang ekstensi Jupyter resmi dari Microsoft:

1. Buka aplikasi **VS Code**.
2. Klik ikon **Extensions** pada bilah menu di sebelah kiri (atau gunakan pintasan tombol `Ctrl + Shift + X`).
3. Pada kotak pencarian di bagian atas, ketik **Jupyter**.
4. Cari ekstensi bernama **Jupyter** yang diterbitkan resmi oleh **Microsoft**.
5. Klik tombol **Install** di sebelah nama ekstensi tersebut.
6. Tunggu hingga proses instalasi selesai.

---

## 2. Mempersiapkan Virtual Environment dan Library Pendukung

Agar Jupyter Notebook dapat memuat pustaka pengolah kata bahasa Indonesia (Sastrawi), pustaka machine learning (Scikit-Learn), serta pustaka grafik (Matplotlib dan Seaborn), Anda harus memasangnya terlebih dahulu di dalam virtual environment proyek Anda.

Jalankan langkah-langkah berikut di terminal VS Code Anda:

1. Buka terminal baru di VS Code (`Ctrl + Shift + \`` atau menu Terminal > New Terminal).
2. Aktifkan virtual environment Anda:
   
   Jika Anda menggunakan **PowerShell** (default VS Code di Windows):
   ```powershell
   .\venv\Scripts\activate
   ```
   
   Jika Anda menggunakan **Command Prompt (CMD)**:
   ```cmd
   venv\Scripts\activate
   ```
   
   *Catatan: Pastikan muncul indikator `(venv)` di ujung kiri baris input terminal Anda.*

3. Lakukan instalasi Jupyter dan modul visualisasi di dalam virtual environment:
   ```bash
   pip install jupyter notebook matplotlib seaborn
   ```
   
   *Tips Pemecahan Masalah (Troubleshooting):*
   Jika Anda menemui error `Access is denied (WinError 5)` saat proses instalasi, hal tersebut dikarenakan terminal mencoba memasang paket di folder sistem utama Windows Anda. Pastikan langkah nomor 2 (mengaktifkan venv) sudah sukses dijalankan terlebih dahulu. Jika Anda sengaja ingin memasang secara global, gunakan opsi user:
   ```bash
   pip install --user jupyter notebook matplotlib seaborn
   ```

---

## 3. Memilih Kernel Virtual Environment di VS Code

Setelah ekstensi terpasang dan paket Jupyter terinstal, Anda harus memberi tahu VS Code untuk menjalankan kode menggunakan Python dari folder virtual environment proyek (`venv`), bukan Python sistem global komputer Anda.

1. Buka file **`sentiment_analysis.ipynb`** di dalam VS Code.
2. Perhatikan bagian pojok kanan atas dari tampilan tab editor notebook. Anda akan menemukan tombol bertuliskan **Select Kernel** (atau nama Python yang saat ini aktif).
3. Klik tombol **Select Kernel** tersebut.
4. Pada menu dropdown yang muncul di bagian atas, pilih opsi **Python Environments...**.
5. Dari daftar lingkungan Python yang terdeteksi, pilih lingkungan yang bertuliskan **venv (Python 3.12.x)** atau yang merujuk pada path `./venv/Scripts/python.exe`.
6. Tunggu beberapa saat hingga indikator di pojok kanan atas berubah menampilkan nama kernel Anda (contoh: `venv (Python 3.12.x)`).

---

## 4. Cara Menjalankan Sel Kode di Notebook

Seluruh blok kode di dalam Jupyter Notebook saling terhubung satu sama lain. Oleh karena itu, sel kode harus dieksekusi secara **berurutan dari paling atas (Step 1) hingga paling bawah (Step 9)**.

1. **Jalankan Sel Satu Per Satu**:
   Arahkan kursor Anda ke sel kode yang ingin dijalankan (misalnya bagian impor library di Step 1). Klik tombol **Play (ikon segitiga kecil)** di sebelah kiri sel tersebut, atau klik di dalam area sel kode lalu tekan tombol kombinasi **`Shift + Enter`**.
   
   *Tanda Berhasil:*
   Jika sel berhasil dieksekusi, akan muncul tanda centang hijau (`✓`) beserta durasi waktu eksekusi di sebelah kiri tombol Play, dan nomor antrean sel akan terisi (misalnya `[1]`).

2. **Jalankan Semua Sel Secara Otomatis**:
   Anda juga dapat menjalankan seluruh alur dari awal sampai akhir secara otomatis dengan mengeklik tombol **Run All** yang ada pada menu bar di bagian atas tampilan tab notebook (sejajar dengan tombol `+ Code` dan `+ Markdown`).

3. **Mereset Status Eksekusi (Mulai Ulang)**:
   Jika Anda melakukan modifikasi pada kode preprocessing atau ingin memulai ulang pemrosesan data dari awal secara bersih:
   * Klik tombol **Restart** di bilah menu atas notebook.
   * Klik tombol **Clear All Outputs** untuk membersihkan seluruh riwayat teks dan grafik yang tercetak di layar.
   * Jalankan kembali sel dari Step 1 secara berurutan ke bawah.
