"""
Flask routes for Sentiment Analysis application.
"""

from flask import Blueprint, render_template, request, jsonify
from models import db, PredictionHistory, TrainingData, TrainingLog
from ml_model import sentiment_model
from preprocessing import preprocess_for_display, preprocess_text
from sqlalchemy import func
from collections import Counter
from datetime import datetime, timedelta
import re
import pandas as pd
import io
import os

main_bp = Blueprint('main', __name__)


@main_bp.route('/api/stats')
def get_stats():
    """Get comprehensive statistics for the interactive dashboard."""
    sentiment_filter = request.args.get('sentiment', 'all')
    time_range = request.args.get('range', '6m') # 3m, 6m, 1y, all
    
    # 1. Base Data
    query = TrainingData.query
    if sentiment_filter != 'all':
        query = query.filter_by(label=sentiment_filter)
    
    all_data = query.all()
    total_reviews = len(all_data)
    
    if total_reviews == 0:
        return jsonify({'summary': {'total_reviews': 0}, 'metrics': {'is_trained': False}, 'error': 'No data'})

    sentiment_counts = Counter([d.label for d in all_data])
    
    # 2. Aspect Analysis (Aspek yang sering dibahas)
    aspect_keywords = {
        'Keindahan': ['indah', 'bagus', 'cantik', 'pemandangan', 'keren', 'view', 'pesona'],
        'Aksesibilitas': ['jalan', 'akses', 'transportasi', 'perjalanan', 'jauh', 'macet', 'lokasi'],
        'Fasilitas': ['toilet', 'mushola', 'fasilitas', 'kamar mandi', 'tempat duduk', 'sarana'],
        'Kebersihan': ['bersih', 'sampah', 'kotor', 'bau', 'limbah', 'terawat'],
        'Harga tiket': ['harga', 'tiket', 'murah', 'mahal', 'biaya', 'tarif', 'bayar'],
        'Pelayanan': ['petugas', 'layanan', 'ramah', 'service', 'pengelola', 'orang']
    }
    
    aspect_stats = []
    for aspect, keywords in aspect_keywords.items():
        count = 0
        for d in all_data:
            if any(kw in d.text.lower() for kw in keywords):
                count += 1
        percent = round((count / total_reviews * 100), 1)
        aspect_stats.append({'aspect': aspect, 'count': count, 'percent': percent})
    
    # Sort aspects by count
    aspect_stats = sorted(aspect_stats, key=lambda x: x['count'], reverse=True)

    # 3. Monthly Trend
    # Determine start date based on range
    now = datetime(2026, 6, 15)
    if time_range == '3m':
        start_date = now - timedelta(days=90)
    elif time_range == '6m':
        start_date = now - timedelta(days=180)
    elif time_range == '1y':
        start_date = now - timedelta(days=365)
    else:
        start_date = datetime(2020, 1, 1)

    # Filter data by date
    trend_data_query = TrainingData.query.filter(TrainingData.tanggal_asli >= start_date.date()).all()
    
    # Group by Month-Year
    month_map = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    
    # Create labels for the range
    monthly_stats = []
    current = start_date.replace(day=1)
    while current <= now:
        m = current.month
        y = current.year
        
        pos = len([d for d in trend_data_query if d.bulan == m and d.tahun == y and d.label == 'positif'])
        neg = len([d for d in trend_data_query if d.bulan == m and d.tahun == y and d.label == 'negatif'])
        
        monthly_stats.append({
            'label': f"{month_map[m]} {y}",
            'positif': pos,
            'negatif': neg
        })
        
        # Advance month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    # 4. Top Keywords (Word Cloud)
    def fast_clean(text):
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        return text.split()

    neg_words = []
    for d in [d for d in all_data if d.label == 'negatif']:
        neg_words.extend([w for w in fast_clean(d.text) if len(w) > 3])
    top_neg = Counter(neg_words).most_common(10)
    
    pos_words = []
    for d in [d for d in all_data if d.label == 'positif']:
        pos_words.extend([w for w in fast_clean(d.text) if len(w) > 3])
    top_pos = Counter(pos_words).most_common(10)

    # 5. Training Metrics (Dynamic based on filter)
    info = sentiment_model.get_model_info()
    metrics = {'is_trained': False}
    
    if info['is_trained'] and hasattr(sentiment_model, 'last_metrics'):
        m = sentiment_model.last_metrics
        report = m.get('report', {})
        
        # Determine which key to look at in the classification report
        # report keys are 'positif', 'netral', 'negatif', 'macro avg', etc.
        target_key = sentiment_filter if (sentiment_filter != 'all' and sentiment_filter in report) else 'macro avg'
        
        if target_key in report:
            class_metrics = report[target_key]
            metrics = {
                'accuracy': m['accuracy'],
                'precision': round(class_metrics.get('precision', 0) * 100, 1),
                'recall': round(class_metrics.get('recall', 0) * 100, 1),
                'f1': round(class_metrics.get('f1-score', 0) * 100, 1),
                'is_trained': True,
                'target': target_key
            }

    return jsonify({
        'summary': {
            'total_reviews': total_reviews,
            'pos_count': sentiment_counts.get('positif', 0),
            'neg_count': sentiment_counts.get('negatif', 0),
            'pos_percent': round((sentiment_counts.get('positif', 0) / total_reviews * 100), 1) if total_reviews > 0 else 0,
            'neg_percent': round((sentiment_counts.get('negatif', 0) / total_reviews * 100), 1) if total_reviews > 0 else 0,
        },
        'metrics': metrics,
        'aspects': aspect_stats,
        'trend': {
            'labels': [m['label'] for m in monthly_stats],
            'positif': [m['positif'] for m in monthly_stats],
            'negatif': [m['negatif'] for m in monthly_stats]
        },
        'distribution': {
            'labels': ['Negatif', 'Netral', 'Positif'],
            'values': [sentiment_counts.get('negatif', 0), sentiment_counts.get('netral', 0), sentiment_counts.get('positif', 0)]
        },
        'top_neg': [{'word': w, 'count': c} for w, c in top_neg],
        'top_pos': [{'word': w, 'count': c} for w, c in top_pos],
        'samples': [d.text for d in all_data[:5]]
    })


@main_bp.route('/')
def index():
    """Home page - Sentiment prediction form."""
    total_data = TrainingData.query.count()
    model_info = sentiment_model.get_model_info()
    
    # Jika database kosong, paksa model_info.is_trained jadi False
    if total_data == 0:
        model_info['is_trained'] = False
        
    return render_template('index.html', model_info=model_info)


@main_bp.route('/predict', methods=['POST'])
def predict():
    """Predict sentiment for input text."""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({'error': 'Teks tidak boleh kosong.'}), 400

        if not sentiment_model.is_trained:
            return jsonify({'error': 'Model belum dilatih. Silakan latih model terlebih dahulu.'}), 400

        # Get preprocessing steps for display
        preprocessing_steps = preprocess_for_display(text)

        # Predict
        result = sentiment_model.predict(text)

        # Save to database
        history = PredictionHistory(
            original_text=text,
            cleaned_text=result['processed_text'],
            sentiment=result['sentiment'],
            confidence=result['confidence'],
            positive_prob=result['probabilities'].get('positif', 0),
            negative_prob=result['probabilities'].get('negatif', 0),
            neutral_prob=result['probabilities'].get('netral', 0)
        )
        db.session.add(history)
        db.session.commit()

        return jsonify({
            'success': True,
            'result': {
                'id': history.id,
                'sentiment': result['sentiment'],
                'confidence': round(result['confidence'] * 100, 2),
                'probabilities': {
                    k: round(v * 100, 2) for k, v in result['probabilities'].items()
                },
                'preprocessing': {
                    'original': text,
                    'case_folding': preprocessing_steps['case_folding'],
                    'cleaning': preprocessing_steps['cleaning'],
                    'normalization': preprocessing_steps['normalization'],
                    'tokenization': preprocessing_steps['tokenization'],
                    'stopword_removal': preprocessing_steps['stopword_removal'],
                    'stemming': preprocessing_steps['stemming'],
                    'final': preprocessing_steps['final']
                }
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/history')
def history():
    """Prediction history page."""
    model_info = sentiment_model.get_model_info()
    return render_template('history.html', model_info=model_info)


@main_bp.route('/dashboard')
def dashboard():
    """Dashboard visualization page."""
    model_info = sentiment_model.get_model_info()
    return render_template('dashboard.html', model_info=model_info)


@main_bp.route('/api/history')
def api_history():
    """API endpoint to get prediction history."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)
    sentiment_filter = request.args.get('sentiment', '', type=str)

    query = PredictionHistory.query

    if search:
        query = query.filter(PredictionHistory.original_text.ilike(f'%{search}%'))

    if sentiment_filter:
        query = query.filter(PredictionHistory.sentiment == sentiment_filter)

    query = query.order_by(PredictionHistory.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'data': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    })


@main_bp.route('/api/history/<int:history_id>', methods=['DELETE'])
def delete_history(history_id):
    """Delete a prediction history entry."""
    try:
        entry = PredictionHistory.query.get_or_404(history_id)
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Data berhasil dihapus.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/history/clear', methods=['DELETE'])
def clear_history():
    """Clear all prediction history."""
    try:
        PredictionHistory.query.delete()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Semua histori berhasil dihapus.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/train')
def train_page():
    """Training page."""
    model_info = sentiment_model.get_model_info()
    total_data = TrainingData.query.count()
    label_counts = db.session.query(
        TrainingData.label,
        db.func.count(TrainingData.id)
    ).group_by(TrainingData.label).all()
    label_stats = {label: count for label, count in label_counts}
    return render_template(
        'train.html',
        model_info=model_info,
        total_data=total_data,
        label_stats=label_stats
    )


@main_bp.route('/api/train', methods=['POST'])
def train_model():
    """Train the model using data from database."""
    try:
        training_data = TrainingData.query.all()

        if len(training_data) < 10:
            return jsonify({
                'error': 'Data training terlalu sedikit. Minimal 10 data diperlukan.'
            }), 400

        texts = [d.text for d in training_data]
        labels = [d.label for d in training_data]

        # Check if we have at least 2 classes
        unique_labels = set(labels)
        if len(unique_labels) < 2:
            return jsonify({
                'error': 'Minimal 2 kelas sentimen diperlukan untuk training.'
            }), 400

        metrics = sentiment_model.train(texts, labels)

        # Log training activity
        log = TrainingLog(
            activity_type='training',
            details=f"Model trained successfully with {len(texts)} samples. Accuracy: {metrics['accuracy']}%"
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'success': True,
            'metrics': metrics
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/upload-dataset', methods=['POST'])
def upload_dataset():
    """Upload CSV dataset and replace current training data."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Tidak ada file yang diupload.'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nama file kosong.'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Hanya file CSV yang diperbolehkan.'}), 400

        # Read CSV
        df = pd.read_csv(io.StringIO(file.stream.read().decode("UTF8")))
        
        # Check required columns
        required_cols = ['Teks Ulasan', 'Rating', 'Tanggal']
        if not all(col in df.columns for col in required_cols):
            return jsonify({'error': f'CSV harus memiliki kolom: {", ".join(required_cols)}'}), 400

        # Clear existing data
        TrainingData.query.delete()
        
        # Parse data (using logic similar to seed_data.py)
        from seed_data import map_rating_to_sentiment, parse_date_info
        
        training_rows = []
        for index, row in df.iterrows():
            text = str(row['Teks Ulasan'])
            rating = row['Rating']
            tanggal_raw = str(row['Tanggal'])
            
            # Map sentiment
            label, rating_val = map_rating_to_sentiment(rating)
            
            # Parse date info (year, month)
            date_info = parse_date_info(tanggal_raw)
            
            training_rows.append(TrainingData(
                text=text,
                label=label,
                rating=rating_val,
                tahun=date_info['year'],
                bulan=date_info['month'],
                tanggal_asli=date_info['date_obj']
            ))
            
        db.session.bulk_save_objects(training_rows)
        added = len(training_rows)

        # Reset model training status because data changed
        sentiment_model.is_trained = False
        # Remove existing model files to force retraining
        from config import Config
        if os.path.exists(Config.MODEL_PATH):
            os.remove(Config.MODEL_PATH)
        if os.path.exists(Config.VECTORIZER_PATH):
            os.remove(Config.VECTORIZER_PATH)
        
        # Log upload activity
        log = TrainingLog(
            activity_type='upload',
            details=f"Dataset uploaded: {file.filename} ({added} records). Model reset."
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Berhasil mengupload {added} data. Silakan lakukan training ulang.',
            'added_count': added
        })

    except Exception as e:
        return jsonify({'error': f'Gagal memproses CSV: {str(e)}'}), 500


@main_bp.route('/api/training-logs')
def get_training_logs():
    """Get history of uploads and training sessions."""
    logs = TrainingLog.query.order_by(TrainingLog.created_at.desc()).limit(20).all()
    return jsonify([log.to_dict() for log in logs])


@main_bp.route('/api/training-data', methods=['POST'])
def add_training_data():
    """Add new training data."""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        label = data.get('label', '').strip().lower()

        if not text or not label:
            return jsonify({'error': 'Teks dan label tidak boleh kosong.'}), 400

        if label not in ['positif', 'negatif', 'netral']:
            return jsonify({'error': 'Label harus positif, negatif, atau netral.'}), 400

        entry = TrainingData(text=text, label=label)
        db.session.add(entry)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Data training berhasil ditambahkan.',
            'data': {'id': entry.id, 'text': entry.text, 'label': entry.label}
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/training-data/bulk', methods=['POST'])
def add_bulk_training_data():
    """Add multiple training data entries at once."""
    try:
        data = request.get_json()
        items = data.get('items', [])

        if not items:
            return jsonify({'error': 'Data tidak boleh kosong.'}), 400

        added = 0
        for item in items:
            text = item.get('text', '').strip()
            label = item.get('label', '').strip().lower()
            if text and label in ['positif', 'negatif', 'netral']:
                entry = TrainingData(text=text, label=label)
                db.session.add(entry)
                added += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'{added} data training berhasil ditambahkan.',
            'added_count': added
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/reset', methods=['POST'])
def reset_system():
    """Reset the entire system: DB and Model."""
    try:
        # 1. Clear DB
        TrainingData.query.delete()
        PredictionHistory.query.delete()
        TrainingLog.query.delete()
        
        # 2. Reset Model
        sentiment_model.reset_model()
        
        db.session.commit()
        return jsonify({'message': 'Sistem berhasil direset ke pengaturan awal.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/model-info')
def model_info():
    """Get current model information."""
    info = sentiment_model.get_model_info()
    return jsonify(info)
