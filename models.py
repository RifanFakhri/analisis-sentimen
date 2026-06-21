"""
Database models for Sentiment Analysis application.
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class PredictionHistory(db.Model):
    """Model to store prediction history."""
    __tablename__ = 'prediction_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    original_text = db.Column(db.Text, nullable=False)
    cleaned_text = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    positive_prob = db.Column(db.Float, nullable=True)
    negative_prob = db.Column(db.Float, nullable=True)
    neutral_prob = db.Column(db.Float, nullable=True)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            'id': self.id,
            'original_text': self.original_text,
            'cleaned_text': self.cleaned_text,
            'sentiment': self.sentiment,
            'confidence': round(self.confidence * 100, 2),
            'positive_prob': round((self.positive_prob or 0) * 100, 2),
            'negative_prob': round((self.negative_prob or 0) * 100, 2),
            'neutral_prob': round((self.neutral_prob or 0) * 100, 2),
            'created_at': self.created_at.strftime('%d %b %Y, %H:%M:%S')
        }


class TrainingData(db.Model):
    """Model to store training dataset."""
    __tablename__ = 'training_data'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text, nullable=False)
    label = db.Column(db.String(20), nullable=False)  # positif, negatif, netral (dari rating)
    rating = db.Column(db.Integer, nullable=True)
    tahun = db.Column(db.Integer, nullable=True)
    bulan = db.Column(db.Integer, nullable=True) # 1-12
    tanggal_asli = db.Column(db.Date, nullable=True)
    # Kolom untuk menyimpan prediksi Naive Bayes (UNTUK SKRIPSI)
    nb_predicted_label = db.Column(db.String(20), nullable=True)  # Hasil prediksi NB
    nb_confidence = db.Column(db.Float, nullable=True)  # Confidence score prediksi
    nb_positif_prob = db.Column(db.Float, nullable=True)  # Probabilitas positif dari NB
    nb_negatif_prob = db.Column(db.Float, nullable=True)  # Probabilitas negatif dari NB
    nb_netral_prob = db.Column(db.Float, nullable=True)  # Probabilitas netral dari NB
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class TrainingLog(db.Model):
    """Model to store logs of uploads and training sessions."""
    __tablename__ = 'training_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    activity_type = db.Column(db.String(50), nullable=False)  # 'upload' or 'training'
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            'id': self.id,
            'activity_type': self.activity_type,
            'details': self.details,
            'created_at': self.created_at.strftime('%d %b %Y, %H:%M:%S')
        }
