"""
Anthill IQ Chatbot Backend Module
This module contains the backend logic for the Anthill IQ Chatbot.

Modified for Vercel serverless deployment.
"""

# Version
__version__ = '1.0.0'

# Import the main components
from .chat import ChatManager
from .booking import BookingHandler
from .sheets_manager import GoogleSheetsManager
from .fine_tuning import FineTuningManager

# This file makes the backend directory a proper Python package
# It can be empty, but its presence is important

# Version information
 