"""
Test endpoint for OpenAI integration
"""
from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print(f"Test endpoint: OpenAI API Key available: {bool(OPENAI_API_KEY)}")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

def debug_log(message):
    """Print a debug message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG TEST {timestamp}] {message}")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request with a simple test of OpenAI"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            debug_log("Testing OpenAI connection")
            
            if not OPENAI_API_KEY:
                debug_log("OpenAI API key not found")
                response = {
                    "status": "error",
                    "message": "OpenAI API key not found in environment variables",
                    "api_version": openai.__version__
                }
            else:
                # Test completion
                debug_log("Sending test request to OpenAI")
                test_completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a test assistant."},
                        {"role": "user", "content": "Say 'OpenAI is working correctly!'"}
                    ],
                    max_tokens=20
                )
                
                debug_log("OpenAI test response received")
                test_response = test_completion.choices[0].message.content
                
                response = {
                    "status": "success",
                    "message": "OpenAI API is working correctly",
                    "api_version": openai.__version__,
                    "test_response": test_response
                }
                
        except Exception as e:
            debug_log(f"Error testing OpenAI: {str(e)}")
            response = {
                "status": "error",
                "message": f"Error: {str(e)}",
                "api_version": openai.__version__
            }
            
        self.wfile.write(json.dumps(response).encode()) 