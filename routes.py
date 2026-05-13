"""
Flask routes for Sentiment Analysis application.
"""

from flask import Blueprint, render_template, request, jsonify
from models import db, PredictionHistory, TrainingData
from ml_model import sentiment_model
from preprocessing import preprocess_for_display, preprocess_text
from sqlalchemy import func
from collections import Counter
import datetime
import re

main_bp = Blueprint('main', __name__)


@main_bp.route('/api/stats')
def get_stats():
    """Get comprehensive statistics for the interactive dashboard."""
    sentiment_filter = request.args.get('sentiment', 'all')
    
    # 1. Dataset Summary & Worst Year
    all_data = TrainingData.query.all()
    total_reviews = len(all_data)
    
    # Calculate counts and percentage
    sentiment_counts = Counter([d.label for d in all_data])
    neg_count = sentiment_counts.get('negatif', 0)
    neg_percent = round((neg_count / total_reviews * 100), 1) if total_reviews > 0 else 0
    
    # 2. Trend per Year (2023 - 2026)
    years = [2023, 2024, 2025, 2026]
    trend_data = {year: {'positif': 0, 'netral': 0, 'negatif': 0} for year in years}
    
    for d in all_data:
        if d.tahun in trend_data:
            trend_data[d.tahun][d.label] += 1
            
    # Find Worst Year (highest negative count)
    worst_year = max(trend_data.keys(), key=lambda y: trend_data[y]['negatif'])
    
    # 3. Top Keywords for Complaints (Negatif) - OPTIMIZED: Skip Stemming for speed
    neg_reviews = [d for d in all_data if d.label == 'negatif']
    neg_words = []
    
    # Simple fast cleaning for dashboard keywords
    def fast_clean(text):
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        return text.split()

    for d in neg_reviews:
        words = fast_clean(d.text)
        # Filter out common stopwords manually or use the list
        neg_words.extend([w for w in words if len(w) > 3]) # Simple filter for dashboard
        
    top_neg = Counter(neg_words).most_common(10)
    
    # Positive keywords for comparison
    pos_reviews = [d for d in all_data if d.label == 'positif']
    pos_words = []
    for d in pos_reviews:
        words = fast_clean(d.text)
        pos_words.extend([w for w in words if len(w) > 3])
    top_pos = Counter(pos_words).most_common(10)

    # 4. Dataset Sample (Filtered)
    filtered_data = all_data
    if sentiment_filter != 'all':
        filtered_data = [d for d in all_data if d.label == sentiment_filter]

    dataset_sample = []
    for d in filtered_data[:50]: # Increased to 50 for better filtering experience
        dataset_sample.append({
            'tahun': d.tahun,
            'rating': d.rating,
            'sentimen': d.label,
            'ulasan': (d.text[:120] + '...') if len(d.text) > 120 else d.text
        })

    # 5. Negative Samples
    neg_samples = []
    for d in neg_reviews[:5]:
        neg_samples.append(d.text)

    return jsonify({
        'summary': {
            'total_reviews': total_reviews,
            'neg_percent': neg_percent,
            'worst_year': worst_year
        },
        'trend': {
            'years': years,
            'positif': [trend_data[y]['positif'] for y in years],
            'netral': [trend_data[y]['netral'] for y in years],
            'negatif': [trend_data[y]['negatif'] for y in years]
        },
        'distribution': {
            'labels': ['Negatif', 'Netral', 'Positif'],
            'values': [sentiment_counts.get('negatif', 0), sentiment_counts.get('netral', 0), sentiment_counts.get('positif', 0)]
        },
        'complaints': {
            'top_keywords': [{'word': w, 'count': c} for w, c in top_neg],
            'samples': neg_samples
        },
        'top_pos': [{'word': w, 'count': c} for w, c in top_pos],
        'dataset': dataset_sample
    })


@main_bp.route('/')
def index():
    """Home page - Sentiment prediction form."""
    model_info = sentiment_model.get_model_info()
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

        return jsonify({
            'success': True,
            'metrics': metrics
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


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


@main_bp.route('/api/model-info')
def model_info():
    """Get current model information."""
    info = sentiment_model.get_model_info()
    return jsonify(info)
