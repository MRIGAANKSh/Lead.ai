require('dotenv').config();
const express = require('express');
const twilio = require('twilio');
const fetch = require('node-fetch');
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;

// Initialize Twilio client
const twilioClient = twilio(
    process.env.TWILIO_ACCOUNT_SID,
    process.env.TWILIO_AUTH_TOKEN
);

app.use(express.json());
app.use(express.static(path.join(__dirname)));

// Function to generate conversation script using Hugging Face
async function generateScript(task, userInput = '', conversationHistory = []) {
    try {
        const response = await fetch(
            "https://api-inference.huggingface.co/models/facebook/opt-350m",
            {
                headers: {
                    Authorization: `Bearer ${process.env.HUGGINGFACE_API_KEY}`,
                    "Content-Type": "application/json",
                },
                method: "POST",
                body: JSON.stringify({
                    inputs: `Create a natural, conversational response for: ${task}. Previous user input: ${userInput}. 
                    Conversation history: ${JSON.stringify(conversationHistory)}. 
                    The response should be engaging, interactive, and maintain context.`,
                    parameters: {
                        max_length: 200,
                        temperature: 0.8,
                        return_full_text: false
                    }
                }),
            }
        );
        const result = await response.json();
        
        if (Array.isArray(result) && result.length > 0) {
            return result[0].generated_text || `I understand. Could you tell me more about that?`;
        }
        
        return `I understand. Could you tell me more about that?`;
    } catch (error) {
        console.error('Error generating script:', error);
        return `I understand. Could you tell me more about that?`;
    }
}

// Function to create interactive TwiML response
async function createInteractiveResponse(script, task, conversationHistory = []) {
    const twiml = new twilio.twiml.VoiceResponse();
    
    // Speak the response with enhanced voice settings
    twiml.say({
        voice: 'Polly.Amy',
        language: 'en-US',
        ssml: `<speak>
            <prosody rate="medium" pitch="medium">
                ${script}
            </prosody>
            <break time="1s"/>
            <prosody rate="medium" pitch="medium">
                How can I help you with that?
            </prosody>
        </speak>`
    });
    
    // Gather user input with enhanced settings
    const gather = twiml.gather({
        input: 'speech',
        speechTimeout: 'auto',
        action: '/api/handle-response',
        method: 'POST',
        language: 'en-US',
        enhanced: true,
        speechRecognition: {
            enhanced: true,
            profanityFilter: false
        }
    });
    
    // Add a fallback message if speech recognition fails
    gather.say({ 
        voice: 'Polly.Amy',
        ssml: `<speak>
            <prosody rate="slow" pitch="medium">
                I didn't catch that. Could you please repeat?
            </prosody>
        </speak>`
    });
    
    return twiml;
}

// Store conversation history (in a real app, use a database)
const conversationHistory = new Map();

// API endpoint to initiate a call
app.post('/api/initiate-call', async (req, res) => {
    try {
        const { phoneNumber, task } = req.body;
        
        // Initialize conversation history for this call
        conversationHistory.set(phoneNumber, []);

        // Generate initial conversation script
        const script = await generateScript(task, '', []);

        // Create TwiML response with interactive gathering
        const twiml = await createInteractiveResponse(script, task, []);

        // Make the call using Twilio
        await twilioClient.calls.create({
            to: phoneNumber,
            from: process.env.TWILIO_PHONE_NUMBER,
            twiml: twiml.toString()
        });

        res.json({ success: true, message: 'Call initiated successfully' });
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ success: false, message: error.message });
    }
});

// Handle user responses
app.post('/api/handle-response', async (req, res) => {
    try {
        const userInput = req.body.SpeechResult;
        const task = req.body.task || 'general conversation';
        const callSid = req.body.CallSid;
        
        // Get conversation history for this call
        const history = conversationHistory.get(callSid) || [];
        history.push({ role: 'user', content: userInput });
        
        // Generate response based on user input and history
        const script = await generateScript(task, userInput, history);
        history.push({ role: 'assistant', content: script });
        
        // Update conversation history
        conversationHistory.set(callSid, history);
        
        // Create new interactive response
        const twiml = await createInteractiveResponse(script, task, history);
        
        res.type('text/xml');
        res.send(twiml.toString());
    } catch (error) {
        console.error('Error handling response:', error);
        const twiml = new twilio.twiml.VoiceResponse();
        twiml.say({ 
            voice: 'Polly.Amy',
            ssml: `<speak>
                <prosody rate="slow" pitch="medium">
                    I apologize, but I encountered an error. Let's try again.
                </prosody>
            </speak>`
        });
        res.type('text/xml');
        res.send(twiml.toString());
    }
});

// Webhook endpoint for call status updates
app.post('/api/call-status', (req, res) => {
    const callStatus = req.body.CallStatus;
    const callSid = req.body.CallSid;
    
    if (callStatus === 'completed' || callStatus === 'failed') {
        // Clean up conversation history
        conversationHistory.delete(callSid);
    }
    
    console.log(`Call status: ${callStatus}`);
    res.sendStatus(200);
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
}); 