"""
Updated seed script to populate training data from CSV dataset with Rating and Year.
"""

import os
import pandas as pd
from models import db, TrainingData
from app import create_app
import re

def map_rating_to_sentiment(rating_input):
    if isinstance(rating_input, (int, float)):
        val = int(rating_input)
    elif isinstance(rating_input, str):
        try:
            val = int(rating_input.split()[0])
        except (ValueError, IndexError):
            val = 3
    else:
        val = 3
    
    if val >= 4:
        return 'positif', val
    elif val == 3:
        return 'netral', val
    else:
        return 'negatif', val

from datetime import datetime, timedelta

def parse_date_info(tanggal_str):
    """
    Parse relative date string into year, month, and a date object.
    Assuming 'now' is June 2026 for consistency with previous seeding.
    """
    now = datetime(2026, 6, 15) # Fixed reference point
    
    if not isinstance(tanggal_str, str):
        return {'year': now.year, 'month': now.month, 'date_obj': now.date()}
    
    t = tanggal_str.lower()
    
    # Defaults
    res_date = now
    
    if 'hari lalu' in t:
        days = int(re.search(r'(\d+)', t).group(1)) if re.search(r'(\d+)', t) else 1
        res_date = now - timedelta(days=days)
    elif 'minggu lalu' in t:
        weeks = int(re.search(r'(\d+)', t).group(1)) if re.search(r'(\d+)', t) else 1
        res_date = now - timedelta(weeks=weeks)
    elif 'bulan lalu' in t:
        months = int(re.search(r'(\d+)', t).group(1)) if re.search(r'(\d+)', t) else 1
        # Simple month subtraction
        m = now.month - months
        y = now.year
        while m <= 0:
            m += 12
            y -= 1
        res_date = datetime(y, m, 1)
    elif 'setahun lalu' in t or '1 tahun lalu' in t:
        res_date = now.replace(year=now.year - 1)
    elif 'tahun lalu' in t:
        years = int(re.search(r'(\d+)', t).group(1)) if re.search(r'(\d+)', t) else 1
        res_date = now.replace(year=now.year - years)

    return {
        'year': res_date.year,
        'month': res_date.month,
        'date_obj': res_date.date()
    }

def seed_from_csv():
    app = create_app()
    csv_path = os.path.join('dataset', 'dataset_master_merak_lengkap.csv')
    
    if not os.path.exists(csv_path):
        print(f"Error: Dataset not found at {csv_path}")
        return

    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Filter columns
    df = df[['Tanggal', 'Teks Ulasan', 'Rating']]
    df = df.dropna(subset=['Teks Ulasan'])
    
    with app.app_context():
        # Recreate tables to apply schema changes
        db.drop_all()
        db.create_all()
        print("Database schema updated.")

        added = 0
        for _, row in df.iterrows():
            text = row['Teks Ulasan'].strip()
            if not text:
                continue
                
            label, rating = map_rating_to_sentiment(row['Rating'])
            tahun = parse_year(row['Tanggal'])
            
            entry = TrainingData(text=text, label=label, rating=rating, tahun=tahun)
            db.session.add(entry)
            added += 1
            
            if added % 100 == 0:
                db.session.commit()
                print(f"Inserted {added} records...")

        db.session.commit()
        print(f"Successfully seeded {added} training data entries with Year and Rating info.")

if __name__ == '__main__':
    seed_from_csv()
