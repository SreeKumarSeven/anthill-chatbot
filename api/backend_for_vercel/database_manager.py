import os
import json
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, MetaData, Table, and_, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# PostgreSQL connection string from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:uEutQJRqyRbgOlzwhsGGgczYXaeBqgxI@yamabiko.proxy.rlwy.net:14599/railway")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Define models
class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    user_id = Column(String(100))
    user_message = Column(Text)
    bot_response = Column(Text)
    source = Column(String(50))
    
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    name = Column(String(100))
    phone = Column(String(50))
    email = Column(String(100))
    source = Column(String(50))
    session_id = Column(String(100))
    
class Booking(Base):
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(50))
    location = Column(String(100))
    service = Column(String(100))
    seats = Column(String(10))
    requested_datetime = Column(String(100))
    status = Column(String(50))
    notes = Column(Text)
    
class FAQ(Base):
    __tablename__ = 'faqs'
    
    id = Column(Integer, primary_key=True)
    question = Column(Text)
    answer = Column(Text)

class DatabaseManager:
    """Manager for PostgreSQL database interactions."""
    
    def __init__(self):
        """Initialize the DatabaseManager with PostgreSQL connection."""
        try:
            # Create tables if they don't exist
            Base.metadata.create_all(engine)
            print("Database initialized successfully")
            self.enabled = True
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            self.enabled = False
    
    def log_conversation(self, user_message: str, bot_response: str, source: str, user_id: Optional[str] = None):
        """
        Log a conversation exchange to the database
        
        Args:
            user_message: The message from the user
            bot_response: The response from the bot
            source: The source of the response (e.g., 'openai', 'fine_tuned', etc.)
            user_id: Optional user identifier
        """
        if not self.enabled:
            print("Database logging disabled. Skipping conversation logging.")
            return
            
        try:
            session = Session()
            conversation = Conversation(
                user_id=user_id if user_id else 'anonymous',
                user_message=user_message,
                bot_response=bot_response,
                source=source
            )
            session.add(conversation)
            session.commit()
            session.close()
            print(f"Logged conversation to database")
        except Exception as e:
            print(f"Error logging conversation to database: {str(e)}")
    
    def log_user_registration(self, user_data: Dict[str, Any]) -> bool:
        """
        Log a user registration to the database
        
        Args:
            user_data: Dictionary containing user information (name, phone, etc.)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.enabled:
            print("Database logging disabled. Skipping user registration logging.")
            return False
            
        try:
            session = Session()
            user = User(
                name=user_data.get('name', ''),
                phone=user_data.get('phone', ''),
                email=user_data.get('email', ''),
                source=user_data.get('source', 'chatbot_widget'),
                session_id=user_data.get('session_id', '')
            )
            session.add(user)
            session.commit()
            user_id = user.id
            session.close()
            
            print(f"Logged user registration to database with ID: {user_id}")
            return True
                
        except Exception as e:
            print(f"Error logging user registration to database: {str(e)}")
            return False
    
    def log_booking(self, booking_data: Dict[str, Any]) -> bool:
        """
        Log a booking to the database
        
        Args:
            booking_data: Dictionary containing booking information
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.enabled:
            print("Database logging disabled. Skipping booking logging.")
            return False
            
        try:
            session = Session()
            booking = Booking(
                name=booking_data.get('name', ''),
                email=booking_data.get('email', ''),
                phone=booking_data.get('phone', ''),
                location=booking_data.get('location', ''),
                service=booking_data.get('service', ''),
                seats=booking_data.get('seats', '1'),
                requested_datetime=booking_data.get('datetime', booking_data.get('message', '')),
                status=booking_data.get('status', 'Pending'),
                notes=booking_data.get('notes', '')
            )
            session.add(booking)
            session.commit()
            booking_id = booking.id
            session.close()
            
            print(f"Logged booking to database with ID: {booking_id}")
            return True
                
        except Exception as e:
            print(f"Error logging booking to database: {str(e)}")
            return False
    
    def get_faqs(self) -> List[Dict[str, str]]:
        """Get all FAQs from the database"""
        if not self.enabled:
            print("Database not configured")
            return []
            
        try:
            session = Session()
            faqs_query = session.query(FAQ).all()
            
            # Format the data
            faqs = []
            for faq in faqs_query:
                faqs.append({
                    'Question': faq.question,
                    'Answer': faq.answer
                })
            
            session.close()
            return faqs
        except Exception as e:
            print(f"Error getting FAQs from database: {str(e)}")
            return []
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversations from the database
        
        Args:
            limit: Maximum number of conversations to retrieve
            
        Returns:
            List of conversation dictionaries
        """
        if not self.enabled:
            print("Database access disabled. Cannot retrieve conversations.")
            return []
            
        try:
            session = Session()
            conversations_query = session.query(Conversation).order_by(Conversation.timestamp.desc()).limit(limit).all()
            
            # Format the data
            conversations = []
            for conv in conversations_query:
                conversations.append({
                    'timestamp': conv.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    'user_id': conv.user_id,
                    'user_message': conv.user_message,
                    'bot_response': conv.bot_response,
                    'source': conv.source
                })
            
            session.close()
            return conversations
            
        except Exception as e:
            print(f"Error retrieving conversations from database: {str(e)}")
            return []
    
    def get_recent_bookings(self, limit: int = 10) -> List[Dict]:
        """Get recent bookings from the database"""
        if not self.enabled:
            print("Database not configured")
            return []
            
        try:
            session = Session()
            bookings_query = session.query(Booking).order_by(Booking.timestamp.desc()).limit(limit).all()
            
            # Format the data
            bookings = []
            for booking in bookings_query:
                bookings.append({
                    'timestamp': booking.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    'name': booking.name,
                    'email': booking.email,
                    'phone': booking.phone,
                    'location': booking.location,
                    'service': booking.service,
                    'seats': booking.seats,
                    'datetime': booking.requested_datetime,
                    'status': booking.status,
                    'notes': booking.notes
                })
            
            session.close()
            return bookings
        except Exception as e:
            print(f"Error getting recent bookings: {str(e)}")
            return [] 