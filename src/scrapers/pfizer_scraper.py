#!/usr/bin/env python3

"""Pfizer news scraper using AgentQL and Playwright."""

import asyncio
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import agentql
from agentql.ext.playwright.async_api import Page
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()
os.environ["AGENTQL_API_KEY"] = os.getenv("AGENTQL_API_KEY")

URL = "https://www.pfizer.com/news/press-releases"

async def set_items_per_page(page: Page) -> bool:
    """Set items per page to 48."""
    try:
        print("Finding items per page dropdown...")
        # Find and click the view toggle button
        toggle_button = page.locator('button.js-toggle-view')
        
        if not await toggle_button.count():
            print("View toggle button not found")
            return False
            
        print("Clicking view toggle...")
        await toggle_button.click()
        
        # Find and click the "View 48" option
        view_48_option = page.locator('text="View 48"')
        
        if not await view_48_option.count():
            print("View 48 option not found")
            return False
            
        print("Selecting 48 items per page...")
        await view_48_option.click()
        
        # Wait for page to reload
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(5)  # Additional wait for content to load
        
        return True
        
    except Exception as e:
        print(f"Error setting items per page: {e}")
        return False

async def accept_cookies(page: Page) -> bool:
    """Handle the cookie consent popup."""
    try:
        print("Looking for cookie consent dialog...")
        # Pfizer uses a specific cookie consent button
        cookie_button = page.locator('button#onetrust-accept-btn-handler')
        
        if not await cookie_button.count():
            print("No cookie dialog found")
            return True
            
        print("Accepting cookies...")
        await cookie_button.click()
        await page.wait_for_load_state("networkidle")
        return True
        
    except Exception as e:
        print(f"Error handling cookie consent: {e}")
        return False

async def extract_news_articles(page: Page) -> list:
    """Extract news articles from the current page."""
    query = """
    {
        articles[] {
            title
            url
            date(in datetime format)
            category(such as regulatory approval, commercialized drug update, clinical trial update, financial news, management update, etc)
        }
    }
    """
    
    try:
        print("Waiting for articles to load...")
        await asyncio.sleep(10)  # Added wait before extraction
        
        print("Extracting articles...")
        data = await page.query_data(query)
        articles = data.get("articles", [])
        print(f"Successfully extracted {len(articles)} articles")
        
        if len(articles) < 48:
            print("Warning: Fewer articles than expected")
            
        return articles
    except Exception as e:
        print(f"Error extracting articles: {e}")
        return []

async def get_next_page(page: Page) -> bool:
    """Navigate to the next page."""
    try:
        print("Finding next page button...")
        next_button = page.locator('a[rel="next"]')
        
        if not await next_button.count():
            print("Next button not found")
            return False
            
        if not await next_button.is_visible():
            print("Next button is not visible - reached last page")
            return False
            
        print("Clicking next page...")
        await next_button.click()
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(5)  # Increased wait time after clicking
        
        return True
        
    except Exception as e:
        print(f"Error navigating to next page: {e}")
        return False

def save_to_csv(articles: list):
    """Save articles to CSV file."""
    if not articles:
        return
    
    df = pd.DataFrame(articles)
    filename = f"pfizer_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"Saved {len(articles)} articles to {filename}")

async def main():
    """Main function to run the scraper."""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await agentql.wrap_async(await browser.new_page())
        
        try:
            print("Opening Pfizer news page...")
            await page.goto(URL)
            await asyncio.sleep(2)
            
            print("Setting items per page to 48...")
            if not await set_items_per_page(page):
                print("Warning: Could not set items per page to 48")
            
            all_articles = []
            page_num = 1
            max_pages = 18
            
            while page_num <= max_pages:
                print(f"\n=== Scraping page {page_num} ===")
                articles = await extract_news_articles(page)
                print(f"Found {len(articles)} articles on this page")
                all_articles.extend(articles)
                
                if not await get_next_page(page):
                    print("No more pages available")
                    break
                
                page_num += 1
                
            print(f"\nTotal articles collected: {len(all_articles)}")
            save_to_csv(all_articles)
            
        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())