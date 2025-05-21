from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional, List
import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
from backend.chat import ChatManager
from backend.booking import BookingHandler, router as booking_router
from backend.sheets_manager import GoogleSheetsManager

# Load environment variables from .env file
load_dotenv()

# Check if OpenAI API key is available
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("Warning: OPENAI_API_KEY environment variable is not set. Please set it in Heroku config vars.")

app = FastAPI()

# Include routers
app.include_router(booking_router, prefix="/api", tags=["booking"])

# Allow CORS - Updated for more permissive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
    expose_headers=["*"],
)

# Initialize managers
chat_manager = ChatManager()
booking_handler = BookingHandler()
sheets_manager = GoogleSheetsManager()

# Models
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

# New model for user registration
class UserRegistration(BaseModel):
    name: str
    phone: str
    timestamp: Optional[str] = None
    source: Optional[str] = "chatbot_widget"
    session_id: Optional[str] = None

# Legacy BookingRequest model - kept for backwards compatibility
class LegacyBookingRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    service: Optional[str] = None
    message: Optional[str] = None
    user_id: Optional[str] = None

@app.get("/")
async def read_root():
    return {"status": "online", "service": "Anthill IQ Chatbot API"}

@app.get("/api/test-config")
async def test_config():
    """Test endpoint to check configuration"""
    return {
        "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "google_service_account_set": bool(os.getenv("GOOGLE_SERVICE_ACCOUNT")),
        "google_sheet_id_set": bool(os.getenv("GOOGLE_SHEET_ID")),
        "service_account_file_exists": os.path.exists("service_account.json")
    }

@app.post("/api/register-user")
async def register_user(registration: UserRegistration):
    """Register a new user and store their information in Google Sheets"""
    try:
        # Prepare the data for Google Sheets
        registration_data = {
            "name": registration.name,
            "phone": registration.phone,
            "timestamp": registration.timestamp or datetime.now().isoformat(),
            "source": registration.source,
            "session_id": registration.session_id or str(uuid.uuid4())
        }
        
        # Log to Google Sheets
        success = sheets_manager.log_user_registration(registration_data)
        
        if not success:
            print("Warning: Failed to log user registration to Google Sheets")
        
        # Log first system message to the chat history if session_id is provided
        if registration.session_id:
            welcome_message = f"Welcome {registration.name}! I'm the Anthill IQ Assistant. How can I help you today?"
            sheets_manager.log_chat_message(
                conversation_id=registration.session_id,
                user_id="anonymous",
                sender="bot",
                message=welcome_message
            )
        
        return {
            "status": "success",
            "message": "User registration successful",
            "user_id": str(uuid.uuid4()),  # Generate a unique ID for this user
            "session_id": registration.session_id or str(uuid.uuid4())  # Return the session ID
        }
    except Exception as e:
        print(f"Error processing user registration: {str(e)}")
        # Still return success to keep the widget working even if backend fails
        return {
            "status": "success",
            "message": "User registration processed",
            "user_id": str(uuid.uuid4()),
            "session_id": registration.session_id or str(uuid.uuid4())
        }

@app.post("/api/chat")
async def chat_endpoint(chat_request: ChatRequest):
    """Process incoming chat messages"""
    try:
        if not chat_request.message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Generate session ID if not provided
        session_id = chat_request.session_id or str(uuid.uuid4())
        
        print(f"Received message: {chat_request.message}")
        
        # Log the user message to chat history
        sheets_manager.log_chat_message(
            conversation_id=session_id,
            user_id=chat_request.user_id or 'anonymous',
            sender='user',
            message=chat_request.message
        )
        
        # Check if message is a booking request
        if booking_handler.is_booking_request(chat_request.message):
            print("Detected booking request")
            booking_result = booking_handler.handle_booking_request(
                chat_request.message, 
                chat_request.user_id
            )
            
            # Log the bot response to chat history
            sheets_manager.log_chat_message(
                conversation_id=session_id,
                user_id=chat_request.user_id or 'anonymous',
                sender='bot',
                message=booking_result.get("message", "Let me help you with your booking.")
            )
            
            # Return response with booking flag
            return {
                "response": booking_result.get("message", "I'll help you with booking. What service are you interested in?"),
                "source": "booking",
                "session_id": session_id,
                "should_start_booking": True
            }
        
        try:
            # Process regular chat message
            result = await chat_manager.handle_message(
                chat_request.message, 
                chat_request.user_id
            )
            
            # Log the bot response to chat history
            sheets_manager.log_chat_message(
                conversation_id=session_id,
                user_id=chat_request.user_id or 'anonymous',
                sender='bot',
                message=result["response"]
            )
            
            # Add booking flag if present in the result
            response_data = {
                "response": result["response"],
                "source": result["source"],
                "session_id": session_id
            }
            
            # Include should_start_booking if it's in the result
            if "should_start_booking" in result:
                response_data["should_start_booking"] = result["should_start_booking"]
            
            return response_data
            
        except Exception as e:
            import traceback
            print(f"Error in chat handling: {str(e)}")
            print(traceback.format_exc())
            return {
                "response": "I apologize, but I'm having trouble processing your request. Please try again or contact us directly at 9119739119.",
                "source": "error",
                "session_id": session_id,
                "error": str(e)
            }
    except Exception as e:
        import traceback
        print(f"Global error in chat endpoint: {str(e)}")
        print(traceback.format_exc())
        
        # Provide a fallback error response
        return {
            "response": "I'm sorry, I encountered an error processing your request. Please try again or contact our team directly if you need immediate assistance.",
            "source": "error",
            "session_id": session_id or str(uuid.uuid4()),
            "error": str(e)
        }

@app.get("/api/conversation/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """Get the complete history of a specific conversation"""
    try:
        history = sheets_manager.get_conversation_history(conversation_id)
        return {
            "status": "success",
            "conversation_id": conversation_id,
            "messages": history
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/api/stats")
async def get_stats():
    """Get chatbot usage statistics"""
    try:
        recent_conversations = sheets_manager.get_recent_conversations(limit=10)
        recent_bookings = sheets_manager.get_recent_bookings(limit=5)
        
        # Calculate some basic stats
        total_conversations = len(sheets_manager.get_recent_conversations(limit=1000))
        total_bookings = len(sheets_manager.get_recent_bookings(limit=1000))
        
        return {
            "status": "success",
            "stats": {
                "total_conversations": total_conversations,
                "total_bookings": total_bookings,
                "recent_conversations": recent_conversations,
                "recent_bookings": recent_bookings
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/health")
async def health_check():
    """Health check endpoint for Heroku"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    # Start the server (development only - use a proper ASGI server in production)
    # Use port 8080 instead of 8000 to avoid conflicts
    port = int(os.getenv("PORT", "8088"))
    uvicorn.run(app, host="0.0.0.0", port=port) 