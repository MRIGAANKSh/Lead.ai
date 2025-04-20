from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Replace with your Clay API Key
CLAY_API_KEY = "59e7adc2120e2f217a23"
CLAY_API_BASE_URL = "https://api.clay.run/v1/leads"

def get_hotel_emails(location="Ghaziabad, India", limit=10):
    """
    Fetch hotel emails from Clay AI for a specific location.
    """
    headers = {
        "Authorization": f"Bearer {CLAY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": f"hotels in {location}",
        "limit": limit
    }

    try:
        response = requests.post(
            CLAY_API_BASE_URL, json=payload, headers=headers, timeout=30
        )
        
        # Check if request was successful
        if response.status_code != 200:
            return {"error": f"API returned {response.status_code}: {response.text}"}

        data = response.json()
        return data.get("results", [])

    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

@app.route("/test-hotels", methods=["GET"])
def test_hotels():
    """
    Test endpoint to fetch hotel emails in Ghaziabad.
    """
    location = request.args.get("location", "Ghaziabad, India")  # Allow user input
    leads = get_hotel_emails(location)

    if "error" in leads:
        return jsonify({"success": False, "error": leads["error"]}), 500

    hotels = [
        {
            "name": lead.get("name", "N/A"),
            "email": lead.get("email", "N/A"),
            "phone": lead.get("phone", "N/A"),
            "website": lead.get("website", "N/A"),
            "address": lead.get("address", "N/A"),
            "rating": lead.get("rating", "N/A"),
        }
        for lead in leads
    ]

    return jsonify({"success": True, "count": len(hotels), "hotels": hotels})

if __name__ == "__main__":
    app.run(debug=True)
