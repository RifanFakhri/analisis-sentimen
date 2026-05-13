"""
Machine Learning model module.
Handles training, saving, loading, and prediction using Multinomial Naive Bayes.
"""

import os
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import ComplementNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

from config import Config
from preprocessing import preprocess_text


class SentimentModel:
    """Sentiment Analysis model using Complement Naive Bayes with TF-IDF."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
        self.model = ComplementNB(alpha=0.5)
        self.is_trained = False
        self.labels = ['negatif', 'netral', 'positif']

    def train(self, texts, labels):
        """
        Train the model on preprocessed texts and their labels.
        Returns training metrics.
        """
        # Preprocess all texts
        processed_texts = [preprocess_text(text) for text in texts]

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            processed_texts, labels, test_size=0.2, random_state=42, stratify=labels
        )

        # Moderate Oversampling for imbalanced data
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        
        unique_labels, counts = np.unique(y_train, return_counts=True)
        max_count = max(counts)
        
        X_resampled = []
        y_resampled = []
        
        for label, count in zip(unique_labels, counts):
            indices = np.where(y_train == label)[0]
            label_X = X_train[indices]
            
            if label == 'positif':
                target_count = count # Keep positive as is
            else:
                # Boost minority classes but not all the way to max_count to avoid heavy overfitting
                target_count = int(max_count * 0.7) 
            
            repeat_factor = target_count // len(label_X)
            remainder = target_count % len(label_X)
            
            resampled_X = np.concatenate([label_X] * repeat_factor + [label_X[:remainder]])
            resampled_y = [label] * target_count
            
            X_resampled.extend(resampled_X)
            y_resampled.extend(resampled_y)
            
        X_train = X_resampled
        y_train = y_resampled

        # TF-IDF Vectorization
        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        X_test_tfidf = self.vectorizer.transform(X_test)

        # Train Multinomial Naive Bayes
        self.model.fit(X_train_tfidf, y_train)
        self.is_trained = True

        # Evaluate
        y_pred = self.model.predict(X_test_tfidf)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        conf_matrix = confusion_matrix(y_test, y_pred, labels=self.labels).tolist()

        # Save model
        self.save_model()

        return {
            'accuracy': round(accuracy * 100, 2),
            'report': report,
            'confusion_matrix': conf_matrix,
            'train_size': len(X_train),
            'test_size': len(X_test),
            'labels': self.labels
        }

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

    def save_model(self):
        """Save trained model and vectorizer to disk."""
        os.makedirs(Config.MODEL_DIR, exist_ok=True)
        joblib.dump(self.model, Config.MODEL_PATH)
        joblib.dump(self.vectorizer, Config.VECTORIZER_PATH)
        print(f"Model saved to {Config.MODEL_DIR}")

    def load_model(self):
        """Load trained model and vectorizer from disk."""
        if os.path.exists(Config.MODEL_PATH) and os.path.exists(Config.VECTORIZER_PATH):
            self.model = joblib.load(Config.MODEL_PATH)
            self.vectorizer = joblib.load(Config.VECTORIZER_PATH)
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
            'model_type': 'Multinomial Naive Bayes',
            'vectorizer_type': 'TF-IDF (max_features=5000, ngram=1-2)',
        }


# Global model instance
sentiment_model = SentimentModel()
