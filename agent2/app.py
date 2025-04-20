from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
import os
import json
from typing import Dict, List
import uvicorn

# Load environment variables
load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Twilio client
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

# Initialize OpenAI
llm = ChatOpenAI(
    temperature=0.7,
    model="gpt-4",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Store conversation memories
conversation_memories: Dict[str, ConversationBufferMemory] = {}

def create_conversation_chain(call_sid: str) -> ConversationChain:
    """Create a new conversation chain with memory."""
    memory = ConversationBufferMemory()
    conversation_memories[call_sid] = memory
    
    chain = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )
    return chain

def generate_response(chain: ConversationChain, user_input: str, task: str) -> str:
    """Generate a response using the conversation chain."""
    prompt = f"""You are an AI assistant having a phone conversation. The task is: {task}
    Previous conversation context is maintained in memory.
    Current user input: {user_input}
    Respond naturally and conversationally, maintaining context and being engaging."""
    
    response = chain.predict(input=prompt)
    return response

def create_twiml_response(text: str, task: str, call_sid: str) -> str:
    """Create a TwiML response with enhanced voice settings."""
    response = VoiceResponse()
    
    # Add SSML for more natural speech
    ssml = f"""
    <speak>
        <prosody rate="medium" pitch="medium">
            {text}
        </prosody>
        <break time="1s"/>
        <prosody rate="medium" pitch="medium">
            How can I help you with that?
        </prosody>
    </speak>
    """
    
    response.say(ssml, voice='Polly.Amy', language='en-US')
    
    # Gather user input with enhanced settings
    gather = Gather(
        input='speech',
        speech_timeout='auto',
        action='/api/handle-response',
        method='POST',
        language='en-US',
        enhanced=True
    )
    
    # Add fallback message
    gather.say(
        "I didn't catch that. Could you please repeat?",
        voice='Polly.Amy',
        language='en-US'
    )
    
    response.append(gather)
    return str(response)

@app.post("/api/initiate-call")
async def initiate_call(request: Request):
    """Initiate a new call with the AI agent."""
    try:
        data = await request.json()
        phone_number = data.get("phoneNumber")
        task = data.get("task")
        
        if not phone_number or not task:
            return JSONResponse(
                status_code=400,
                content={"error": "Phone number and task are required"}
            )
        
        # Create initial response
        chain = create_conversation_chain(phone_number)
        initial_response = generate_response(chain, "", task)
        
        # Create TwiML response
        twiml = create_twiml_response(initial_response, task, phone_number)
        
        # Make the call
        call = twilio_client.calls.create(
            to=phone_number,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            twiml=twiml
        )
        
        return JSONResponse(
            content={"success": True, "message": "Call initiated successfully"}
        )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.post("/api/handle-response")
async def handle_response(request: Request):
    """Handle user responses during the call."""
    try:
        form_data = await request.form()
        user_input = form_data.get("SpeechResult", "")
        call_sid = form_data.get("CallSid")
        task = form_data.get("task", "general conversation")
        
        if not call_sid:
            raise ValueError("CallSid is required")
        
        # Get or create conversation chain
        chain = create_conversation_chain(call_sid)
        
        # Generate response
        response_text = generate_response(chain, user_input, task)
        
        # Create TwiML response
        twiml = create_twiml_response(response_text, task, call_sid)
        
        return Response(
            content=twiml,
            media_type="application/xml"
        )
    
    except Exception as e:
        error_response = VoiceResponse()
        error_response.say(
            "I apologize, but I encountered an error. Let's try again.",
            voice='Polly.Amy',
            language='en-US'
        )
        return Response(
            content=str(error_response),
            media_type="application/xml"
        )

@app.post("/api/call-status")
async def call_status(request: Request):
    """Handle call status updates."""
    try:
        form_data = await request.form()
        call_status = form_data.get("CallStatus")
        call_sid = form_data.get("CallSid")
        
        if call_status in ["completed", "failed"] and call_sid:
            # Clean up conversation memory
            conversation_memories.pop(call_sid, None)
        
        return Response(status_code=200)
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 