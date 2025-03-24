import requests
from dotenv import load_dotenv
import os
from spider import Spider

# Load environment variables from .env file
load_dotenv()

# Initialize the Spider with your API key
app = Spider(api_key=os.getenv("SPIDER_API_KEY"))

# Scrape a single URL
url = 'https://spider.cloud'
scraped_data = app.scrape_url(url)

# Crawl a website
crawler_params = {
    'limit': 1,
    'proxy_enabled': True,
    'store_data': False,
    'metadata': False,
    'request': 'http'
}
crawl_result = app.crawl_url(url, params=crawler_params)