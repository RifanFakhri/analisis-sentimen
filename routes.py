"""
Flask routes for Sentiment Analysis application.
"""

from flask import Blueprint, render_template, request, jsonify, send_file
from models import db, PredictionHistory, TrainingData, TrainingLog
from ml_model import sentiment_model
from preprocessing import preprocess_for_display, preprocess_text
from sqlalchemy import func
from collections import Counter
from datetime import datetime, timedelta
import re
import pandas as pd
import io

POSITIVE_TERMS = {
    'bagus', 'baik', 'nyaman', 'puas', 'menarik', 'indah', 'mantap', 'baguss', 'keren',
    'sejuk', 'bersih', 'ramah', 'enak', 'murah', 'recommended', 'terbaik', 'oke', 'ok'
}
NEGATIVE_TERMS = {
    'jelek', 'buruk', 'menakutkan', 'kotor', 'panas', 'macet', 'jauh', 'mahal', 'parah',
    'payah', 'susah', 'tidak nyaman', 'kecewa', 'ramai', 'ribet', 'berantakan', 'bau',
    'rusak', 'sedih', 'mengerikan', 'jijik'
}

def infer_text_sentiment(text):
    clean = preprocess_text(text)
    tokens = clean.split()
    pos = sum(1 for w in tokens if w in POSITIVE_TERMS)
    neg = sum(1 for w in tokens if w in NEGATIVE_TERMS)
    if pos > neg:
        return 'positif', pos, neg
    if neg > pos:
        return 'negatif', pos, neg
    return 'netral', pos, neg


def combine_rating_text_label(rating_label, text_label, rating_val, pos_count, neg_count):
    if rating_label == text_label:
        return rating_label

    if rating_label == 'netral':
        return text_label if text_label != 'netral' else rating_label

    if text_label == 'netral':
        return rating_label

    diff = abs(pos_count - neg_count)
    if diff >= 2:
        return text_label

    return rating_label
import os

main_bp = Blueprint('main', __name__)


def has_text(text):
    """Return True if the text contains non-empty content."""
    return bool(text and str(text).strip())


@main_bp.route('/api/stats')
def get_stats():
    """Get comprehensive statistics for the interactive dashboard (using NB predictions for thesis)."""
    sentiment_filter = request.args.get('sentiment', 'all')
    time_range = request.args.get('range', '6m') # 3m, 6m, 1y, all
    
    # 1. Base Data - GUNAKAN NB PREDICTIONS UNTUK SKRIPSI
    query = TrainingData.query
    all_data = query.all()
    total_reviews = len(all_data)
    
    if total_reviews == 0:
        return jsonify({'summary': {'total_reviews': 0}, 'metrics': {'is_trained': False}, 'error': 'No data'})

    # FILTER BY NB PREDICTION (bukan rating label)
    if sentiment_filter != 'all':
        filtered_data = [d for d in all_data if d.nb_predicted_label == sentiment_filter]
    else:
        filtered_data = all_data
    
    # Count by NB prediction (bukan by label)
    nb_predictions = [d.nb_predicted_label for d in filtered_data if d.nb_predicted_label]
    sentiment_counts = Counter(nb_predictions) if nb_predictions else Counter()
    
    if len(filtered_data) == 0:
        filtered_data = all_data
        nb_predictions = [d.nb_predicted_label for d in filtered_data if d.nb_predicted_label]
        sentiment_counts = Counter(nb_predictions) if nb_predictions else Counter()
    
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
        for d in filtered_data:
            if has_text(d.text) and any(kw in d.text.lower() for kw in keywords):
                count += 1
        percent = round((count / len(filtered_data) * 100), 1) if len(filtered_data) > 0 else 0
        aspect_stats.append({'aspect': aspect, 'count': count, 'percent': percent})
    
    # Sort aspects by count
    aspect_stats = sorted(aspect_stats, key=lambda x: x['count'], reverse=True)

    # 3. Monthly Trend (using NB predictions)
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
    
    # Group by Month-Year using NB predictions
    month_map = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    
    # Create labels for the range
    monthly_stats = []
    current = start_date.replace(day=1)
    while current <= now:
        m = current.month
        y = current.year
        
        # Count NB predictions per month
        pos = len([d for d in trend_data_query if d.bulan == m and d.tahun == y and d.nb_predicted_label == 'positif'])
        neg = len([d for d in trend_data_query if d.bulan == m and d.tahun == y and d.nb_predicted_label == 'negatif'])
        net = len([d for d in trend_data_query if d.bulan == m and d.tahun == y and d.nb_predicted_label == 'netral'])
        
        monthly_stats.append({
            'label': f"{month_map[m]} {y}",
            'positif': pos,
            'netral': net,
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
    for d in [d for d in filtered_data if d.nb_predicted_label == 'negatif' and has_text(d.text)]:
        neg_words.extend([w for w in fast_clean(d.text) if len(w) > 3])
    top_neg = Counter(neg_words).most_common(10)
    
    pos_words = []
    for d in [d for d in filtered_data if d.nb_predicted_label == 'positif' and has_text(d.text)]:
        pos_words.extend([w for w in fast_clean(d.text) if len(w) > 3])
    top_pos = Counter(pos_words).most_common(10)

    # 5. Training Metrics (Dynamic based on filter)
    info = sentiment_model.get_model_info()
    metrics = {'is_trained': False}
    
    if info['is_trained'] and hasattr(sentiment_model, 'last_metrics'):
        m = sentiment_model.last_metrics
        report = m.get('report', {})
        
        # Determine which key to look at in the classification report
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

    # UNTUK SKRIPSI: Comparison Rating vs NB Prediction
    all_data_for_comparison = all_data if not filtered_data else all_data
    rating_based_counts = Counter([d.label for d in all_data_for_comparison if d.label])
    nb_based_counts = Counter([d.nb_predicted_label for d in all_data_for_comparison if d.nb_predicted_label])

    total_for_stats = len(all_data_for_comparison)
    
    return jsonify({
        'summary': {
            'total_reviews': total_reviews,
            'pos_count': sentiment_counts.get('positif', 0),
            'neg_count': sentiment_counts.get('negatif', 0),
            'netral_count': sentiment_counts.get('netral', 0),
            'pos_percent': round((sentiment_counts.get('positif', 0) / len(filtered_data) * 100), 1) if len(filtered_data) > 0 else 0,
            'neg_percent': round((sentiment_counts.get('negatif', 0) / len(filtered_data) * 100), 1) if len(filtered_data) > 0 else 0,
            'netral_percent': round((sentiment_counts.get('netral', 0) / len(filtered_data) * 100), 1) if len(filtered_data) > 0 else 0,
        },
        'metrics': metrics,
        'aspects': aspect_stats,
        'trend': {
            'labels': [m['label'] for m in monthly_stats],
            'positif': [m['positif'] for m in monthly_stats],
            'netral': [m.get('netral', 0) for m in monthly_stats],
            'negatif': [m['negatif'] for m in monthly_stats]
        },
        'distribution': {
            'labels': ['Negatif', 'Netral', 'Positif'],
            'values': [sentiment_counts.get('negatif', 0), sentiment_counts.get('netral', 0), sentiment_counts.get('positif', 0)]
        },
        'top_neg': [{'word': w, 'count': c} for w, c in top_neg],
        'top_pos': [{'word': w, 'count': c} for w, c in top_pos],
        'samples': [{'text': d.text, 'sentiment': d.nb_predicted_label or 'netral', 'confidence': d.nb_confidence or 0} for d in filtered_data[:5]],
        # UNTUK SKRIPSI: Tambah comparison rating vs NB
        'rating_based': {
            'positif': rating_based_counts.get('positif', 0),
            'negatif': rating_based_counts.get('negatif', 0),
            'netral': rating_based_counts.get('netral', 0),
        },
        'nb_based': {
            'positif': nb_based_counts.get('positif', 0),
            'negatif': nb_based_counts.get('negatif', 0),
            'netral': nb_based_counts.get('netral', 0),
        },
        'source': 'Naive Bayes Prediction (for thesis)'
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
    
    # If model is trained, show NB predictions; otherwise show original labels
    if model_info.get('is_trained'):
        label_counts = db.session.query(
            TrainingData.nb_predicted_label,
            db.func.count(TrainingData.id)
        ).filter(TrainingData.nb_predicted_label != None).group_by(TrainingData.nb_predicted_label).all()
    else:
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


@main_bp.route('/api/train-stats')
def get_train_stats():
    """Get training stats for the training page (after training completion)."""
    model_info = sentiment_model.get_model_info()
    
    # If model is trained, show NB predictions; otherwise show original labels
    if model_info.get('is_trained'):
        label_counts = db.session.query(
            TrainingData.nb_predicted_label,
            db.func.count(TrainingData.id)
        ).filter(TrainingData.nb_predicted_label != None).group_by(TrainingData.nb_predicted_label).all()
    else:
        label_counts = db.session.query(
            TrainingData.label,
            db.func.count(TrainingData.id)
        ).group_by(TrainingData.label).all()
    
    label_stats = {label: count for label, count in label_counts}
    total_data = TrainingData.query.count()
    
    return jsonify({
        'total_data': total_data,
        'label_stats': label_stats,
        'is_trained': model_info.get('is_trained', False)
    })


@main_bp.route('/report')
def report():
    """Report/Laporan page."""
    model_info = sentiment_model.get_model_info()
    return render_template('report.html', model_info=model_info)


@main_bp.route('/analysis')
def analysis():
    """Analisis Sentimen page - comprehensive analysis."""
    model_info = sentiment_model.get_model_info()
    return render_template('analysis.html', model_info=model_info)


@main_bp.route('/api/train', methods=['POST'])
def train_model():
    """Train the model using data from database and predict all data (for thesis)."""
    try:
        training_data = TrainingData.query.filter(TrainingData.text != '', TrainingData.text != None).order_by(TrainingData.id).all()

        if len(training_data) < 10:
            return jsonify({
                'error': 'Data training terlalu sedikit. Minimal 10 data dengan teks ulasan diperlukan.'
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

        # UNTUK SKRIPSI: Predict semua baris dengan teks ulasan menggunakan trained model
        print("Predicting sentiments for all training data using Naive Bayes...")
        predictions = sentiment_model.predict_batch(texts)
        
        # Update database dengan prediksi NB
        for i, training_entry in enumerate(training_data):
            prediction = predictions[i]
            training_entry.nb_predicted_label = prediction['sentiment']
            training_entry.nb_confidence = prediction['confidence']
            training_entry.nb_positif_prob = prediction['probabilities'].get('positif', 0)
            training_entry.nb_negatif_prob = prediction['probabilities'].get('negatif', 0)
            training_entry.nb_netral_prob = prediction['probabilities'].get('netral', 0)
        
        db.session.commit()
        print(f"Successfully predicted and saved {len(training_data)} predictions to database.")

        # Log training activity
        log = TrainingLog(
            activity_type='training',
            details=f"Model trained successfully with {len(texts)} samples. Accuracy: {metrics['accuracy']}%. All data predicted with Naive Bayes."
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            'success': True,
            'metrics': metrics,
            'predictions_saved': len(predictions)
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

        # Flexible column detection (case-insensitive)
        cols_lower = {c.lower(): c for c in df.columns}
        # Required: text and tanggal (date). Accept common variants.
        text_col = cols_lower.get('teks ulasan') or cols_lower.get('text') or cols_lower.get('teks')
        date_col = cols_lower.get('tanggal') or cols_lower.get('date')

        # Detect label column variants (support Indonesian/English headers)
        label_keys = ['label', 'sentimen', 'sentiment', 'label sentimen', 'label_sentimen']
        label_col_key = next((k for k in label_keys if k in cols_lower), None)
        has_label_col = label_col_key is not None
        has_rating_col = 'rating' in cols_lower or 'rating bintang' in cols_lower

        if not text_col or not date_col:
            return jsonify({'error': 'CSV harus memiliki kolom: Teks Ulasan (atau text) dan Tanggal.'}), 400

        if not has_label_col and not has_rating_col:
            return jsonify({'error': 'CSV harus memiliki kolom `label` atau `Rating` untuk pelabelan.'}), 400

        # Clear existing data
        TrainingData.query.delete()

        # Parse data (use seed_data helpers when rating->label mapping needed)
        from seed_data import map_rating_to_sentiment, parse_date_info

        training_rows = []
        for index, row in df.iterrows():
            text = str(row[text_col]) if pd.notna(row[text_col]) else ''
            tanggal_raw = str(row[date_col]) if pd.notna(row[date_col]) else ''

            label = None
            rating_val = None

            # Prefer explicit label column if present
            if has_label_col:
                raw_label = str(row[cols_lower[label_col_key]]).strip().lower() if pd.notna(row[cols_lower[label_col_key]]) else ''
                if raw_label in ('positif', 'negatif', 'netral'):
                    label = raw_label
                else:
                    # Try parse numeric-like label (e.g., '4' or '4.0') into sentiment
                    try:
                        num = int(float(raw_label))
                        label, rating_val = map_rating_to_sentiment(num)
                    except Exception:
                        label = None

            # If no valid explicit label, fallback to rating mapping and text inference
            if label is None and has_rating_col:
                raw_rating = row[cols_lower['rating']]
                base_label, rating_val = map_rating_to_sentiment(raw_rating)
                text_label, pos_count, neg_count = infer_text_sentiment(text) if has_text(text) else (base_label, 0, 0)
                label = combine_rating_text_label(base_label, text_label, rating_val, pos_count, neg_count)

            # If still no label, skip row
            if not label:
                continue

            # Allow rating-only rows to be stored as reference data
            if not has_text(text):
                text = ''

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

        # Optional: trigger automatic training if caller requested
        auto_train = request.form.get('auto_train') == '1' or request.args.get('auto_train') == '1'
        if auto_train:
            training_rows_with_text = TrainingData.query.filter(TrainingData.text != '', TrainingData.text != None).order_by(TrainingData.id).all()
            if len(training_rows_with_text) >= 10:
                try:
                    texts = [r.text for r in training_rows_with_text]
                    labels = [r.label for r in training_rows_with_text]

                    # Ensure at least two classes
                    if len(set(labels)) >= 2:
                        metrics = sentiment_model.train(texts, labels)

                        # Predict and save NB predictions only for rows with text
                        predictions = sentiment_model.predict_batch(texts)
                        for i, training_entry in enumerate(training_rows_with_text):
                            pred = predictions[i]
                            training_entry.nb_predicted_label = pred['sentiment']
                            training_entry.nb_confidence = pred['confidence']
                            training_entry.nb_positif_prob = pred['probabilities'].get('positif', 0)
                            training_entry.nb_negatif_prob = pred['probabilities'].get('negatif', 0)
                            training_entry.nb_netral_prob = pred['probabilities'].get('netral', 0)
                        db.session.commit()

                        log = TrainingLog(
                            activity_type='training',
                            details=f"Auto-training completed after upload ({added} samples). Accuracy: {metrics.get('accuracy')}%"
                        )
                        db.session.add(log)
                        db.session.commit()

                        return jsonify({'success': True, 'message': f'Uploaded {added} rows and auto-trained model.', 'metrics': metrics, 'added_count': added})
                    else:
                        return jsonify({'success': True, 'message': f'Uploaded {added} rows but auto-training skipped because dataset has fewer than 2 sentiment classes.', 'added_count': added})
                except Exception as e:
                    # If auto-training fails, still return upload success but include error
                    return jsonify({'success': True, 'message': f'Uploaded {added} rows, but auto-train failed: {str(e)}', 'added_count': added}), 500

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


@main_bp.route('/api/model-evaluation', methods=['GET'])
def model_evaluation():
    """
    API endpoint untuk menampilkan evaluasi model Naive Bayes (untuk skripsi).
    Menampilkan confusion matrix, metrics, dan comparison rating vs NB prediction.
    """
    try:
        if not sentiment_model.is_trained or not hasattr(sentiment_model, 'last_metrics'):
            return jsonify({'error': 'Model belum dilatih. Silakan latih model terlebih dahulu.'}), 400

        metrics = sentiment_model.last_metrics
        training_data = TrainingData.query.order_by(TrainingData.id).all()

        # Hitung misclassification rate (rating vs NB prediction)
        misclassified = 0
        for d in training_data:
            if d.label != d.nb_predicted_label and d.nb_predicted_label:
                misclassified += 1

        total = len([d for d in training_data if d.nb_predicted_label])
        misclassification_rate = round((misclassified / total * 100), 2) if total > 0 else 0

        # Hitung confidence distribution
        confidences = [d.nb_confidence for d in training_data if d.nb_confidence]
        high_confidence = len([c for c in confidences if c >= 0.8])
        medium_confidence = len([c for c in confidences if 0.5 <= c < 0.8])
        low_confidence = len([c for c in confidences if c < 0.5])

        return jsonify({
            'model_info': {
                'algorithm': 'Complement Naive Bayes',
                'is_trained': sentiment_model.is_trained,
                'training_samples': metrics['train_size'],
                'test_samples': metrics['test_size'],
                'total_samples': metrics['train_size'] + metrics['test_size'],
            },
            'performance_metrics': {
                'accuracy': metrics['accuracy'],
                'confusion_matrix': metrics['confusion_matrix'],
                'classification_report': metrics['report'],
                'labels': metrics['labels']
            },
            'thesis_analysis': {
                'comparison_rating_vs_nb': {
                    'misclassified_count': misclassified,
                    'total_count': total,
                    'misclassification_rate': misclassification_rate,
                    'message': f'{misclassification_rate}% data memiliki perbedaan antara rating dan prediksi Naive Bayes'
                },
                'confidence_distribution': {
                    'high_confidence_80plus': high_confidence,
                    'medium_confidence_50_80': medium_confidence,
                    'low_confidence_below_50': low_confidence,
                    'message': 'Distribusi tingkat kepercayaan prediksi Naive Bayes'
                }
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/thesis-report', methods=['GET'])
def thesis_report():
    """
    Generate comprehensive thesis report untuk penelitian skripsi.
    Menampilkan ringkasan implementasi Naive Bayes, analisis, dan statistik lengkap.
    """
    try:
        training_data = TrainingData.query.order_by(TrainingData.id).all()
        
        if len(training_data) == 0:
            return jsonify({'error': 'Tidak ada data untuk dianalisis.'}), 400

        # 1. Data Summary
        total_data = len(training_data)
        rating_based = Counter([d.label for d in training_data if d.label])
        nb_based = Counter([d.nb_predicted_label for d in training_data if d.nb_predicted_label])

        # 2. Model Performance
        model_performance = {'is_trained': False}
        if sentiment_model.is_trained and hasattr(sentiment_model, 'last_metrics'):
            m = sentiment_model.last_metrics
            model_performance = {
                'is_trained': True,
                'accuracy': m['accuracy'],
                'training_size': m['train_size'],
                'test_size': m['test_size'],
                'labels': m['labels'],
                'report': m['report']
            }

        # 3. Sentiment Distribution Comparison
        all_sentiments = ['positif', 'netral', 'negatif']
        distribution_comparison = {}
        for sentiment in all_sentiments:
            rating_count = rating_based.get(sentiment, 0)
            nb_count = nb_based.get(sentiment, 0)
            difference = nb_count - rating_count
            distribution_comparison[sentiment] = {
                'rating_based': rating_count,
                'nb_predicted': nb_count,
                'difference': difference,
                'percentage_diff': round((difference / rating_count * 100), 2) if rating_count > 0 else 0
            }

        # 4. Agreement Analysis
        agreement_count = 0
        disagreement_count = 0
        for d in training_data:
            if d.label and d.nb_predicted_label:
                if d.label == d.nb_predicted_label:
                    agreement_count += 1
                else:
                    disagreement_count += 1

        agreement_rate = round((agreement_count / (agreement_count + disagreement_count) * 100), 2) if (agreement_count + disagreement_count) > 0 else 0

        # 5. Aspect Analysis
        aspect_keywords = {
            'Keindahan': ['indah', 'bagus', 'cantik', 'pemandangan', 'keren', 'view', 'pesona'],
            'Aksesibilitas': ['jalan', 'akses', 'transportasi', 'perjalanan', 'jauh', 'macet', 'lokasi'],
            'Fasilitas': ['toilet', 'mushola', 'fasilitas', 'kamar mandi', 'tempat duduk', 'sarana'],
            'Kebersihan': ['bersih', 'sampah', 'kotor', 'bau', 'limbah', 'terawat'],
            'Harga tiket': ['harga', 'tiket', 'murah', 'mahal', 'biaya', 'tarif', 'bayar'],
            'Pelayanan': ['petugas', 'layanan', 'ramah', 'service', 'pengelola', 'orang']
        }

        aspect_analysis = {}
        for aspect, keywords in aspect_keywords.items():
            count = sum(1 for d in training_data if has_text(d.text) and any(kw in d.text.lower() for kw in keywords))
            aspect_analysis[aspect] = {
                'count': count,
                'percentage': round((count / total_data * 100), 2)
            }

        return jsonify({
            'thesis_research_report': {
                'title': 'IMPLEMENTASI ALGORITMA NAIVE BAYES PADA DASHBOARD VISUALISASI ANALISIS SENTIMEN WISATAWAN PULAU MERAK',
                'research_focus': 'Data crowdsourcing dari Google Maps',
                'algorithm': 'Complement Naive Bayes with TF-IDF',
                'data_summary': {
                    'total_reviews': total_data,
                    'date_range': f"Analysis date: June 2026",
                    'source': 'Google Maps Reviews (Crowdsourcing)'
                },
                'rating_based_distribution': {
                    'positif': rating_based.get('positif', 0),
                    'netral': rating_based.get('netral', 0),
                    'negatif': rating_based.get('negatif', 0),
                    'note': 'Distribution berdasarkan rating bintang mapping'
                },
                'naive_bayes_prediction': {
                    'positif': nb_based.get('positif', 0),
                    'netral': nb_based.get('netral', 0),
                    'negatif': nb_based.get('negatif', 0),
                    'note': 'Distribution berdasarkan Naive Bayes text analysis'
                },
                'distribution_comparison': distribution_comparison,
                'agreement_analysis': {
                    'agreement_count': agreement_count,
                    'disagreement_count': disagreement_count,
                    'agreement_rate': agreement_rate,
                    'interpretation': f'{agreement_rate}% dari data memiliki kesamaan antara rating dan prediksi NB'
                },
                'aspect_analysis': aspect_analysis,
                'model_performance': model_performance,
                'conclusion': {
                    'implementation_status': 'Fully Implemented',
                    'naive_bayes_application': 'Used for text classification and sentiment prediction',
                    'preprocessing_stages': '6 stages (case folding, cleaning, normalization, tokenization, stopword removal, stemming)',
                    'vectorization': 'TF-IDF with 5000 features and n-gram (1-2)',
                    'ready_for_thesis': True
                }
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/api/export-report')
def export_report():
    """Export report in different formats (PDF, Excel, CSV)."""
    try:
        export_format = request.args.get('format', 'csv').lower()
        
        # Get data
        training_data = TrainingData.query.all()
        if not training_data:
            return jsonify({'error': 'Tidak ada data untuk diekspor.'}), 400
        
        # Prepare data
        data_list = []
        for d in training_data:
            data_list.append({
                'Teks Ulasan': d.text,
                'Rating': d.rating or '-',
                'Label Rating': d.label or '-',
                'Sentimen NB': d.nb_predicted_label or '-',
                'Kepercayaan': round(d.nb_confidence * 100, 2) if d.nb_confidence else 0,
                'Prob Positif': round(d.nb_positif_prob * 100, 2) if d.nb_positif_prob else 0,
                'Prob Netral': round(d.nb_netral_prob * 100, 2) if d.nb_netral_prob else 0,
                'Prob Negatif': round(d.nb_negatif_prob * 100, 2) if d.nb_negatif_prob else 0,
                'Tanggal': d.tanggal_asli.strftime('%Y-%m-%d') if d.tanggal_asli else (d.created_at.strftime('%Y-%m-%d') if d.created_at else '-')
            })
        
        df = pd.DataFrame(data_list)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if export_format == 'csv':
            output = io.StringIO()
            df.to_csv(output, index=False, encoding='utf-8-sig')
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8-sig')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'Laporan_Sentimen_{timestamp}.csv'
            )
        
        elif export_format == 'excel':
            try:
                import openpyxl
                import openpyxl.styles
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Data')
                    
                    # Style the header
                    worksheet = writer.sheets['Data']
                    for cell in worksheet[1]:
                        cell.font = openpyxl.styles.Font(bold=True, color='FFFFFF')
                        cell.fill = openpyxl.styles.PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
                        cell.alignment = openpyxl.styles.Alignment(horizontal='center', vertical='center')
                    
                    # Auto adjust column widths
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
                
                output.seek(0)
                return send_file(
                    output,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True,
                    download_name=f'Laporan_Sentimen_{timestamp}.xlsx'
                )
            except ImportError:
                return jsonify({'error': 'Library openpyxl tidak terinstall.'}), 400
        
        elif export_format == 'pdf':
            try:
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4)
                elements = []
                styles = getSampleStyleSheet()
                
                # Title
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    textColor=colors.HexColor('#1e3a8a'),
                    spaceAfter=12,
                    alignment=1
                )
                elements.append(Paragraph('Laporan Analisis Sentimen', title_style))
                elements.append(Spacer(1, 0.3 * inch))
                
                # Summary
                summary_data = [
                    ['Metrik', 'Nilai'],
                    ['Total Data', str(len(training_data))],
                    ['Data Positif', str(len([d for d in training_data if d.nb_predicted_label == 'positif']))],
                    ['Data Netral', str(len([d for d in training_data if d.nb_predicted_label == 'netral']))],
                    ['Data Negatif', str(len([d for d in training_data if d.nb_predicted_label == 'negatif']))],
                    ['Tanggal Generate', datetime.now().strftime('%d-%m-%Y %H:%M:%S')],
                ]
                
                summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(summary_table)
                elements.append(Spacer(1, 0.3 * inch))
                
                # Data table (first 50 rows)
                elements.append(Paragraph('Detail Data', styles['Heading2']))
                elements.append(Spacer(1, 0.2 * inch))
                
                table_data = [['Teks', 'Sentimen', 'Kepercayaan', 'Rating']]
                for d in training_data[:50]:
                    text = (d.text[:50] + '...') if len(d.text) > 50 else d.text
                    sentiment = d.nb_predicted_label or '-'
                    confidence = f"{round(d.nb_confidence * 100, 1)}%" if d.nb_confidence else '-'
                    rating = str(d.rating) if d.rating else '-'
                    table_data.append([text, sentiment, confidence, rating])
                
                data_table = Table(table_data, colWidths=[3 * inch, 1.5 * inch, 1.5 * inch, 1 * inch])
                data_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                
                elements.append(data_table)
                doc.build(elements)
                buffer.seek(0)
                
                return send_file(
                    buffer,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f'Laporan_Sentimen_{timestamp}.pdf'
                )
            
            except ImportError:
                return jsonify({'error': 'Library reportlab tidak terinstall. Silakan gunakan format Excel atau CSV.'}), 400
        
        else:
            return jsonify({'error': 'Format tidak didukung. Gunakan: csv, excel, atau pdf.'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500