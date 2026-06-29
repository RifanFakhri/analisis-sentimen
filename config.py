"""
Configuration module for Flask Sentiment Analysis application.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Check if a single full URL is provided (e.g. on Vercel/Supabase/Neon/Render)
    _db_url = os.getenv('DATABASE_URL')
    if _db_url:
        if _db_url.startswith("postgres://"):
            _db_url = _db_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = _db_url
    else:
        # Database Configuration from separate variables
        DB_USERNAME = os.getenv('DB_USERNAME', 'postgres')
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '5432')
        DB_NAME = os.getenv('DB_NAME', 'sentimen')
        SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')

    # Model paths
    MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model')
    MODEL_PATH = os.path.join(MODEL_DIR, 'naive_bayes_model.pkl')
    VECTORIZER_PATH = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')
    USE_SMOTE = os.getenv('USE_SMOTE', 'False').lower() in ('true', '1', 'yes')
    MODEL_PATH_SMOTE = os.path.join(MODEL_DIR, 'naive_bayes_smote_model.pkl')
    VECTORIZER_PATH_SMOTE = os.path.join(MODEL_DIR, 'tfidf_vectorizer_smote.pkl')
