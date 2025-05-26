from openai import OpenAI
import os
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
from backend.fine_tuning import FineTuningManager
from .sheets_manager import GoogleSheetsManager
import re
import logging

# Load environment variables from .env file
load_dotenv()

LOCATIONS = """Anthill IQ has four locations in Bangalore:
1. Cunningham Road (Central Bangalore)
2. Hulimavu (South Bangalore)
3. Arekere (South Bangalore)
4. Hebbal (North Bangalore)"""

LOCATIONS_DETAILED = """Here are our locations in Bangalore:
1. Cunningham Road
   1st Floor, Anthill IQ, 20, Cunningham Rd, Vasanth Nagar, Bengaluru, Karnataka 560052
2. Hulimavu
   75/B Windsor F4, Bannerghatta Rd, opp. Christ University, Hulimavu, Bengaluru, Karnataka 560076
3. Arekere
   224, Bannerghatta Rd, near Arekere Gate, Arekere, Bengaluru, Karnataka 560076
4. Hebbal
   AnthillIQ Workspaces, 44/2A, Kodigehalli gate, Sahakarnagar post, Hebbal, Bengaluru, Karnataka 560092"""

LOCATIONS_WITH_DETAILS = """Anthill IQ has four locations in Bangalore:
1. Cunningham Road (Central Bangalore)
   1st Floor, Anthill IQ, 20, Cunningham Rd, Vasanth Nagar, Bengaluru, Karnataka 560052
2. Hulimavu (South Bangalore)
   75/B Windsor F4, Bannerghatta Rd, opp. Christ University, Hulimavu, Bengaluru, Karnataka 560076
3. Arekere (South Bangalore)
   224, Bannerghatta Rd, near Arekere Gate, Arekere, Bengaluru, Karnataka 560076
4. Hebbal (North Bangalore)
   AnthillIQ Workspaces, 44/2A, Kodigehalli gate, Sahakarnagar post, Hebbal, Bengaluru, Karnataka 560092"""

class ChatManager:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set. Please check your .env file.")
        
        # Fix for Heroku compatibility - simplified initialization
        try:
            self.client = OpenAI(api_key=openai_api_key)
        except Exception as e:
            print(f"Error initializing OpenAI client: {str(e)}")
            # Fallback to basic initialization without extra parameters
            self.client = OpenAI(api_key=openai_api_key)
        
        self.sheets_manager = GoogleSheetsManager()
        self.fine_tuning_manager = FineTuningManager()
        self.booking_states = {}  # Store booking states for different users

    def log_conversation(self, user_message: str, bot_response: str, source: str, user_id: Optional[str] = None):
        """Log the conversation to Google Sheets"""
        try:
            self.sheets_manager.log_conversation(
                user_message=user_message,
                bot_response=bot_response,
                source=source,
                user_id=user_id
            )
        except Exception as e:
            print(f"Error logging conversation: {str(e)}")

    def is_booking_request(self, message: str) -> bool:
        """Check if the message is a booking request"""
        # More precise booking keywords
        booking_keywords = [
            'book', 'reserve', 'schedule', 'appointment',
            'want to reserve', 'need to book', 'like to schedule',
            'book a desk', 'book an office', 'book a meeting room',
            'book a meeting', 'book a coworking space',
            'reserve a space', 'plan an event', 'day pass'
        ]
        
        message_lower = message.lower()
        
        # Check for explicit booking intentions
        for keyword in booking_keywords:
            if keyword in message_lower:
                # Make sure they're not just asking what they can book
                if "what" in message_lower and "can" in message_lower:
                    continue
                if "what services" in message_lower:
                    continue
                if "services" in message_lower and "provide" in message_lower:
                    continue
                if "tell me about" in message_lower or "list of" in message_lower:
                    continue
                    
                return True
                
        return False

    def extract_booking_info(self, message: str) -> Dict:
        """Extract booking information from the message"""
        # Extract email if present
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email = re.search(email_pattern, message)
        email = email.group(0) if email else None

        # Extract phone if present
        phone_pattern = r'\+?[\d\s-]{10,}'
        phone = re.search(phone_pattern, message)
        phone = phone.group(0) if phone else None

        # Extract name if present (assuming it's before the email or phone)
        name = None
        if email:
            name = message.split(email)[0].strip()
        elif phone:
            name = message.split(phone)[0].strip()

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "service": "Day Pass" if "day pass" in message.lower() else "Membership",
            "message": message
        }
        
    def preprocess_location_query(self, message: str) -> Optional[Dict]:
        """
        Preprocess location-related queries to ensure correct information
        
        This function detects and handles queries about Anthill IQ's locations
        to ensure accurate information, especially about BTM Layout.
        
        Args:
            message: The user's message
            
        Returns:
            A response dict if location query is detected, None otherwise
        """
        message_lower = message.lower()
        
        # Format simple location list - NO directions
        def format_simple_locations():
            return LOCATIONS_WITH_DETAILS
            
        # Format detailed location addresses - ONLY NAMES and ADDRESSES
        def format_detailed_addresses():
            return LOCATIONS_DETAILED
        
        # Check for BTM Layout mentions
        if "btm" in message_lower or "btm layout" in message_lower:
            return {
                "response": """Anthill IQ doesn't have a branch in BTM Layout. Our fully operational locations are:

1. Cunningham Road (Central Bangalore)
2. Arekere (South Bangalore)
3. Hulimavu (South Bangalore)
4. Hebbal (North Bangalore)

All our centers are open and ready to serve you. Would you like to know more about any of these locations?""",
                "source": "location_correction",
                "confidence": 1.0
            }
            
        # Check for address-specific queries
        address_queries = [
            "address", "location address", "office address", "full address", 
            "where exactly", "directions to", "how to reach", "where is",
            "get address", "need address", "reach there", "where are you"
        ]
        
        if any(query in message_lower for query in address_queries):
            return {
                "response": format_detailed_addresses(),
                "source": "location_addresses",
                "confidence": 1.0
            }
        
        # Check for general location queries
        location_queries = [
            "where are you located", 
            "your location", 
            "where is your office",
            "where is anthill",
            "branch",
            "location",
            "locations",
            "branches",
            "centers"
        ]
        
        if any(query in message_lower for query in location_queries) or (
            "where" in message_lower and "located" in message_lower):
            return {
                "response": format_simple_locations(),
                "source": "location_info",
                "confidence": 1.0
            }
        
        # Check for specific location queries (Cunningham Road)
        if "cunningham" in message_lower:
            return {
                "response": "Our Cunningham Road branch is located at:\n\n1st Floor, Anthill IQ, 20, Cunningham Rd, Vasanth Nagar, Bengaluru, Karnataka 560052\n\nThis is one of our premium locations with all services available including private offices, dedicated desks, coworking spaces, and meeting rooms.",
                "source": "specific_location",
                "confidence": 1.0
            }
            
        # Check for specific location queries (Arekere)
        if "arekere" in message_lower:
            return {
                "response": "Our Arekere branch is located at:\n\n224, Bannerghatta Rd, near Arekere Gate, Arekere, Bengaluru, Karnataka 560076\n\nThis location offers all our services including private offices, dedicated desks, coworking spaces, and meeting rooms.",
                "source": "specific_location",
                "confidence": 1.0
            }
            
        # Check for specific location queries (Hulimavu)
        if "hulimavu" in message_lower:
            return {
                "response": "Our Hulimavu branch is located at:\n\n75/B Windsor F4, Bannerghatta Rd, opp. Christ University, Hulimavu, Bengaluru, Karnataka 560076\n\nThis location offers all our services including private offices, dedicated desks, coworking spaces, and meeting rooms.",
                "source": "specific_location",
                "confidence": 1.0
            }
            
        # Check for specific location queries (Hebbal)
        if "hebbal" in message_lower:
            return {
                "response": "Our Hebbal branch is now fully operational in North Bangalore. This location offers all our services including private offices, dedicated desks, coworking spaces, and meeting rooms. The branch is ready for immediate bookings and tours. Would you like to know more about our services or schedule a visit to our Hebbal branch?",
                "source": "specific_location",
                "confidence": 1.0
            }
            
        # Check for contact number queries
        if "contact" in message_lower or "number" in message_lower or "phone" in message_lower:
            return {
                "response": "You can reach Anthill IQ through the following contact information:\n\n• Phone: 9119739119\n• Email: connect@anthilliq.com\n• Website: www.anthilliq.com\n\nOur team is ready to assist you with any inquiries about our workspace solutions at our locations in Bangalore: Cunningham Road, Hulimavu, Arekere, and Hebbal.",
                "source": "contact_info",
                "confidence": 1.0
            }
            
        return None

    def preprocess_service_inquiry(self, message: str) -> Optional[Dict]:
        """
        Handle inquiries about services offered by Anthill IQ
        
        Args:
            message: The user's message
            
        Returns:
            A response dict if service inquiry is detected, None otherwise
        """
        message_lower = message.lower()
        
        # List of service inquiry patterns
        service_queries = [
            "services", "what do you offer", "what does anthill offer",
            "what does anthill provide", "what can i book", "types of space",
            "facilities", "amenities", "what services", "workspace options",
            "what are the services", "services that anthill"
        ]
        
        # Check if the user is asking about services
        if any(query in message_lower for query in service_queries):
            return {
                "response": """Here are the services offered by Anthill IQ:

1. **Private Office Space**

   • Dedicated private offices for teams
   • 24/7 access
   • Fully furnished with high-speed internet

2. **Coworking Space**

   • Flexible shared workspace for professionals
   • Day pass and monthly membership options
   • Access to common amenities

3. **Dedicated Desk**

   • Reserved desk in a shared environment
   • 24/7 access with lockable storage
   • Business address services

4. **Meeting Rooms**

   • Professional spaces for client meetings and team discussions
   • Various sizes (4-seater to 10-seater)
   • Hourly and daily booking options

5. **Event Spaces**

   • Versatile venues for corporate events and workshops
   • Flexible seating arrangements
   • Evening and weekend availability

6. **Training Rooms**

   • Equipped spaces for workshops and training sessions
   • Projectors, screens and whiteboards
   • Half-day and full-day booking options

All our locations (Cunningham Road, Hulimavu, Arekere, and Hebbal) offer these services.

For pricing information, please contact us at 9119739119 or email connect@anthilliq.com.""",
                "source": "service_info",
                "confidence": 1.0
            }
            
        # Check for specific service inquiries
        if "private office" in message_lower or "office space" in message_lower:
            return {
                "response": """Our **Private Office Spaces** at Anthill IQ provide:

• Fully furnished private offices for teams
• 24/7 access
• High-speed internet
• Meeting room credits
• Office maintenance and cleaning
• Access to common areas and community events
• Flexible lease terms

Available at all our locations (Cunningham Road, Hulimavu, Arekere, and Hebbal).

For pricing and availability, please contact us at 9119739119.""",
                "source": "service_specific",
                "confidence": 1.0
            }
            
        if "coworking" in message_lower or "co-working" in message_lower or "shared workspace" in message_lower:
            return {
                "response": """Our Coworking Spaces at Anthill IQ provide:

• Flexible hot desks in a collaborative environment
• High-speed internet
• Tea and coffee facilities
• Access to meeting rooms (paid)
• Community networking events
• Day pass and monthly membership options
• Business address services (for members)

Available at all our locations (Cunningham Road, Hulimavu, Arekere, and Hebbal).

For pricing and current promotions, please contact us at 9119739119.""",
                "source": "service_specific",
                "confidence": 1.0
            }
            
        if "dedicated desk" in message_lower or "fixed desk" in message_lower:
            return {
                "response": """Our Dedicated Desk service at Anthill IQ provides:

• Your own permanent desk in a shared environment
• 24/7 access
• Lockable storage
• High-speed internet
• Meeting room credits
• Business address services
• Community membership benefits

Available at all our locations (Cunningham Road, Hulimavu, Arekere, and Hebbal).

For pricing and availability, please contact us at 9119739119.""",
                "source": "service_specific",
                "confidence": 1.0
            }
            
        if "meeting room" in message_lower or "conference room" in message_lower:
            return {
                "response": """Our Meeting Rooms at Anthill IQ provide:

• Professional, fully equipped spaces for client meetings and team discussions
• Various sizes (4-seater to 10-seater options)
• HD video conferencing equipment
• Whiteboards and presentation facilities
• High-speed internet
• Complimentary tea and coffee
• Hourly and daily booking options

Available at all our locations (Cunningham Road, Hulimavu, Arekere, and Hebbal).

For pricing and availability, please contact us at 9119739119.""",
                "source": "service_specific",
                "confidence": 1.0
            }
            
        if "event space" in message_lower or "event venue" in message_lower:
            return {
                "response": """Our Event Spaces at Anthill IQ provide:

• Versatile venues for corporate events, workshops, and networking sessions
• Flexible seating arrangements
• Audio-visual equipment
• High-speed internet
• Catering options available
• Event coordination assistance
• Evening and weekend availability

Available at all our locations (Cunningham Road, Hulimavu, Arekere, and Hebbal).

For pricing, capacity information, and availability, please contact us at 9119739119.""",
                "source": "service_specific",
                "confidence": 1.0
            }
            
        if "training room" in message_lower or "workshop space" in message_lower:
            return {
                "response": """Our Training Rooms at Anthill IQ provide:

• Specially designed spaces for workshops and training sessions
• Classroom-style or U-shaped seating options
• Projectors and screens
• Whiteboards and flip charts
• High-speed internet
• Refreshment options available
• Half-day and full-day booking options

Available at all our locations (Cunningham Road, Hulimavu, Arekere, and Hebbal).

For pricing, capacity information, and availability, please contact us at 9119739119.""",
                "source": "service_specific",
                "confidence": 1.0
            }
            
        return None

    def preprocess_pricing_query(self, message: str) -> Optional[Dict]:
        """
        Handle pricing inquiries about Anthill IQ services
        
        Args:
            message: The user's message
            
        Returns:
            A response dict if pricing inquiry is detected, None otherwise
        """
        message_lower = message.lower()
        
        # List of pricing inquiry patterns
        pricing_patterns = [
            "price", "pricing", "cost", "fee", "how much", "charges",
            "payment", "rate", "subscription", "package", "membership cost"
        ]
        
        # Check if the message is asking about pricing
        for pattern in pricing_patterns:
            if pattern in message_lower:
                # Pricing response
                return {
                    "response": get_pricing_response(),
                    "source": "pricing_info",
                    "confidence": 1.0
                }
                    
        return None

    def preprocess_social_media_query(self, message):
        """Check if the message is asking about social media, especially Instagram."""
        message_lower = message.lower()
        
        # Check for Instagram-related keywords
        instagram_keywords = ["instagram", "insta", "ig", "social media"]
        is_instagram_query = any(keyword in message_lower for keyword in instagram_keywords)
        
        if is_instagram_query:
            if "handle" in message_lower or "username" in message_lower or "account" in message_lower or "instagram" in message_lower:
                return {
                    "type": "social_media",
                    "platform": "instagram",
                    "response": "You can follow Anthill IQ on Instagram at @anthill_iq for updates, events, and community highlights!"
                }
            else:
                return {
                    "type": "social_media",
                    "platform": "general",
                    "response": "You can connect with Anthill IQ on various social media platforms. Our Instagram handle is @anthill_iq. We're also on LinkedIn and Facebook!"
                }
        
        return None

    def preprocess_identity_query(self, message: str) -> Optional[Dict]:
        """Handle queries about the chatbot's identity and Anthill IQ"""
        message_lower = message.lower()
        
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
        
        if any(pattern in message_lower for pattern in identity_patterns):
            return {
                "response": """I am the Anthill IQ Assistant, your dedicated guide to our premium coworking spaces in Bangalore. 

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

Our spaces are designed to create an ecosystem where professionals, startups, and enterprises can thrive together. Would you like to know more about our services or locations?""",
                "source": "identity_info",
                "confidence": 1.0
            }
        
        return None

    async def get_gpt_response(self, message: str) -> str:
        """Get a response from OpenAI's API"""
        try:
            # Enhanced system message with more personality and conversation guidance
            system_message = SYSTEM_MESSAGE

            # Get response from OpenAI with enhanced system message
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Post-process the response to ensure Hebbal is shown as open
            bot_response = response.choices[0].message.content
            
            # Fix any remaining references to Hebbal being upcoming
            hebbal_fixes = [
                ("upcoming branch in Hebbal", "branch in Hebbal"),
                ("opening soon in Hebbal", "now open in Hebbal"),
                ("new branch in Hebbal", "branch in Hebbal"),
                ("Hebbal (opening soon)", "Hebbal"),
                ("Hebbal branch (opening soon)", "Hebbal branch"),
                ("Hebbal branch is opening soon", "Hebbal branch is now open"),
                ("Hebbal branch will be opening soon", "Hebbal branch is now open"),
                ("set to open soon", "now open"),
                ("Hebbal soon", "Hebbal"),
                ("soon-to-open Hebbal", "Hebbal"),
                ("planning to open in Hebbal", "now open in Hebbal"),
                ("upcoming location in Hebbal", "location in Hebbal"),
                ("Hebbal location will soon be", "Hebbal location is now"),
                ("new Hebbal branch", "Hebbal branch"),
                ("Hebbal branch is not yet open", "Hebbal branch is now open"),
                ("Hebbal branch isn't open yet", "Hebbal branch is now open"),
                ("Hebbal branch is coming soon", "Hebbal branch is now open"),
                ("fourth branch in Hebbal", "branch in Hebbal"),
                ("4th branch in Hebbal", "branch in Hebbal"),
                ("Hebbal, which is not yet open", "Hebbal"),
                ("Hebbal which is not yet open", "Hebbal"),
                ("planning to launch in Hebbal", "now operating in Hebbal"),
                ("Hebbal (launching", "Hebbal"),
                ("excited about our Hebbal branch", "excited about our now open Hebbal branch"),
                ("excited about the Hebbal branch", "excited about our now open Hebbal branch"),
                ("Hebbal branch that will be", "Hebbal branch that is now"),
                ("Hebbal branch, which will be", "Hebbal branch, which is now"),
                ("we're really excited about", "we're really excited that it's now open. Would you like to know more about"),
                ("we're excited about", "we're excited that it's now open. Would you like to know more about")
            ]
            
            for old, new in hebbal_fixes:
                bot_response = bot_response.replace(old, new)
            
            return bot_response
            
        except Exception as e:
            print(f"Error in get_gpt_response: {str(e)}")
            return "I apologize, but I'm having trouble connecting to my knowledge base at the moment. Please try again later or contact us directly at 9119739119."

    async def handle_message(self, message, conversation_id=None, user_id=None):
        """Handle incoming message and generate appropriate response."""
        try:
            message_lower = message.lower()
            
            # Check identity queries first
            identity_info = self.preprocess_identity_query(message)
            if identity_info:
                self.log_conversation(message, identity_info["response"], identity_info["source"], user_id)
                return {
                    "response": identity_info["response"],
                    "conversation_id": conversation_id
                }
                
            # Check if message is about a non-Anthill IQ topic
            non_anthill_keywords = ["wework", "bhive", "91springboard", "awfis", "cowrks", "innov8", "indiqube", "smartworks"]
            if any(keyword in message_lower for keyword in non_anthill_keywords):
                return {
                    "response": "I'm specialized in providing information about Anthill IQ's coworking spaces and services. I don't have detailed information about other coworking providers.",
                    "conversation_id": conversation_id
                }
            
            # Check if message is a booking request
            is_booking = self.is_booking_request(message)
            if is_booking:
                booking_info = self.extract_booking_info(message)
                return {
                    "response": "I'd be happy to help you book a space at Anthill IQ! Please provide the following details:\n\n" +
                               "1. Your name\n2. Phone number\n3. Email address\n4. Preferred location (Cunningham Road, Arekere, Hulimavu, or Hebbal)\n" +
                               "5. Number of seats needed\n6. Date and time\n\nAlternatively, you can use our booking form for a smoother experience.",
                    "is_booking": True,
                    "booking_info": booking_info,
                    "conversation_id": conversation_id
                }
            
            # Check if message is a social media query
            social_media_response = self.preprocess_social_media_query(message)
            if social_media_response:
                return {
                    "response": social_media_response["response"],
                    "conversation_id": conversation_id
                }
            
            # Check if message is a location query
            location_info = self.preprocess_location_query(message)
            if location_info:
                self.log_conversation(message, location_info["response"], location_info["source"], user_id)
                return {
                    "response": location_info["response"],
                    "conversation_id": conversation_id
                }
            
            # Check if message is a service inquiry
            service_info = self.preprocess_service_inquiry(message)
            if service_info:
                self.log_conversation(message, service_info["response"], service_info["source"], user_id)
                return {
                    "response": service_info["response"],
                    "conversation_id": conversation_id
                }
            
            # Check if message is a pricing inquiry
            pricing_info = self.preprocess_pricing_query(message)
            if pricing_info:
                self.log_conversation(message, pricing_info["response"], pricing_info["source"], user_id)
                return {
                    "response": pricing_info["response"],
                    "conversation_id": conversation_id
                }
            
            # If no specific handler matched, use GPT response
            gpt_response = await self.get_gpt_response(message)
            
            # If GPT response indicates it doesn't know, add a note about specialization
            if "don't know" in gpt_response.lower() or "don't have" in gpt_response.lower() or "no information" in gpt_response.lower():
                gpt_response += "\n\nI specialize in providing information about Anthill IQ's coworking spaces, services, locations, and booking procedures. If you have any questions about these topics, I'd be happy to help!"
            
            self.log_conversation(message, gpt_response, "openai", user_id)
            
            return {
                "response": gpt_response,
                "conversation_id": conversation_id
            }
        except Exception as e:
            logging.error(f"Error handling message: {str(e)}")
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again or contact our support team.",
                "conversation_id": conversation_id
            }

    def handle_message_sync(self, message, user_id=None):
        """Synchronous version of handle_message for serverless functions"""
        try:
            # Basic intent classification
            if self._is_greeting(message):
                return {
                    "response": "Hello! I'm the Anthill IQ Assistant. How can I help you today?",
                    "source": "rule_based"
                }
            
            if self._is_booking_request(message):
                return {
                    "response": "I'd be happy to help you schedule a consultation. What would you like to discuss?",
                    "source": "rule_based",
                    "should_start_booking": True
                }
            
            # Call the AI model for more complex responses
            response = self._generate_response(message)
            
            # Check if the response suggests a booking
            if self._suggests_booking(response):
                return {
                    "response": response,
                    "source": "ai",
                    "should_start_booking": True
                }
            
            return {
                "response": response,
                "source": "ai"
            }
        except Exception as e:
            print(f"Error in chat handling: {str(e)}")
            return {
                "response": "I'm sorry, I'm having trouble processing your request. Please try again later.",
                "source": "error"
            }

def get_location_response(message_lower):
    """Handle location-specific queries"""
    if any(loc in message_lower for loc in ["cunningham", "hulimavu", "arekere"]):
        return {
            "response": "All our locations are fully operational and offer our complete range of services. Would you like to know more about our services or schedule a visit?",
            "context": "location"
        }

    return {
        "response": f"{LOCATIONS}\n\nAll our locations are fully operational and offer our complete range of services. Would you like to know more about any specific location?",
        "context": "location"
    }

SYSTEM_MESSAGE = """You are the Anthill IQ Assistant, helping users with information about our coworking spaces in Bangalore.

Key Information:
1. We have four locations:
   - Cunningham Road (Central Bangalore)
   - Hulimavu (South Bangalore)
   - Arekere (South Bangalore)
   - Hebbal (North Bangalore)

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
7. Focus on convenience and flexibility

Remember to:
1. Always be accurate about our locations
2. Encourage in-person visits
3. Highlight the benefits of each location
4. Mention our 24/7 access and amenities
5. Direct specific pricing questions to our team"""

def get_service_response(service_type):
    base_response = f"This service is available at all our locations (Cunningham Road, Hulimavu, and Arekere)."
    # ... rest of the function remains the same ...

def get_pricing_response():
    return "Our pricing varies based on location, service type, and duration. Each of our branches (Cunningham Road, Arekere, and Hulimavu) offers customized packages designed to meet your specific needs. Would you like to schedule a consultation to discuss pricing options for a specific location?"