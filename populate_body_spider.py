import pandas as pd
import requests
from dotenv import load_dotenv
import os
import time
from tqdm import tqdm

# Load environment variables
load_dotenv()

def fetch_article_body(url):
    """Fetch article body using Spider Cloud API"""
    try:
        headers = {
            'Authorization': f'Bearer {os.getenv("SPIDER_API_KEY")}',
            'Content-Type': 'application/json',
        }
        
        json_data = {
            "limit": 1,
            "return_format": "markdown",
            "url": url
        }
        
        response = requests.post(
            'https://api.spider.cloud/crawl',
            headers=headers, 
            json=json_data
        )
        
        if response.status_code == 200:
            response_data = response.json()
            return response_data[0].get('content')
        else:
            print(f"Error fetching {url}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Exception fetching {url}: {str(e)}")
        return None

def process_file(file_path):
    """Process a single file and add body content"""
    # Read CSV
    df = pd.read_csv(file_path)
    
    # Add body column if it doesn't exist
    if 'body' not in df.columns:
        df['body'] = None
    
    # Process each URL
    for idx in tqdm(df.index, desc=f"Processing {file_path}"):
        if pd.isna(df.loc[idx, 'body']):  # Only process if body is empty
            url = df.loc[idx, 'url']
            body = fetch_article_body(url)
            if body:
                df.loc[idx, 'body'] = body
            time.sleep(1)  # Rate limiting
    
    return df

# File paths
files = [
    # 'data/clean/lilly_news_cleaned_test.csv',
    # 'data/clean/lilly_news_cleaned.csv',
    'data/clean/merck_news_cleaned.csv',
    'data/clean/pfizer_news_cleaned.csv'
]

# Process each file
for file_path in files:
    print(f"\nProcessing {file_path}")
    df = process_file(file_path)
    
    # Create processed directory if it doesn't exist
    os.makedirs('data/processed', exist_ok=True)
    
    # Get the filename from the path and create new path
    filename = os.path.basename(file_path)
    processed_path = os.path.join('data/processed', filename)
    
    # Save to processed directory
    df.to_csv(processed_path, index=False)
    print(f"Saved to {processed_path}")
