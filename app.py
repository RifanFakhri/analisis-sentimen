"""
Flask Sentiment Analysis Application
Main application factory and entry point.
"""

from flask import Flask
from sqlalchemy import inspect, text
from config import Config
from models import db
from routes import main_bp

if Config.USE_SMOTE:
    from ml_model_smote import sentiment_model
else:
    from ml_model import sentiment_model


def ensure_training_data_columns():
    """Ensure training_data table has the latest schema columns."""
    inspector = inspect(db.engine)
    if not inspector.has_table('training_data'):
        return

    existing_cols = [col['name'] for col in inspector.get_columns('training_data')]
    alterations = []

    if 'processed_text' not in existing_cols:
        alterations.append('ADD COLUMN processed_text TEXT')
    if 'bulan' not in existing_cols:
        alterations.append('ADD COLUMN bulan INTEGER')
    if 'tanggal_asli' not in existing_cols:
        alterations.append('ADD COLUMN tanggal_asli DATE')
    
    # Kolom untuk NB predictions (untuk skripsi)
    if 'nb_predicted_label' not in existing_cols:
        alterations.append("ADD COLUMN nb_predicted_label VARCHAR(20)")
    if 'nb_confidence' not in existing_cols:
        alterations.append('ADD COLUMN nb_confidence FLOAT')
    if 'nb_positif_prob' not in existing_cols:
        alterations.append('ADD COLUMN nb_positif_prob FLOAT')
    if 'nb_negatif_prob' not in existing_cols:
        alterations.append('ADD COLUMN nb_negatif_prob FLOAT')
    if 'nb_netral_prob' not in existing_cols:
        alterations.append('ADD COLUMN nb_netral_prob FLOAT')

    if alterations:
        with db.engine.connect() as conn:
            conn.execute(text(f'ALTER TABLE training_data {", ".join(alterations)}'))
            conn.commit()
        print(f"Updated training_data schema: {', '.join(alterations)}")


def create_app():
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)

    # Create database tables and apply schema updates if needed
    with app.app_context():
        try:
            db.create_all()
            ensure_training_data_columns()

            # Seed default users if they don't exist
            from models import User
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin', role='admin')
                admin.set_password('admin123')
                db.session.add(admin)
                print("Seeded default admin (admin / admin123)")
            if not User.query.filter_by(username='user').first():
                user = User(username='user', role='user')
                user.set_password('user123')
                db.session.add(user)
                print("Seeded default user (user / user123)")
            db.session.commit()
        except Exception as db_error:
            print(f"Warning: Database initialization or connection failed: {db_error}")

        # Try to load existing model
        sentiment_model.load_model()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
