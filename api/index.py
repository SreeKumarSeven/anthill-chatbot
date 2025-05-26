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
SYSTEM_MESSAGE = """You are the Anthill IQ Assistant, helping users with information about our coworking spaces in Bangalore.

Key Information:
1. We have four locations:
   - Cunningham Road (Central Bangalore)
     1st Floor, Anthill IQ, 20, Cunningham Rd, Vasanth Nagar, Bengaluru, Karnataka 560052
   - Hulimavu (South Bangalore)
     75/B Windsor F4, Bannerghatta Rd, opp. Christ University, Hulimavu, Bengaluru, Karnataka 560076
   - Arekere (South Bangalore)
     224, Bannerghatta Rd, near Arekere Gate, Arekere, Bengaluru, Karnataka 560076
   - Hebbal (North Bangalore)
     AnthillIQ Workspaces, 44/2A, Kodigehalli gate, Sahakarnagar post, Hebbal, Bengaluru, Karnataka 560092

2. All locations are fully operational and offer:
   - Private Offices
   - Dedicated Desks
   - Coworking Spaces
   - Meeting Rooms
   - Event Spaces

3. Our services are available at all locations:
   - 24/7 Access
   - High-speed Internet
   - Meeting Room Credits
   - Printing & Scanning
   - Mail & Package Handling
   - Housekeeping
   - Unlimited Tea/Coffee

4. For pricing and availability:
   - Varies by location and service type
   - Customized packages available
   - Contact us for current offers

Guidelines:
1. Be friendly and professional
2. All locations are fully operational
3. Encourage visitors to schedule tours
4. Provide location-specific details when asked
5. Direct pricing queries to our team
6. Highlight amenities and benefits
7. Focus on convenience and flexibility"""

LOCATIONS = """Anthill IQ has four locations in Bangalore:
1. Cunningham Road (Central Bangalore)
2. Hulimavu (South Bangalore)
3. Arekere (South Bangalore)
4. Hebbal (North Bangalore)"""

def get_location_response():
    return f"{LOCATIONS}\n\nAll our locations are fully operational and offer our complete range of services. Would you like to know more about any specific location?"

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

def fix_hebbal_references(text):
    """
    Post-process text to ensure Hebbal is described as open, not upcoming
    This is a safety measure in case the AI still mentions Hebbal as 'opening soon'
    """
    if not text:
        return text
        
    # First check if this is a location-related response
    location_keywords = ['location', 'where', 'branch', 'branches', 'center', 'centers', 'office', 'offices']
    is_location_response = any(keyword in text.lower() for keyword in location_keywords)
    
    # If it's a location response or mentions any of our locations, use the standardized response
    if is_location_response or any(loc in text.lower() for loc in ['cunningham', 'hulimavu', 'arekere', 'hebbal']):
        return """Anthill IQ has four locations in Bangalore:

1. Cunningham Road (Central Bangalore)
   1st Floor, Anthill IQ, 20, Cunningham Rd, Vasanth Nagar, Bengaluru, Karnataka 560052
2. Hulimavu (South Bangalore)
   75/B Windsor F4, Bannerghatta Rd, opp. Christ University, Hulimavu, Bengaluru, Karnataka 560076
3. Arekere (South Bangalore)
   224, Bannerghatta Rd, near Arekere Gate, Arekere, Bengaluru, Karnataka 560076
4. Hebbal (North Bangalore)
   AnthillIQ Workspaces, 44/2A, Kodigehalli gate, Sahakarnagar post, Hebbal, Bengaluru, Karnataka 560092

All our centers are open and offer the complete range of services including private offices, dedicated desks, coworking spaces, and meeting rooms. Would you like to know more about any specific location?"""
    
    return text

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
            
            # SPECIAL CASE: Direct handling for location queries
            message_lower = message.lower()
            location_keywords = ['location', 'where', 'branch', 'branches', 'centers', 'places', 'areas']
            if any(word in message_lower for word in location_keywords):
                location_response = get_location_response()
                
                result = {
                    "response": location_response,
                    "source": "direct_handler",
                    "session_id": session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                }
                
                self._send_json_response(200, result)
                return
            
            # SPECIAL CASE: Direct handling for Hebbal branch queries
            if 'hebbal' in message_lower:
                hebbal_response = "Our Hebbal branch is now fully operational in North Bangalore. This location offers all our services including private offices, dedicated desks, coworking spaces, and meeting rooms. The branch is ready for immediate bookings and tours. Would you like to know more about our services or schedule a visit to our Hebbal branch?"
                
                result = {
                    "response": hebbal_response,
                    "source": "direct_handler",
                    "session_id": session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                }
                
                self._send_json_response(200, result)
                return
            
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
                
                # Apply post-processing to fix any references to Hebbal
                response = fix_hebbal_references(response)
                
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
                
                # Post-process to fix any remaining Hebbal references
                bot_response = fix_hebbal_references(bot_response)
                
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