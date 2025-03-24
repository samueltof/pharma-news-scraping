import pandas as pd
import asyncio
from dotenv import load_dotenv
import os
import time
from tqdm import tqdm
import agentql
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()
os.environ["AGENTQL_API_KEY"] = os.getenv("AGENTQL_API_KEY")

async def fetch_article_body(url, page):
    """Fetch article body using AgentQL"""
    try:
        query = """
        {
            article {
                body(in markdown format)
            }
        }
        """
        
        print(f"Fetching content from: {url}")
        await page.goto(url)
        await page.wait_for_load_state("networkidle")
        
        data = await page.query_data(query)
        return data.get("article", {}).get("body")
            
    except Exception as e:
        print(f"Exception fetching {url}: {str(e)}")
        return None

async def process_file(file_path):
    """Process a single file and add body content"""
    # Read CSV
    df = pd.read_csv(file_path)
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await agentql.wrap_async(await browser.new_page())
        
        try:
            # Process each URL with delay
            for idx in tqdm(range(len(df))):
                if pd.isna(df.iloc[idx]['body']):  # Only process if body is empty
                    url = df.iloc[idx]['url']
                    body = await fetch_article_body(url, page)
                    
                    if body:
                        df.at[idx, 'body'] = body
                    
                    # Save after each successful fetch
                    df.to_csv(file_path, index=False)
                    time.sleep(1)  # Small delay between requests
                    
        finally:
            await browser.close()
    
    return df

def main():
    """Main function to process files"""
    files = [f for f in os.listdir('.') if f.startswith('pfizer_news_') and f.endswith('.csv')]
    
    for file in files:
        print(f"Processing {file}...")
        asyncio.run(process_file(file))

if __name__ == "__main__":
    main()
