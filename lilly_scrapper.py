#!/usr/bin/env python3

"""Lilly news scraper using AgentQL and Playwright."""

import asyncio
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import agentql
from agentql.ext.playwright.async_api import Page
from playwright.async_api import async_playwright
from urllib.parse import urlparse, parse_qs, urlencode

# Load environment variables
load_dotenv()
os.environ["AGENTQL_API_KEY"] = os.getenv("AGENTQL_API_KEY")

BASE_URL = "https://lilly.mediaroom.com/index.php"
ITEMS_PER_PAGE = 50  # Changed from 100 to 50

START_PAGE = 5  # Modify this to start from specific page
STOP_PAGE = 6  # Modify this to stop at specific page

async def extract_news_articles(page: Page) -> list:
    """Extract news articles from the current page."""
    query = """
    {
        articles[] {
            title
            url
            date(in datetime format)
            category(list of categories such as regulatory approval, commercialized drug update, clinical trial update, financial news, management update, etc)
        }
    }
    """
    
    try:
        print("Extracting articles...")
        data = await page.query_data(query)
        articles = data.get("articles", [])
        print(f"Successfully extracted {len(articles)} articles")
        
        if len(articles) < ITEMS_PER_PAGE:  # Updated to use constant
            print(f"Warning: Fewer articles than expected ({ITEMS_PER_PAGE})")
            
        return articles
    except Exception as e:
        print(f"Error extracting articles: {e}")
        return []

def get_page_url(page_num: int) -> str:
    """Generate URL for specific page number."""
    offset = (page_num - 1) * ITEMS_PER_PAGE  # This calculates correct offset
    
    if page_num == 1:
        return f"{BASE_URL}?s=9042&l={ITEMS_PER_PAGE}"
    else:
        return f"{BASE_URL}?s=9042&l={ITEMS_PER_PAGE}&o={offset}"

async def has_next_page(page: Page) -> bool:
    """Check if next page exists by looking for the next button."""
    next_button = page.locator('li.wd_page_link.wd_page_next a')
    return await next_button.count() > 0

def save_to_csv(articles: list):
    """Save articles to CSV file."""
    if not articles:
        return
    
    df = pd.DataFrame(articles)
    filename = f"lilly_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"Saved {len(articles)} articles to {filename}")

async def main():
    """Main function to run the scraper."""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await agentql.wrap_async(await browser.new_page())
        
        try:
            all_articles = []
            
            for page_num in range(START_PAGE, STOP_PAGE + 1):
                print(f"\n=== Scraping page {page_num} ===")
                current_url = get_page_url(page_num)
                print(f"Loading URL: {current_url}")
                
                await page.goto(current_url)
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(10)
                
                articles = await extract_news_articles(page)
                print(f"Found {len(articles)} articles on this page")
                all_articles.extend(articles)
                
                if not await has_next_page(page):
                    print("No more pages available")
                    break
                
            print(f"\nTotal articles collected: {len(all_articles)}")
            save_to_csv(all_articles)
            
        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())