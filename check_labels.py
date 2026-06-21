import pandas as pd

df = pd.read_csv('dataset/DATASETPULAUMERAK.csv')

print("Unique Ratings:")
print(df['Rating'].value_counts().sort_index())
print(f"\nNaN count in Label Sentimen: {df['Label Sentimen'].isna().sum()}")
print(f"Non-NaN count: {df['Label Sentimen'].notna().sum()}")
