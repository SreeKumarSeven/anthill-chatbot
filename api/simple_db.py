"""
Minimal database connection manager for Vercel deployment
"""
import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# PostgreSQL connection string from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:uEutQJRqyRbgOlzwhsGGgczYXaeBqgxI@yamabiko.proxy.rlwy.net:14599/railway")

class SimpleDB:
    """Simple database connection manager using only psycopg2"""
    
    def __init__(self):
        """Initialize DB connection"""
        try:
            # Connect to the database
            self.conn = psycopg2.connect(DATABASE_URL)
            self.conn.autocommit = True
            
            # Create tables if they don't exist
            self._create_tables()
            self.enabled = True
        except Exception as e:
            print(f"DB error: {str(e)}")
            self.enabled = False
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        with self.conn.cursor() as cursor:
            # Create conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id VARCHAR(100),
                    user_message TEXT,
                    bot_response TEXT,
                    source VARCHAR(50)
                )
            """)
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    name VARCHAR(100),
                    phone VARCHAR(50),
                    email VARCHAR(100),
                    source VARCHAR(50),
                    session_id VARCHAR(100)
                )
            """)
    
    def log_conversation(self, user_message, bot_response, source="openai", user_id="anonymous"):
        """Log a conversation to the database"""
        if not self.enabled:
            return False
            
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO conversations (user_id, user_message, bot_response, source)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, user_message, bot_response, source))
            return True
        except Exception:
            return False
    
    def log_user_registration(self, name, phone, email="", source="chatbot", session_id=""):
        """Log user registration to the database"""
        if not self.enabled:
            return False
            
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (name, phone, email, source, session_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, phone, email, source, session_id))
            return True
        except Exception:
            return False
            
    def get_user_by_session(self, session_id):
        """Get user info by session ID"""
        if not self.enabled or not session_id:
            return None
        return {} 