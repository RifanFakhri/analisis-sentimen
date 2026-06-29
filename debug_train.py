from app import app
from models import db, TrainingData
from ml_model import sentiment_model
from preprocessing import preprocess_text

with app.app_context():
    data = TrainingData.query.filter(
        TrainingData.text != '',
        TrainingData.text != None
    ).order_by(TrainingData.id).all()

    # Preprocess on the fly and save if any row is missing processed_text
    needs_commit = False
    total = len(data)
    print(f"Mengecek {total} data ulasan untuk kolom processed_text...")
    for i, d in enumerate(data):
        if not d.processed_text:
            if i % 50 == 0 or i == total - 1:
                print(f"Memproses & migrasi ulasan ke-{i} dari {total}...", flush=True)
            d.processed_text = preprocess_text(d.text)
            db.session.add(d)
            needs_commit = True
    if needs_commit:
        print("Menyimpan hasil preprocessing ke database...", flush=True)
        db.session.commit()
        print("Penyimpanan selesai!", flush=True)

    texts = [d.processed_text for d in data if d.processed_text]
    labels = [d.label for d in data if d.processed_text]

    print(f"Data ready for training: {len(texts)}")

    metrics = sentiment_model.train(texts, labels, is_preprocessed=True)

    print(metrics)