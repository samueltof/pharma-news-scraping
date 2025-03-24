import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

headers = {
    'Authorization': f'Bearer {os.getenv("JINA_API_KEY")}'
}

url = 'https://lilly.mediaroom.com/2024-12-20-FDA-approves-Zepbound-R-tirzepatide-as-the-first-and-only-prescription-medicine-for-moderate-to-severe-obstructive-sleep-apnea-in-adults-with-obesity'

response = requests.get(f'https://r.jina.ai/{url}', headers=headers)

print(response.text)
