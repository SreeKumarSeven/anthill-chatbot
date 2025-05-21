from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        # Allow CORS to handle local testing
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self._set_headers()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        path = self.path
        
        if path == '/api/chat':
            user_message = data.get('message', '')
            user_id = data.get('user_id', 'anonymous')
            session_id = data.get('session_id', 'session-123')
            
            print(f"Received message: {user_message}")
            
            # Check if it's a booking request
            booking_keywords = ['book', 'appointment', 'consultation', 'schedule', 'reserve', 'meeting',
                'day pass', 'talk to someone', 'speak with', 'meet']
            
            is_booking = any(keyword in user_message.lower() for keyword in booking_keywords)
            
            if is_booking:
                response = {
                    'response': "I can help you book a service at Anthill IQ! Please let me know what type of service you're interested in.",
                    'source': 'booking',
                    'user_id': user_id,
                    'session_id': session_id
                }
            else:
                # Generate hardcoded responses based on keywords in the message
                user_message_lower = user_message.lower()
                
                # Greeting responses
                if any(word in user_message_lower for word in ["hello", "hi", "hey", "welcome", "hii"]):
                    ai_response = "Hello! I'm the Anthill IQ Assistant. How can I help you today?"
                
                # About Anthill IQ
                elif any(phrase in user_message_lower for phrase in ["what is anthill", "about anthill", "tell me about anthill"]):
                    ai_response = "Anthill IQ is a coworking space located in BTM Layout, Bangalore. We offer various workspace solutions including day passes, dedicated desks, private cabins, meeting rooms, and virtual offices."
                
                # Location queries
                elif any(word in user_message_lower for word in ["location", "address", "where", "situated", "placed"]):
                    ai_response = "Anthill IQ is located at 1st Floor, Thor Signia, 1st Main Road, 1st Stage, BTM Layout, Bangalore - 560029."
                
                # Pricing queries
                elif any(word in user_message_lower for word in ["pricing", "cost", "rate", "how much", "price", "fees"]):
                    ai_response = "Our pricing is as follows: Day Pass (₹999/day), Dedicated Desk (₹15,000/month), Private Cabin (₹25,000/month), Meeting Room (₹1,000/hour), and Virtual Office (₹5,000/month)."
                
                # Amenities and services
                elif any(word in user_message_lower for word in ["amenities", "facilities", "services", "offer", "provide"]):
                    ai_response = "Anthill IQ offers a range of amenities including high-speed internet, meeting rooms, cafeteria, printing services, 24/7 access, security, housekeeping, and parking."
                
                # Hours of operation
                elif any(word in user_message_lower for word in ["hours", "timing", "when", "open", "close"]):
                    ai_response = "Our operating hours are Monday to Friday, 9:00 AM to 6:00 PM."
                
                # Contact information
                elif any(word in user_message_lower for word in ["contact", "phone", "email", "reach", "call"]):
                    ai_response = "You can contact us through our website at https://anthilliq.com or by visiting our location at 1st Floor, Thor Signia, 1st Main Road, 1st Stage, BTM Layout, Bangalore - 560029."
                
                # Coworking space information
                elif any(phrase in user_message_lower for phrase in ["coworking", "co-working", "shared workspace", "workspace"]):
                    ai_response = "Anthill IQ provides modern coworking spaces designed for productivity and networking. Our spaces include hot desks, dedicated desks, private cabins, and meeting rooms, all equipped with high-speed internet and essential amenities for professionals."
                
                # Specific service information
                elif "day pass" in user_message_lower:
                    ai_response = "Our Day Pass costs ₹999 per day. It gives you access to a hot desk, high-speed internet, and all common amenities for a full business day."
                
                elif "dedicated desk" in user_message_lower:
                    ai_response = "Our Dedicated Desk option costs ₹15,000 per month. You'll get your own permanent desk that no one else uses, access to all amenities, and 24/7 access to the facility."
                
                elif any(phrase in user_message_lower for phrase in ["private cabin", "office", "cabin"]):
                    ai_response = "Our Private Cabins are priced at ₹25,000 per month. These are enclosed office spaces that provide privacy while still allowing you to be part of the coworking community."
                
                elif any(phrase in user_message_lower for phrase in ["meeting room", "conference", "meeting"]):
                    ai_response = "Meeting Rooms can be booked at ₹1,000 per hour. They come equipped with presentation equipment and are perfect for client meetings or team discussions."
                
                elif "virtual office" in user_message_lower:
                    ai_response = "Our Virtual Office service costs ₹5,000 per month. It provides you with a professional business address without the need for physical office space."
                
                # Specific amenity information
                elif "parking" in user_message_lower:
                    ai_response = "Yes, we do provide parking facilities for our members."
                
                elif any(word in user_message_lower for word in ["internet", "wifi", "wi-fi", "connectivity"]):
                    ai_response = "We offer high-speed internet connectivity throughout our facilities to ensure you can work efficiently."
                
                elif any(word in user_message_lower for word in ["cafeteria", "food", "coffee", "eat", "snacks"]):
                    ai_response = "Yes, we have a cafeteria on-site where you can get refreshments and meals throughout the day."
                
                # Chatbot identification
                elif any(phrase in user_message_lower for phrase in ["how are you", "how do you do", "how's it going"]):
                    ai_response = "I'm doing well, thank you for asking! I'm here to help you learn more about Anthill IQ and our services. How can I assist you today?"
                
                elif any(phrase in user_message_lower for phrase in ["who are you", "what are you", "your name", "your purpose"]):
                    ai_response = "I'm the Anthill IQ Assistant. I can help you with information about our coworking spaces, pricing, amenities, and booking services. What would you like to know about our facilities?"
                
                # Thank you responses
                elif any(word in user_message_lower for word in ["thank", "thanks", "appreciate"]):
                    ai_response = "You're welcome! If you have any other questions about Anthill IQ, please don't hesitate to ask. I'm here to help!"
                
                # Default response
                else:
                    ai_response = "I'm the Anthill IQ Assistant. I can help you with information about our coworking spaces, pricing, amenities, and booking services. What would you like to know about our facilities?"
                
                response = {
                    'response': ai_response,
                    'source': 'simulated-model',
                    'user_id': user_id,
                    'session_id': session_id
                }
            
            self._set_headers()
            self.wfile.write(json.dumps(response).encode())
            
        elif path == '/api/booking':
            name = data.get('name', '')
            email = data.get('email', '')
            phone = data.get('phone', '')
            service = data.get('service', 'Consultation')
            message = data.get('message', '')
            
            print(f"Booking request received from {name} ({email}) for {service}")
            
            response = {
                'success': True,
                'message': f'Booking request for {service} has been received and will be processed shortly.'
            }
            
            self._set_headers()
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())

def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f'Starting simple proxy server on port {port}...')
    print('Using hardcoded responses instead of OpenAI API')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server() 