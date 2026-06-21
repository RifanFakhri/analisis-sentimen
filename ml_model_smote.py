"""
SMOTE-enabled model wrapper.

This module provides the same `sentiment_model` API used by the app,
but can be extended later to apply SMOTE during training.
For now it uses the same `SentimentModel` implementation from `ml_model.py`.
"""

from ml_model import SentimentModel

# Create a separate instance so app import paths work unchanged.
sentiment_model = SentimentModel()
