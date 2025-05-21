from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import parse_qs

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import service account handler
from api.service_account_handler import load_service_account

# Load service account credentials
load_service_account()

# Import backend modules
try:
    from api.backend_for_vercel.chat import ChatManager
    from api.backend_for_vercel.booking import BookingHandler
    from api.backend_for_vercel.sheets_manager import GoogleSheetsManager
    
    # Initialize managers
    chat_manager = ChatManager()
    booking_handler = BookingHandler()
    sheets_manager = GoogleSheetsManager()
    backend_loaded = True
except Exception as e:
    print(f"Error loading backend modules: {str(e)}")
    backend_loaded = False

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
            "backend_loaded": backend_loaded,
            "env_vars": {
                "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
                "google_sheet_id_set": bool(os.getenv("GOOGLE_SHEET_ID")),
                "google_service_account_set": bool(os.getenv("GOOGLE_SERVICE_ACCOUNT"))
            }
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
            
            if not backend_loaded:
                self._send_json_response(500, {
                    "response": "I'm sorry, the chatbot backend is not available at the moment.",
                    "source": "error",
                    "session_id": session_id or "new_session"
                })
                return
            
            # Process the chat message
            result = chat_manager.handle_message_sync(message, user_id)
            
            response = {
                "response": result["response"],
                "source": result.get("source", "chatbot"),
                "session_id": session_id or "new_session"
            }
            
            # Include should_start_booking if present
            if "should_start_booking" in result:
                response["should_start_booking"] = result["should_start_booking"]
                
            self._send_json_response(200, response)
            
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})
            
    def _handle_register_user(self, data):
        try:
            name = data.get('name')
            phone = data.get('phone')
            session_id = data.get('session_id', None)
            
            if not name or not phone:
                self._send_json_response(400, {"error": "Name and phone are required"})
                return
                
            response = {
                "status": "success",
                "message": "User registration successful",
                "user_id": "user_" + name.lower().replace(" ", "_"),
                "session_id": session_id or "session_" + name.lower().replace(" ", "_")
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