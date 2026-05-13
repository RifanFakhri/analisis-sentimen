# Flask Sentiment Analysis Bootstrap

## Project Name
sentiment-analysis-flask

## Goal
Membangun aplikasi analisis sentimen berbasis Flask menggunakan algoritma Multinomial Naive Bayes dengan PostgreSQL sebagai database.

Sistem melakukan:
- preprocessing text
- training model
- prediksi sentimen
- penyimpanan history prediksi

Kategori sentimen:
- positif
- negatif
- netral

---

# Stack

## Backend
- Python
- Flask

## Machine Learning
- scikit-learn
- pandas
- Sastrawi

## Database
- PostgreSQL
- SQLAlchemy

---

# Folder Structure

```text
sentiment-analysis-flask/
│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── preprocessing.py
│   ├── model_loader.py
│   │
│   ├── models/
│   │   ├── naive_bayes_model.pkl
│   │   └── vectorizer.pkl
│   │
│   ├── templates/
│   │   └── index.html
│   │
│   └── static/
│
├── dataset/
│   └── dataset.csv
│
├── requirements.txt
├── train_model.py
├── config.py
├── run.py
└── bootstrap.md
```

---

# Initial Setup

## Create Project

```bash
mkdir sentiment-analysis-flask
cd sentiment-analysis-flask
```

## Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/Mac

```bash
python -m venv venv
source venv/bin/activate
```

---

# Install Dependencies

```bash
pip install flask pandas scikit-learn sastrawi joblib psycopg2-binary sqlalchemy
```

---

# requirements.txt

```txt
flask
pandas
scikit-learn
sastrawi
joblib
psycopg2-binary
sqlalchemy
```

---

# Dataset Structure

## dataset.csv

```csv
text,sentiment
pelayanan sangat bagus,positif
pengiriman cepat,positif
barang rusak,negatif
admin tidak merespon,negatif
biasa saja,netral
```

---

# Preprocessing Pipeline

Tahapan preprocessing:

1. Cleaning
2. Case Folding
3. Tokenization
4. Stopword Removal
5. Stemming

Gunakan:
- regex
- Sastrawi

---

# Machine Learning Pipeline

## TF-IDF

Gunakan:
- TfidfVectorizer

## Model

Gunakan:
- MultinomialNB

## Save Model

Simpan:
- naive_bayes_model.pkl
- vectorizer.pkl

Menggunakan:
- joblib

---

# Flask Features

## Homepage

Form input text:
- textarea
- button predict

## Prediction

Saat user submit:
1. preprocessing
2. vectorization
3. prediction
4. tampil hasil

---

# PostgreSQL Plan

## Database Name

```text
sentiment_db
```

## Table predictions

| Column | Type |
|---|---|
| id | integer |
| text | text |
| sentiment | varchar |
| created_at | timestamp |

---

# Flask Route Plan

## GET /

Menampilkan halaman utama.

## POST /

Melakukan prediksi sentimen.

---

# Future API

## POST /predict

Request:

```json
{
  "text": "pelayanan sangat bagus"
}
```

Response:

```json
{
  "sentiment": "positif"
}
```

---

# Development Steps

## Step 1
Setup Flask project structure.

## Step 2
Buat preprocessing module.

## Step 3
Buat training script.

## Step 4
Training model Naive Bayes.

## Step 5
Save model dan vectorizer.

## Step 6
Load model ke Flask.

## Step 7
Buat halaman input sentimen.

## Step 8
Tampilkan hasil prediksi.

## Step 9
Integrasi PostgreSQL.

## Step 10
Simpan history prediction.

---

# Coding Standards

- gunakan Blueprint Flask
- gunakan modular structure
- pisahkan preprocessing
- pisahkan model loader
- gunakan clean architecture
- gunakan environment virtual python