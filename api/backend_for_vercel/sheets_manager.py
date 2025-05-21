import os
import json
import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
import gspread
from google.oauth2 import service_account
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Define a simple service account generator for Vercel
    def generate_service_account():
        service_account_env = os.getenv("GOOGLE_SERVICE_ACCOUNT")
        if not service_account_env:
            return False
        try:
            service_account_data = json.loads(service_account_env)
            with open("service_account.json", "w") as f:
                json.dump(service_account_data, f, indent=2)
            return True
        except Exception:
            return False

# Try both import methods for better compatibility
try:
    from google.oauth2.service_account import Credentials as GoogleCredentials
except ImportError:
    print("Could not import google.oauth2.service_account, will fallback to oauth2client")
    GoogleCredentials = None

try:
    from oauth2client.service_account import ServiceAccountCredentials
except ImportError:
    print("Could not import oauth2client.service_account, will fallback to google-auth")
    ServiceAccountCredentials = None

try:
    from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound
except ImportError:
    # Define fallback exception classes if gspread.exceptions can't be imported
    class SpreadsheetNotFound(Exception):
        pass
    class WorksheetNotFound(Exception):
        pass

class GoogleSheetsManager:
    """Manager for Google Sheets interactions."""
    
    # Define scopes
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self):
        """Initialize the GoogleSheetsManager with credentials."""
        try:
            # Try to get the service account details from environment variables first
            service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT")
            if service_account_json:
                # Use credentials directly from environment variable
                try:
                    import json
                    service_account_info = json.loads(service_account_json)
                    self.credentials = service_account.Credentials.from_service_account_info(
                        service_account_info,
                        scopes=self.SCOPES
                    )
                    print("Using service account from environment variable")
                except Exception as e:
                    print(f"Error using service account from environment variable: {str(e)}")
                    # Fall back to file-based authentication
                    self.credentials = service_account.Credentials.from_service_account_file(
                        'service_account.json',
                        scopes=self.SCOPES
                    )
                    print("Using service account from file")
            else:
                # Fall back to file-based authentication
                self.credentials = service_account.Credentials.from_service_account_file(
                    'service_account.json',
                    scopes=self.SCOPES
                )
                print("Using service account from file (no env var)")

            # Authorize and get sheet ID from environment variables
            self.gc = gspread.authorize(self.credentials)
            self.sheet_id = os.getenv("GOOGLE_SHEET_ID", "your_sheet_id")  # Get sheet ID from environment
            self.spreadsheet = self.gc.open_by_key(self.sheet_id)
            self.conversations_sheet = self.spreadsheet.worksheet("Conversations")
            self.feedback_sheet = self.spreadsheet.worksheet("Feedback")
            self.bookings_sheet = self.spreadsheet.worksheet("Bookings")
            self.users_sheet = self.spreadsheet.worksheet("Users")
            
            # Ensure we have a chat messages sheet
            try:
                self.chat_messages_sheet = self.spreadsheet.worksheet("ChatMessages")
            except gspread.exceptions.WorksheetNotFound:
                # Create the sheet if it doesn't exist
                self.chat_messages_sheet = self.spreadsheet.add_worksheet(
                    title="ChatMessages", 
                    rows=1000, 
                    cols=6
                )
                # Add headers
                self.chat_messages_sheet.append_row([
                    "timestamp", "conversation_id", "user_id", "sender", "message", "metadata"
                ])
            
        except Exception as e:
            print(f"Error initializing Google Sheets manager: {str(e)}")
            # Create dummy methods that don't fail if sheets are unavailable
            self.gc = None
            self.spreadsheet = None
    
    def _init_sheets(self):
        """Initialize the sheets structure if needed"""
        if not self.enabled:
            return
            
        try:
            # Check if Users sheet exists, create it if not
            try:
                self.sheets.values().get(
                    spreadsheetId=self.conversation_sheet_id,
                    range='Users!A1:A1'
                ).execute()
            except Exception:
                # Create Users sheet with headers
                self.create_sheet("Users", ["Timestamp", "Name", "Phone", "Source", "Session ID"])
                print("Created new Users sheet")
            
            # Check if ChatHistory sheet exists, create it if not
            try:
                self.sheets.values().get(
                    spreadsheetId=self.conversation_sheet_id,
                    range='ChatHistory!A1:A1'
                ).execute()
            except Exception:
                # Create ChatHistory sheet with headers
                self.create_sheet("ChatHistory", ["Timestamp", "Conversation ID", "User ID", "Sender", "Message"])
                print("Created new ChatHistory sheet")
            
            # Check existing sheets for backward compatibility
            # These were implemented in the original code
            try:
                self.sheets.values().get(
                    spreadsheetId=self.conversation_sheet_id,
                    range='Conversations!A1:A1'
                ).execute()
            except Exception:
                # Create Conversations sheet with headers
                self.create_sheet("Conversations", ["Timestamp", "User ID", "User Message", "Bot Response", "Source"])
                print("Created new Conversations sheet")
                
            # Check Bookings sheet exists and has the right headers
            try:
                # Get the first row to check headers
                result = self.sheets.values().get(
                    spreadsheetId=self.booking_sheet_id,
                    range='Bookings!A1:J1'
                ).execute()
                
                # Check if "Number of Seats" or "Seats" column exists
                headers = result.get('values', [[]])[0]
                has_seats_column = "Seats" in headers or "Number of Seats" in headers
                
                if not has_seats_column:
                    print("Bookings sheet exists but is missing the Seats column. Recreating...")
                    # Delete the existing sheet
                    sheet_id = self._get_sheet_id_by_name("Bookings")
                    if sheet_id:
                        self._delete_sheet(sheet_id)
                    # Create new sheet with updated headers
                    self.create_sheet("Bookings", ["Timestamp", "Name", "Email", "Phone", "Location", "Service", "Seats", "Requested DateTime", "Status", "Notes"])
                    print("Recreated Bookings sheet with Seats column")
            except Exception as e:
                # Create Bookings sheet with headers
                print(f"Error checking Bookings sheet: {str(e)}")
                self.create_sheet("Bookings", ["Timestamp", "Name", "Email", "Phone", "Location", "Service", "Seats", "Requested DateTime", "Status", "Notes"])
                print("Created new Bookings sheet with Seats column")
                
        except Exception as e:
            print(f"Error initializing sheets: {str(e)}")
            
    def _get_sheet_id_by_name(self, sheet_name):
        """Get the sheet ID by name"""
        if not self.enabled:
            return None
            
        try:
            # Get all sheets
            spreadsheet = self.sheets.get(
                spreadsheetId=self.booking_sheet_id
            ).execute()
            
            # Find the sheet with the given name
            for sheet in spreadsheet.get('sheets', []):
                if sheet.get('properties', {}).get('title') == sheet_name:
                    return sheet.get('properties', {}).get('sheetId')
                    
            return None
        except Exception as e:
            print(f"Error getting sheet ID by name: {str(e)}")
            return None
            
    def _delete_sheet(self, sheet_id):
        """Delete a sheet by ID"""
        if not self.enabled or sheet_id is None:
            return False
            
        try:
            # Delete the sheet
            request = {
                "requests": [{
                    "deleteSheet": {
                        "sheetId": sheet_id
                    }
                }]
            }
            
            self.sheets.batchUpdate(
                spreadsheetId=self.booking_sheet_id,
                body=request
            ).execute()
            
            return True
        except Exception as e:
            print(f"Error deleting sheet: {str(e)}")
            return False
    
    def create_sheet(self, sheet_name, headers):
        """Create a new sheet with the given name and headers"""
        if not self.enabled:
            return False
            
        try:
            # Add a new sheet
            request = {
                "requests": [{
                    "addSheet": {
                        "properties": {
                            "title": sheet_name
                        }
                    }
                }]
            }
            
            self.sheets.batchUpdate(
                spreadsheetId=self.conversation_sheet_id,
                body=request
            ).execute()
            
            # Add headers
            self.sheets.values().update(
                spreadsheetId=self.conversation_sheet_id,
                range=f'{sheet_name}!A1',
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            
            return True
        except Exception as e:
            print(f"Error creating sheet {sheet_name}: {str(e)}")
            return False
    
    def log_user_registration(self, user_data: Dict[str, Any]) -> bool:
        """
        Log a user registration to Google Sheets
        
        Args:
            user_data: Dictionary containing user information (name, phone, etc.)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.enabled:
            print("Google Sheets logging disabled. Skipping user registration logging.")
            return False
            
        try:
            # Prepare the data
            timestamp = user_data.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            # Create a well-structured row with user information
            row = [
                timestamp,  # Timestamp
                user_data.get('name', ''),  # Name
                user_data.get('phone', ''),  # Phone
                user_data.get('source', 'chatbot_widget'),  # Source
                user_data.get('session_id', '')  # Session ID
            ]
            
            # Append to the Users sheet
            try:
                result = self.sheets.values().append(
                    spreadsheetId=self.user_sheet_id,
                    range='Users!A:E',  # Using the Users sheet with added Session ID column
                    valueInputOption='RAW',
                    insertDataOption='INSERT_ROWS',
                    body={'values': [row]}
                ).execute()
                
                # Log the result for debugging
                print(f"Logged user registration to Google Sheets: {result.get('updates').get('updatedRange')}")
                return True
                
            except Exception as e:
                if "Quota exceeded" in str(e):
                    print(f"Warning: API rate limit exceeded. Failed to log user registration: {str(e)}")
                    # Consider it a "soft" success since this is a transient error
                    return True
                else:
                    raise
            
        except Exception as e:
            print(f"Error logging user registration to Google Sheets: {str(e)}")
            return False

    def log_conversation(self, user_message: str, bot_response: str, source: str, user_id: Optional[str] = None):
        """
        Log a conversation exchange to Google Sheets
        
        Args:
            user_message: The message from the user
            bot_response: The response from the bot
            source: The source of the response (e.g., 'openai', 'fine_tuned', etc.)
            user_id: Optional user identifier
        """
        if not self.enabled:
            print("Google Sheets logging disabled. Skipping conversation logging.")
            return
            
        try:
            # Prepare the data
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = [
                now,  # Timestamp
                user_id if user_id else 'anonymous',  # User ID
                user_message,  # User message
                bot_response,  # Bot response
                source  # Response source
            ]
            
            # Append to the sheet
            try:
                result = self.sheets.values().append(
                    spreadsheetId=self.conversation_sheet_id,
                    range='Conversations!A:E',  # Using a separate sheet for conversations
                    valueInputOption='RAW',
                    insertDataOption='INSERT_ROWS',
                    body={'values': [row]}
                ).execute()
                
                # Log the result for debugging
                print(f"Logged conversation to Google Sheets: {result.get('updates').get('updatedRange')}")
            except Exception as e:
                if "Quota exceeded" in str(e):
                    print(f"Warning: API rate limit exceeded. Failed to log conversation: {str(e)}")
                else:
                    raise
            
        except Exception as e:
            print(f"Error logging conversation to Google Sheets: {str(e)}")
    
    def log_booking(self, booking_data: Dict[str, Any]):
        """
        Log a booking to Google Sheets
        
        Args:
            booking_data: Dictionary containing booking information
        """
        if not self.enabled:
            print("Google Sheets logging disabled. Skipping booking logging.")
            return False
            
        try:
            # Prepare the data
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Create a well-structured row with all booking information
            row = [
                now,  # Timestamp
                booking_data.get('name', ''),
                booking_data.get('email', ''),
                booking_data.get('phone', ''),
                booking_data.get('location', ''),
                booking_data.get('service', ''),
                booking_data.get('seats', '1'),  # Default to 1 seat if not provided
                booking_data.get('datetime', booking_data.get('message', '')),  # Use message as fallback for datetime
                booking_data.get('status', 'Pending'),
                booking_data.get('notes', '')
            ]
            
            # Append to the bookings sheet
            try:
                result = self.sheets.values().append(
                    spreadsheetId=self.booking_sheet_id,
                    range='Bookings!A:J',  # Updated range to include the seats column
                    valueInputOption='RAW',
                    insertDataOption='INSERT_ROWS',
                    body={'values': [row]}
                ).execute()
                
                # Log the result for debugging
                print(f"Logged booking to Google Sheets: {result.get('updates').get('updatedRange')}")
                return True
            except Exception as e:
                if "Quota exceeded" in str(e):
                    print(f"Warning: API rate limit exceeded. Failed to log booking: {str(e)}")
                    # Consider it a "soft" success since this is a transient error
                    return True
                else:
                    raise
            
        except Exception as e:
            print(f"Error logging booking to Google Sheets: {str(e)}")
            return False
            
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversations from Google Sheets
        
        Args:
            limit: Maximum number of conversations to retrieve
            
        Returns:
            List of conversation dictionaries
        """
        if not self.enabled:
            print("Google Sheets logging disabled. Cannot retrieve conversations.")
            return []
            
        try:
            # Get the data from the sheet
            result = self.sheets.values().get(
                spreadsheetId=self.conversation_sheet_id,
                range='Conversations!A:E'
            ).execute()
            
            # Extract the values
            rows = result.get('values', [])
            
            # Skip header row if it exists
            if rows and rows[0][0] == 'Timestamp':
                rows = rows[1:]
                
            # Format the data
            conversations = []
            for row in rows[-limit:]:  # Get only the most recent ones
                # Make sure the row has enough columns
                if len(row) >= 5:
                    conversations.append({
                        'timestamp': row[0],
                        'user_id': row[1],
                        'user_message': row[2],
                        'bot_response': row[3],
                        'source': row[4]
                    })
                    
            return conversations
            
        except Exception as e:
            print(f"Error retrieving conversations from Google Sheets: {str(e)}")
            return []

    def get_faqs(self) -> List[Dict[str, str]]:
        """Get all FAQs from the Google Sheet"""
        if not self.enabled or not self.conversation_sheet_id:
            print("Google Sheets not configured")
            return []
            
        try:
            # Get the data from the sheet
            result = self.sheets.values().get(
                spreadsheetId=self.conversation_sheet_id,
                range='FAQ!A:B'
            ).execute()
            
            # Extract the values
            rows = result.get('values', [])
            
            # Skip header row if it exists
            if rows and rows[0][0] == 'Question':
                rows = rows[1:]
                
            # Format the data
            faqs = []
            for row in rows:
                if len(row) >= 2:
                    faqs.append({
                        'question': row[0],
                        'answer': row[1]
                    })
                    
            return faqs
        except Exception as e:
            print(f"Error getting FAQs from Google Sheets: {str(e)}")
            return []
            
    def save_booking(self, name: str, email: str, phone: str, datetime_str: str, seats: str = "1", user_id: Optional[str] = None) -> bool:
        """Save booking details to Google Sheets"""
        if not self.enabled:
            print("Google Sheets not configured")
            return False
            
        try:
            # Prepare the data
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Create a well-structured row with booking information
            row = [
                now,  # Timestamp
                name,
                email,
                phone,
                "",  # Empty location
                "",  # Empty service
                seats, # Number of seats
                datetime_str,  # Datetime string
                "New",  # Initial status
                user_id or ""  # User ID as notes
            ]
            
            # Append to the bookings sheet
            result = self.sheets.values().append(
                spreadsheetId=self.booking_sheet_id,
                range='Bookings!A:J',  # Updated range to include the seats column
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': [row]}
            ).execute()
            
            # Log the result for debugging
            print(f"Saved booking to Google Sheets: {result.get('updates').get('updatedRange')}")
            return True
        except Exception as e:
            print(f"Error saving booking to Google Sheets: {str(e)}")
            return False
     
    def get_recent_bookings(self, limit: int = 10) -> List[Dict]:
        """Get recent bookings from Google Sheets"""
        if not self.enabled:
            print("Google Sheets not configured")
            return []
            
        try:
            # Get the data from the sheet
            result = self.sheets.values().get(
                spreadsheetId=self.booking_sheet_id,
                range='Bookings!A:J'  # Updated range to include the seats column
            ).execute()
            
            # Extract the values
            rows = result.get('values', [])
            
            # Skip header row if it exists
            if rows and rows[0][0] == 'Timestamp':
                rows = rows[1:]
                
            # Format the data
            bookings = []
            for row in rows[-limit:]:  # Get only the most recent ones
                # Make sure the row has enough columns
                if len(row) >= 9:
                    booking_data = {
                        'timestamp': row[0],
                        'name': row[1],
                        'email': row[2],
                        'phone': row[3],
                        'location': row[4] if len(row) > 4 else "",
                        'service': row[5] if len(row) > 5 else "",
                        'seats': row[6] if len(row) > 6 else "1",
                        'datetime': row[7] if len(row) > 7 else "",
                        'status': row[8] if len(row) > 8 else "New"
                    }
                    # Add notes if available
                    if len(row) > 9:
                        booking_data['notes'] = row[9]
                    
                    bookings.append(booking_data)
                    
            return bookings
        except Exception as e:
            print(f"Error getting recent bookings: {str(e)}")
            return []

    def log_chat_message(self, conversation_id: str, user_id: str, sender: str, message: str) -> bool:
        """
        Log an individual chat message to the ChatHistory sheet
        
        Args:
            conversation_id: Unique ID for the conversation
            user_id: User identifier
            sender: Who sent the message ('user' or 'bot')
            message: The message content
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.enabled:
            print("Google Sheets logging disabled. Skipping chat history logging.")
            return False
            
        try:
            # Prepare the data
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Create a well-structured row with message data
            row = [
                timestamp,           # Timestamp
                conversation_id,     # Conversation ID
                user_id or 'anonymous',  # User ID
                sender,              # Sender (user/bot)
                message              # Message content
            ]
            
            # Append to the ChatHistory sheet
            try:
                result = self.sheets.values().append(
                    spreadsheetId=self.conversation_sheet_id,
                    range='ChatHistory!A:E',  # Using the ChatHistory sheet
                    valueInputOption='RAW',
                    insertDataOption='INSERT_ROWS',
                    body={'values': [row]}
                ).execute()
                
                # Log the result for debugging
                print(f"Logged chat message to history: {result.get('updates').get('updatedRange')}")
                return True
                
            except Exception as e:
                if "Quota exceeded" in str(e):
                    print(f"Warning: API rate limit exceeded. Failed to log chat history: {str(e)}")
                    # Consider it a "soft" success since this is a transient error
                    return True
                else:
                    raise
            
        except Exception as e:
            print(f"Error logging chat message to history: {str(e)}")
            return False
            
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get the complete history of a specific conversation
        
        Args:
            conversation_id: The unique conversation identifier
            
        Returns:
            List of message dictionaries in chronological order
        """
        if not self.enabled:
            print("Google Sheets logging disabled. Cannot retrieve conversation history.")
            return []
            
        try:
            # Get the data from the sheet
            result = self.sheets.values().get(
                spreadsheetId=self.conversation_sheet_id,
                range='ChatHistory!A:E'
            ).execute()
            
            # Extract the values
            rows = result.get('values', [])
            
            # Skip header row if it exists
            if rows and rows[0][0] == 'Timestamp':
                rows = rows[1:]
                
            # Filter messages for the specific conversation
            conversation_messages = []
            for row in rows:
                # Check if this message belongs to the requested conversation
                if len(row) >= 5 and row[1] == conversation_id:
                    conversation_messages.append({
                        'timestamp': row[0],
                        'conversation_id': row[1],
                        'user_id': row[2],
                        'sender': row[3],
                        'message': row[4]
                    })
                    
            return conversation_messages
            
        except Exception as e:
            print(f"Error retrieving conversation history from Google Sheets: {str(e)}")
            return [] 