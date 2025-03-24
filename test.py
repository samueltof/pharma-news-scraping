import requests, os

headers = {
    'Authorization': f'Bearer {os.getenv("SPIDER_API_KEY")}',
    'Content-Type': 'application/json',
}

url='https://lilly.mediaroom.com/2024-12-20-FDA-approves-Zepbound-R-tirzepatide-as-the-first-and-only-prescription-medicine-for-moderate-to-severe-obstructive-sleep-apnea-in-adults-with-obesity'
json_data = {"limit":1,"return_format":"markdown","url":url}

response = requests.post('https://api.spider.cloud/crawl', 
  headers=headers, json=json_data)

response = response.json()

print(response[0].get('content'))