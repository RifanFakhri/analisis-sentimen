"""
Flask Sentiment Analysis Application
Main application factory and entry point.
"""

from flask import Flask
from config import Config
from models import db
from routes import main_bp
from ml_model import sentiment_model


def create_app():
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

        # Try to load existing model
        sentiment_model.load_model()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
