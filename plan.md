# Sentiment Analysis Project Plan

## Project Title
Analisis Sentimen Ulasan Menggunakan Algoritma Multinomial Naive Bayes Berbasis Flask

---

# Project Overview

Project ini bertujuan membangun sistem analisis sentimen berbasis web menggunakan framework Flask dan algoritma Multinomial Naive Bayes.

Sistem digunakan untuk melakukan klasifikasi sentimen terhadap data ulasan teks ke dalam kategori:
- Positif
- Negatif
- Netral

Project difokuskan pada:
- text preprocessing
- machine learning classification
- sentiment prediction
- history prediction storage
- REST API preparation

---

# Main Objectives

## Objectives

1. Membangun sistem analisis sentimen berbasis web.
2. Mengimplementasikan algoritma Multinomial Naive Bayes.
3. Melakukan preprocessing data teks bahasa Indonesia.
4. Menampilkan hasil klasifikasi sentimen secara realtime.
5. Menyimpan histori prediksi ke database PostgreSQL.

---

# Scope

## Included Features

- Input teks ulasan
- Prediksi sentimen
- Text preprocessing
- TF-IDF vectorization
- Training model
- Save/load model
- Penyimpanan histori prediksi
- Web interface menggunakan Flask

## Excluded Features (Current Version)

- Authentication
- Multi-user system
- Dashboard analytics
- Deep learning model
- Deployment production

---

# System Architecture

```text
User
↓
Flask Web Interface
↓
Text Preprocessing
↓
TF-IDF Vectorizer
↓
Multinomial Naive Bayes
↓
Prediction Result
↓
PostgreSQL Database