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
            locations_text = "Anthill IQ has locations at:\n\n"
            
            locations_text += "1. Cunningham Road (Central Bangalore)\n"
            locations_text += "2. Arekere (South Bangalore)\n"
            locations_text += "3. Hulimavu (South Bangalore)\n"
            locations_text += "4. Hebbal (North Bangalore)\n\n"
            
            locations_text += "You can select any of these locations when booking through our website or this chatbot."
            
            return locations_text
            
        # Format detailed location addresses - ONLY NAMES and ADDRESSES
        def format_detailed_addresses():
            locations_text = "Anthill IQ Workspace Locations:\n\n"
            
            locations_text += "1. Cunningham Road\n"
            locations_text += "1st Floor, Anthill IQ, 20, Cunningham Rd, Vasanth Nagar, Bengaluru, Karnataka 560052\n\n"
            
            locations_text += "2. Arekere\n"
            locations_text += "224, Bannerghatta Rd, near Arekere Gate, Arekere, Bengaluru, Karnataka 560076\n\n"
            
            locations_text += "3. Hulimavu\n"
            locations_text += "75/B Windsor F4, Bannerghatta Rd, opp. Christ University, Hulimavu, Bengaluru, Karnataka 560076\n\n"
            
            locations_text += "4. Hebbal (North Bangalore)\n"
            
            return locations_text
        
        # Check for BTM Layout mentions
        if "btm" in message_lower or "btm layout" in message_lower:
            return {
                "response": "Anthill IQ doesn't have a branch in BTM Layout. Our locations are:\n\n1. Cunningham Road (Central Bangalore)\n2. Arekere (South Bangalore)\n3. Hulimavu (South Bangalore)\n4. Hebbal (North Bangalore)\n\nWould you like to book a workspace at any of these locations?",
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
                "response": "Our Hebbal branch is now open in North Bangalore. This location offers all services including private offices, dedicated desks, coworking spaces, and meeting rooms. Would you like to know more about our services or book a tour?",
                "sources": []
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
                    "response": """Thank you for your interest in our pricing!

Our pricing varies based on location, service type, and duration. Each of our branches (Cunningham Road, Arekere, Hulimavu, and Hebbal) offers customized packages designed to meet your specific needs.

For detailed pricing information, please contact us directly:
• Phone: 9119739119
• Email: connect@anthilliq.com

Our team will be happy to provide you with current rates and help you find the perfect solution for your requirements. We often have special promotions and flexible packages available.

Would you like me to help you connect with our team for pricing details?""",
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

    async def get_gpt_response(self, message: str) -> str:
        """Get a response from OpenAI's API"""
        try:
            # Enhanced system message with more personality and conversation guidance
            system_message = """You are the Anthill IQ virtual assistant, designed to provide helpful, friendly, and detailed information about Anthill IQ's premium coworking spaces in Bangalore.

Your personality traits:
- Friendly and warm, like a helpful concierge
- Professional but conversational in tone
- Enthusiastic about Anthill IQ's offerings
- Knowledgeable about workspaces and coworking benefits
- Proactive in providing relevant information and asking follow-up questions

IMPORTANT INFORMATION:
- Anthill IQ has FOUR locations: Cunningham Road (Central Bangalore), Hulimavu (Bannerghatta Road), Arekere (Bannerghatta Road), and our branch in Hebbal
- We offer private offices, coworking spaces, dedicated desks, meeting rooms, event spaces, and virtual office services
- All locations feature high-speed internet, 24/7 security, professional meeting spaces, and community events
- Our contact: Phone: 9119739119, Email: connect@anthilliq.com

CONVERSATIONAL GUIDELINES:
1. Always acknowledge the user's question before answering
2. Be detailed but concise in your responses
3. Use a friendly, conversational tone with some personality
4. End responses with a related follow-up question to continue the conversation
5. Personalize responses when possible using information from the conversation
6. If you don't know something, admit it but offer to help in another way

RESPONSE FORMAT:
- Use natural paragraphs rather than bullet points when possible
- Include relevant emojis occasionally to add personality
- When mentioning locations, always specify which branch you're referring to
- Add follow-up questions at the end of your responses

Remember: you are having a conversation, not just providing information. Make the user feel valued and understood."""

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
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error in get_gpt_response: {str(e)}")
            return "I apologize, but I'm having trouble connecting to my knowledge base at the moment. Please try again later or contact us directly at 9119739119."

    async def handle_message(self, message, conversation_id=None, user_id=None):
        """Handle incoming message and generate appropriate response."""
        try:
            # Check if message is about a non-Anthill IQ topic
            non_anthill_keywords = ["wework", "bhive", "91springboard", "awfis", "cowrks", "innov8", "indiqube", "smartworks"]
            message_lower = message.lower()
            
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