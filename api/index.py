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

About Anthill IQ:
Anthill IQ is Bangalore's premium coworking space provider, offering intelligent workspace solutions that foster productivity, creativity, and community. The name represents our core values:
- "Anthill": A collaborative and industrious community working together
- "IQ": Intelligence in workspace solutions and smart amenities

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

2. Our Services (available at all locations):
   - Private Offices: Dedicated spaces for teams
   - Dedicated Desks: Fixed workstations in shared environment
   - Coworking Spaces: Flexible hot desks
   - Meeting Rooms: Professional meeting spaces
   - Event Spaces: Venues for corporate events
   - Training Rooms: Equipped for workshops

3. Premium Amenities:
   - 24/7 Access
   - High-speed Internet
   - Meeting Room Credits
   - Printing & Scanning
   - Mail & Package Handling
   - Housekeeping
   - Unlimited Tea/Coffee
   - Community Events
   - Business Address Services

4. Pricing Overview:
   - Private Offices: From ₹12,000 per seat/month
   - Dedicated Desks: From ₹8,000 per seat/month
   - Coworking Space: From ₹6,000 per seat/month
   - Meeting Rooms: From ₹800 per hour
   - Day Pass: From ₹500 per day

Contact Information:
- Phone: 9119739119
- Email: connect@anthilliq.com
- Website: www.anthilliq.com

Guidelines for Responses:
1. Be friendly, professional, and enthusiastic
2. Provide specific, accurate information
3. Encourage workspace visits and tours
4. Highlight relevant amenities for each query
5. Mention nearby landmarks when discussing locations
6. Emphasize community and networking opportunities
7. Always offer to provide more specific information

Remember:
1. All locations are fully operational
2. Each location has its unique advantages
3. Flexible packages are available
4. Community is a key focus
5. We cater to individuals, startups, and enterprises"""

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

# Add specific handling for "what is Anthill IQ" queries
def is_about_anthill_query(message_lower):
    about_keywords = [
        'what is anthill',
        'what is anthill iq',
        'what does anthill',
        'tell me about anthill',
        'about anthill iq',
        'meaning of anthill',
        'who is anthill',
        'what anthill'
    ]
    return any(keyword in message_lower for keyword in about_keywords)

# Add identity query detection
def is_identity_query(message_lower):
    """Check if the message is asking about the chatbot's identity or Anthill IQ"""
    identity_patterns = [
        'who are you',
        'what are you',
        'are you a bot',
        'are you human',
        'are you ai',
        'what is anthill',
        'what is anthill iq',
        'tell me about anthill',
        'what does anthill mean',
        'meaning of anthill',
        'about anthill'
    ]
    return any(pattern in message_lower for pattern in identity_patterns)

def get_identity_response():
    """Get response for identity queries"""
    return """I am the Anthill IQ Assistant, your dedicated guide to our premium coworking spaces in Bangalore. 

Anthill IQ is Bangalore's premium coworking space provider, offering intelligent workspace solutions that foster productivity, creativity, and community. The name represents our core values:
- "Anthill": A collaborative and industrious community working together
- "IQ": Intelligence in workspace solutions and smart amenities

We provide premium workspace solutions including:
• Private Offices
• Dedicated Desks
• Coworking Spaces
• Meeting Rooms
• Event Spaces
• Training Rooms

Our spaces are designed to create an ecosystem where professionals, startups, and enterprises can thrive together. Would you like to know more about our services or locations?"""

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
            message_lower = message.lower()
            user_id = data.get('user_id', 'anonymous')
            session_id = data.get('session_id', None)
            
            debug_log(f"Received chat request. Message: '{message[:30]}...', User: {user_id}, Session: {session_id}")
            
            # Process all messages with OpenAI
            try:
                # Ensure API key is set for this request
                openai.api_key = OPENAI_API_KEY
                
                # Use OpenAI for all responses
                debug_log("Using OpenAI for response generation")
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