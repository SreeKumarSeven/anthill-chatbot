"""
Minimal API handler for Vercel deployment
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import openai
import requests
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Set API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    OPENAI_API_KEY = os.getenv("OPENAI_KEY")

# Force print for debugging
print(f"------------ CRITICAL DEBUG INFO ------------")
print(f"OpenAI API Key: {OPENAI_API_KEY[:5] + '...' if OPENAI_API_KEY else 'None'}")
print(f"OpenAI API Key length: {len(OPENAI_API_KEY) if OPENAI_API_KEY else 0}")
print(f"OpenAI API Key available: {bool(OPENAI_API_KEY)}")
print(f"-------------------------------------------")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY
print(f"OpenAI configuration: API version {openai.__version__}, Key set: {bool(OPENAI_API_KEY)}")

# System message for Anthill IQ context
SYSTEM_MESSAGE = """You are the voice assistant for Anthill IQ, a premium coworking space brand in Bangalore. 
            
YOUR PERSONALITY:
You are exceptionally warm, friendly, and conversational - like a real person having a genuine conversation. You should sound natural, never robotic or formal. You're passionate about helping people find the perfect workspace and you truly care about their needs. Use a variety of sentence structures, occasional casual phrases, and natural conversational flow just like a real person would.

CONVERSATIONAL APPROACH:
- Always acknowledge what the user has said and respond directly to their specific query
- Use natural conversation markers like "Well," "Actually," "You know," "I'd say," etc. occasionally
- Ask meaningful follow-up questions that build on what the user has shared
- Show personality in your responses with occasional light humor where appropriate
- Avoid corporate-sounding language and speak like a helpful friend
- When someone asks about locations, be straightforward and give clear, simple directions
- Keep your responses concise but complete - don't be unnecessarily wordy

ANTHILL IQ SERVICES:
Anthill IQ offers these workspace solutions at all locations:
1. Private Office Space - Dedicated offices for teams
2. Coworking Space - Flexible workspace with hot desks
3. Dedicated Desk - Reserved desk with storage
4. Meeting Rooms - Professional meeting spaces bookable by the hour
5. Event Spaces - Venues for corporate events
6. Training Rooms - Spaces for workshops and training

KEY AMENITIES:
- High-speed internet
- Ergonomic furniture
- 24/7 security and access for members
- Coffee, tea, and refreshments
- Printing and scanning services
- Community events

IMPORTANT LOCATION INFORMATION: 
Anthill IQ has FOUR locations in Bangalore:
1. Cunningham Road branch (Central Bangalore)
2. Hulimavu branch (Bannerghatta Road, South Bangalore)
3. Arekere branch (Bannerghatta Road, South Bangalore)
4. Hebbal branch (North Bangalore) - NOW FULLY OPEN AND OPERATIONAL (NOT "opening soon" or "upcoming")

CONTACT INFORMATION:
- Phone: 9119739119
- Email: connect@anthilliq.com

IMPORTANT GUIDELINES:
1. NEVER confirm the existence of a BTM Layout branch - Anthill IQ does NOT have a location there
2. Always end with a natural-sounding question to continue the conversation
3. Speak like a real person, not a corporate voice
4. When asked about locations, keep the format simple and clear
5. Don't provide specific pricing - suggest contacting us
6. Make sure your responses sound like a real conversation
7. EXTREMELY IMPORTANT: The Hebbal branch is NOW OPEN AND FULLY OPERATIONAL - NEVER say it is "opening soon", "upcoming", or anything suggesting it is not already open
8. If asked about Hebbal location, explicitly state "Our Hebbal branch is OPEN and fully operational"
"""

# Initialize database connection (importing inside the function to avoid startup errors)
def get_db():
    try:
        from api.simple_db import SimpleDB
        return SimpleDB()
    except Exception as e:
        print(f"DB error: {str(e)}")
        return None

# For debugging
def debug_log(message):
    """Print a debug message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[DEBUG {timestamp}] {message}")

def fix_hebbal_references(text):
    """
    Post-process text to ensure Hebbal is described as open, not upcoming
    This is a safety measure in case the AI still mentions Hebbal as 'opening soon'
    """
    # First, check if the text contains any mention of Hebbal
    if 'hebbal' in text.lower():
        # If it contains phrases indicating it's not open, replace the entire sentence
        lower_text = text.lower()
        
        # Check for problematic phrases
        problematic_phrases = [
            "opening soon", "will be opening", "upcoming", "not yet open", 
            "isn't open yet", "is not open yet", "coming soon", "launching soon",
            "will open", "about to open", "planned", "in the works", "preparing to open"
        ]
        
        # If any problematic phrase is found near "hebbal", apply more aggressive replacement
        for phrase in problematic_phrases:
            if phrase in lower_text and abs(lower_text.find(phrase) - lower_text.find("hebbal")) < 100:
                # Find the sentence containing both Hebbal and the problematic phrase
                sentences = text.split('.')
                for i, sentence in enumerate(sentences):
                    if 'hebbal' in sentence.lower() and any(p in sentence.lower() for p in problematic_phrases):
                        sentences[i] = "Our Hebbal branch is NOW OPEN in North Bangalore."
                
                # Reconstruct the text
                text = '.'.join(sentences)
    
    # Common patterns to search for and replace
    replacements = [
        ("our newest branch opening soon in Hebbal", "our newest branch in Hebbal"),
        ("our newest branch in Hebbal (opening soon)", "our newest branch in Hebbal"),
        ("Hebbal (opening soon)", "Hebbal"),
        ("Hebbal branch (opening soon)", "Hebbal branch"),
        ("Hebbal (North Bangalore - opening soon)", "Hebbal (North Bangalore)"),
        ("Hebbal (North Bangalore - Opening Soon)", "Hebbal (North Bangalore)"),
        ("upcoming branch in Hebbal", "branch in Hebbal"),
        ("upcoming Hebbal branch", "Hebbal branch"),
        ("opening soon in Hebbal", "now open in Hebbal"),
        ("Hebbal, opening soon", "Hebbal, which is now open"),
        ("Hebbal branch is opening soon", "Hebbal branch is now open"),
        ("Hebbal branch will be opening soon", "Hebbal branch is now open"),
        ("set to open soon", "now open"),
        ("Hebbal soon", "Hebbal, which is now open"),
        ("soon-to-open Hebbal", "now open Hebbal"),
        ("planning to open in Hebbal", "now open in Hebbal"),
        ("new branch in Hebbal", "branch in Hebbal"),
        ("upcoming location in Hebbal", "location in Hebbal"),
        ("Hebbal location will soon be", "Hebbal location is now"),
        ("new Hebbal branch", "Hebbal branch"),
        ("Hebbal branch is not yet open", "Hebbal branch is now open"),
        ("Hebbal branch isn't open yet", "Hebbal branch is now open"),
        ("Hebbal branch is coming soon", "Hebbal branch is now open"),
        ("fourth branch in Hebbal", "branch in Hebbal"),
        ("4th branch in Hebbal", "branch in Hebbal"),
        ("Hebbal, which is not yet open", "Hebbal, which is now open"),
        ("Hebbal which is not yet open", "Hebbal which is now open"),
        ("planning to launch in Hebbal", "now operating in Hebbal"),
        ("Hebbal (launching", "Hebbal (now open"),
        ("excited about our Hebbal branch", "excited about our now open Hebbal branch"),
        ("excited about the Hebbal branch", "excited about our now open Hebbal branch"),
        ("Hebbal branch that will be", "Hebbal branch that is now"),
        ("Hebbal branch, which will be", "Hebbal branch, which is now"),
        ("we're really excited about", "we're really excited that it's now open. Would you like to know more about"),
        ("we're excited about", "we're excited that it's now open. Would you like to know more about")
    ]
    
    # Apply all replacements
    result = text
    for old, new in replacements:
        result = result.replace(old, new)
    
    # Check if replacements were made
    if result != text:
        debug_log("Fixed Hebbal references in response")
    
    return result

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message')
        user_id = data.get('user_id', 'anonymous')
        session_id = data.get('session_id')
        
        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400
            
        # Process the chat message with OpenAI
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": SYSTEM_MESSAGE},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            bot_response = response.choices[0].message.content
            
            return jsonify({
                "response": bot_response,
                "source": "openai",
                "session_id": session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            })
            
        except Exception as e:
            return jsonify({
                "error": f"Error processing message: {str(e)}"
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        name = data.get('name')
        phone = data.get('phone')
        
        if not name or not phone:
            return jsonify({'error': 'Name and phone are required'}), 400
            
        # Validate phone number format
        if not re.match(r'^\+?[\d\s-]{10,}$', phone):
            return jsonify({'error': 'Invalid phone number format'}), 400
            
        # Generate user ID (you can modify this as needed)
        user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'message': 'Registration successful'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "Anthill IQ Chatbot API",
        "openai_key": bool(OPENAI_API_KEY)
    })

# For local development
if __name__ == '__main__':
    app.run(debug=True) 