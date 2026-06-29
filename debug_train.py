from app import create_app
from models import db, TrainingData
from ml_model import sentiment_model
from preprocessing import preprocess_text

app = create_app()

with app.app_context():
    data = TrainingData.query.filter(
        TrainingData.text != '',
        TrainingData.text != None
    ).order_by(TrainingData.id).all()

    # Preprocess on the fly and save if any row is missing processed_text
    needs_commit = False
    for d in data:
        if not d.processed_text:
            d.processed_text = preprocess_text(d.text)
            db.session.add(d)
            needs_commit = True
    if needs_commit:
        db.session.commit()

    texts = [d.processed_text for d in data if d.processed_text]
    labels = [d.label for d in data if d.processed_text]

    print(f"Data: {len(texts)}")

    metrics = sentiment_model.train(texts, labels, is_preprocessed=True)

    print(metrics)