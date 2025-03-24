#!/usr/bin/env python3

"""Merck news scraper using AgentQL and Playwright."""

import asyncio
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import agentql
from agentql.ext.playwright.async_api import Page
from playwright.async_api import async_playwright

# Load environment variables from .env file
load_dotenv()

os.environ["AGENTQL_API_KEY"] = os.getenv("AGENTQL_API_KEY")

URL = "https://www.merck.com/media/news/"

async def extract_news_articles(page: Page) -> list:
    """Extract news articles from the current page."""
    # Define the query structure matching Merck's news page HTML
    query = """
    {
        articles[] {
            title
            url
            date(in datetime format)
            category(categories such as regulatory approval, commercialized drug update, clinical trial update, financial news, management update, etc)
        }
    }
    """
    
    try:
        print("Extracting articles...")
        data = await page.query_data(query)
        articles = data.get("articles", [])
        print(f"Successfully extracted {len(articles)} articles")
        
        # Verify expected count
        if len(articles) < 50:
            print("Warning: Extracted fewer articles than expected")
            
        return articles
    except Exception as e:
        print(f"Error extracting articles: {e}")
        return []

async def get_next_page(page: Page) -> bool:
    """Navigate to the next page by clicking the next button."""
    try:
        # Get current range before clicking
        current_range = await get_pagination_range(page)
        if not current_range:
            return False
        
        expected_start = current_range[1] + 1
        
        print("Finding next page button...")
        # Locate the next page button using class
        next_button = page.locator('div.d8-page-right.page-right')
        
        if not await next_button.count():
            print("Next button not found")
            return False
            
        # Check if button is visible
        is_visible = await next_button.is_visible()
        if not is_visible:
            print("Next button is not visible - reached last page")
            return False
            
        print("Clicking next page...")
        # Click the button and wait for navigation
        await next_button.click()
        # Wait for page content to load
        await page.wait_for_load_state("networkidle")
        
        # Additional wait for articles to load
        print("Waiting for articles to load...")
        await asyncio.sleep(7)
        
        # # Verify new page loaded correctly
        # if not await verify_next_page(page, expected_start):
        #     print("Failed to load next page correctly")
        #     return False
            
        return True
        
    except Exception as e:
        print(f"Error navigating to next page: {e}")
        return False

async def set_items_per_page(page: Page) -> bool:
    """Set items per page to 50."""
    try:
        print("Finding items per page dropdown...")
        # Use Playwright's locator to find the select element
        select_element = page.locator('select[aria-label="Items per page"]')
        
        if not await select_element.count():
            print("Items per page select not found")
            return False
        
        print("Selecting 50 items per page...")    
        # Select 50 items option
        await select_element.select_option(value="50")
        
        # Wait for page to reload
        await page.wait_for_load_state("networkidle")
        
        # Additional wait for articles to load
        print("Waiting for articles to load...")
        await asyncio.sleep(6)
        
        # # Verify 50 items are shown
        # if not await verify_items_per_page(page):
        #     print("Failed to set 50 items per page")
        #     return False
            
        return True
        
    except Exception as e:
        print(f"Error setting items per page: {e}")
        return False

async def accept_cookies(page: Page) -> bool:
    """Handle the cookie consent popup."""
    try:
        print("Looking for cookie consent dialog...")
        # Find accept button using prompt
        accept_btn = await page.get_by_prompt("Accept cookies button")
        
        if not accept_btn:
            print("No cookie dialog found")
            return True
            
        print("Accepting cookies...")
        await accept_btn.click()
        await page.wait_for_load_state("networkidle")
        return True
        
    except Exception as e:
        print(f"Error handling cookie consent: {e}")
        return False

def save_to_csv(articles: list):
    """Save articles to CSV file."""
    if not articles:
        return
    
    df = pd.DataFrame(articles)
    filename = f"merck_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"Saved {len(articles)} articles to {filename}")

async def get_pagination_range(page: Page) -> tuple:
    """Get current pagination range from page."""
    try:
        # Get pagination text
        pagination_text = await page.locator('div.d8-pagination-pagers p').text_content()
        if not pagination_text:
            return None
            
        # Parse range (e.g., "1-100 of 1768" -> (1, 100))
        range_part = pagination_text.split(' of ')[0]
        start, end = map(int, range_part.split('-'))
        return (start, end)
    except Exception as e:
        print(f"Error getting pagination range: {e}")
        return None

# async def verify_items_per_page(page: Page) -> bool:
#     """Verify 100 items per page is set correctly."""
#     range_tuple = await get_pagination_range(page)
#     if not range_tuple:
#         return False
    
#     start, end = range_tuple
#     return (end - start + 1) == 100

# async def verify_next_page(page: Page, expected_start: int) -> bool:
#     """Verify next page loaded correctly."""
#     range_tuple = await get_pagination_range(page)
#     if not range_tuple:
#         return False
    
#     start, end = range_tuple
#     return start == expected_start

async def main():
    """Main function to run the scraper."""
    async with async_playwright() as playwright:
        # Launch browser in visible mode with slower speed
        browser = await playwright.chromium.launch(
            headless=False,  # Make browser visible
        )
        page = await agentql.wrap_async(await browser.new_page())
        
        try:
            print("Opening Merck news page...")
            await page.goto(URL)
            await asyncio.sleep(2)  # Wait to see the page
            
            # Handle cookies first
            if not await accept_cookies(page):
                print("Warning: Could not handle cookie consent")
                
            print("Setting items per page to 50...")
            if not await set_items_per_page(page):
                print("Warning: Could not set items per page to 50")
            await asyncio.sleep(5)
            
            all_articles = []
            page_num = 1
            max_pages = 20
            
            while page_num <= max_pages:
                print(f"\n=== Scraping page {page_num} ===")
                articles = await extract_news_articles(page)
                print(f"Found {len(articles)} articles on this page")
                all_articles.extend(articles)
                
                if not await get_next_page(page):
                    print("No more pages available")
                    break
                
                await asyncio.sleep(1)  # See the page transition
                page_num += 1
                
            print(f"\nTotal articles collected: {len(all_articles)}")
            save_to_csv(all_articles)
            
        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            input("Press Enter to close the browser...")  # Keep browser open
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())