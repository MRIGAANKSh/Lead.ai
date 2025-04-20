import requests
from tabulate import tabulate

api_key = 
query = "software companies in New York"
url = f"https://serpapi.com/search?q={query}&api_key={api_key}"
response = requests.get(url).json()

# Extract relevant information from the response
organic_results = response.get('organic_results', [])
table_data = []

for result in organic_results:
    title = result.get('title', 'N/A')
    link = result.get('link', 'N/A')
    snippet = result.get('snippet', 'N/A')
    table_data.append([title, link, snippet])

# Create and display the table
headers = ['Company Name', 'Website', 'Description']
print("\nSoftware Companies in New York:")
print(tabulate(table_data, headers=headers, tablefmt='grid', showindex=False))
