import pandas as pd
import requests
from dotenv import load_dotenv
import os
import time
from tqdm import tqdm
from firecrawl import FirecrawlApp

# Load environment variables
load_dotenv()

# Initialize Firecrawl
app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

def fetch_article_body(url):
    """Fetch article body using Firecrawl API"""
    try:
        scrape_status = app.scrape_url(
            url,
            params={'formats': ['markdown']}
        )
        
        if scrape_status and 'markdown' in scrape_status:
            return scrape_status.get('markdown')
        else:
            print(f"Error fetching {url}: No markdown content")
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
input_files = [
    'data/clean/lilly_news_cleaned_test.csv',
    # 'data/clean/merck_news_cleaned.csv',
    # 'data/clean/pfizer_news_cleaned.csv'
]

# Create processed directory if it doesn't exist
os.makedirs('data/processed', exist_ok=True)

# Process each file
for input_file in input_files:
    print(f"\nProcessing {input_file}")
    
    # Read and process file
    df = process_file(input_file)
    
    # Create output path
    output_file = input_file.replace('data/clean', 'data/processed')
    
    # Save updated file
    df.to_csv(output_file, index=False)
    print(f"Saved processed file to {output_file}")
