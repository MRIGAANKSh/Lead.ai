import requests
from bs4 import BeautifulSoup
import re
import csv
import os

# 1️⃣ Google Search Function (Using SerpAPI)
def search_leads(query):
    api_key = "2a05bd86f3ea7be95de574ce1ac831767674f96cc14632fe7181b456d96d43b3"  # Replace with a valid key
    url = f"https://serpapi.com/search?q={query}&api_key={api_key}"
    
    try:
        response = requests.get(url).json()
        results = response.get("organic_results", [])
        
        # Extract website links
        links = [res.get("link") for res in results if "link" in res]
        return links
    
    except Exception as e:
        print(f"❌ Error fetching search results: {e}")
        return []

# 2️⃣ Extract Emails & Phone Numbers from Websites
def extract_contact_info(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Improved regex for better phone & email detection
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}", soup.text)
        phones = re.findall(r"\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}", soup.text)

        return {"url": url, "email": ", ".join(set(emails)), "phone": ", ".join(set(phones))}
    
    except Exception as e:
        print(f"⚠️ Failed to fetch {url}: {e}")
        return {"url": url, "email": "N/A", "phone": "N/A"}

# 3️⃣ Save Leads to a CSV File
def save_to_csv(data, filename="leads.csv"):
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Write header if file does not exist
        if not file_exists:
            writer.writerow(["Website", "Email", "Phone"])
        
        # Write data
        for lead in data:
            writer.writerow([lead["url"], lead["email"], lead["phone"]])

# 4️⃣ Run the Lead Generator
def generate_leads(business_type, location, max_results=10):
    query = f"{business_type} companies in {location} contact details"
    websites = search_leads(query)
    
    # Process only the top `max_results`
    leads = [extract_contact_info(url) for url in websites[:max_results]]
    
    save_to_csv(leads)
    print(f"✅ {len(leads)} Leads saved to leads.csv")
    return leads

# Example Usage
if __name__ == "__main__":
    leads = generate_leads("software development", "New York", max_results=10)
    print(leads)
