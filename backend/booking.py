import csv
import os
from datetime import datetime
from typing import Dict, Optional
from .sheets_manager import GoogleSheetsManager
import re
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

router = APIRouter()
sheets_manager = GoogleSheetsManager()

class BookingRequest(BaseModel):
    """Model for booking requests"""
    name: str
    email: str = Field(..., description="Email address of the requester")
    phone: str
    service: str
    location: str
    seats: str = Field("1", description="Number of seats requested")
    message: Optional[str] = None
    datetime: Optional[str] = None
    status: Optional[str] = "Pending"
    source: Optional[str] = "chatbot"
    notes: Optional[str] = None

@router.post("/booking")
async def create_booking(booking: BookingRequest):
    """
    Create a new booking request.
    
    This endpoint processes booking requests and logs them to Google Sheets.
    """
    try:
        # Prepare booking data for Google Sheets
        booking_data = {
            "name": booking.name,
            "email": booking.email,
            "phone": booking.phone,
            "service": booking.service,
            "location": booking.location,
            "seats": booking.seats,
            "message": booking.message,
            "datetime": booking.datetime,
            "status": booking.status,
            "notes": booking.notes,
            "source": booking.source
        }
        
        # Log to Google Sheets only, don't use BookingHandler to prevent duplication
        success = sheets_manager.log_booking(booking_data)
        
        if not success:
            print("Warning: Failed to log booking to Google Sheets")
        
        # Generate a unique booking ID using timestamp
        booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "status": "success",
            "message": "Booking request received successfully",
            "booking_id": booking_id
        }
    except Exception as e:
        print(f"Error processing booking: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing booking: {str(e)}"
        )

class BookingManager:
    def __init__(self):
        self.sheets_manager = GoogleSheetsManager()
        self.ensure_leads_file()  # Keep local file as fallback
        self.services = [
            "Business Strategy Consulting",
            "Digital Transformation",
            "Process Optimization",
            "Data Analytics",
            "Technology Implementation"
        ]

    def ensure_leads_file(self):
        """Ensure leads.csv exists with correct headers (fallback)"""
        try:
            if not os.path.exists("leads.csv"):
                with open("leads.csv", "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "timestamp",
                        "user_id",
                        "name",
                        "email",
                        "phone",
                        "requested_datetime"
                    ])
        except Exception as e:
            print(f"Error creating leads.csv: {str(e)}")

    def save_booking(self, booking_data: Dict) -> Dict:
        """Save booking details to Google Sheets and local CSV"""
        try:
            # First try Google Sheets
            sheets_success = self.sheets_manager.log_booking(booking_data)
            
            if sheets_success:
                print(f"Successfully saved booking to Google Sheets: {booking_data}")
                return {
                    "success": True,
                    "message": "Booking saved successfully",
                    "storage": "google_sheets"
                }
            
            # If Google Sheets fails, try local CSV
            self.ensure_leads_file()
            
            # Prepare data for CSV
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            csv_data = {
                "timestamp": timestamp,
                "name": booking_data.get("name", ""),
                "email": booking_data.get("email", ""),
                "phone": booking_data.get("phone", ""),
                "company": booking_data.get("company", ""),
                "service": booking_data.get("service", ""),
                "message": booking_data.get("message", ""),
                "status": "New"
            }
            
            # Save to CSV
            df = pd.DataFrame([csv_data])
            df.to_csv("leads.csv", mode="a", header=False, index=False)
            
            print(f"Successfully saved booking to local CSV: {booking_data}")
            return {
                "success": True,
                "message": "Booking saved to local storage",
                "storage": "local_csv"
            }
            
        except Exception as e:
            print(f"Error saving booking: {str(e)}")
            print(f"Booking data that failed: {booking_data}")
            return {
                "success": False,
                "message": f"Failed to save booking: {str(e)}",
                "error": str(e)
            }

class BookingHandler:
    def __init__(self):
        self.sheets_manager = GoogleSheetsManager()
        self.services = [
            "Private Office",
            "Dedicated Desk",
            "Coworking Space",
            "Meeting Room",
            "Event Space",
            "Training Room",
            "Day Pass",
            "Virtual Office"
        ]
    
    def extract_booking_info(self, message: str) -> Dict:
        """
        Extract booking information from a message.
        Returns a dictionary with extracted information.
        """
        booking_info = {
            "name": None,
            "email": None,
            "phone": None,
            "company": None,
            "service": None,
            "seats": "1",  # Default to 1 seat
            "preferred_location": None,
            "message": message
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, message)
        if email_match:
            booking_info["email"] = email_match.group(0)
        
        # Extract phone
        phone_pattern = r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        phone_match = re.search(phone_pattern, message)
        if phone_match:
            booking_info["phone"] = phone_match.group(0)
        
        # Try to identify the service
        message_lower = message.lower()
        for service in self.services:
            if service.lower() in message_lower:
                booking_info["service"] = service
                break
                
        # Try to identify the location
        locations = ["cunningham", "arekere", "hulimavu"]
        for location in locations:
            if location.lower() in message_lower:
                booking_info["preferred_location"] = location.capitalize()
                break
                
        # Try to extract number of seats
        seats_patterns = [
            r'(\d+)\s+(?:seat|seats)',  # "5 seats" or "1 seat"
            r'for\s+(\d+)\s+people',     # "for 4 people"
            r'(\d+)\s+person',           # "3 person"
            r'group\s+of\s+(\d+)'        # "group of 6"
        ]
        
        for pattern in seats_patterns:
            match = re.search(pattern, message_lower)
            if match:
                booking_info["seats"] = match.group(1)
                break
                
        return booking_info
    
    def handle_booking_request(self, message: str, user_id: Optional[str] = None) -> Dict:
        """
        Handle a booking request from a user.
        Extract information and save to Google Sheets.
        """
        try:
            # Check if it's a valid booking request
            if not self.is_booking_request(message):
                return {
                    "success": False,
                    "message": "This doesn't appear to be a booking request.",
                    "should_start_booking": True
                }
            
            # Extract booking information
            booking_info = self.extract_booking_info(message)
            
            # If we already have user information, prioritize it
            if user_id:
                try:
                    # Fetch recent conversations to find user info
                    conversations = self.sheets_manager.get_recent_conversations(100)
                    for convo in conversations:
                        if convo.get('user_id') == user_id:
                            # Try to find name, email, phone
                            if not booking_info['name'] and 'My name is' in convo.get('user_message', ''):
                                name_match = re.search(r'My name is\s+(.+)', convo.get('user_message', ''))
                                if name_match:
                                    booking_info['name'] = name_match.group(1).strip()
                            
                            if not booking_info['email'] and '@' in convo.get('user_message', ''):
                                email_match = re.search(email_pattern, convo.get('user_message', ''))
                                if email_match:
                                    booking_info['email'] = email_match.group(0)
                                    
                            if not booking_info['phone'] and re.search(r'\d{10}', convo.get('user_message', '')):
                                phone_match = re.search(phone_pattern, convo.get('user_message', ''))
                                if phone_match:
                                    booking_info['phone'] = phone_match.group(0)
                except Exception as e:
                    print(f"Error retrieving user information from conversations: {str(e)}")
            
            # Check if we have enough information
            if not booking_info['name'] or not booking_info['phone']:
                return {
                    "success": False,
                    "message": "I need more information to complete your booking. Could you please provide your name and phone number?",
                    "should_start_booking": True
                }
            
            # Set defaults for missing fields
            booking_data = {
                "name": booking_info['name'],
                "email": booking_info['email'] or "",
                "phone": booking_info['phone'],
                "service": booking_info['service'] or "Not specified",
                "location": booking_info['preferred_location'] or "Not specified",
                "seats": booking_info['seats'],
                "message": booking_info['message'],
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "New",
                "source": "chatbot",
                "notes": f"User ID: {user_id}" if user_id else ""
            }
            
            # Save to Google Sheets
            result = self.sheets_manager.log_booking(booking_data)
            
            if not result:
                return {
                    "success": False,
                    "message": "I encountered an error saving your booking. Please try again or contact our team directly.",
                    "should_start_booking": False
                }
            
            return {
                "success": True,
                "message": f"Thank you for your booking request! I've saved the following details:\n\nName: {booking_data['name']}\nPhone: {booking_data['phone']}\nService: {booking_data['service']}\nLocation: {booking_data['location']}\nSeats: {booking_data['seats']}\n\nOur team will contact you shortly to confirm your booking.",
                "should_start_booking": False,
                "booking_data": booking_data
            }
            
        except Exception as e:
            print(f"Error handling booking request: {str(e)}")
            return {
                "success": False,
                "message": "I encountered an error processing your booking request. Please try again or contact our team directly.",
                "should_start_booking": False,
                "error": str(e)
            }
    
    def is_booking_request(self, message: str) -> bool:
        """
        Check if a message is likely a booking request.
        """
        booking_keywords = [
            "book", "schedule", "appointment", "meeting", "consultation",
            "would like to meet", "speak with", "talk to", "discuss",
            "hire", "engage", "services", "reserve", "get a", "sign up",
            "membership", "office", "join", "register", "day pass"
        ]
        
        booking_phrases = [
            "i need a", "i want to book", "i'd like to book", 
            "can i book", "looking to book", "interested in booking",
            "how do i book", "i want to reserve", "need to reserve",
            "can i get a", "would like to sign up", "interested in getting"
        ]
        
        # Exclude address-related queries
        address_keywords = [
            "address", "location address", "office address", "full address", 
            "where exactly", "directions to", "how to reach", "where is",
            "get address", "need address", "reach there", "where are you"
        ]
        
        message_lower = message.lower()
        
        # First check if it's an address request (should not trigger booking flow)
        if any(keyword in message_lower for keyword in address_keywords):
            return False
            
        # Check for booking phrases (stronger indicators)
        for phrase in booking_phrases:
            if phrase in message_lower:
                # Make sure they're not just asking about the booking process
                if "how do i" in message_lower and not any(service.lower() in message_lower for service in self.services):
                    continue
                return True
        
        # Check for booking keywords (weaker indicators)
        if any(keyword in message_lower for keyword in booking_keywords):
            # Only return true if more than one keyword is present, to reduce false positives
            count = sum(1 for keyword in booking_keywords if keyword in message_lower)
            return count > 1
        
        return False 

def validate_booking_info(booking_info):
    """Validate booking information"""
    locations = ["cunningham", "arekere", "hulimavu"]
    
    location = booking_info.get("preferred_location", "").lower()
    if location and location not in locations:
        return False, "Invalid location selected"
    
    if location:
        if location == "cunningham":
            booking_info["preferred_location"] = "Cunningham Road"
        elif location == "arekere":
            booking_info["preferred_location"] = "Arekere"
        elif location == "hulimavu":
            booking_info["preferred_location"] = "Hulimavu"
    
    # ... rest of the function remains the same ... 