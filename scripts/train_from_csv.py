"""
Train sentiment model directly from a CSV file (no Flask/DB required).
Usage:
    python scripts/train_from_csv.py dataset/MASTER DATASET PULAU MERAK.csv

The script will:
- Read CSV, detect text & label columns (support 'Teks Ulasan'/'text' and 'Sentimen'/'label' or 'Rating')
- Build lists of texts and labels (skip rows without valid text/label)
- Train model using `ml_model.sentiment_model.train`
- Save model and vectorizer to `model/`
- Print training metrics
"""
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from seed_data import map_rating_to_sentiment
from ml_model import sentiment_model


def detect_columns(df):
    cols_lower = {c.lower(): c for c in df.columns}
    text_col = cols_lower.get('teks ulasan') or cols_lower.get('text') or cols_lower.get('teks')
    label_col = None
    for k in ['label', 'sentimen', 'sentiment', 'label sentimen', 'label_sentimen']:
        if k in cols_lower:
            label_col = cols_lower[k]
            break
    rating_col = cols_lower.get('rating')
    return text_col, label_col, rating_col


def load_data(path):
    df = pd.read_csv(path)
    text_col, label_col, rating_col = detect_columns(df)
    if not text_col:
        raise ValueError('CSV must contain a text column: Teks Ulasan or text')

    texts = []
    labels = []
    for _, r in df.iterrows():
        text = str(r.get(text_col) or '').strip()
        if not text:
            continue
        label = None
        if label_col and pd.notna(r.get(label_col)):
            raw_label = str(r.get(label_col)).strip().lower()
            if raw_label in ('positif','negatif','netral'):
                label = raw_label
            else:
                try:
                    num = int(float(raw_label))
                    label, _ = map_rating_to_sentiment(num)
                except Exception:
                    label = None
        if label is None and rating_col and pd.notna(r.get(rating_col)):
            label, _ = map_rating_to_sentiment(r.get(rating_col))
        if label is None:
            continue
        texts.append(text)
        labels.append(label)
    return texts, labels


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python scripts/train_from_csv.py path/to/dataset.csv')
        sys.exit(1)
    path = sys.argv[1]
    print(f'Loading data from: {path}')
    texts, labels = load_data(path)
    print(f'Loaded {len(texts)} labeled samples. Label distribution:')
    from collections import Counter
    print(Counter(labels))

    if len(texts) < 10:
        print('Not enough samples to train (minimum 10 required).')
        sys.exit(1)

    print('Training model...')
    metrics = sentiment_model.train(texts, labels)
    print('Training finished. Metrics:')
    print(metrics)
    print('Model files saved under model/ directory.')
