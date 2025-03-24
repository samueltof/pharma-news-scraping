import pandas as pd
from datetime import datetime
import numpy as np

def clean_date(date_str):
    """Convert various date formats to datetime"""
    if pd.isna(date_str):
        return None
    
    # Handle 'Month DD, YYYY' format
    try:
        return pd.to_datetime(date_str)
    except:
        try:
            # Try parsing with various formats
            formats = [
                '%B %d, %Y',  # e.g. "November 30, 2022"
                '%Y-%m-%dT%H:%M:%S',  # e.g. "2024-12-20T00:00:00"
                '%Y-%m-%d'  # e.g. "2024-12-20"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
                    
            return None
        except:
            return None

def clean_news_data(file_path):
    """Clean and standardize news data"""
    # Read CSV file
    df = pd.read_csv(file_path)
    
    # Convert dates to datetime
    df['date'] = df['date'].apply(clean_date)
    
    # Filter for dates from 2019 onwards
    df = df[df['date'].dt.year >= 2019]
    
    # Convert category to lowercase if it exists
    if 'category' in df.columns:
        df['category'] = df['category'].str.lower()
    elif 'tags' in df.columns:
        df['tags'] = df['tags'].str.lower()
    
    return df

# Clean each file
lilly_df = clean_news_data('data/raw/lilly/lilly_news_20250101_113822_latest.csv')
merck_df = clean_news_data('data/raw/merck/merck_news_20241231_160018.csv')
pfizer_df = clean_news_data('data/raw/pfizer/pfizer_news_20241231_221326_latest.csv')

# Save cleaned files
merck_df = merck_df.drop('excerpt', axis=1)
merck_df = merck_df.rename(columns={'tags': 'category'})

lilly_df.to_csv('data/clean/lilly_news_cleaned.csv', index=False)
merck_df.to_csv('data/clean/merck_news_cleaned.csv', index=False)
pfizer_df.to_csv('data/clean/pfizer_news_cleaned.csv', index=False)