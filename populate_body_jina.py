import pandas as pd
import requests
from dotenv import load_dotenv
import os
import time
from tqdm import tqdm

# Load environment variables
load_dotenv()

def fetch_article_body(url):
    """Fetch article body using Jina AI API"""
    try:
        headers = {
            'Authorization': f'Bearer {os.getenv("JINA_API_KEY")}'
        }
        response = requests.get(f'https://r.jina.ai/{url}', headers=headers)
        
        if response.status_code == 200:
            return response.text
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
        if pd.isna(df.loc[idx, 'body']) or df.loc[idx, 'body'] is None:  # Only process if body is empty or None
            url = df.loc[idx, 'url']
            body = fetch_article_body(url)
            if body:
                df.loc[idx, 'body'] = body
            time.sleep(1)  # Rate limiting
    
    return df

def main():
    # File paths
    files = [
        'data/clean/lilly_news_cleaned_test.csv',
        # 'data/clean/merck_news_cleaned.csv',
        # 'data/clean/pfizer_news_cleaned.csv'
    ]
    
    # Process each file
    for file_path in files:
        print(f"\nProcessing {file_path}")
        
        # Read and process file
        df = process_file(file_path)
        
        # Create output path in processed folder
        output_path = file_path.replace('clean/', 'processed/')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save updated file
        df.to_csv(output_path, index=False)
        print(f"Saved updated {output_path}")

if __name__ == "__main__":
    main()