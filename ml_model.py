"""
Machine Learning model module.
Handles training, saving, loading, and prediction using Multinomial Naive Bayes.
"""

import os
import joblib
import numpy as np
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import ComplementNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, f1_score
from collections import Counter

from config import Config
from preprocessing import preprocess_text


def random_oversample_negative(X_train, y_train, random_state=42):
    """
    Simple random oversampling for minority class (negatif).
    Duplicates negative samples to match the majority class.
    """
    random.seed(random_state)
    
    X_train = list(X_train)
    y_train = list(y_train)
    
    # Count classes
    class_counts = Counter(y_train)
    max_count = max(class_counts.values())
    neg_count = class_counts.get('negatif', 0)
    
    if neg_count > 0 and neg_count < max_count:
        # Get negative indices
        neg_indices = [i for i, label in enumerate(y_train) if label == 'negatif']
        # Random sample to add
        num_to_add = max_count - neg_count
        oversample_indices = random.choices(neg_indices, k=num_to_add)
        
        # Add oversampled data
        for idx in oversample_indices:
            X_train.append(X_train[idx])
            y_train.append(y_train[idx])
        
        print(f"Random Oversampling: Negatif {neg_count} → {neg_count + num_to_add}")
    
    return X_train, y_train


class SentimentModel:
    """Sentiment Analysis model using Complement Naive Bayes with TF-IDF."""

    def __init__(self):
        self.tfidf_params = {
            'max_features': 5000,
            'ngram_range': (1, 2),
            'min_df': 5,
            'max_df': 0.90,
            'sublinear_tf': True,
            'smooth_idf': True
        }
        self.vectorizer = self._create_vectorizer(self.tfidf_params)
        self.model = ComplementNB(alpha=1.0)
        self.is_trained = False
        self.labels = ['negatif', 'netral', 'positif']

    def train(self, texts, labels, is_preprocessed=False):
        """
        Train the model on preprocessed texts and their labels.
        Applies random oversampling for minority class (negatif).
        Returns training metrics.
        """
        # Set seed for reproducibility
        np.random.seed(42)
        random.seed(42)
        
        # Preprocess all texts and filter empty ones (containing only stopwords/symbols)
        print("START PREPROCESS", flush=True)
        valid_pairs = []
        if is_preprocessed:
            for text, label in zip(texts, labels):
                if text and text.strip():
                    valid_pairs.append((text, label))
        else:
            for i, (text, label) in enumerate(zip(texts, labels)):
                if i % 100 == 0:
                    print(f"Preprocessing {i}/{len(texts)}", flush=True)
                proc = preprocess_text(text)
                if proc.strip():
                    valid_pairs.append((proc, label))
                
        print("PREPROCESS DONE", flush=True)
        if not valid_pairs:
            raise ValueError(
                "Semua ulasan kosong atau hanya berisi stopword/simbol setelah proses pembersihan (preprocessing). "
                "Harap masukkan ulasan yang lebih bermakna (mengandung kata sifat/kata benda)."
            )
            
        processed_texts, labels = zip(*valid_pairs)
        processed_texts = list(processed_texts)
        labels = list(labels)

        # Split data
        print("START SPLIT", flush=True)
        X_train, X_test, y_train, y_test = train_test_split(
            processed_texts, labels, test_size=0.2, random_state=42, stratify=labels
        )
        print("SPLIT DONE", flush=True)

        # Apply random oversampling for negative class
        print("START OVERSAMPLING", flush=True)
        print("\n=== Applying Random Oversampling ===")
        X_train, y_train = random_oversample_negative(X_train, y_train, random_state=42)
        print("OVERSAMPLING DONE", flush=True)
        print("=" * 35 + "\n")

        X_train = np.array(X_train)
        y_train = np.array(y_train)

        # TF-IDF tuning and vectorization
        print("START TFIDF PARAM SEARCH", flush=True)
        self.tfidf_params = self._select_best_tfidf_params(X_train, y_train)
        print("TFIDF PARAM SEARCH DONE", flush=True)
        self.vectorizer = self._create_vectorizer(self.tfidf_params, n_samples=len(X_train))

        print("START TFIDF FIT", flush=True)
        try:
            X_train_tfidf = self.vectorizer.fit_transform(X_train)
        except ValueError as e:
            if "empty vocabulary" in str(e):
                print("Vocabulary empty with selected params. Falling back to min_df=1 and ngram_range=(1,1)")
                self.tfidf_params = self.tfidf_params.copy()
                self.tfidf_params['min_df'] = 1
                self.tfidf_params['ngram_range'] = (1, 1)
                self.vectorizer = self._create_vectorizer(self.tfidf_params, n_samples=len(X_train))
                X_train_tfidf = self.vectorizer.fit_transform(X_train)
            else:
                raise e
        print("TFIDF FIT DONE", flush=True)

        X_test_tfidf = self.vectorizer.transform(X_test)

        # Train Complement Naive Bayes
        print("START MODEL FIT", flush=True)
        self.model.fit(X_train_tfidf, y_train)
        print("MODEL FIT DONE", flush=True)
        self.is_trained = True

        # Evaluate
        print("START EVALUATION", flush=True)
        y_pred = self.model.predict(X_test_tfidf)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        conf_matrix = confusion_matrix(y_test, y_pred, labels=self.labels).tolist()
        print("EVALUATION DONE", flush=True)

        # Save model
        self.last_metrics = {
            'accuracy': round(accuracy * 100, 2),
            'report': report,
            'confusion_matrix': conf_matrix,
            'train_size': len(X_train),
            'test_size': len(X_test),
            'labels': self.labels
        }
        print("START SAVE MODEL", flush=True)
        self.save_model()
        print("SAVE MODEL DONE", flush=True)

        return self.last_metrics

    def predict(self, text):
        """
        Predict sentiment for a single text.
        Returns prediction result with probabilities.
        """
        if not self.is_trained:
            raise ValueError("Model belum dilatih. Silakan latih model terlebih dahulu.")

        # Preprocess
        processed_text = preprocess_text(text)

        # Vectorize
        text_tfidf = self.vectorizer.transform([processed_text])

        # Predict
        prediction = self.model.predict(text_tfidf)[0]
        probabilities = self.model.predict_proba(text_tfidf)[0]

        # Map probabilities to labels
        prob_dict = {}
        for label, prob in zip(self.model.classes_, probabilities):
            prob_dict[label] = float(prob)

        confidence = float(max(probabilities))

        return {
            'sentiment': prediction,
            'confidence': confidence,
            'probabilities': prob_dict,
            'processed_text': processed_text
        }

    def predict_batch(self, texts):
        """
        Predict sentiment for multiple texts in batch.
        Returns list of predictions with probabilities.
        Ideal untuk prediction semua data di dashboard (untuk skripsi).
        """
        if not self.is_trained:
            raise ValueError("Model belum dilatih. Silakan latih model terlebih dahulu.")

        results = []
        for text in texts:
            # Preprocess
            processed_text = preprocess_text(text)

            # Vectorize
            text_tfidf = self.vectorizer.transform([processed_text])

            # Predict
            prediction = self.model.predict(text_tfidf)[0]
            probabilities = self.model.predict_proba(text_tfidf)[0]

            # Map probabilities to labels
            prob_dict = {}
            for label, prob in zip(self.model.classes_, probabilities):
                prob_dict[label] = float(prob)

            confidence = float(max(probabilities))

            results.append({
                'sentiment': prediction,
                'confidence': confidence,
                'probabilities': prob_dict,
                'processed_text': processed_text
            })

        return results

    def save_model(self):
        """Save trained model and vectorizer to disk."""
        os.makedirs(Config.MODEL_DIR, exist_ok=True)
        joblib.dump(self.model, Config.MODEL_PATH)
        joblib.dump(self.vectorizer, Config.VECTORIZER_PATH)
        if hasattr(self, 'last_metrics'):
            joblib.dump(self.last_metrics, os.path.join(Config.MODEL_DIR, 'metrics.pkl'))
        print(f"Model saved to {Config.MODEL_DIR}")

    def _create_vectorizer(self, params, n_samples=None):
        min_df_val = params.get('min_df', 5)
        if n_samples is not None:
            if n_samples < 5:
                min_df_val = 1
            elif n_samples < 15:
                min_df_val = min(min_df_val, 2)
            else:
                min_df_val = min(min_df_val, max(1, n_samples // 3))

        return TfidfVectorizer(
            max_features=params.get('max_features', 5000),
            ngram_range=params.get('ngram_range', (1, 2)),
            min_df=min_df_val,
            max_df=params.get('max_df', 0.90),
            sublinear_tf=params.get('sublinear_tf', False),
            smooth_idf=params.get('smooth_idf', True),
            strip_accents='unicode',
            norm='l2',
            token_pattern=r'(?u)\b\w+\b'
        )

    def _select_best_tfidf_params(self, X_train, y_train):
        """Search TF-IDF parameter grid using a single validation split."""
        if len(X_train) < 10:
            return self.tfidf_params

        candidates = [
            {'max_features': 5000, 'ngram_range': (1, 2), 'min_df': 5, 'max_df': 0.90, 'sublinear_tf': True, 'smooth_idf': True},
            {'max_features': 8000, 'ngram_range': (1, 2), 'min_df': 5, 'max_df': 0.90, 'sublinear_tf': True, 'smooth_idf': True},
            {'max_features': 10000, 'ngram_range': (1, 2), 'min_df': 5, 'max_df': 0.90, 'sublinear_tf': True, 'smooth_idf': True},
        ]

        X_search, X_val, y_search, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
        )

        best_score = -1.0
        best_params = self.tfidf_params

        for params in candidates:
            try:
                vectorizer = self._create_vectorizer(params, n_samples=len(X_search))
                X_search_tfidf = vectorizer.fit_transform(X_search)
                X_val_tfidf = vectorizer.transform(X_val)

                model = ComplementNB(alpha=self.model.alpha)
                model.fit(X_search_tfidf, y_search)
                score = f1_score(y_val, model.predict(X_val_tfidf), average='macro', zero_division=0)

                if score > best_score:
                    best_score = score
                    best_params = params
            except ValueError as e:
                # If vocabulary becomes empty with min_df=5, fallback to min_df=1
                if "empty vocabulary" in str(e):
                    fallback_params = params.copy()
                    fallback_params['min_df'] = 1
                    try:
                        vectorizer = self._create_vectorizer(fallback_params, n_samples=len(X_search))
                        X_search_tfidf = vectorizer.fit_transform(X_search)
                        X_val_tfidf = vectorizer.transform(X_val)

                        model = ComplementNB(alpha=self.model.alpha)
                        model.fit(X_search_tfidf, y_search)
                        score = f1_score(y_val, model.predict(X_val_tfidf), average='macro', zero_division=0)

                        if score > best_score:
                            best_score = score
                            best_params = fallback_params
                    except ValueError:
                        continue
                else:
                    raise e

        print(f"Selected TF-IDF params: {best_params} with macro F1={best_score:.4f}")
        return best_params

    def load_model(self):
        """Load trained model and vectorizer from disk."""
        if os.path.exists(Config.MODEL_PATH) and os.path.exists(Config.VECTORIZER_PATH):
            self.model = joblib.load(Config.MODEL_PATH)
            self.vectorizer = joblib.load(Config.VECTORIZER_PATH)
            metrics_path = os.path.join(Config.MODEL_DIR, 'metrics.pkl')
            if os.path.exists(metrics_path):
                self.last_metrics = joblib.load(metrics_path)
            self.is_trained = True
            print("Model loaded successfully.")
            return True
        else:
            print("No saved model found.")
            return False

    def get_model_info(self):
        """Get information about the current model state."""
        return {
            'is_trained': self.is_trained,
            'model_exists': os.path.exists(Config.MODEL_PATH),
            'vectorizer_exists': os.path.exists(Config.VECTORIZER_PATH),
            'model_type': 'Complement Naïve Bayes',
            'vectorizer_type': f"TF-IDF (max_features={self.tfidf_params['max_features']}, ngram={self.tfidf_params['ngram_range']})",
        }

    def reset_model(self):
        """Delete all saved model files and reset internal state."""
        self.is_trained = False
        self.last_trained = None
        self.last_metrics = None
        self.model = ComplementNB(alpha=1.0)
        self.tfidf_params = {
            'max_features': 5000,
            'ngram_range': (1, 2),
            'min_df': 5,
            'max_df': 0.90,
            'sublinear_tf': True,
            'smooth_idf': True
        }
        self.vectorizer = self._create_vectorizer(self.tfidf_params)
        
        files_to_delete = [
            Config.MODEL_PATH,
            Config.VECTORIZER_PATH,
            os.path.join(Config.MODEL_DIR, 'metrics.pkl')
        ]
        
        for f in files_to_delete:
            if os.path.exists(f):
                os.remove(f)
        return True


# Global model instance
sentiment_model = SentimentModel()
