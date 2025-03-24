import requests

# Base URL for ClinicalTrials.gov API
base_url = "https://clinicaltrials.gov/api/v2/studies"

# Correct parameters
params = {
    "query.term": "Heart Failure",  # General search term
    "fields": "NCTId,BriefTitle,OverallStatus",  # Correct field names
}

# Send the GET request
response = requests.get(base_url, params=params)

# Check the response
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    for study in data.get("studies", []):
        print(f"NCT ID: {study.get('NCTId')}")
        print(f"Title: {study.get('BriefTitle')}")
        print(f"Status: {study.get('OverallStatus')}\n")
else:
    print(f"Error {response.status_code}: {response.text}")