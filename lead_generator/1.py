import requests
import time
import pandas as pd

# Apify credentials
API_TOKEN = 'apify_api_gK18DAYeTpaDac0JlVYnzAkZQep72r2cKEuA'
TASK_ID = 'mrigaanksh~google-maps-scraper-task'

# Endpoint to run the actor task
run_url = f'https://api.apify.com/v2/actor-tasks/{TASK_ID}/runs?token={API_TOKEN}'

# Updated payload as per your input
payload = {
    "includeWebResults": False,
    "language": "en",
    "locationQuery": "Ghaziabad,India",
    "maxCrawledPlacesPerSearch": 1,
    "maxImages": 0,
    "maxQuestions": 0,
    "maxReviews": 0,
    "scrapeContacts": False,
    "scrapeDirectories": False,
    "scrapeImageAuthors": False,
    "scrapePlaceDetailPage": False,
    "scrapeReviewsPersonalData": True,
    "scrapeTableReservationProvider": False,
    "searchStringsArray": [
        "restaurant"
    ],
    "skipClosedPlaces": False,
    "website": "withoutWebsite"
}

# Start the task run
print("[INFO] Starting Apify run...")
response = requests.post(run_url, json=payload)
run_data = response.json()
run_id = run_data['data']['id']
print(f"[INFO] Run ID: {run_id}")

# Wait for the run to complete
status_url = f'https://api.apify.com/v2/actor-runs/{run_id}?token={API_TOKEN}'
while True:
    status_response = requests.get(status_url).json()
    status = status_response['data']['status']
    print(f"[INFO] Run status: {status}")
    if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
        break
    time.sleep(5)

if status != "SUCCEEDED":
    print(f"[ERROR] Run ended with status: {status}")
    exit()

# Get dataset ID and download data
dataset_id = status_response['data']['defaultDatasetId']
dataset_url = f'https://api.apify.com/v2/datasets/{dataset_id}/items?token={API_TOKEN}&format=json'

print("[INFO] Fetching dataset items...")
dataset_response = requests.get(dataset_url)
data = dataset_response.json()

# Save to CSV
df = pd.DataFrame(data)
csv_file = "restaurants_ghaziabad_no_website.csv"
df.to_csv(csv_file, index=False)
print(f"[✅] Results saved to {csv_file}")
