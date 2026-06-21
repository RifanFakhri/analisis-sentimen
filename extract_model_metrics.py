"""
Script untuk ekstrak metrik model terbaru dan karakteristik sistem.
Output untuk pembaruan BAB 4.3 template.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import ComplementNB
from preprocessing import preprocess_text
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, f1_score
from collections import Counter
import json

print("\n" + "="*100)
print("EKSTRAKSI METRIK MODEL DAN SISTEM TERBARU UNTUK BAB 4.3")
print("="*100)

# 1. LOAD DATA
print("\n[1] LOADING DATASET...")
# Try to load from best available source
try:
    df = pd.read_csv('dataset/MASTER DATASET PULAU MERAK.csv')
    print("  Using: dataset/MASTER DATASET PULAU MERAK.csv")
except:
    try:
        df = pd.read_csv('DATASETPULAUMERAK.csv')
        print("  Using: DATASETPULAUMERAK.csv")
    except:
        df = pd.read_csv('merged_data_all.csv')
        print("  Using: merged_data_all.csv")

# Map ratings to sentiments
def map_rating_to_sentiment(rating):
    try:
        # Handle different input formats
        if isinstance(rating, str):
            # Extract numeric part (e.g., "5 bintang" → 5)
            rating_val = int(''.join(filter(str.isdigit, rating.split()[0])))
        else:
            rating_val = int(rating)
        
        if rating_val >= 4: return 'positif'
        elif rating_val == 3: return 'netral'
        else: return 'negatif'
    except:
        return None

df['sentiment'] = df['Rating'].apply(map_rating_to_sentiment)
# Remove rows with missing text or sentiment
df_clean = df.dropna(subset=['Teks Ulasan']).copy()
df_clean = df_clean[df_clean['sentiment'].notna()].copy()

print(f"✓ Total records: {len(df)}")
print(f"✓ Records with complete data (text + rating): {len(df_clean)}")
print(f"✓ Records with missing text: {df['Teks Ulasan'].isna().sum()}")

# 2. DATA DISTRIBUTION ANALYSIS
print("\n[2] DATA DISTRIBUTION ANALYSIS...")
print("\n  Rating Distribution (Original):")
rating_dist = df['Rating'].value_counts().sort_index()
for rating, count in rating_dist.items():
    pct = (count / len(df)) * 100
    print(f"    Rating {rating}: {count:5d} ({pct:6.2f}%)")

print("\n  Sentiment Distribution (Mapped):")
sentiment_dist = df_clean['sentiment'].value_counts()
for sentiment in ['positif', 'netral', 'negatif']:
    if sentiment in sentiment_dist.index:
        count = sentiment_dist[sentiment]
        pct = (count / len(df_clean)) * 100
        print(f"    {sentiment:10s}: {count:5d} ({pct:6.2f}%)")

# Calculate class imbalance ratio
counts = [sentiment_dist.get(s, 0) for s in ['positif', 'netral', 'negatif']]
valid_counts = [c for c in counts if c > 0]
if len(valid_counts) > 1:
    max_count = max(valid_counts)
    min_count = min(valid_counts)
    imbalance_ratio = max_count / min_count
    print(f"\n  Class Imbalance Ratio (max/min): {imbalance_ratio:.2f}:1")
else:
    imbalance_ratio = 1.0
    print(f"\n  Class Imbalance Ratio: N/A (insufficient classes)")

# 3. TEXT LENGTH ANALYSIS
print("\n[3] TEXT LENGTH STATISTICS...")
df_clean['text_length'] = df_clean['Teks Ulasan'].str.len()
print(f"  Mean length: {df_clean['text_length'].mean():.1f} characters")
print(f"  Median length: {df_clean['text_length'].median():.1f} characters")
print(f"  Min length: {df_clean['text_length'].min()} characters")
print(f"  Max length: {df_clean['text_length'].max()} characters")
print(f"  Std Dev: {df_clean['text_length'].std():.1f}")

# 4. PREPROCESSING ANALYSIS
print("\n[4] PREPROCESSING ANALYSIS...")
print("  Sample preprocessing results:")
sample_texts = df_clean['Teks Ulasan'].head(3).values
for i, text in enumerate(sample_texts):
    processed = preprocess_text(text)
    tokens = processed.split()
    print(f"\n    Example {i+1}:")
    print(f"      Original ({len(text)} chars): {text[:60]}...")
    print(f"      Processed ({len(processed)} chars): {processed[:80]}...")
    print(f"      Tokens: {len(tokens)}")

# 5. PREPARE DATA FOR TRAINING
print("\n[5] PREPARING DATA FOR TRAINING...")
X = df_clean['Teks Ulasan'].values
y = df_clean['sentiment'].values

# Preprocess all texts
print("  Preprocessing all texts...")
X_processed = np.array([preprocess_text(text) for text in X])

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_processed, y, test_size=0.2, random_state=42, stratify=y
)

print(f"  Train set size: {len(X_train)}")
print(f"  Test set size: {len(X_test)}")

# Show class distribution after split
print("\n  Train set class distribution:")
train_counts = Counter(y_train)
for label in ['positif', 'netral', 'negatif']:
    count = train_counts[label]
    pct = (count / len(y_train)) * 100
    print(f"    {label:10s}: {count:5d} ({pct:6.2f}%)")

print("\n  Test set class distribution:")
test_counts = Counter(y_test)
for label in ['positif', 'netral', 'negatif']:
    count = test_counts[label]
    pct = (count / len(y_test)) * 100
    print(f"    {label:10s}: {count:5d} ({pct:6.2f}%)")

# 6. TFIDF VECTORIZATION
print("\n[6] TFIDF VECTORIZATION...")
tfidf_params = {
    'max_features': 5000,
    'ngram_range': (1, 2),
    'min_df': 5,
    'max_df': 0.90,
    'sublinear_tf': True,
    'smooth_idf': True
}

vectorizer = TfidfVectorizer(**tfidf_params)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print(f"  TF-IDF Parameters:")
for key, val in tfidf_params.items():
    print(f"    {key}: {val}")

print(f"\n  Vectorization Results:")
print(f"    Features extracted: {len(vectorizer.get_feature_names_out())}")
print(f"    Train matrix shape: {X_train_tfidf.shape}")
print(f"    Test matrix shape: {X_test_tfidf.shape}")
print(f"    Sparsity: {(1 - X_train_tfidf.nnz / (X_train_tfidf.shape[0] * X_train_tfidf.shape[1])) * 100:.2f}%")

# Get top features
feature_names = vectorizer.get_feature_names_out()
print(f"\n  Top 20 Features (by mean TF-IDF weight):")
mean_tfidf = np.asarray(X_train_tfidf.mean(axis=0)).ravel()
top_indices = np.argsort(mean_tfidf)[-20:][::-1]
for i, idx in enumerate(top_indices, 1):
    print(f"    {i:2d}. {feature_names[idx]:20s} (weight: {mean_tfidf[idx]:.4f})")

# 7. MODEL TRAINING
print("\n[7] MODEL TRAINING...")
print("  Model: Complement Naive Bayes")
model = ComplementNB(alpha=1.0)
model.fit(X_train_tfidf, y_train)

print("  Training complete!")

# 8. MODEL EVALUATION
print("\n[8] MODEL EVALUATION...")

# Predictions
y_pred = model.predict(X_test_tfidf)
y_pred_proba = model.predict_proba(X_test_tfidf)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"  Overall Accuracy: {accuracy*100:.2f}%")

# Confusion Matrix
conf_matrix = confusion_matrix(y_test, y_pred, labels=['negatif', 'netral', 'positif'])
print(f"\n  Confusion Matrix:")
labels_list = ['negatif', 'netral', 'positif']
print(f"       {'Pred: Neg':>12} {'Pred: Neu':>12} {'Pred: Pos':>12}")
for i, true_label in enumerate(labels_list):
    print(f"  {true_label:6s}: {conf_matrix[i,0]:12d} {conf_matrix[i,1]:12d} {conf_matrix[i,2]:12d}")

# Classification Report
print(f"\n  Classification Report:")
report = classification_report(y_test, y_pred, labels=['negatif', 'netral', 'positif'], output_dict=True, zero_division=0)
print(f"  {'Kelas':<12} {'Precision':>12} {'Recall':>12} {'F1-Score':>12} {'Support':>12}")
print(f"  {'-'*60}")
for label in ['negatif', 'netral', 'positif']:
    if label in report:
        r = report[label]
        print(f"  {label:<12} {r['precision']:>12.4f} {r['recall']:>12.4f} {r['f1-score']:>12.4f} {int(r['support']):>12d}")

# Macro and weighted averages
print(f"  {'-'*60}")
macro = report['macro avg']
print(f"  {'Macro Avg':<12} {macro['precision']:>12.4f} {macro['recall']:>12.4f} {macro['f1-score']:>12.4f} {int(macro['support']):>12d}")

weighted = report['weighted avg']
print(f"  {'Weighted Avg':<12} {weighted['precision']:>12.4f} {weighted['recall']:>12.4f} {weighted['f1-score']:>12.4f} {int(weighted['support']):>12d}")

# 9. SYSTEM FEATURES
print("\n[9] SISTEM FITUR TERBARU...")
print("  ✓ Database Fields (NB Predictions):")
print("    - nb_predicted_label (POSITIF/NETRAL/NEGATIF)")
print("    - nb_confidence (0-1)")
print("    - nb_positif_prob, nb_netral_prob, nb_negatif_prob")

print("\n  ✓ Web Application Routes:")
routes = [
    ('/', 'Home/Dashboard - Landing page'),
    ('/predict', 'Single prediction + batch CSV upload'),
    ('/train', 'Model retraining interface'),
    ('/dashboard', 'Analytics & visualization'),
    ('/history', 'Prediction history & filtering'),
    ('/api/stats', 'Statistics API - trend analysis'),
]
for route, desc in routes:
    print(f"    {route:20s} → {desc}")

print("\n  ✓ Preprocessing Features:")
preprocessing_features = [
    'Lowercase conversion',
    'Emoji & symbol removal',
    'Repeat character normalization',
    'Custom text normalization (slang → standard)',
    'Tokenization',
    'Stopword removal (preserves negation)',
    'Sastrawi stemming',
]
for feat in preprocessing_features:
    print(f"    ✓ {feat}")

print("\n  ✓ Dashboard Features:")
dashboard_features = [
    'Sentiment distribution (pie chart)',
    'Aspect-based analysis (6 aspects: keindahan, aksesibilitas, fasilitas, etc.)',
    'Monthly trend analysis (NB predictions)',
    'Real-time statistics',
    'Sentiment filtering',
]
for feat in dashboard_features:
    print(f"    ✓ {feat}")

# 10. SUMMARY FOR BAB 4.3
print("\n" + "="*100)
print("RINGKASAN DATA UNTUK BAB 4.3 TEMPLATE")
print("="*100)

summary = {
    "dataset": {
        "total_records": len(df),
        "records_with_text": len(df_clean),
        "text_length_mean": round(df_clean['text_length'].mean(), 1),
        "text_length_max": int(df_clean['text_length'].max()),
    },
    "sentiment_distribution": {
        "positif": {"count": sentiment_dist.get('positif', 0), "pct": round((sentiment_dist.get('positif', 0) / len(df_clean)) * 100, 2)},
        "netral": {"count": sentiment_dist.get('netral', 0), "pct": round((sentiment_dist.get('netral', 0) / len(df_clean)) * 100, 2)},
        "negatif": {"count": sentiment_dist.get('negatif', 0), "pct": round((sentiment_dist.get('negatif', 0) / len(df_clean)) * 100, 2)},
    },
    "class_imbalance_ratio": round(imbalance_ratio, 2),
    "train_test_split": {
        "train_size": len(X_train),
        "test_size": len(X_test),
    },
    "tfidf": {
        "max_features": 5000,
        "ngram_range": "(1, 2)",
        "min_df": 5,
        "max_df": 0.90,
        "features_extracted": len(vectorizer.get_feature_names_out()),
        "sparsity_pct": round((1 - X_train_tfidf.nnz / (X_train_tfidf.shape[0] * X_train_tfidf.shape[1])) * 100, 2),
    },
    "model_performance": {
        "accuracy_pct": round(accuracy * 100, 2),
        "macro_f1": round(report['macro avg']['f1-score'], 4),
        "weighted_f1": round(report['weighted avg']['f1-score'], 4),
    }
}

print("\n📊 JSON Summary:")
print(json.dumps(summary, indent=2))

print("\n✅ EKSTRAKSI SELESAI!")
print("="*100)
