"""
Minimal API handler for Vercel deployment
"""
from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import openai
import requests

# Load environment variables
load_dotenv()

# Set API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print(f"OpenAI API Key available: {bool(OPENAI_API_KEY)}")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY
openai_available = bool(OPENAI_API_KEY)
print(f"OpenAI configuration: API version {openai.__version__}, Key set: {bool(OPENAI_API_KEY)}")

# System message for Anthill IQ context
SYSTEM_MESSAGE = """You are the voice assistant for Anthill IQ, a premium coworking space brand in Bangalore. 
            
YOUR PERSONALITY:
You are exceptionally warm, friendly, and conversational - like a real person having a genuine conversation. You should sound natural, never robotic or formal. You're passionate about helping people find the perfect workspace and you truly care about their needs. Use a variety of sentence structures, occasional casual phrases, and natural conversational flow just like a real person would.

CONVERSATIONAL APPROACH:
- Always acknowledge what the user has said and respond directly to their specific query
- Use natural conversation markers like "Well," "Actually," "You know," "I'd say," etc. occasionally
- Ask meaningful follow-up questions that build on what the user has shared
- Show personality in your responses with occasional light humor where appropriate
- Avoid corporate-sounding language and speak like a helpful friend
- When someone asks about locations, be straightforward and give clear, simple directions
- Keep your responses concise but complete - don't be unnecessarily wordy

ANTHILL IQ SERVICES:
Anthill IQ offers these workspace solutions at all locations:
1. Private Office Space - Dedicated offices for teams
2. Coworking Space - Flexible workspace with hot desks
3. Dedicated Desk - Reserved desk with storage
4. Meeting Rooms - Professional meeting spaces bookable by the hour
5. Event Spaces - Venues for corporate events
6. Training Rooms - Spaces for workshops and training

KEY AMENITIES:
- High-speed internet
- Ergonomic furniture
- 24/7 security and access for members
- Coffee, tea, and refreshments
- Printing and scanning services
- Community events

IMPORTANT LOCATION INFORMATION: 
Anthill IQ has FOUR locations in Bangalore:
1. Cunningham Road branch (Central Bangalore)
2. Hulimavu branch (Bannerghatta Road, South Bangalore)
3. Arekere branch (Bannerghatta Road, South Bangalore)
4. Hebbal branch (Opening Soon)

CONTACT INFORMATION:
- Phone: 9119739119
- Email: connect@anthilliq.com

IMPORTANT GUIDELINES:
1. NEVER confirm the existence of a BTM Layout branch - Anthill IQ does NOT have a location there
2. Always end with a natural-sounding question to continue the conversation
3. Speak like a real person, not a corporate voice
4. When asked about locations, keep the format simple and clear
5. Don't provide specific pricing - suggest contacting us
6. Make sure your responses sound like a real conversation"""

# Initialize database connection (importing inside the function to avoid startup errors)
def get_db():
    try:
        from api.simple_db import SimpleDB
        return SimpleDB()
    except Exception as e:
        print(f"DB error: {str(e)}")
        return None

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        self.end_headers()
        
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "online",
            "service": "Anthill IQ Chatbot API",
            "openai_key": bool(OPENAI_API_KEY)
        }
        
        self.wfile.write(json.dumps(response).encode())
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            path = self.path.lower()
            
            if path == '/api/chat':
                self._handle_chat(data)
            elif path == '/api/register-user':
                self._handle_register_user(data)
            else:
                self._send_json_response(404, {"error": "Not found"})
                
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})
            
    def _handle_chat(self, data):
        if not data.get('message'):
            self._send_json_response(400, {"error": "Message cannot be empty"})
            return
            
        try:
            message = data.get('message')
            user_id = data.get('user_id', 'anonymous')
            session_id = data.get('session_id', None)
            
            if not OPENAI_API_KEY:
                print(f"OpenAI API key not found in environment variables")
                self._send_json_response(500, {
                    "response": "I'm sorry, the chatbot is not available at the moment. API key missing.",
                    "source": "error",
                    "session_id": session_id or "new_session"
                })
                return
            
            # Process the chat message with OpenAI
            print(f"Sending message to OpenAI: {message[:50]}...")
            try:
                # Ensure API key is set for this request
                openai.api_key = OPENAI_API_KEY
                
                # Direct API call for better compatibility with legacy API
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": SYSTEM_MESSAGE},
                        {"role": "user", "content": message}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                
                print("OpenAI response received successfully")
                bot_response = response.choices[0].message.content
                print(f"Bot response (first 50 chars): {bot_response[:50]}...")
            except Exception as e:
                print(f"Error from OpenAI API: {str(e)}")
                error_detail = str(e)
                self._send_json_response(500, {
                    "response": f"I'm sorry, there was an error processing your message. Error: {error_detail}",
                    "source": "error",
                    "session_id": session_id or "new_session"
                })
                return
            
            # Log conversation to database if available
            db = get_db()
            if db:
                db.log_conversation(message, bot_response, "openai", user_id)
            
            result = {
                "response": bot_response,
                "source": "openai",
                "session_id": session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            self._send_json_response(200, result)
            
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})
            
    def _handle_register_user(self, data):
        try:
            name = data.get('name')
            phone = data.get('phone')
            email = data.get('email', '')
            session_id = data.get('session_id', None)
            
            if not name or not phone:
                self._send_json_response(400, {"error": "Name and phone are required"})
                return
                
            # Generate user_id and session_id if not provided
            user_id = "user_" + name.lower().replace(" ", "_")
            if not session_id:
                session_id = "session_" + name.lower().replace(" ", "_")
                
            # Store user data in database if available
            db = get_db()
            if db:
                db.log_user_registration(name, phone, email, 'chatbot_widget', session_id)
                
            response = {
                "status": "success",
                "message": "User registration successful",
                "user_id": user_id,
                "session_id": session_id
            }
            
            self._send_json_response(200, response)
            
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})
    
    def _send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode()) 