import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Replace with your actual VAPI API Key
VAPI_API_KEY = "b101e8c4-f9e3-4474-b395-f6216d319b64"

class CallRequest(BaseModel):
    phone: str
    name: str = ""  # Optional name field
    context: str

def call_lead(phone: str, name: str, context: str):
    url = "https://api.vapi.ai/call"
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "customer": {
            "number": phone,
            "name": name,
            "extension": ""
        },
        "assistant": {},
        "phoneNumberId": "e5e1a57c-052c-4ccd-9f03-3a55ce2232df"  # Your VAPI phone number ID
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"VAPI API Error: {str(e)}")

@app.post("/call-lead/")
async def call_lead_api(request: CallRequest):
    try:
        result = call_lead(request.phone, request.name, request.context)
        return {
            "status": "Call initiated",
            "data": result
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
