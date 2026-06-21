"""Quick metric extraction for BAB 4.3 template update"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import ComplementNB
from preprocessing import preprocess_text
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from collections import Counter

# Load data
try:
    df = pd.read_csv('dataset/MASTER DATASET PULAU MERAK.csv')
except:
    df = pd.read_csv('merged_data_all.csv')

def map_rating_to_sentiment(rating):
    try:
        if isinstance(rating, str):
            rating_val = int(''.join(filter(str.isdigit, rating.split()[0])))
        else:
            rating_val = int(rating)
        if rating_val >= 4: return 'positif'
        elif rating_val == 3: return 'netral'
        else: return 'negatif'
    except:
        return None

df['sentiment'] = df['Rating'].apply(map_rating_to_sentiment)
df_clean = df.dropna(subset=['Teks Ulasan']).copy()
df_clean = df_clean[df_clean['sentiment'].notna()].copy()

# Quick stats
print("\n### DATA METRICS ###")
print(f"Total usable records: {len(df_clean)}")
sentiment_dist = df_clean['sentiment'].value_counts()
for s in ['positif', 'netral', 'negatif']:
    count = sentiment_dist.get(s, 0)
    pct = (count / len(df_clean)) * 100
    print(f"{s:10s}: {count:5d} ({pct:6.2f}%)")

# Text stats
df_clean['text_len'] = df_clean['Teks Ulasan'].str.len()
print(f"\nText length - Mean: {df_clean['text_len'].mean():.1f}, Max: {df_clean['text_len'].max()}")

# Prepare training
X = df_clean['Teks Ulasan'].values
y = df_clean['sentiment'].values
X_processed = np.array([preprocess_text(text) for text in X])
X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42, stratify=y)

print(f"\n### TRAINING DATA ###")
print(f"Train/Test split: {len(X_train)}/{len(X_test)}")

# TF-IDF
tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1,2), min_df=5, max_df=0.90, sublinear_tf=True)
X_train_tf = tfidf.fit_transform(X_train)
X_test_tf = tfidf.transform(X_test)
print(f"TF-IDF features: {X_train_tf.shape[1]}")
print(f"Sparsity: {(1 - X_train_tf.nnz / (X_train_tf.shape[0] * X_train_tf.shape[1])) * 100:.2f}%")

# Train model
model = ComplementNB(alpha=1.0)
model.fit(X_train_tf, y_train)

# Evaluate
y_pred = model.predict(X_test_tf)
acc = accuracy_score(y_test, y_pred)
print(f"\n### MODEL RESULTS ###")
print(f"Accuracy: {acc*100:.2f}%")

report = classification_report(y_test, y_pred, labels=['negatif', 'netral', 'positif'], output_dict=True, zero_division=0)
print(f"\nPer-Class Performance:")
print(f"{'Label':<12} {'Precision':>10} {'Recall':>10} {'F1-Score':>10} {'Support':>10}")
for label in ['negatif', 'netral', 'positif']:
    r = report.get(label, {})
    print(f"{label:<12} {r.get('precision', 0):>10.4f} {r.get('recall', 0):>10.4f} {r.get('f1-score', 0):>10.4f} {int(r.get('support', 0)):>10d}")

print(f"\nMacro Avg F1: {report['macro avg']['f1-score']:.4f}")
print(f"Weighted Avg F1: {report['weighted avg']['f1-score']:.4f}")

# Confusion matrix
cm = confusion_matrix(y_test, y_pred, labels=['negatif', 'netral', 'positif'])
print(f"\nConfusion Matrix (rows=true, cols=pred):")
print(f"       Neg  Neu  Pos")
for i, label in enumerate(['Negatif', 'Netral', 'Positif']):
    print(f"{label:10s} {cm[i,0]:3d} {cm[i,1]:3d} {cm[i,2]:3d}")

print("\n✓ Metrics extraction complete!")
