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

# Set API key - with direct fallback option
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    # Try alternative environment variable names
    OPENAI_API_KEY = os.getenv("OPENAI_KEY")
    
# Force print for debugging
print(f"------------ CRITICAL DEBUG INFO ------------")
print(f"OpenAI API Key: {OPENAI_API_KEY[:5] + '...' if OPENAI_API_KEY else 'None'}")
print(f"OpenAI API Key length: {len(OPENAI_API_KEY) if OPENAI_API_KEY else 0}")
print(f"OpenAI API Key available: {bool(OPENAI_API_KEY)}")
print(f"-------------------------------------------")

# Initialize OpenAI - use a more direct approach
openai.api_key = OPENAI_API_KEY
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
4. Hebbal branch (North Bangalore)

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

# For debugging
def debug_log(message):
    """Print a debug message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG {timestamp}] {message}")

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
            
            debug_log(f"Received chat request. Message: '{message[:30]}...', User: {user_id}, Session: {session_id}")
            
            # EMERGENCY FALLBACK - Respond directly if OpenAI is not available
            if not OPENAI_API_KEY:
                debug_log("⚠️ EMERGENCY MODE: OpenAI API key not found - using hardcoded responses")
                
                # Basic keyword matching for emergency responses
                message_lower = message.lower()
                
                # Simple responses based on common queries
                if any(word in message_lower for word in ['location', 'where', 'address', 'branch', 'center']):
                    response = "We have four locations in Bangalore: Cunningham Road (Central Bangalore), Arekere (South Bangalore), Hulimavu (South Bangalore), and Hebbal (North Bangalore). Which location would be most convenient for you?"
                elif any(word in message_lower for word in ['price', 'cost', 'fee', 'pricing', 'rate', 'charges']):
                    response = "Our pricing varies based on your specific requirements and the location you choose. I'd be happy to connect you with our team for a personalized quote. Could you tell me which of our services you're most interested in?"
                elif any(word in message_lower for word in ['contact', 'phone', 'call', 'email', 'reach']):
                    response = "You can reach our team at 9119739119 or email us at connect@anthilliq.com. Would you like me to arrange for someone to contact you directly?"
                elif any(word in message_lower for word in ['service', 'offer', 'workspace', 'amenities']):
                    response = "We offer private offices, coworking spaces, dedicated desks, meeting rooms, event spaces, and training rooms. All our locations have high-speed internet, ergonomic furniture, 24/7 security, refreshments, and printing services. What type of workspace are you looking for?"
                elif 'hello' in message_lower or 'hi' in message_lower.split() or 'hey' in message_lower:
                    response = "Hello there! Welcome to Anthill IQ - Bangalore's premium coworking space. How can I assist you today?"
                else:
                    response = "Thank you for reaching out to Anthill IQ. We offer premium workspace solutions across Bangalore. Could you please let me know what you're looking for so I can better assist you?"
                
                result = {
                    "response": response,
                    "source": "fallback",
                    "session_id": session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                }
                
                self._send_json_response(200, result)
                return
            
            # Process the chat message with OpenAI
            debug_log(f"Sending message to OpenAI: {message[:50]}...")
            try:
                # Ensure API key is set for this request
                openai.api_key = OPENAI_API_KEY
                
                # NEW: Simplified direct API request using the legacy client
                debug_log("Using legacy OpenAI client (v0.28.1)")
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": SYSTEM_MESSAGE},
                        {"role": "user", "content": message}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                
                debug_log("OpenAI response received successfully")
                bot_response = response.choices[0].message.content
                debug_log(f"Bot response (first 50 chars): {bot_response[:50]}...")
                
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
                error_detail = str(e)
                debug_log(f"Error from OpenAI API: {error_detail}")
                self._send_json_response(500, {
                    "response": f"I'm sorry, there was an error processing your message. Error: {error_detail}",
                    "source": "error",
                    "session_id": session_id or "new_session"
                })
                return
            
        except Exception as e:
            error_detail = str(e)
            debug_log(f"General error in _handle_chat: {error_detail}")
            self._send_json_response(500, {"error": error_detail})
            
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