import requests
from dotenv import load_dotenv
import os
from firecrawl import FirecrawlApp
import pandas as pd

# Load environment variables from .env file
load_dotenv()

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Scrape a website:
scrape_status = app.scrape_url(
  'https://lilly.mediaroom.com/2024-12-20-FDA-approves-Zepbound-R-tirzepatide-as-the-first-and-only-prescription-medicine-for-moderate-to-severe-obstructive-sleep-apnea-in-adults-with-obesity', 
  params={'formats': ['markdown']}
)
print(scrape_status)


scrape_status.get('markdown')

df = pd.DataFrame()
df['title'] = ['FDA approves Zepbound-R (tirzepatide) as the first and only prescription medicine for moderate to severe obstructive sleep apnea in adults with obesity']
df['url'] = ['https://lilly.mediaroom.com/2024-12-20-FDA-approves-Zepbound-R-tirzepatide-as-the-first-and-only-prescription-medicine-for-moderate-to-severe-obstructive-sleep-apnea-in-adults-with-obesity']
df['date'] = ['2024-12-20']
df['category'] = ['regulatory approval']
df['body'] = [scrape_status.get('markdown')]

