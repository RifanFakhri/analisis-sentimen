"""
Updated seed script to populate training data from CSV dataset with Rating and Year.
"""

import os
import pandas as pd
from models import db, TrainingData
from app import create_app
import re

def map_rating_to_sentiment(rating_str):
    if not isinstance(rating_str, str):
        return 'netral', 3
    
    rating_val = rating_str.split()[0]
    try:
        val = int(rating_val)
        if val >= 4:
            return 'positif', val
        elif val == 3:
            return 'netral', val
        else:
            return 'negatif', val
    except ValueError:
        return 'netral', 3

def parse_year(tanggal_str):
    """
    Map relative dates to years (assuming current year is 2026).
    3 bulan lalu -> 2026
    setahun lalu -> 2025
    2 tahun lalu -> 2024
    3 tahun lalu -> 2023
    """
    if not isinstance(tanggal_str, str):
        return 2026
    
    tanggal_str = tanggal_str.lower()
    if 'setahun' in tanggal_str or '1 tahun' in tanggal_str:
        return 2025
    
    match = re.search(r'(\d+) tahun lalu', tanggal_str)
    if match:
        diff = int(match.group(1))
        return 2026 - diff
        
    return 2026 # Default to current year for months/weeks/days ago

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
